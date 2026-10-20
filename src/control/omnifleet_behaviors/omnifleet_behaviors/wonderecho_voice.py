import json
import math
import signal
import time
from functools import partial

import rclpy
from action_msgs.msg import GoalStatusArray
from action_msgs.srv import CancelGoal
from geometry_msgs.msg import Point, Twist
from nav2_msgs.action import BackUp, DriveOnHeading
from omnifleet_interfaces.msg import SteeringAngleCommand
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    QoSProfile,
    ReliabilityPolicy,
    qos_profile_action_status_default,
)
from rclpy.signals import SignalHandlerOptions
from std_msgs.msg import Bool, String
from std_srvs.srv import SetBool

from .voice_commands import (
    COMMANDS,
    DIRECT_MAX_SPEED,
    DIRECT_MIN_SPEED,
    DIRECT_SPEED_STEP,
    MONITORED_ACTIONS,
    VoiceCommand,
    active_action_present,
    direct_motion_segments,
    voice_cancel_required,
)
from .wonderecho_device import WonderEchoDevice, WonderEchoSerialDevice


class WonderEchoVoiceNode(Node):
    ACTION_NAMES = MONITORED_ACTIONS
    CONTROL_FRAME_NAMES = {
        0x01: "欢迎语",
        0x02: "休息语",
        0x04: "增大音量",
        0x05: "减小音量",
        0x06: "最大音量",
        0x07: "中等音量",
        0x08: "最小音量",
        0x09: "开启播报",
        0x0A: "关闭播报",
    }

    def __init__(self):
        super().__init__("omnifleet_t2_wonderecho_voice")
        self._transport = str(
            self.declare_parameter("transport", "serial").value
        ).strip().lower()
        self._serial_port = str(
            self.declare_parameter(
                "serial_port", "/dev/wonderecho_flash"
            ).value
        )
        self._serial_baud = int(
            self.declare_parameter("serial_baud", 115200).value
        )
        self._bus_number = int(self.declare_parameter("bus", 7).value)
        self._address = int(self.declare_parameter("address", 0x34).value)
        self._result_register = int(
            self.declare_parameter("result_register", 0x64).value
        )
        self._speak_register = int(
            self.declare_parameter("speak_register", 0x6E).value
        )
        poll_hz = float(self.declare_parameter("poll_hz", 20.0).value)
        self._reconnect_sec = float(
            self.declare_parameter("reconnect_sec", 2.0).value
        )
        cooldown_sec = float(
            self.declare_parameter("same_id_cooldown_sec", 2.0).value
        )
        self._time_allowance_sec = float(
            self.declare_parameter("time_allowance_sec", 6.0).value
        )
        self._stop_timeout_sec = float(
            self.declare_parameter("stop_timeout_sec", 5.0).value
        )
        self._max_voice_distance = float(
            self.declare_parameter("max_voice_distance", 0.8).value
        )
        self._motion_enabled = bool(
            self.declare_parameter("enable_motion", False).value
        )
        self._motion_backend = str(
            self.declare_parameter("motion_backend", "nav2").value
        ).strip().lower()
        self._cmd_vel_topic = str(
            self.declare_parameter("cmd_vel_topic", "/cmd_vel").value
        ).strip()
        self._direct_publish_hz = float(
            self.declare_parameter("direct_publish_hz", 10.0).value
        )
        self._speak_on_accept = bool(
            self.declare_parameter("speak_on_accept", False).value
        )
        if self._transport not in ("i2c", "serial"):
            raise ValueError("transport must be 'i2c' or 'serial'")
        if self._motion_backend not in ("nav2", "twist"):
            raise ValueError("motion_backend must be 'nav2' or 'twist'")
        if not self._cmd_vel_topic:
            raise ValueError("cmd_vel_topic must not be empty")
        if not 5.0 <= self._direct_publish_hz <= 50.0:
            raise ValueError("direct_publish_hz must be in [5, 50]")
        if poll_hz <= 0.0 or poll_hz > 100.0:
            raise ValueError("poll_hz must be in (0, 100]")
        if self._reconnect_sec <= 0.0:
            raise ValueError("reconnect_sec must be positive")
        if not 0.0 < self._time_allowance_sec <= 10.0:
            raise ValueError("time_allowance_sec must be in (0, 10]")
        if not 0.5 <= self._stop_timeout_sec <= 10.0:
            raise ValueError("stop_timeout_sec must be in [0.5, 10]")
        if not 0.0 < self._max_voice_distance <= 0.8:
            raise ValueError("max_voice_distance must be in (0, 0.8]")

        from .voice_commands import CommandEdgeFilter

        self._edge_filter = CommandEdgeFilter(
            cooldown_sec, cooldown_exempt_ids=(9, 0x7B)
        )
        self._device = None
        self._device_online = False
        self._next_reconnect_at = 0.0
        self._localization_ready = False
        self._lifecycle_ready = False
        self._action_statuses = {name: () for name in self.ACTION_NAMES}
        self._voice_busy = False
        self._active_command = None
        self._active_goal_handle = None
        self._goal_send_future = None
        self._result_future = None
        self._cancel_on_accept = False
        self._stop_generation = 0
        self._stop_waiting = False
        self._stop_pending_responses = 0
        self._stop_deadline = 0.0
        self._stop_not_before = 0.0
        self._stop_unavailable = []
        self._direct_deadline = 0.0
        self._direct_started_at = 0.0
        self._direct_twist = Twist()
        self._direct_segments = ()
        self._direct_segment_index = 0
        self._direct_cruise_speed = DIRECT_MIN_SPEED
        self._direct_zero_burst = 0
        self._cmd_vel_publisher = None
        self._steering_publisher = None

        self._action_clients = {}
        self._cancel_clients = {}
        if self._motion_backend == "nav2":
            self._action_clients = {
                "drive_on_heading": ActionClient(
                    self, DriveOnHeading, "drive_on_heading"
                ),
                "backup": ActionClient(self, BackUp, "backup"),
            }
            self._cancel_clients = {
                name: self.create_client(
                    CancelGoal, f"/{name}/_action/cancel_goal"
                )
                for name in self.ACTION_NAMES
            }
        else:
            self._cmd_vel_publisher = self.create_publisher(
                Twist, self._cmd_vel_topic, 10
            )
            self._steering_publisher = self.create_publisher(
                SteeringAngleCommand,
                "/omnifleet_t2/chassis/steering_angle_cmd",
                10,
            )

        latched_qos = QoSProfile(depth=1)
        latched_qos.reliability = ReliabilityPolicy.RELIABLE
        latched_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self._recognized_publisher = self.create_publisher(
            String, "/omnifleet_t2/voice/recognized", latched_qos
        )
        self._status_publisher = self.create_publisher(
            String, "/omnifleet_t2/voice/status", latched_qos
        )
        if self._motion_backend == "nav2":
            self.create_subscription(
                Bool,
                "/omnifleet_t2/system/localization_ready",
                partial(self._on_readiness, "localization"),
                latched_qos,
            )
            self.create_subscription(
                Bool,
                "/omnifleet_t2/system/lifecycle_ready",
                partial(self._on_readiness, "lifecycle"),
                latched_qos,
            )
            for name in self.ACTION_NAMES:
                self.create_subscription(
                    GoalStatusArray,
                    f"/{name}/_action/status",
                    partial(self._on_action_status, name),
                    qos_profile_action_status_default,
                )
        self.create_service(
            SetBool, "/omnifleet_t2/voice/enable_motion", self._set_motion_enabled
        )
        self.create_timer(1.0 / poll_hz, self._poll_device)
        if self._motion_backend == "twist":
            self.create_timer(
                1.0 / self._direct_publish_hz, self._direct_motion_tick
            )
        startup_detail = (
            f"直接控制{self._cmd_vel_topic}；运动锁"
            + ("已开启" if self._motion_enabled else "默认关闭")
            if self._motion_backend == "twist"
            else "运动锁默认关闭；等待WonderEcho和导航就绪"
        )
        self._publish_status(
            "started",
            detail=startup_detail,
            transport=self._transport,
        )

    def _on_readiness(self, kind, message):
        value = bool(message.data)
        attribute = f"_{kind}_ready"
        if value != getattr(self, attribute):
            setattr(self, attribute, value)
            self._publish_status(
                "readiness_changed", readiness=kind, ready=value
            )

    def _on_action_status(self, action_name, message):
        statuses = tuple(
            int(status.status) for status in message.status_list
        )
        self._action_statuses[action_name] = statuses
        if voice_cancel_required(self._voice_busy, action_name, statuses):
            if not self._cancel_on_accept:
                self._cancel_on_accept = True
                self._publish_status(
                    "safety_cancel_requested",
                    detail=f"检测到并发导航动作：{action_name}",
                )
                self._request_active_cancel(
                    f"检测到并发导航动作：{action_name}"
                )

    def _active_actions(self):
        return sorted(
            name
            for name, statuses in self._action_statuses.items()
            if active_action_present(statuses)
        )

    def _poll_device(self):
        now_sec = time.monotonic()
        self._check_stop_progress(now_sec)
        if self._device is None:
            if now_sec < self._next_reconnect_at:
                return
            self._device = self._make_device()
        try:
            if self._transport == "serial":
                event = self._device.read_event()
            else:
                command_id = self._device.read_command()
        except Exception as error:
            self._mark_device_error(error, now_sec)
            return

        if not self._device_online:
            self._device_online = True
            fields = {"transport": self._transport}
            if self._transport == "serial":
                fields.update(
                    port=self._serial_port, baud=self._serial_baud
                )
            else:
                fields.update(
                    bus=self._bus_number,
                    address=f"0x{self._address:02x}",
                )
            self._publish_status("device_connected", **fields)

        if self._transport == "serial":
            if event is None:
                return
            frame_type, command_id = event
            if frame_type == 0x03:
                self._publish_status(
                    "wake_detected",
                    command_id=command_id,
                    frame_type=frame_type,
                )
                return
            if frame_type != 0x00:
                self._publish_status(
                    "control_frame",
                    command_id=command_id,
                    frame_type=frame_type,
                    phrase=self.CONTROL_FRAME_NAMES.get(
                        frame_type, "未映射控制帧"
                    ),
                )
                return
            event_id = command_id
        else:
            event_id = self._edge_filter.observe(command_id, now_sec)
        if event_id is not None:
            self._handle_recognition(event_id)

    def _make_device(self):
        if self._transport == "serial":
            return WonderEchoSerialDevice(
                port=self._serial_port,
                baudrate=self._serial_baud,
            )
        return WonderEchoDevice(
            bus_number=self._bus_number,
            address=self._address,
            result_register=self._result_register,
            speak_register=self._speak_register,
        )

    def _mark_device_error(self, error, now_sec=None):
        was_online = self._device_online
        self._device_online = False
        self._next_reconnect_at = (now_sec or time.monotonic()) + self._reconnect_sec
        self._close_device()
        self._edge_filter.disarm()
        if was_online or not hasattr(self, "_last_device_error"):
            self._last_device_error = str(error)
            self._publish_status(
                "device_unavailable",
                detail=str(error),
                transport=self._transport,
                retry_in_sec=self._reconnect_sec,
            )

    def _handle_recognition(self, command_id):
        command = COMMANDS.get(command_id)
        self._publish_recognized(command_id, command)
        if command is None:
            self._publish_status(
                "ignored", command_id=command_id, detail="未映射的命令ID"
            )
            return
        if command.kind == "stop":
            self._stop_all(command)
            return
        if command.kind in ("speed_up", "speed_down"):
            self._adjust_direct_speed(command)
            return
        if command.kind == "unsupported":
            self._publish_status(
                "rejected",
                command_id=command.command_id,
                phrase=command.phrase,
                detail="Ackermann底盘不支持原地左转或右转",
            )
            return

        rejection = self._motion_rejection(command)
        if rejection:
            self._publish_status(
                "rejected",
                command_id=command.command_id,
                phrase=command.phrase,
                detail=rejection,
            )
            return
        self._send_motion(command)

    def _adjust_direct_speed(self, command):
        if self._motion_backend != "twist":
            self._publish_status(
                "rejected",
                command_id=command.command_id,
                phrase=command.phrase,
                detail="速度调节仅支持直接cmd_vel后端",
            )
            return
        delta = DIRECT_SPEED_STEP if command.kind == "speed_up" else -DIRECT_SPEED_STEP
        old_speed = self._direct_cruise_speed
        self._direct_cruise_speed = round(
            max(DIRECT_MIN_SPEED, min(DIRECT_MAX_SPEED, old_speed + delta)),
            2,
        )
        self._publish_status(
            "speed_changed",
            command_id=command.command_id,
            phrase=command.phrase,
            old_speed=old_speed,
            speed=self._direct_cruise_speed,
            applies_to="next_motion",
        )

    def _motion_rejection(self, command):
        if not self._motion_enabled:
            return "语音运动锁未开启"
        if self._voice_busy:
            return "已有语音动作正在发送或执行"
        if self._motion_backend == "twist":
            if self._cmd_vel_publisher.get_subscription_count() == 0:
                return f"底盘速度话题没有订阅者：{self._cmd_vel_topic}"
            return ""
        if command.kind in ("direct_twist", "direct_sequence"):
            return "该转向动作仅支持直接cmd_vel后端"
        if not self._localization_ready:
            return "SLAM/定位尚未就绪"
        if not self._lifecycle_ready:
            return "Nav2 lifecycle尚未就绪"
        active_actions = self._active_actions()
        if active_actions:
            return "已有动作正在执行：" + ", ".join(active_actions)
        client = self._action_clients[command.kind]
        if not client.server_is_ready():
            return f"Nav2动作服务器不可用：{command.kind}"
        return ""

    def _send_motion(self, command: VoiceCommand):
        if self._motion_backend == "twist":
            self._send_direct_motion(command)
            return
        target_x = math.copysign(
            min(abs(command.target_x), self._max_voice_distance), command.target_x
        )
        if command.kind == "drive_on_heading":
            goal = DriveOnHeading.Goal()
        else:
            goal = BackUp.Goal()
        goal.target = Point(x=target_x, y=0.0, z=0.0)
        goal.speed = float(command.speed)
        goal.time_allowance = Duration(
            seconds=self._time_allowance_sec
        ).to_msg()

        self._voice_busy = True
        self._active_command = command
        self._cancel_on_accept = False
        self._publish_status(
            "sending",
            command_id=command.command_id,
            phrase=command.phrase,
            action=command.kind,
            target_x=target_x,
            speed=command.speed,
            time_allowance_sec=self._time_allowance_sec,
        )
        future = self._action_clients[command.kind].send_goal_async(
            goal, feedback_callback=partial(self._on_feedback, command)
        )
        self._goal_send_future = future
        future.add_done_callback(partial(self._on_goal_response, command))

    def _send_direct_motion(self, command: VoiceCommand):
        segments = direct_motion_segments(
            command, self._max_voice_distance, self._direct_cruise_speed
        )
        self._voice_busy = True
        self._active_command = command
        self._direct_segments = segments
        self._direct_segment_index = 0
        self._direct_started_at = time.monotonic()
        self._direct_zero_burst = 0
        self._start_direct_segment(0, self._direct_started_at)
        self._publish_status(
            "sending",
            command_id=command.command_id,
            phrase=command.phrase,
            action="cmd_vel",
            cmd_vel_topic=self._cmd_vel_topic,
            cruise_speed=self._direct_cruise_speed,
            segment_count=len(segments),
            duration_sec=sum(segment.duration_sec for segment in segments),
        )

    def _start_direct_segment(self, index, now_sec):
        segment = self._direct_segments[index]
        twist = Twist()
        twist.linear.x = segment.linear_x
        twist.angular.z = segment.angular_z
        if segment.steering_angle_rad is not None:
            steering = SteeringAngleCommand()
            steering.steering_angle_rad = segment.steering_angle_rad
            self._steering_publisher.publish(steering)
        self._direct_segment_index = index
        self._direct_twist = twist
        self._direct_deadline = now_sec + segment.duration_sec
        self._cmd_vel_publisher.publish(twist)

    def _direct_motion_tick(self):
        if self._direct_zero_burst > 0:
            self._cmd_vel_publisher.publish(Twist())
            self._direct_zero_burst -= 1
        if not self._voice_busy or self._active_command is None:
            return
        if not self._motion_enabled:
            self._stop_direct_motion("stopped", "语音运动锁已关闭")
            return
        now_sec = time.monotonic()
        if now_sec >= self._direct_deadline:
            next_index = self._direct_segment_index + 1
            if next_index < len(self._direct_segments):
                self._start_direct_segment(next_index, now_sec)
                return
            self._stop_direct_motion("finished", "分段速度动作已完成")
            return
        self._cmd_vel_publisher.publish(self._direct_twist)

    def _stop_direct_motion(self, state, detail, trigger_command=None):
        active_command = self._active_command
        elapsed_sec = (
            max(0.0, time.monotonic() - self._direct_started_at)
            if self._direct_started_at > 0.0
            else 0.0
        )
        self._cmd_vel_publisher.publish(Twist())
        self._direct_zero_burst = max(self._direct_zero_burst, 4)
        self._direct_deadline = 0.0
        self._direct_started_at = 0.0
        self._direct_twist = Twist()
        self._direct_segments = ()
        self._direct_segment_index = 0
        self._voice_busy = False
        self._active_command = None
        command = trigger_command or active_command
        self._publish_status(
            state,
            command_id=0 if command is None else command.command_id,
            phrase="" if command is None else command.phrase,
            interrupted_command_id=(
                0 if active_command is None else active_command.command_id
            ),
            cmd_vel_topic=self._cmd_vel_topic,
            elapsed_sec=elapsed_sec,
            detail=detail,
        )

    def _on_goal_response(self, command, future):
        self._goal_send_future = None
        try:
            goal_handle = future.result()
        except Exception as error:
            self._finish_without_result("send_failed", str(error))
            return
        if not goal_handle.accepted:
            self._finish_without_result("rejected", "Nav2拒绝了语音动作目标")
            return

        self._active_goal_handle = goal_handle
        self._result_future = goal_handle.get_result_async()
        self._result_future.add_done_callback(
            partial(self._on_action_result, command)
        )
        self._publish_status(
            "accepted",
            command_id=command.command_id,
            phrase=command.phrase,
            action=command.kind,
        )
        if self._cancel_on_accept or not self._motion_enabled:
            self._request_active_cancel("目标接受前已收到停止/锁定请求")
        elif self._speak_on_accept:
            self._speak(command.command_id)

    def _on_feedback(self, command, feedback_message):
        distance = float(feedback_message.feedback.distance_traveled)
        self._publish_status(
            "active",
            command_id=command.command_id,
            phrase=command.phrase,
            distance_traveled=distance,
        )

    def _on_action_result(self, command, future):
        try:
            wrapped = future.result()
            status = int(wrapped.status)
            elapsed = wrapped.result.total_elapsed_time
            elapsed_sec = float(elapsed.sec) + float(elapsed.nanosec) / 1.0e9
            detail = "Nav2动作已结束"
        except Exception as error:
            status = -1
            elapsed_sec = 0.0
            detail = str(error)
        self._active_goal_handle = None
        self._result_future = None
        self._voice_busy = False
        self._active_command = None
        self._cancel_on_accept = False
        self._publish_status(
            "finished",
            command_id=command.command_id,
            phrase=command.phrase,
            action_status=status,
            elapsed_sec=elapsed_sec,
            detail=detail,
        )

    def _finish_without_result(self, state, detail):
        command = self._active_command
        self._active_goal_handle = None
        self._result_future = None
        self._voice_busy = False
        self._active_command = None
        self._cancel_on_accept = False
        self._publish_status(
            state,
            command_id=0 if command is None else command.command_id,
            detail=detail,
        )

    def _set_motion_enabled(self, request, response):
        self._motion_enabled = bool(request.data)
        if not self._motion_enabled:
            if self._motion_backend == "twist":
                self._stop_direct_motion("stopped", "语音运动锁已关闭")
            else:
                self._cancel_on_accept = True
                self._request_active_cancel("语音运动锁已关闭")
        response.success = True
        if self._motion_backend == "twist":
            response.message = (
                f"语音运动已解锁；直接发布到{self._cmd_vel_topic}"
                if self._motion_enabled
                else f"语音运动已锁定；已向{self._cmd_vel_topic}发布零速"
            )
        else:
            response.message = (
                "语音运动已解锁；仍受SLAM/Nav2/动作占用门禁约束"
                if self._motion_enabled
                else "语音运动已锁定；已请求取消现有语音动作"
            )
        self._publish_status(
            "motion_lock_changed", motion_enabled=self._motion_enabled
        )
        return response

    def _request_active_cancel(self, detail):
        if self._active_goal_handle is None:
            return None
        future = self._active_goal_handle.cancel_goal_async()
        future.add_done_callback(
            partial(self._on_cancel_response, "voice_goal", detail)
        )
        return future

    def _stop_all(self, command):
        if self._motion_backend == "twist":
            self._stop_direct_motion(
                "stopped", "语音停止命令已直接发布零速", command
            )
            return
        now_sec = time.monotonic()
        self._stop_generation += 1
        stop_generation = self._stop_generation
        self._stop_waiting = True
        self._stop_pending_responses = 0
        self._stop_deadline = now_sec + self._stop_timeout_sec
        self._stop_not_before = now_sec + 0.25
        self._cancel_on_accept = True
        own_future = self._request_active_cancel("语音停止命令")
        if own_future is not None:
            self._track_stop_future(stop_generation, own_future)
        requested = []
        unavailable = []
        for action_name, client in self._cancel_clients.items():
            if not client.service_is_ready():
                unavailable.append(action_name)
                continue
            requested.append(action_name)
            future = client.call_async(CancelGoal.Request())
            future.add_done_callback(
                partial(self._on_cancel_response, action_name, "取消全部目标")
            )
            self._track_stop_future(stop_generation, future)
        self._stop_unavailable = unavailable
        self._publish_status(
            "stop_requested",
            command_id=command.command_id,
            phrase=command.phrase,
            cancel_requested=requested,
            cancel_unavailable=unavailable,
        )

    def _track_stop_future(self, stop_generation, future):
        self._stop_pending_responses += 1
        future.add_done_callback(
            partial(self._on_stop_future_done, stop_generation)
        )

    def _on_stop_future_done(self, stop_generation, _):
        if stop_generation != self._stop_generation or not self._stop_waiting:
            return
        self._stop_pending_responses = max(
            0, self._stop_pending_responses - 1
        )

    def _check_stop_progress(self, now_sec):
        if not self._stop_waiting:
            return
        active_actions = self._active_actions()
        if (
            now_sec >= self._stop_not_before
            and self._stop_pending_responses == 0
            and not active_actions
            and not self._voice_busy
        ):
            self._stop_waiting = False
            self._publish_status(
                "stopped",
                detail="所有可见语音/任务/Nav2动作均已进入终态",
                cancel_unavailable=self._stop_unavailable,
            )
            return
        if now_sec >= self._stop_deadline:
            self._stop_waiting = False
            self._publish_status(
                "stop_timeout",
                detail="等待动作终态超时",
                active_actions=active_actions,
                voice_busy=self._voice_busy,
                pending_cancel_responses=self._stop_pending_responses,
                cancel_unavailable=self._stop_unavailable,
            )

    def _on_cancel_response(self, source, detail, future):
        try:
            response = future.result()
            count = len(getattr(response, "goals_canceling", ()))
            return_code = int(getattr(response, "return_code", 0))
            message = f"{detail}：return_code={return_code}, goals={count}"
        except Exception as error:
            message = f"{detail}失败：{error}"
        self._publish_status(
            "cancel_response", source=source, detail=message
        )

    def _speak(self, command_id):
        if self._device is None:
            return
        if self._transport != "i2c":
            self._publish_status(
                "speak_unsupported",
                command_id=command_id,
                detail="串口传输未配置主控到语音模块的播报协议",
            )
            return
        try:
            self._device.speak_command(command_id)
        except Exception as error:
            self._mark_device_error(error)

    def _publish_recognized(self, command_id, command):
        payload = {
            "command_id": int(command_id),
            "known": command is not None,
            "phrase": "" if command is None else command.phrase,
            "kind": "unknown" if command is None else command.kind,
        }
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        self._recognized_publisher.publish(message)

    def _publish_status(self, state, **fields):
        payload = {
            "state": state,
            "motion_enabled": self._motion_enabled,
            "motion_backend": self._motion_backend,
            **fields,
        }
        if self._motion_backend == "nav2":
            payload.update(
                localization_ready=self._localization_ready,
                lifecycle_ready=self._lifecycle_ready,
            )
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        self._status_publisher.publish(message)

    def begin_shutdown(self):
        self._motion_enabled = False
        if self._motion_backend == "twist":
            self._stop_direct_motion("stopped", "语音节点正在退出")
        else:
            self._cancel_on_accept = True
            self._request_active_cancel("语音节点正在退出")

    @property
    def voice_busy(self):
        return self._voice_busy

    def _close_device(self):
        device = self._device
        self._device = None
        if device is not None:
            try:
                device.close()
            except Exception:
                pass

    def close_device(self):
        self._close_device()


def main(args=None):
    rclpy.init(
        args=args, signal_handler_options=SignalHandlerOptions.NO
    )
    node = WonderEchoVoiceNode()

    def request_shutdown(_signum, _frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, request_shutdown)
    signal.signal(signal.SIGTERM, request_shutdown)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        if rclpy.ok():
            node.begin_shutdown()
            deadline = time.monotonic() + 2.0
            while node.voice_busy and time.monotonic() < deadline:
                rclpy.spin_once(node, timeout_sec=0.05)
        node.close_device()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
