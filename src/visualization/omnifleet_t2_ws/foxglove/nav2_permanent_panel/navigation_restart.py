#!/usr/bin/env python3
"""Panel-controlled application restart; base services remain owned by systemd."""
import json
from collections import deque
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys
import threading
import time
import uuid

DIRECTORY = Path.home() / '.local/share/omnifleet_t2/navigation-stack'
SETTINGS = DIRECTORY / 'command.json'
STATUS = DIRECTORY / 'status.json'
WRAPPER = Path(__file__).with_suffix('.sh')
DEFAULT = 'ros2 launch omnifleet_bringup mola_nav2_unified.launch.py startup_mode:=mapping'
BUSY = {'queued', 'stopping', 'starting', 'waiting'}
LOCK = threading.Lock()
MAP_TOPICS = ('/map', '/global_costmap/costmap', '/local_costmap/costmap')


def readiness_session_config(source, target):
    config = read_json(Path(source), {})
    # A panel worker inherits the user manager's 64 KiB memlock limit. Keep
    # this small control/health observer on TCP; production nodes retain SHM.
    config.setdefault('transport', {}).setdefault('shared_memory', {})['enabled'] = False
    write_json(Path(target), config)
    return str(target)


def map_readiness(samples, monotonic_now, ros_now):
    missing = []
    for topic in MAP_TOPICS:
        sample = samples.get(topic)
        if sample is None:
            missing.append(topic + ' 未收到')
        elif not sample['valid']:
            missing.append(topic + ' 尚无有效地图数据')
        elif sample['count'] < 2:
            missing.append(topic + ' 等待连续更新')
        elif monotonic_now - sample['received'] >= 3 or ros_now - sample['stamp'] >= 3:
            missing.append(topic + ' 超过3秒未更新')
    return not missing, '；'.join(missing)


def robot_topic(name):
    """Return an absolute ROS name in the local domain."""
    return '/' + name.lstrip('/')


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False))
    temporary.replace(path)


