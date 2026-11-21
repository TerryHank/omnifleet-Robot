#!/usr/bin/env python3
"""Run the tutorial catalogue on 104; Foxglove only sends case selections."""
import json
import os
import queue
import shlex
import signal
import subprocess
import sys
import threading
import time
from collections import deque
from pathlib import Path

import rclpy
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node
from std_msgs.msg import String
from rcl_interfaces.msg import Parameter, ParameterType, ParameterValue
from rcl_interfaces.srv import SetParameters

APP_CASES = ("04_09_body_tracking", "02_07_kcf")


class DemoManager(Node):
    def __init__(self):
        super().__init__('vision_demo_manager')
        catalog = Path(get_package_share_directory('omnifleet_tutorials')) / 'config/vision_cases.json'
        self.cases = {case['id']: case for case in json.loads(catalog.read_text())}
        self.commands = queue.Queue()
        self.lock = threading.RLock()
        self.logs = deque(maxlen=100)
        self.requests = deque(maxlen=100)
        self.process = None
        self.warm_cases = {}
        self.active_warm = None
        self.parameter_clients = {}
        self.busy = False
        self.state = dict(phase='IDLE', case_id=None, message='请选择案例并开始演示',
                          request_id=None, exit_code=None, started_at=None, motion_enabled=False)
        self.publisher = self.create_publisher(String, '/vision/demo/status', 1)
        self.create_subscription(String, '/vision/demo/control', self.receive, 10)
        self.create_timer(.5, self.publish)
        threading.Thread(target=self.work, daemon=True).start()

    def find_cases(self):
        found = []
        for entry in Path('/proc').iterdir():
            if not entry.name.isdigit():
                continue
            try:
                if entry.stat().st_uid != os.getuid() or (entry / 'stat').read_text().split()[2] == 'Z':
                    continue
                args = (entry / 'cmdline').read_bytes().decode().strip('\0').split('\0')
                for i, arg in enumerate(args[:-3]):
                    if Path(arg).name == 'ros2' and args[i+1:i+3] == ['launch', 'omnifleet_tutorials']:
                        case = args[i+3].removeprefix('vision_').removesuffix('.launch.py')
                        if case in self.cases and args[i+3] == f'vision_{case}.launch.py':
                            found.append(dict(pid=int(entry.name), case_id=case))
            except (OSError, UnicodeError, IndexError):
                continue
        return sorted(found, key=lambda item: item['pid'])

    def update(self, **values):
        with self.lock:
            self.state.update(values)

    def receive(self, message):
        try:
            request = json.loads(message.data)
            if request.get('op') not in ('start', 'stop', 'navigation', 'restart_slam', 'preload'):
                raise ValueError('操作只能是 start、stop、navigation 或 restart_slam')
            if request['op'] == 'preload' and request.get('case_id') not in APP_CASES:
                raise ValueError('预加载只用于 App 识别模式')
            if request['op'] == 'start' and request.get('case_id') not in self.cases:
                raise ValueError('案例不在功能列表中')
            request_id = str(request['id'])
            with self.lock:
                if request_id in self.requests:
                    return
                self.requests.append(request_id)
            self.commands.put(request)
        except (ValueError, KeyError, TypeError) as error:
            self.update(message=f'请求错误：{error}')

    def stop_cases(self, exclude=()):
        running = [case for case in self.find_cases() if case["pid"] not in exclude]
        if not running:
            return
        self.update(phase='STOPPING', message='正在停止当前视觉案例')
        for item in running:
            try:
                os.kill(item['pid'], signal.SIGINT)
            except ProcessLookupError:
                pass
        pids = {item['pid'] for item in running}
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            if not any(item['pid'] in pids for item in self.find_cases()):
                return
            time.sleep(.1)
        for item in self.find_cases():
            pid = item['pid']
            if pid not in pids:
                continue
            try:
                if os.getpgid(pid) == pid:
                    os.killpg(pid, signal.SIGKILL)
                else:
                    os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            if not any(item['pid'] in pids for item in self.find_cases()):
                return
            time.sleep(.1)
        raise RuntimeError('案例尚未退出，请查看下方日志；未启动新的案例')

    def arguments(self, request):
        case = self.cases[request['case_id']]
        values = request.get('parameters') or {}
        if not isinstance(values, dict):
            raise ValueError('案例参数格式错误')
        args = ['ros2', 'launch', 'omnifleet_tutorials', f"vision_{case['id']}.launch.py",
                'start_camera:=false', 'use_gui:=true', 'enable_motion:=false']
        for field in case.get('fields', []):
            if any(str(values.get(key, next((f.get('default', '') for f in case['fields'] if f['name'] == key), ''))) != expected
                   for key, expected in field.get('when', {}).items()):
                continue
            value = str(values.get(field['name'], field.get('default', ''))).strip()
            if field.get('required') and not value:
                raise ValueError(f"请填写{field['label']}")
            if value:
                if field['name'] == 'enable_motion':
                    args = [arg for arg in args if not arg.startswith('enable_motion:=')]
                args.append(f"{field['name']}:={value}")
        return args

    def read_output(self, process):
        for line in process.stdout:
            if '模型预加载完成' in line or '模型预加载失败' in line or 'NanoTrack 预加载失败' in line:
                self.get_logger().info(line.rstrip())
            with self.lock:
                if self.process is process:
                    self.logs.append(line.rstrip())

    def set_switch(self, node, **values):
        client = self.parameter_clients.get(node)
        if client is None:
            client = self.create_client(SetParameters, node + '/set_parameters')
            self.parameter_clients[node] = client
        if not client.wait_for_service(timeout_sec=38.):
            raise RuntimeError(f'{node} 尚未完成启动')
        request = SetParameters.Request()
        request.parameters = [Parameter(name=name, value=ParameterValue(
            type=ParameterType.PARAMETER_BOOL, bool_value=value)) for name, value in values.items()]
        deadline = time.monotonic() + 42.
        while True:
            result = client.call_async(request)
            done = threading.Event()
            result.add_done_callback(lambda _, event=done: event.set())
            if done.wait(max(0., min(6., deadline - time.monotonic()))) and result.result() is not None:
                break
            client.remove_pending_request(result)
            if time.monotonic() >= deadline:
                raise RuntimeError(f'{node} 切换响应超时')
        replies = result.result().results
        if len(replies) != len(values):
            raise RuntimeError(f'{node} 未返回完整切换状态')
        for item in replies:
            if not item.successful:
                raise RuntimeError(f'{node}: {item.reason}')

    def set_case_active(self, case_id, active):
        if case_id == APP_CASES[0]:
            self.set_switch('/body_tracking_104/horizon_tracking_RobotCmdVel', enable_motion=False)
            self.set_switch('/course_gesture_person_follow', vision_active=active)
        elif active:
            self.set_switch('/course_nanotrack', vision_active=True)
            self.set_switch('/kcf_follower', vision_active=True, enable_motion=False)
        else:
            self.set_switch('/kcf_follower', vision_active=False, enable_motion=False)
            self.set_switch('/course_nanotrack', vision_active=False)

    def ensure_warm(self, case_id):
        process = self.warm_cases.get(case_id)
        if process is not None and process.poll() is None:
            return process
        args = self.arguments(dict(case_id=case_id, parameters={'enable_motion': 'false'}))
        process = subprocess.Popen(args, env=dict(os.environ, OMNIFLEET_WARM_CASE='1'),
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, errors='replace', bufsize=1, start_new_session=True)
        self.warm_cases[case_id] = process
        threading.Thread(target=self.read_output, args=(process,), daemon=True).start()
        self.get_logger().info(f'App 识别预加载 {case_id} pid={process.pid}')
        return process

    def start_warm(self, case_id):
        previous = self.active_warm
        if previous == case_id and self.process is not None and self.process.poll() is None:
            self.update(phase='RUNNING', case_id=case_id, message='识别模式已运行')
            return
        if previous is not None:
            self.set_case_active(previous, False)
        else:
            self.stop_cases(exclude={p.pid for p in self.warm_cases.values() if p.poll() is None})
        self.update(phase='STARTING', case_id=case_id, motion_enabled=False,
                    started_at=time.time(), message='正在切换识别模式')
        process = self.ensure_warm(case_id)
        try:
            self.set_case_active(case_id, True)
        except (ValueError, RuntimeError, OSError):
            if previous is not None:
                self.set_case_active(previous, True)
            raise
        self.process, self.active_warm = process, case_id
        self.update(phase='RUNNING', case_id=case_id, motion_enabled=False,
                    message='已切换至加载完成的识别模式')
        self.get_logger().info(f'App 识别切换 {case_id} pid={process.pid}')

    def work(self):
        while True:
            request = self.commands.get()
            if request['op'] == 'preload':
                try:
                    if self.state['phase'] == 'RUNNING' and self.state['case_id'] == request['case_id']:
                        self.ensure_warm(next(case for case in APP_CASES if case != request['case_id']))
                except (ValueError, OSError) as error:
                    self.get_logger().warning(f'识别预加载失败: {error}')
                finally:
                    self.commands.task_done()
                continue
            with self.lock:
                self.busy = True
            self.update(request_id=request['id'])
            try:
                # Validate the existing launch inputs before replacing a running demo.
                args = self.arguments(request) if request['op'] == 'start' else None
                if (args is not None and request.get('warm') is True
                        and request['case_id'] in APP_CASES and 'enable_motion:=true' not in args):
                    self.start_warm(request['case_id'])
                    continue
                self.stop_cases()
                self.warm_cases.clear()
                self.active_warm = None
                if request['op'] in ('navigation', 'restart_slam'):
                    self.update(phase='STARTING', case_id=None, motion_enabled=False,
                                message='正在清空当前地图并重启 SLAM' if request['op']=='restart_slam' else '正在启动 104 定位、导航和航点服务')
                    subprocess.run([sys.executable,
                                    '/home/iecme/omnifleet_ws/src/system/operator_tools/robot_104_mode.py',
                                    request['op'], '--keep-vision-manager'], check=True, timeout=180)
                    self.update(phase='NAVIGATION', message='导航服务已启动，等待定位和航点状态')
                elif args is None:
                    self.update(phase='STOPPED', message='当前视觉案例已停止', case_id=None, motion_enabled=False)
                else:
                    with self.lock:
                        self.logs.clear()
                    self.update(phase='STARTING', case_id=request['case_id'], exit_code=None,
                                motion_enabled='enable_motion:=true' in args,
                                started_at=time.time(), message='正在 104 上启动案例')
                    # The service already loaded the workspace and its transport
                    # settings. Sourcing it again clears ZENOH_CONFIG_OVERRIDE.
                    subprocess.run([sys.executable,
                                    '/home/iecme/omnifleet_ws/src/system/operator_tools/robot_104_mode.py',
                                    'vision'], check=True, timeout=90)
                    process = subprocess.Popen(args,
                                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                               text=True, errors='replace', bufsize=1,
                                               start_new_session=True)
                    with self.lock:
                        self.process = process
                        self.logs.append('$ ' + shlex.join(args))
                    threading.Thread(target=self.read_output, args=(process,), daemon=True).start()
                    time.sleep(.4)
                    self.update(phase='RUNNING', message='案例进程已启动，等待结果话题')
            except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as error:
                self.update(phase='ERROR', message=str(error))
            finally:
                with self.lock:
                    self.busy = False
                self.commands.task_done()

    def publish(self):
        parked = {process.pid for process in self.warm_cases.copy().values() if process is not self.process}
        running = [case for case in self.find_cases() if case['pid'] not in parked]
        with self.lock:
            if not self.busy:
                if self.process is not None and self.process.poll() is not None:
                    code = self.process.returncode
                    self.process = None
                    self.active_warm = None
                    self.state.update(exit_code=code)
                    if not running and self.state['phase'] not in ('STOPPED', 'ERROR', 'NAVIGATION'):
                        self.state.update(phase='COMPLETED' if code == 0 else 'ERROR',
                                          message=f'案例进程已结束，退出码 {code}')
                if running and self.state['phase'] != 'ERROR':
                    self.state.update(phase='RUNNING', case_id=running[0]['case_id'])
                    if self.state['started_at'] is None:
                        self.state['message'] = '104上已有案例运行，可直接停止或切换演示'
            payload = dict(self.state, server_time=time.time(), busy=self.busy,
                           running=running, logs=list(self.logs), catalog=list(self.cases.values()),
                           host='192.168.3.104', result_topic=self.cases.get(self.state['case_id'], {}).get('imageTopic'))
        self.publisher.publish(String(data=json.dumps(payload)))

    def close(self):
        processes = set(self.warm_cases.values())
        if self.process is not None:
            processes.add(self.process)
        running = [process for process in processes if process.poll() is None]
        for process in running:
            process.send_signal(signal.SIGINT)
        deadline = time.monotonic() + 15.
        for process in running:
            try:
                process.wait(timeout=max(0., deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                process.terminate()


def main():
    rclpy.init()
    node = DemoManager()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
