"""Save and restore waypoints alongside the exact MOLA map they describe."""

import hashlib
import json
import math
import time

import yaml
from pathlib import Path

from geometry_msgs.msg import PoseWithCovarianceStamped
from mola_msgs.srv import MapLoad, MapSave, MolaRuntimeParamGet, MolaRuntimeParamSet, RelocalizeNearPose
from nav_msgs.msg import Odometry
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from rclpy.qos import qos_profile_sensor_data
from rclpy.task import Future
from std_msgs.msg import Float32
from std_srvs.srv import Trigger


SAVED_MAPS = Path("/var/lib/omnifleet_a2/maps/112-live/saved")


def bundle_paths(value):
    prefix = Path(value)
    if prefix.suffix == ".mm":
        prefix = prefix.with_suffix("")
    if prefix.parent.resolve() != SAVED_MAPS.resolve() or not prefix.name:
        raise ValueError("地图路径不在 124 的保存目录")
    return prefix, prefix.parent / (prefix.name + ".mm"), prefix.parent / (prefix.name + ".waypoints.json")


def map_digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_matching_route(sidecar, digest, frame):
    from .waypoint_ui_bridge import load_route

    try:
        record = json.loads(sidecar.read_text(encoding="utf-8"))
        if record.get("map_sha256") == digest and record.get("frame_id") == frame:
            return load_route(sidecar)
    except (OSError, ValueError, AttributeError, TypeError):
        pass
    return []


async def call_response(node, client, request, timeout):
    if not client.service_is_ready():
        raise RuntimeError(f'车端服务未就绪：{client.srv_name}')
    future = client.call_async(request)
    timer = node.create_timer(timeout, future.cancel)
    try:
        return await future
    finally:
        node.destroy_timer(timer)


async def call_map(node, client, request, timeout=60.0):
    result = await call_response(node, client, request, timeout)
    if result is None or not getattr(result, 'success', getattr(result, 'accepted', False)):
        raise RuntimeError(getattr(result, 'error_message', '') or 'MOLA未接受请求或应答超时')
    return result


class MapLocalization:
    def __init__(self, node, group):
        self.node = node
        self.pose = None
        self.quality = None
        self.relocate = node.create_client(RelocalizeNearPose, '/relocalize_near_pose', callback_group=group)
        self.get_parameters = node.create_client(MolaRuntimeParamGet, '/mola_runtime_param_get', callback_group=group)
        self.set_parameters = node.create_client(MolaRuntimeParamSet, '/mola_runtime_param_set', callback_group=group)
        node.create_subscription(Odometry, '/lidar_odometry/pose', self.observe_pose, qos_profile_sensor_data, callback_group=group)
        node.create_subscription(Float32, '/lidar_odometry/pose_quality', self.observe_quality, qos_profile_sensor_data, callback_group=group)

    def observe_pose(self, message):
        if message.header.frame_id == self.node.frame_id:
            stamp = message.header.stamp
            self.pose = ((stamp.sec, stamp.nanosec), time.monotonic(), message.pose.pose)

    def observe_quality(self, message):
        self.quality = (time.monotonic(), message.data)

    async def mapping_mode(self):
        reply = await call_response(self.node, self.get_parameters, MolaRuntimeParamGet.Request(), 7.0)
        if reply is None:
            raise RuntimeError('读取 MOLA 建图状态超时')
        for name, params in yaml.safe_load(reply.parameters).items():
            if name.startswith('mola::LidarOdometry:'):
                return name, params['mapping_enabled']
        raise RuntimeError('当前 MOLA 未公布建图状态')

    async def set_mapping(self, module, enabled):
        parameters = yaml.safe_dump({module: {'mapping_enabled': enabled}})
        await call_map(self.node, self.set_parameters, MolaRuntimeParamSet.Request(parameters=parameters), timeout=7.0)

    async def confirm_match(self, pose):
        await call_map(self.node, self.relocate, RelocalizeNearPose.Request(pose=pose), timeout=8.0)
        requested_at = time.monotonic()
        previous_stamp = self.pose[0] if self.pose else (0, 0)
        result = Future()
        deadline = requested_at + 20.0
        matched = 0

        def check_match():
            nonlocal matched, previous_stamp
            if result.done():
                return
            newest, quality = self.pose, self.quality
            now = time.monotonic()
            if newest and quality and min(newest[1], quality[0]) > requested_at and now - min(newest[1], quality[0]) < 0.75:
                if not math.isfinite(quality[1]) or quality[1] <= 0:
                    matched = 0
                elif newest[0] > previous_stamp and abs(newest[1] - quality[0]) < 0.2:
                    previous_stamp = newest[0]
                    matched += 1
                    if matched >= 3:
                        result.set_result(quality[1])
                        return
            else:
                matched = 0
            if now >= deadline:
                result.set_result(None)

        monitor = self.node.create_timer(0.25, check_match)
        try:
            quality = await result
        finally:
            self.node.destroy_timer(monitor)
        if quality is None:
            raise RuntimeError('重定位未确认，请在地图上设置当前位置和朝向')
        return quality


