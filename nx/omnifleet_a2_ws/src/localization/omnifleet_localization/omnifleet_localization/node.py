import hashlib
import math
import re
import signal
import subprocess
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import rclpy
from action_msgs.msg import GoalInfo
from action_msgs.srv import CancelGoal
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Twist
from lifecycle_msgs.msg import State as LifecycleState
from lifecycle_msgs.msg import Transition
from lifecycle_msgs.srv import ChangeState, GetState
from nav_msgs.msg import OccupancyGrid, Odometry
from nav2_msgs.srv import ManageLifecycleNodes
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from rclpy.signals import SignalHandlerOptions
from rclpy.time import Time
from std_srvs.srv import Trigger
from tf2_ros import Buffer, TransformListener

from omnifleet_interfaces.msg import SlamStatus
from omnifleet_interfaces.srv import SaveMap, SwitchMode

from .map_registry import MapRegistry
from .mode_catalog import ModeCatalog
from .occupancy_grid_saver import save_occupancy_grid
from .process_supervisor import ProcessSupervisor
from .state_machine import State, SwitchStateMachine


class SlamManagerNode(Node):
    NAV_ACTIONS = ("navigate_to_pose", "navigate_through_poses", "follow_waypoints")
    NAV_LIFECYCLE_NODES = (
        "controller_server",
        "planner_server",
        "smoother_server",
        "behavior_server",
        "bt_navigator",
        "waypoint_follower",
        "velocity_smoother",
        "collision_monitor",
    )

    def __init__(self):
        super().__init__("rrc_slam_manager")
        slam_share = Path(get_package_share_directory("omnifleet_localization"))
        sensor_share = Path(get_package_share_directory("omnifleet_localization"))
        description_share = Path(get_package_share_directory("omnifleet_description"))

        modes_file = self.declare_parameter(
            "modes_file", str(slam_share / "config" / "modes.yaml")
        ).value
        self.map_root = Path(
            self.declare_parameter("map_root", "~/robot_maps").value
        ).expanduser()
        self.main_setup = str(
            Path(
                self.declare_parameter(
                    "main_setup", "~/omnifleet_a2_ws/install/setup.bash"
                ).value
            ).expanduser()
        )
        state_dir = Path(
            self.declare_parameter(
                "state_dir", "~/.local/state/rrc_slam"
            ).value
        ).expanduser()
        self.health_timeout_sec = float(
            self.declare_parameter("health_timeout_sec", 90.0).value
        )
        self.require_foxglove = bool(
            self.declare_parameter("require_foxglove", False).value
        )
        self.zero_hold_sec = float(
            self.declare_parameter("zero_hold_sec", 0.6).value
        )
        self.shutdown_manual_stack_on_stop = bool(
            self.declare_parameter("shutdown_manual_stack_on_stop", True).value
        )
        self.glim_launch_arguments = {
            "map_path": str(self.declare_parameter("glim_map_path", "").value),
            "initial_pose_x": float(self.declare_parameter("glim_initial_pose_x", 0.0).value),
            "initial_pose_y": float(self.declare_parameter("glim_initial_pose_y", 0.0).value),
            "initial_pose_z": float(
                self.declare_parameter(
                    "glim_initial_pose_z", 0.0
                ).value
            ),
            "initial_pose_yaw": float(self.declare_parameter("glim_initial_pose_yaw", 0.0).value),
            "obstacle_z_min": float(self.declare_parameter("glim_obstacle_z_min", -0.03).value),
            "obstacle_z_max": float(self.declare_parameter("glim_obstacle_z_max", 0.75).value),
            "lidar_range_min": float(self.declare_parameter("glim_lidar_range_min", 0.18).value),
            "lidar_range_max": float(self.declare_parameter("glim_lidar_range_max", 8.0).value),
            "lidar_voxel_size": float(self.declare_parameter("glim_lidar_voxel_size", 0.08).value),
            "lidar_max_rate": float(self.declare_parameter("glim_lidar_max_rate", 10.0).value),
            "use_camera": bool(self.declare_parameter("use_camera", False).value),
        }
        self.sensor_config_sha256 = self._hash_files(
            [
                sensor_share / "config" / "airy" / "airy.yaml",
            ]
        )
        self.extrinsics_sha256 = self._hash_files(
            [description_share / "config" / "extrinsics.yaml"]
        )

        self.catalog = ModeCatalog(modes_file)
        self.registry = MapRegistry(self.map_root)
        self.supervisor = ProcessSupervisor(state_dir)
        self.machine = SwitchStateMachine()
        self.current_mode = ""
        self.current_operation = ""
        self.current_map_id = ""
        self._transaction_lock = threading.Lock()
        self._manual_shutdown_requested = threading.Event()
        self._zero_hold_active = True
        self._startup_timer = None
        self._service_clients = {}
        self._map_lock = threading.Lock()
        self._latest_map = None

        latched_qos = QoSProfile(depth=1)
        latched_qos.reliability = ReliabilityPolicy.RELIABLE
        latched_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.status_publisher = self.create_publisher(
            SlamStatus, "/rrc_slam/status", latched_qos
        )
        self.map_subscription = self.create_subscription(
            OccupancyGrid, "/map", self._cache_occupancy_grid, latched_qos
        )
        self.zero_publisher = self.create_publisher(
            Twist, "/rrc_safety/zero_cmd", 10
        )
        self.create_timer(0.05, self._zero_timer)
        self.switch_service = self.create_service(
            SwitchMode, "/rrc_slam/switch_mode", self._switch_callback
        )
        self.save_service = self.create_service(
            SaveMap, "/rrc_slam/save_map", self._save_callback
        )
        self.stop_stack_service = self.create_service(
            Trigger,
            "/rrc_system/stop_manual_stack",
            self._stop_stack_callback,
        )
        self.tf_buffer = Buffer(cache_time=Duration(seconds=10.0))
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self._finite_odom_events = {"/odom": threading.Event()}
        self._health_subscriptions = [
            self.create_subscription(
                Odometry,
                topic,
                lambda message, event=event: self._mark_finite_odom(message, event),
                10,
            )
            for topic, event in self._finite_odom_events.items()
        ]

        record = self.supervisor.load_record()
        if record is not None:
            self.current_mode = record.mode
            self.machine.fail("检测到托管后端的残留状态，必须先显式停止")
        self._publish_status("SLAM 管理器已就绪")
        startup_mode = self.declare_parameter("startup_mode", "").value.strip()
        self._startup_operation = self.declare_parameter(
            "startup_operation", "mapping"
        ).value.strip()
        self._startup_map_id = self.declare_parameter(
            "startup_map_id", ""
        ).value.strip()
        if startup_mode:
            self._startup_mode = startup_mode
            self._startup_timer = self.create_timer(0.25, self._start_initial_mode)

    def _start_initial_mode(self):
        if self._startup_timer is None:
            return
        self._startup_timer.cancel()
        self._startup_timer = None
        request = SwitchMode.Request()
        request.mode = self._startup_mode
        request.operation = self._startup_operation
        request.map_id = self._startup_map_id
        response = self._switch_callback(request, SwitchMode.Response())
        if not response.accepted:
            self.get_logger().error(f"初始模式被拒绝：{response.message}")

    def _switch_callback(self, request, response):
        stop_only = request.mode == "__stop__"
        if stop_only and self.shutdown_manual_stack_on_stop:
            self._request_manual_stack_shutdown()
            response.accepted = True
            response.transaction_id = "manual-stack-stop"
            response.message = "手动启动栈关闭请求已接受"
            return response

        if not self._transaction_lock.acquire(blocking=False):
            response.accepted = False
            response.message = "已有另一个 SLAM 操作正在执行"
            return response

        try:
            if stop_only:
                mode = ""
                operation = ""
                map_id = ""
            else:
                mode = request.mode.strip()
                operation = request.operation.strip()
                self.catalog.require(mode, operation)
                map_id = self._normalize_map_id(mode, operation, request.map_id)
                # Only prior-map localization consumes an existing map manifest.
                # slam_navigation is online mapping with Nav2 and creates a new
                # timestamped map session, just like mapping mode.
                if operation == "localization":
                    manifest = self.registry.assert_compatible(
                        mode,
                        map_id,
                        sensor_config_sha256=self.sensor_config_sha256,
                        extrinsics_sha256=self.extrinsics_sha256,
                    )
                    if not manifest["navigation_compatible"]:
                        raise ValueError("该地图尚未通过导航兼容性验证")
        except Exception as error:
            self._transaction_lock.release()
            response.accepted = False
            response.message = str(error)
            return response

        transaction_id = uuid.uuid4().hex
        worker = threading.Thread(
            target=self._switch_worker,
            args=(transaction_id, mode, operation, map_id, stop_only),
            daemon=True,
            name=f"slam-switch-{transaction_id[:8]}",
        )
        worker.start()
        response.accepted = True
        response.transaction_id = transaction_id
        response.message = "操作请求已接受"
        return response

    def _stop_stack_callback(self, _, response):
        request = SwitchMode.Request()
        request.mode = "__stop__"
        result = self._switch_callback(request, SwitchMode.Response())
        response.success = bool(result.accepted)
        response.message = (
            "已接受：正在保持零速度、取消导航并关闭手动启动栈"
            if result.accepted
            else result.message
        )
        return response

    def _request_manual_stack_shutdown(self):
        if self._manual_shutdown_requested.is_set():
            return
        self._manual_shutdown_requested.set()
        self._set_zero_hold(True)
        self._publish_status("正在保持零速度、取消导航并关闭统一 Launch")
        worker = threading.Thread(
            target=self._manual_stack_shutdown_worker,
            daemon=True,
            name="manual-stack-stop",
        )
        worker.start()

    def _manual_stack_shutdown_worker(self):
        try:
            self._cancel_navigation()
        except Exception as error:
            self.get_logger().warning(f"取消导航目标时出现非致命异常：{error}")
        time.sleep(max(self.zero_hold_sec, 0.5))
        self.get_logger().warning(
            "已保持零速度并取消导航，正在退出统一 Launch"
        )
        rclpy.shutdown(context=self.context)

    def _switch_worker(self, transaction_id, mode, operation, map_id, stop_only):
        try:
            old_mode = self.current_mode
            self.machine.begin(transaction_id)
            self._set_zero_hold(True)
            self.machine.lock_zero_speed()
            self._publish_status("正在取消导航并保持零速度")
            self._cancel_navigation()
            if old_mode:
                self._deactivate_navigation()
            time.sleep(max(self.zero_hold_sec, 0.5))

            if stop_only and self.shutdown_manual_stack_on_stop:
                # 中键停止的最终目标是关闭本次手动启动的整个统一 Launch。
                # 此处不能等待 DDS 图中的旧节点名消失：进程退出后，DDS
                # 发现缓存仍可能短暂保留 /glim_ros，造成“进程已停但误报失败”。
                # 管理器退出时 destroy_node() 会有界停止其托管的 GLIM 进程组，
                # 随后的 OnProcessExit 负责关闭本 Launch 中其余手动节点。
                self._publish_status(
                    "Nav2 已停用，正在关闭统一 Launch；继续发送零速度"
                )
                self.get_logger().warning(
                    "已保持零速度并取消导航，正在退出统一 Launch"
                )
                time.sleep(0.25)
                rclpy.shutdown(context=self.context)
                return

            if not self.supervisor.stop(self._old_shutdown_timeout(old_mode)):
                raise RuntimeError("托管后端进程组未能停止")
            self.machine.old_backend_stopped()
            self._publish_status("正在确认旧后端与旧 TF 发布者已经退出")
            self._verify_old_owners_absent(old_mode, 30.0)
            self.machine.old_tf_owners_absent()

            if stop_only:
                self.current_mode = ""
                self.current_operation = ""
                self.current_map_id = ""
                self.machine.stop_complete()
                self._publish_status("后端已停止，继续发送零速度")
                return

            with self._map_lock:
                self._latest_map = None
            self.current_mode = mode
            self.current_operation = operation
            self.current_map_id = map_id
            command = self.catalog.launch_command(
                mode,
                operation,
                map_id,
                map_root=str(self.map_root),
                main_setup=self.main_setup,
                launch_arguments=(
                    self.glim_launch_arguments if mode == "glim_cuda" else None
                ),
            )
            log_path = (
                Path.home()
                / "robot_logs"
                / "slam"
                / f"{transaction_id}-{mode}.log"
            )
            self.supervisor.start(
                command,
                transaction_id=transaction_id,
                mode=mode,
                log_path=log_path,
            )
            self.machine.backend_started()
            self._publish_status("后端已启动，正在等待健康检查通过")
            self._verify_health(mode, operation, self.health_timeout_sec)
            self.machine.backend_healthy()
            if self._navigation_requested(mode, operation):
                self._publish_status("后端运行正常，正在激活 Nav2")
                self._activate_navigation()
            self.machine.unlock_zero_speed()
            self._set_zero_hold(False)
            self._publish_status("后端运行正常")
        except Exception as error:
            try:
                self.supervisor.stop(5.0)
            except Exception as stop_error:
                self.get_logger().error(f"回退过程中停止后端失败：{stop_error}")
            self.machine.fail(str(error))
            self._set_zero_hold(True)
            self._publish_status(f"安全启动失败：{error}")
        finally:
            self._transaction_lock.release()

    def _save_callback(self, request, response):
        if not self._transaction_lock.acquire(blocking=False):
            response.message = "已有另一个 SLAM 操作正在执行"
            return response
        try:
            if self.machine.state is not State.RUNNING or not self.current_mode:
                raise RuntimeError("当前没有运行正常的建图后端")
            if self.current_operation not in {"mapping", "slam_navigation"}:
                raise RuntimeError("当前操作不会生成地图")
            self._set_zero_hold(True)
            self._cancel_navigation()
            if self._navigation_requested(self.current_mode, self.current_operation):
                self._deactivate_navigation()
            time.sleep(max(self.zero_hold_sec, 0.5))
            self._write_current_2d_map()
            timeout = float(
                self.catalog.modes[self.current_mode]["shutdown_timeout_sec"]
            )
            if not self.supervisor.stop(timeout):
                raise RuntimeError("地图保存后后端未能停止")
            manifest = self._write_current_manifest()
            response.success = True
            response.map_id = manifest["map_id"]
            response.message = "地图已保存为 map.pgm/map.yaml；后端已停止并继续发送零速度"
            self.machine.reset_idle()
            self.current_mode = ""
            self.current_operation = ""
            self.current_map_id = ""
            self._publish_status(response.message)
        except Exception as error:
            self.machine.fail(str(error))
            self._set_zero_hold(True)
            response.message = str(error)
            self._publish_status(f"地图保存失败：{error}")
        finally:
            self._transaction_lock.release()
        return response

    def _cache_occupancy_grid(self, message):
        with self._map_lock:
            self._latest_map = message

    def _write_current_2d_map(self):
        with self._map_lock:
            message = self._latest_map
        if message is None:
            raise RuntimeError("尚未收到 /map，无法保存二维占据栅格地图")
        directory = self.map_root / self.current_mode / self.current_map_id
        pgm_path, yaml_path = save_occupancy_grid(message, directory)
        self.get_logger().info(
            f"二维地图已写入 {pgm_path} 和 {yaml_path}"
        )

    def _write_current_manifest(self):
        directory = self.map_root / self.current_mode / self.current_map_id
        artifacts = sorted(
            str(path.relative_to(directory))
            for path in directory.rglob("*")
            if path.is_file() and path.name != "manifest.yaml"
        )
        if not artifacts:
            raise RuntimeError(f"在 {directory} 下没有找到地图文件")
        now = datetime.now(timezone.utc).replace(microsecond=0)
        manifest = {
            "schema_version": 1,
            "map_id": self.current_map_id,
            "backend": self.current_mode,
            "operation": "mapping",
            "created_at_utc": now.isoformat().replace("+00:00", "Z"),
            "ros_distro": "humble",
            "software_versions": self._software_versions(),
            "frames": {
                "map": "map",
                "odom": "odom",
                "base": "base_link",
                "lidar": "rslidar",
            },
            "sensor_config_sha256": self.sensor_config_sha256,
            "extrinsics_sha256": self.extrinsics_sha256,
            "artifacts": artifacts,
            "navigation_compatible": False,
            "validation_report": "validation/pending.md",
        }
        self.registry.write(manifest)
        return manifest

    def _verify_health(self, mode, operation, timeout_sec):
        contract = self.catalog.modes[mode]
        required = set(contract["required_topics"] + contract["required_outputs"])
        required.update(contract.get("operation_required_outputs", {}).get(operation, []))
        odom_topic = "/odom"
        finite_odom = self._finite_odom_events[odom_topic]
        finite_odom.clear()
        deadline = time.monotonic() + timeout_sec
        next_foxglove_check = 0.0
        while time.monotonic() < deadline:
            if not self.supervisor.is_running():
                raise RuntimeError("后端进程在启动期间意外退出")
            if self.require_foxglove and time.monotonic() >= next_foxglove_check:
                if not self._foxglove_active():
                    raise RuntimeError("Foxglove Bridge 未运行")
                next_foxglove_check = time.monotonic() + 2.0
            topics = {name for name, _ in self.get_topic_names_and_types()}
            topics_ready = required <= topics
            node_names = set(self.get_node_names())
            expected_owners = {
                contract["map_to_odom_owner"],
                contract["odom_to_base_owner"],
            }
            owners_ready = expected_owners <= node_names
            forbidden_pose_owners = {"ekf_filter_node", "map_odom_corrector"}
            active_forbidden_owners = forbidden_pose_owners & node_names
            odom_tf_ready = self.tf_buffer.can_transform(
                "odom", "base_link", Time(), timeout=Duration(seconds=0.05)
            )
            map_tf_ready = operation == "mapping" or self.tf_buffer.can_transform(
                "map", "odom", Time(), timeout=Duration(seconds=0.05)
            )
            tf_ready = odom_tf_ready and map_tf_ready
            if (
                topics_ready
                and finite_odom.is_set()
                and tf_ready
                and owners_ready
                and not active_forbidden_owners
            ):
                return
            time.sleep(0.1)
        missing = sorted(required - {name for name, _ in self.get_topic_names_and_types()})
        raise RuntimeError(
            "健康检查超时："
            f"缺失话题={missing}，里程计有效={finite_odom.is_set()}，"
            f"缺失TF发布者={sorted(expected_owners - node_names)}，"
            f"旧位姿发布者={sorted(active_forbidden_owners)}，"
            f"odom坐标变换就绪={odom_tf_ready}，map坐标变换就绪={map_tf_ready}"
        )

    @staticmethod
    def _mark_finite_odom(message, event):
        values = (
            message.pose.pose.position.x,
            message.pose.pose.position.y,
            message.pose.pose.position.z,
            message.pose.pose.orientation.x,
            message.pose.pose.orientation.y,
            message.pose.pose.orientation.z,
            message.pose.pose.orientation.w,
            message.twist.twist.linear.x,
            message.twist.twist.angular.z,
        )
        if all(math.isfinite(value) for value in values):
            event.set()

    def _cancel_navigation(self):
        request = CancelGoal.Request()
        request.goal_info = GoalInfo()
        for action in self.NAV_ACTIONS:
            self._call_if_available(
                CancelGoal, f"/{action}/_action/cancel_goal", request, 2.0
            )

    def _deactivate_navigation(self):
        request = ManageLifecycleNodes.Request()
        request.command = ManageLifecycleNodes.Request.PAUSE
        response = self._call_if_available(
            ManageLifecycleNodes,
            "/lifecycle_manager_navigation/manage_nodes",
            request,
            30.0,
        )
        if response is not None:
            if not response.success:
                self.get_logger().info(
                    "Nav2 暂停请求返回失败；相关节点可能已经停止或尚未配置"
                )
            return
        for node_name in self.NAV_LIFECYCLE_NODES:
            request = ChangeState.Request()
            request.transition.id = Transition.TRANSITION_DEACTIVATE
            self._call_if_available(
                ChangeState, f"/{node_name}/change_state", request, 1.0
            )

    def _call_if_available(self, service_type, name, request, timeout_sec):
        key = (service_type, name)
        client = self._service_clients.get(key)
        if client is None:
            client = self.create_client(service_type, name)
            self._service_clients[key] = client
        if not client.wait_for_service(timeout_sec=0.1):
            return None
        event = threading.Event()
        future = client.call_async(request)
        future.add_done_callback(lambda _: event.set())
        event.wait(timeout_sec)
        return future.result() if future.done() else None

    def _activate_navigation(self):
        # Smac Reeds-Shepp may need tens of seconds to build its heuristic table
        # on the first configure. Never overlap STARTUP with a second bulk
        # lifecycle request.
        request = ManageLifecycleNodes.Request()
        request.command = ManageLifecycleNodes.Request.STARTUP
        response = self._call_if_available(
            ManageLifecycleNodes,
            "/lifecycle_manager_navigation/manage_nodes",
            request,
            90.0,
        )
        if response is not None and response.success:
            return
        # The bulk manager can partially succeed while its service reports a
        # timeout. Reconcile the actual state of each node with bounded retries.
        if self._wait_navigation_active(10.0):
            return
        if self._reconcile_navigation_active(60.0):
            return
        raise RuntimeError("Nav2 生命周期管理器未能激活全部节点")

    def _wait_navigation_active(self, timeout_sec):
        deadline = time.monotonic() + timeout_sec
        request = GetState.Request()
        while time.monotonic() < deadline:
            all_active = True
            for node_name in self.NAV_LIFECYCLE_NODES:
                response = self._call_if_available(
                    GetState,
                    f"/{node_name}/get_state",
                    request,
                    1.0,
                )
                if (
                    response is None
                    or response.current_state.id
                    != LifecycleState.PRIMARY_STATE_ACTIVE
                ):
                    all_active = False
                    break
            if all_active:
                return True
            time.sleep(0.2)
        return False

    def _reconcile_navigation_active(self, timeout_sec):
        deadline = time.monotonic() + timeout_sec
        get_request = GetState.Request()
        for node_name in self.NAV_LIFECYCLE_NODES:
            while time.monotonic() < deadline:
                state = self._call_if_available(
                    GetState,
                    f"/{node_name}/get_state",
                    get_request,
                    2.0,
                )
                if state is None:
                    time.sleep(0.2)
                    continue
                state_id = state.current_state.id
                if state_id == LifecycleState.PRIMARY_STATE_ACTIVE:
                    break
                if state_id == LifecycleState.PRIMARY_STATE_UNCONFIGURED:
                    transition_id = Transition.TRANSITION_CONFIGURE
                elif state_id == LifecycleState.PRIMARY_STATE_INACTIVE:
                    transition_id = Transition.TRANSITION_ACTIVATE
                else:
                    time.sleep(0.2)
                    continue
                change = ChangeState.Request()
                change.transition.id = transition_id
                self._call_if_available(
                    ChangeState,
                    f"/{node_name}/change_state",
                    change,
                    5.0,
                )
                time.sleep(0.2)
            else:
                return False
        return self._wait_navigation_active(10.0)

    def _navigation_requested(self, mode, operation):
        contract = self.catalog.modes[mode]
        return bool(contract["navigation_capable"]) and operation in contract.get(
            "navigation_operations", ["localization", "slam_navigation"]
        )

    def _verify_old_owners_absent(
        self, old_mode, timeout_sec, allowed_owners=None
    ):
        if not old_mode or old_mode not in self.catalog.modes:
            return
        contract = self.catalog.modes[old_mode]
        owners = {
            contract["map_to_odom_owner"],
            contract["odom_to_base_owner"],
        }
        owners -= set(allowed_owners or ())
        deadline = time.monotonic() + timeout_sec
        while time.monotonic() < deadline:
            names = set(self.get_node_names())
            if owners.isdisjoint(names):
                return
            time.sleep(0.1)
        raise RuntimeError(f"旧 TF 发布节点仍未退出：{sorted(owners & names)}")

    def _old_shutdown_timeout(self, mode):
        if mode in self.catalog.modes:
            return float(self.catalog.modes[mode]["shutdown_timeout_sec"])
        return 10.0

    def _normalize_map_id(self, mode, operation, requested):
        requested = requested.strip()
        if operation == "localization":
            if not requested:
                raise ValueError("加载地图时必须提供 map_id")
            MapRegistry._validate_identifier("map_id", requested)
            return requested
        label = requested or mode
        label = re.sub(r"[^A-Za-z0-9._-]+", "-", label).strip("-.")
        if not label:
            raise ValueError("地图标签清理后为空")
        if re.fullmatch(r"\d{8}T\d{6}Z-[A-Za-z0-9._-]+", label):
            return label
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"{stamp}-{label}"

    def _zero_timer(self):
        if self._zero_hold_active:
            self.zero_publisher.publish(Twist())

    def _set_zero_hold(self, active):
        self._zero_hold_active = bool(active)

    def _publish_status(self, message):
        status = SlamStatus()
        status.stamp = self.get_clock().now().to_msg()
        status.state = self.machine.state.value
        status.mode = self.current_mode
        status.operation = self.current_operation
        status.map_id = self.current_map_id
        status.transaction_id = self.machine.transaction_id
        status.message = message or self.machine.message
        self.status_publisher.publish(status)

    @staticmethod
    def _foxglove_active():
        return (
            subprocess.run(
                ["systemctl", "is-active", "--quiet", "foxglove-websocket.service"],
                check=False,
                timeout=2.0,
            ).returncode
            == 0
        )

    @staticmethod
    def _hash_files(paths):
        digest = hashlib.sha256()
        for path in sorted(Path(path) for path in paths):
            digest.update(path.name.encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
        return digest.hexdigest()

    def _software_versions(self):
        return {"omnifleet_localization": "0.2.0", "glim": "1.2.2"}

    def destroy_node(self):
        try:
            if rclpy.ok(context=self.context):
                self._set_zero_hold(True)
        except Exception as error:
            self.get_logger().error(f"关闭时保持零速度失败：{error}")
        try:
            self.supervisor.stop(
                min(2.0, self._old_shutdown_timeout(self.current_mode))
            )
        except Exception as error:
            self.get_logger().error(f"关闭托管后端失败：{error}")
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = SlamManagerNode()
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    try:
        executor.spin()
    except ExternalShutdownException:
        pass
    except KeyboardInterrupt:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    finally:
        executor.remove_node(node)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
