"""Invalidate the live route when its map session ends; preserve map snapshots."""
import json
import os
import time
from pathlib import Path


def process_started_at(epoch):
    try:
        pid, ticks = epoch.rsplit('|', 1)[-1].split(':')
        actual = Path('/proc', pid, 'stat').read_text().rsplit(')', 1)[1].split()[19]
        if actual != ticks:
            return None
        uptime = float(Path('/proc/uptime').read_text().split()[0])
        return time.time() - uptime + int(ticks) / os.sysconf('SC_CLK_TCK')
    except (OSError, ValueError, IndexError):
        return None


class MapLifecycle:
    def __init__(self, node):
        self.node = node
        self.process_epoch = None
        self.map_stamp = None
        self.map_frame = None
        self.pending = ''
        self.loading = False
        self.expected_stamp_change = False
        self.awaiting_loaded_map = False
        self.map_empty = False
        try:
            if self.binding_file.exists():
                value = json.loads(self.binding_file.read_text())
                self.process_epoch = value.get('process_epoch')
                self.map_stamp = value.get('map_stamp')
                self.map_frame = value.get('map_frame')
                self.pending = value.get('pending', '')
        except (OSError, ValueError):
            self.pending = '地图绑定记录不可用'

    @property
    def binding_file(self):
        route = Path(self.node.route_file)
        return route.with_name(route.name + '.map-session.json')

    @property
    def blocked(self):
        return bool(self.pending or self.map_empty or self.loading)

    def bind(self):
        path = self.binding_file
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + f'.tmp-{os.getpid()}')
        temporary.write_text(json.dumps({'process_epoch': self.process_epoch,
            'map_stamp': self.map_stamp, 'map_frame': self.map_frame,
            'pending': self.pending}, ensure_ascii=False))
        temporary.replace(path)

    def retry(self):
        if not self.pending:
            return True
        from .waypoint_ui_bridge import save_route
        node = self.node
        reason = self.pending
        try:
            self.bind()  # Persist invalidation intent before clearing the live route.
            save_route(node.route_file, node.frame_id, [], node.pass_radius)
            node.waypoints = []
            node.pending_name = ''
            if node.preview_goal_handle:
                node.preview_goal_handle.cancel_goal_async()
            node.publish_visuals()  # DELETEALL, empty path, empty catalog.
            self.pending = ''
            self.bind()
            node.publish_status('地图已变更，当前航点及路线预览已清空：' + reason)
            return True
        except (OSError, ValueError) as error:
            self.pending = reason
            node.publish_status('旧地图航点清除未确认，已禁止使用旧路线：' + str(error))
            return False

    def invalidate(self, reason):
        self.pending = reason
        node = self.node
        if node.navigation_active or (node.edit_navigation_state or {}).get('navigation_active'):
            node.execution.stop('地图已变更，取消旧地图导航')
        node.waypoints = []
        node.pending_name = ''
        if node.preview_goal_handle:
            node.preview_goal_handle.cancel_goal_async()
        node.publish_visuals()
        return self.retry()

    def observe_status(self, state):
        value = state.get('localization_epoch')
        if not isinstance(value, str):
            return
        # The last counter also changes on pose jumps, which are not map reloads.
        epoch = value.rsplit(':', 1)[0] if ':' in value else value
        previous, self.process_epoch = self.process_epoch, epoch
        if previous is not None and previous != epoch:
            self.map_stamp = None
            self.map_frame = None
            self.invalidate('定位建图进程已停止或重新启动')
        elif previous is None:
            started = process_started_at(epoch)
            if started is not None and self.node.route_file.exists() and self.node.route_file.stat().st_mtime < started - 1:
                self.invalidate('保存的航点早于本次建图进程启动')
            else:
                self.bind()

    def observe_map(self, message):
        if self.loading:
            return
        if not message.info.width or not message.info.height or not message.data:
            if not self.map_empty and not self.awaiting_loaded_map:
                self.map_empty = True
                self.invalidate('当前地图已清空')
            return
        self.map_empty = False
        self.awaiting_loaded_map = False
        frame = message.header.frame_id
        stamp = message.info.map_load_time
        stamp = [stamp.sec, stamp.nanosec] if stamp.sec or stamp.nanosec else None
        changed = ((self.map_frame is not None and frame != self.map_frame) or
                   (self.map_stamp is not None and stamp is not None and stamp != self.map_stamp))
        if self.expected_stamp_change and (changed or (self.map_stamp is None and stamp is not None)):
            self.expected_stamp_change = False
            changed = False
        previous = self.map_frame, self.map_stamp
        self.map_frame, self.map_stamp = frame, stamp
        if changed:
            self.invalidate('地图坐标系或地图加载时间已改变')
        elif previous != (frame, stamp):
            self.bind()

    def finish_map_load(self, success):
        self.loading = False
        if success:
            self.pending = ''
            self.map_empty = False
            self.awaiting_loaded_map = True
            self.expected_stamp_change = True
            self.bind()


def install_map_lifecycle(node):
    from nav_msgs.msg import OccupancyGrid
    from std_srvs.srv import Trigger
    from rclpy.qos import QoSProfile, DurabilityPolicy
    lifecycle = node.map_lifecycle = MapLifecycle(node)
    qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
    node.create_subscription(OccupancyGrid, '/map', lifecycle.observe_map, qos)
    node.create_timer(1., lifecycle.retry)
    def invalidate(_request, response):
        response.success = lifecycle.invalidate('导航栈重启或地图重置请求')
        response.message = '当前航点、持久路线与预览已清空' if response.success else '航点清除失败，地图操作已取消'
        return response
    node.create_service(Trigger, '/omnifleet_t2/waypoints/invalidate_map', invalidate)