def install_map_bundle(node):
    from .waypoint_ui_bridge import save_route

    clients = ReentrantCallbackGroup()
    services = MutuallyExclusiveCallbackGroup()
    saver = node.create_client(MapSave, "/map_save", callback_group=clients)
    loader = node.create_client(MapLoad, "/map_load", callback_group=clients)
    grid = node.create_client(Trigger, "/mola_realtime_nav_grid/clear", callback_group=clients)
    localization = MapLocalization(node, clients)
    pending = None

    async def save(request, response):
        try:
            prefix, map_file, sidecar = bundle_paths(request.map_path)
            prefix.parent.mkdir(parents=True, exist_ok=True)
            node.sync_map_session()
            if node.map_changing or not node.map_session:
                raise RuntimeError("当前地图尚未就绪")
            session = node.map_session
            points = list(node.waypoints)
            await call_map(node, saver, MapSave.Request(map_path=str(prefix)))
            node.sync_map_session()
            if node.map_session != session:
                raise RuntimeError("保存时地图已经切换，请重新保存")
            save_route(sidecar, node.frame_id, points, map_sha256=map_digest(map_file))
            response.success = True
            node.publish_status(f"地图和关联航点已保存（{len(points)} 个航点）")
        except Exception as error:
            response.error_message = str(error)
        return response

    async def load(request, response):
        nonlocal pending
        try:
            if node.navigation_active:
                raise RuntimeError("请先停止当前导航")
            prefix, map_file, sidecar = bundle_paths(request.map_path)
            points = load_matching_route(sidecar, map_digest(map_file), node.frame_id)
            node.sync_map_session()
            session = node.map_session
            if not session:
                raise RuntimeError("当前建图进程未就绪")
            module, enabled = await localization.mapping_mode()
            restore_mapping = enabled or bool(pending and pending[0] == session and pending[3])
            if enabled:
                await localization.set_mapping(module, False)
            node.map_changing = True
            pending = None
            try:
                node.clear_map_waypoints()
                await call_map(node, loader, MapLoad.Request(map_path=str(prefix)))
            except Exception:
                node.map_changing = False
                if restore_mapping:
                    await localization.set_mapping(module, True)
                raise
            pending = (session, points, module, restore_mapping)
            response.success = True
            response.error_message = "地图已加载。请使用初始定位工具，定位确认后将显示关联航点。"
            node.publish_status(response.error_message)
        except Exception as error:
            response.error_message = str(error)
        return response

    async def initial_pose(message):
        nonlocal pending
        if node.navigation_active or message.header.frame_id != node.frame_id:
            return
        node.sync_map_session()
        if pending and pending[0] != node.map_session:
            pending = None
            node.map_changing = False
        try:
            node.publish_status("正在用激光扫描精细对齐地图…")
            quality = await localization.confirm_match(message)
            if pending:
                session, points, module, restore_mapping = pending
                node.sync_map_session()
                if session != node.map_session:
                    raise RuntimeError("建图进程已切换，请重新加载地图")
                await call_map(node, grid, Trigger.Request(), timeout=5.0)
                if restore_mapping:
                    await localization.set_mapping(module, True)
                node.waypoints = points
                node.persist()
                node.publish_visuals()
                pending = None
                node.map_changing = False
            node.publish_status(f"重定位已确认（ICP 匹配质量 {quality:.2f}）")
        except Exception as error:
            node.publish_status(f"初始定位未完成：{error}")

    node.create_service(MapSave, "/omnifleet_t2/waypoints/map_save", save, callback_group=services)
    node.create_service(MapLoad, "/omnifleet_t2/waypoints/map_load", load, callback_group=services)
    node.create_subscription(PoseWithCovarianceStamped, "/initialpose", initial_pose, 1, callback_group=services)

