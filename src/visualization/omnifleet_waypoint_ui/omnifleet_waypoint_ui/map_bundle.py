"""Acknowledged map operations with a waypoint snapshot beside each map."""
import copy
import json
import os
import shutil
import time
from pathlib import Path

from mola_msgs.srv import MapLoad, MapSave, RelocalizeNearPose
from geometry_msgs.msg import PointStamped, PoseStamped, PoseWithCovarianceStamped
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup


CURRENT_ROAD_NETWORK = Path('/home/iecme/omnifleet_data/missions/road_networks/current_map_waypoints/road_network.geojson')


def road_snapshot_path(waypoint_sidecar):
    return Path(str(waypoint_sidecar)[:-len('.waypoints.json')] + '.road_network.geojson')


def copy_road_network(source, destination):
    if destination.exists():
        shutil.copy2(destination, destination.with_name(destination.name + f'.backup-{time.time_ns()}'))
    if source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        stage = destination.with_name(destination.name + '.pending')
        shutil.copyfile(source, stage)
        os.replace(stage, destination)
    else:
        destination.unlink(missing_ok=True)


async def call_map(node, client, request):
    if not client.service_is_ready():
        raise RuntimeError('MOLA地图服务未就绪')
    future = client.call_async(request)
    timer = node.create_timer(60.0, future.cancel)
    try:
        result = await future
        if future.cancelled():
            raise RuntimeError('MOLA地图操作超时；结果未确认')
        if result is None or not getattr(result, 'success', getattr(result, 'accepted', False)):
            raise RuntimeError(getattr(result, 'error_message', '') or 'MOLA未接受请求')
        return result
    finally:
        node.destroy_timer(timer)


async def save_map(node, client, request, response):
    from .waypoint_ui_bridge import map_sidecar_path, save_route
    stage = None
    try:
        sidecar = map_sidecar_path(request.map_path)
        stage = sidecar.with_name(sidecar.name + '.pending')
        save_route(stage, node.frame_id, copy.deepcopy(node.waypoints), node.pass_radius)
        await call_map(node, client, MapSave.Request(map_path=str(sidecar)[:-len('.waypoints.json')]))
        if sidecar.exists():
            shutil.copy2(sidecar, sidecar.with_name(sidecar.name + f'.backup-{time.time_ns()}'))
        os.replace(stage, sidecar)
        copy_road_network(CURRENT_ROAD_NETWORK, road_snapshot_path(sidecar))
        response.success = True
        response.error_message = ''
        node.publish_status(f'地图、航点及已有全局路网已保存：{sidecar}')
    except Exception as error:
        response.success = False
        response.error_message = f'地图及航点保存未完成：{error}'
        node.publish_status(response.error_message)
    finally:
        if stage is not None:
            stage.unlink(missing_ok=True)
    return response


async def load_map(node, client, request, response):
    lifecycle = getattr(node, "map_lifecycle", None)
    from .waypoint_ui_bridge import load_pass_radius, load_route, map_sidecar_path, save_route
    try:
        state = node.edit_navigation_state
        if node.navigation_active or state is None or time.monotonic() - node.edit_navigation_time > 2:
            raise RuntimeError('导航状态未确认停稳，不能加载地图')
        if state.get('navigation_active'):
            raise RuntimeError('正在导航，请先停止再加载地图')
        sidecar = map_sidecar_path(request.map_path)
        points = load_route(sidecar)
        radius = load_pass_radius(sidecar)
        if sidecar.is_file():
            frame = json.loads(sidecar.read_text()).get('frame_id', node.frame_id)
            if frame != node.frame_id:
                raise ValueError(f'地图航点坐标系不匹配：{frame}')
        if lifecycle:
            lifecycle.loading = True
            node.publish_catalog()
        await call_map(node, client, MapLoad.Request(map_path=str(sidecar)[:-len('.waypoints.json')]))
        # The sidecar is a saved snapshot; subsequent edits belong to the live route.
        save_route(node.route_file, node.frame_id, points, radius)
        copy_road_network(road_snapshot_path(sidecar), CURRENT_ROAD_NETWORK)
        node.waypoints, node.pass_radius, node.pending_name = points, radius, ''
        if lifecycle:
            lifecycle.finish_map_load(True)
        node.publish_visuals()
        response.success = True
        response.error_message = ''
        node.publish_status(f'地图及航点已加载：{sidecar}（{len(points)}个点）' if sidecar.is_file()
                            else '地图已加载；没有关联航点文件，当前航点已清空')
    except Exception as error:
        response.success = False
        if lifecycle:
            lifecycle.finish_map_load(False)
        response.error_message = f'地图及航点加载未完成：{error}'
        node.publish_status(response.error_message)
    return response


def add_point(node, message):
    pose = PoseStamped()
    pose.header = message.header
    pose.pose.position = message.point
    pose.pose.orientation.w = 1.0
    node.on_add_pose(pose)


async def set_initial_pose(node, client, message):
    from .waypoint_ui_bridge import normalized_pose
    try:
        state = node.edit_navigation_state
        if node.navigation_active or not state or state.get('navigation_active') or time.monotonic() - node.edit_navigation_time > 2:
            raise RuntimeError('请先停止导航，等待状态确认后再设置定位')
        if message.header.frame_id != node.frame_id:
            raise ValueError(f'定位坐标系必须是 {node.frame_id}')
        pose = copy.deepcopy(message)
        pose.pose.pose = normalized_pose(pose.pose.pose)
        await call_map(node, client, RelocalizeNearPose.Request(pose=pose))
        node.publish_status('MOLA已接受工具栏初始定位请求')
    except Exception as error:
        node.publish_status(f'初始定位未完成：{error}')


def install_map_bundle(node):
    node.create_subscription(PointStamped, '/clicked_point', lambda message: add_point(node, message), 10)
    clients = ReentrantCallbackGroup()
    services = MutuallyExclusiveCallbackGroup()
    saver = node.create_client(MapSave, '/map_save', callback_group=clients)
    loader = node.create_client(MapLoad, '/map_load', callback_group=clients)
    reloc = node.create_client(RelocalizeNearPose, '/relocalize_near_pose', callback_group=clients)
    async def initial_pose(message):
        await set_initial_pose(node, reloc, message)
    node.create_subscription(PoseWithCovarianceStamped, '/initialpose', initial_pose, 10, callback_group=clients)
    async def save(request, response):
        return await save_map(node, saver, request, response)
    async def load(request, response):
        return await load_map(node, loader, request, response)
    node.create_service(MapSave, '/omnifleet_t2/waypoints/map_save', save, callback_group=services)
    node.create_service(MapLoad, '/omnifleet_t2/waypoints/map_load', load, callback_group=services)