def read_json(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def parse_command(command):
    command = command.strip()
    if not command.strip() or len(command) > 2048 or any(c in command for c in '\n\r;|&`<>$'):
        raise ValueError('请只填写一条 ros2 launch 命令，不要填写 source、管道或多条命令')
    argv = shlex.split(command)
    if (len(argv) < 4 or argv[:2] != ['ros2', 'launch'] or
            not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', argv[2]) or
            not re.fullmatch(r'[A-Za-z0-9_.-]+\.(py|xml|yaml|yml)', argv[3]) or
            any(not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*:=.+', a) for a in argv[4:])):
        raise ValueError('格式：ros2 launch 包名 文件.launch.py 参数名:=值')
    return argv


def validate(command):
    parse_command(command)
    result = subprocess.run(['/bin/bash', str(WRAPPER), '--check'], input=command,
                            text=True, capture_output=True, timeout=30)
    if result.returncode:
        raise ValueError(result.stderr.strip().splitlines()[-1] if result.stderr else '启动文件不存在')


def user_env():
    return {**os.environ, 'XDG_RUNTIME_DIR': f'/run/user/{os.getuid()}',
            'DBUS_SESSION_BUS_ADDRESS': f'unix:path=/run/user/{os.getuid()}/bus'}


def state():
    result = read_json(STATUS, {'phase': 'idle', 'message': '尚未通过面板重启'})
    if not result.get('message'):
        result['message'] = '导航进程已中断；可点击按钮重新启动'
    result['command'] = read_json(SETTINGS, {'command': DEFAULT})['command']
    if result['phase'] in BUSY | {'running'} and result.get('unit'):
        active = subprocess.run(['systemctl', '--user', 'is-active', result['unit']],
                                env=user_env(), capture_output=True, text=True, timeout=2)
        if active.returncode and time.time() - result.get('updated', 0) > 5:
            result.update(phase='stopped', message='启动进程已退出；请检查日志后重新启动')
    return result


def handle(name, command=''):
    if name == '__stack_status':
        return state()
    with LOCK:
        current = state()
        if current['phase'] in BUSY:
            raise ValueError('正在重启，请等待本次操作结束')
        validate(command)  # Reject bad launch files before canceling any navigation.
        write_json(SETTINGS, {'command': command.strip()})
        if name == '__stack_command':
            return state()
        operation = uuid.uuid4().hex[:12]
        unit = 'omnifleet-panel-stack-' + operation
        log = DIRECTORY / (operation + '.log')
        status = {'operation': operation, 'unit': unit, 'phase': 'queued',
                  'command': command.strip(), 'message': '已收到重启请求',
                  'updated': time.time(), 'log': str(log)}
        request = DIRECTORY / (operation + '.json')
        write_json(request, {**status, 'previous_unit': current.get('unit')})
        write_json(STATUS, status)
        result = subprocess.run(['systemd-run', '--user', '--collect', '--unit=' + unit,
                                 '--property=TimeoutStopSec=15', '/bin/bash', str(WRAPPER),
                                 '--worker', str(request)], env=user_env(),
                                capture_output=True, text=True, timeout=5)
        if result.returncode:
            status.update(phase='failed', message=result.stderr.strip())
            write_json(STATUS, status)
            raise RuntimeError(status['message'])
        return status


def worker(request_file):
    data = read_json(Path(request_file), {})
    os.environ['ZENOH_SESSION_CONFIG_URI'] = readiness_session_config(
        os.environ['ZENOH_SESSION_CONFIG_URI'], DIRECTORY / (data['operation'] + '-observer.json5'))
    import rclpy
    from action_msgs.srv import CancelGoal
    from geometry_msgs.msg import Twist
    from lifecycle_msgs.srv import GetState
    from nav_msgs.msg import OccupancyGrid, Odometry
    from std_msgs.msg import Empty
    from std_srvs.srv import Trigger
    from mola_msgs.srv import MapSave
    from tf2_ros import Buffer, TransformListener, TransformException
    from rclpy.time import Time
    from rclpy.qos import QoSProfile, DurabilityPolicy
    from omnifleet_waypoint_ui.localization_health import LocalizationHealth
    log = open(data['log'], 'a', buffering=1)
    os.dup2(log.fileno(), 1)
    os.dup2(log.fileno(), 2)
    def update(phase, message, **extra):
        if read_json(STATUS, {}).get('operation') == data['operation']:
            data.update(phase=phase, message=message, updated=time.time(), **extra)
            write_json(STATUS, data)
        print(phase + ': ' + message, flush=True)
    from fleet_scope import ros_args, frame
    rclpy.init(args=ros_args())
    node = rclpy.create_node('panel_navigation_restart')
    health = LocalizationHealth()
    tf_buffer = Buffer()
    tf_listener = TransformListener(tf_buffer, node)
    child = None
    managed_unit = 'omnifleet-t2-mola.service'
    nav2_unit = 'omnifleet-t2-pure-lio-nav2.service'
    router_unit = 'omnifleet-t2-zenoh-router.service'

    def system_service(action, unit, timeout=40):
        units = [unit] if isinstance(unit, str) else list(unit)
        result = subprocess.run(
            ['sudo', '-n', 'systemctl', action, *units],
            capture_output=True, text=True, timeout=timeout)
        if result.returncode:
            detail = (result.stderr or result.stdout).strip()
            raise RuntimeError(f'systemd {action} {", ".join(units)} 失败：{detail}')

    def system_service_active(unit):
        result = subprocess.run(
            ['systemctl', 'is-active', '--quiet', unit],
            timeout=3)
        return result.returncode == 0
    def request(client, value, seconds=3):
        if not client.wait_for_service(timeout_sec=seconds):
            raise RuntimeError('服务不可用：' + client.srv_name)
        future = client.call_async(value)
        rclpy.spin_until_future_complete(node, future, timeout_sec=seconds)
        if not future.done():
            raise TimeoutError('服务没有应答：' + client.srv_name)
        return future.result()
    def spin(seconds):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            rclpy.spin_once(node, timeout_sec=.1)
            try:
                transform = tf_buffer.lookup_transform(frame('map'), frame('base_link'), Time())
                stamp = transform.header.stamp.sec + transform.header.stamp.nanosec * 1e-9
                if stamp != health.stamp:
                    health.observe(stamp, time.monotonic())
            except TransformException:
                health.stamp = None
                health.stable_since = None
            health.check(node.get_clock().now().nanoseconds / 1e9, time.monotonic())
    try:
        update('stopping', '正在取消导航并等待车辆停止')
        stop = node.create_publisher(Empty, robot_topic('/omnifleet_t2/waypoints/stop'), 10)
        zero = node.create_publisher(Twist, robot_topic('/cmd_vel'), 10)
        odom = deque(maxlen=200)
        node.create_subscription(Odometry, robot_topic('/odom'), lambda m: odom.append(
            (time.monotonic(), m.twist.twist.linear.x, m.twist.twist.angular.z)), 10)
        spin(.5)
        stop.publish(Empty())
        for action in ('navigation/execute', 'navigate_to_pose', 'navigate_through_poses', 'follow_path'):
            client = node.create_client(CancelGoal, robot_topic(action + '/_action/cancel_goal'))
            if client.wait_for_service(timeout_sec=.5):
                reply = request(client, CancelGoal.Request())
                if reply.return_code not in (0, 3):
                    raise RuntimeError('取消导航被拒绝：' + action)
        for _ in range(15):
            zero.publish(Twist())
            spin(.1)
        recent = [v for v in odom if time.monotonic() - v[0] < .8]
        if not recent or any(abs(v[1]) > .02 or abs(v[2]) > .05 for v in recent):
            raise RuntimeError('尚未确认车辆停止，已取消重启；请检查里程计或底盘')
        mapping_mode = re.search(r'(?:^|\s)startup_mode:=mapping(?:\s|$)', data['command']) is not None
        if 'mola_nav2_unified.launch.py' in data['command'] and not mapping_mode:
            save = node.create_client(MapSave, robot_topic('/map_save'))
            if save.wait_for_service(timeout_sec=1):
                prefix = str(DIRECTORY / (data['operation'] + '-map'))
                reply = request(save, MapSave.Request(map_path=prefix), seconds=15)
                if not reply.success:
                    raise RuntimeError('当前地图备份失败，保留现有导航栈：' + reply.error_message)
                update('stopping', '地图已备份，正在清理旧应用节点', map_backup=prefix)
        previous = data.get('previous_unit')
        if previous and re.fullmatch(r'omnifleet-panel-stack-[a-f0-9]{12}', previous):
            active = subprocess.run(['systemctl', '--user', 'is-active', previous], env=user_env(),
                                    capture_output=True, timeout=2)
            if active.returncode == 0:
                subprocess.run(['systemctl', '--user', 'stop', previous], env=user_env(), timeout=20, check=True)
        if 'mola_nav2_unified.launch.py' not in data['command']:
            raise RuntimeError('当前导航重启入口只允许使用 systemd 管理的统一 MOLA/Nav2 服务')
        invalidator = node.create_client(Trigger, robot_topic('/omnifleet_t2/waypoints/invalidate_map'))
        cleared = request(invalidator, Trigger.Request(), seconds=5)
        if not cleared.success:
            raise RuntimeError('旧地图航点清除失败，已取消重启：' + cleared.message)
        update('stopping', '旧航点、持久路线及路线预览已清空，正在重启地图与导航')
        system_service('stop', ('omnifleet-t2-waypoints.service',
                               'omnifleet-local-navigation.service', 'omnifleet-t2-foxglove.service'))
        system_service('stop', nav2_unit)
        system_service('stop', managed_unit)
        cleanup = Path('/home/iecme/omnifleet_a2_ws/src/system/omnifleet_bringup/scripts/cleanup_unified_application_nodes.py')
        subprocess.run([sys.executable, str(cleanup)], timeout=12, check=True)
        # The router caches mapped SHM pools from the old application sessions.
        # Rebuild that cache while the navigation applications are stopped.
        update('starting', '正在清理旧共享内存会话并恢复本机通信')
        system_service('restart', router_unit, timeout=40)
        update('starting', '正在通过 systemd 启动 MOLA 与 Nav2')
        system_service('start', managed_unit, timeout=50)
        system_service('start', nav2_unit, timeout=50)
        system_service('start', 'omnifleet-local-navigation.service', timeout=20)
        system_service('start', 'omnifleet-t2-waypoints.service', timeout=20)
        system_service('start', 'omnifleet-t2-foxglove.service', timeout=20)
        mapping_mode = re.search(r'(?:^|\s)startup_mode:=mapping(?:\s|$)', data['command']) is not None
        wait_label = '等待实时建图地图、导航节点与局部代价地图就绪' if mapping_mode else '等待已加载地图、导航节点与局部代价地图就绪'
        update('waiting', wait_label + '（systemd：' + managed_unit + ' + ' + nav2_unit + '）')
        maps = {}
        map_subscriptions = []
        def observe_map(topic, message):
            stamp = message.header.stamp.sec + message.header.stamp.nanosec * 1e-9
            previous = maps.get(topic)
            maps[topic] = {
                'received': time.monotonic(),
                'stamp': stamp,
                'count': (previous['count'] if previous else 0) +
                         (0 if previous and previous['stamp'] == stamp else 1),
                'valid': bool(message.data) and (topic != '/map' or any(v >= 0 for v in message.data)),
            }
        map_qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        for topic in MAP_TOPICS:
            map_subscriptions.append(node.create_subscription(
                OccupancyGrid, robot_topic(topic), lambda m, topic=topic: observe_map(topic, m), map_qos))
        clients = [node.create_client(GetState, robot_topic(n + '/get_state'))
                   for n in ('controller_server', 'planner_server', 'bt_navigator',
                             'behavior_server', 'waypoint_follower')]
        deadline = time.monotonic() + 150
        map_reason = '等待地图数据'
        while (system_service_active(managed_unit) and
               system_service_active(nav2_unit) and time.monotonic() < deadline):
            spin(.5)
            localization_ready = health.ready(node.get_clock().now().nanoseconds / 1e9, time.monotonic())
            maps_ready, map_reason = map_readiness(
                maps, time.monotonic(), node.get_clock().now().nanoseconds / 1e9)
            if maps_ready and localization_ready:
                try:
                    if all(request(c, GetState.Request(), seconds=1).current_state.id == 3 for c in clients):
                        maps_ready, map_reason = map_readiness(
                            maps, time.monotonic(), node.get_clock().now().nanoseconds / 1e9)
                        if not maps_ready or not health.ready(node.get_clock().now().nanoseconds / 1e9, time.monotonic()):
                            continue
                        update('running', '重启完成：地图、代价地图、导航节点及定位已就绪；' + health.reason,
                               tf_age_ms=health.age_ms, localization_ready=True, localization_status=health.reason,
                               maps_ready=True, map_status='三份地图持续更新')
                        break
                except (RuntimeError, TimeoutError):
                    pass
            update('waiting', wait_label + ('；' + map_reason if map_reason else '') + '；' + health.reason,
                   tf_age_ms=health.age_ms, localization_ready=localization_ready, localization_status=health.reason,
                   maps_ready=maps_ready, map_status=map_reason)
        else:
            raise RuntimeError('启动退出或等待就绪超时；' + map_reason + '；' + health.reason + '；请查看启动日志')
        while system_service_active(managed_unit) and system_service_active(nav2_unit):
            spin(1)
            localization_ready = health.ready(node.get_clock().now().nanoseconds / 1e9, time.monotonic())
            maps_ready, map_reason = map_readiness(
                maps, time.monotonic(), node.get_clock().now().nanoseconds / 1e9)
            update('running', ('导航栈运行中；' if maps_ready and localization_ready else '导航数据未就绪；') +
                   (map_reason + '；' if map_reason else '') + health.reason,
                   tf_age_ms=health.age_ms, localization_ready=localization_ready, localization_status=health.reason,
                   maps_ready=maps_ready, map_status=map_reason)
        update('stopped', 'systemd 服务已停止：' + managed_unit + ' + ' + nav2_unit)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        update('stopped', '导航栈已停止；可点击按钮重新启动')
    except Exception as error:
        update('failed', str(error) or type(error).__name__)
    finally:
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGINT)
            try:
                child.wait(timeout=8)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    if sys.argv[1] == '--check':
        from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
        argv = parse_command(sys.stdin.read())
        try:
            share = Path(get_package_share_directory(argv[2]))
        except PackageNotFoundError:
            sys.exit('找不到 ROS 包：' + argv[2] + '，请检查包名或工作空间安装情况')
        if not any(p.is_file() for p in share.rglob(argv[3])):
            sys.exit('找不到启动文件：' + argv[2] + '/' + argv[3])
    elif sys.argv[1] == '--worker':
        worker(sys.argv[2])
