import copy
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
from geometry_msgs.msg import Pose
from nav_msgs.msg import OccupancyGrid
from omnifleet_waypoint_ui.waypoint_ui_bridge import SemanticWaypoint, load_route, save_route

HERE = Path(__file__).parent


def candidate(name, filename):
    path = HERE / filename
    if not path.exists():
        path = (HERE.parent/'omnifleet_waypoint_ui/map_lifecycle.py' if filename == 'map_lifecycle.py'
                else Path('/home/iecme/omnifleet_ws/src/visualization/omnifleet_t2_ws/foxglove/nav2_permanent_panel/nav2_parameter_store.py'))
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


lifecycle_module = candidate('omnifleet_waypoint_ui.map_lifecycle', 'map_lifecycle.py')
MapLifecycle = lifecycle_module.MapLifecycle


@pytest.fixture
def node(tmp_path):
    pose = Pose(); pose.position.x = 1.; pose.orientation.w = 1.
    n = SimpleNamespace(route_file=tmp_path/'live.json', frame_id='map', pass_radius=.25,
        waypoints=[SemanticWaypoint('旧地图航点', pose)], pending_name='临时名称', navigation_active=False,
        edit_navigation_state={'navigation_active': False}, preview_goal_handle=None,
        status=[], frames=[], stopped=[])
    n.execution = SimpleNamespace(stop=n.stopped.append)
    n.publish_status = n.status.append
    n.publish_visuals = lambda:n.frames.append(copy.deepcopy(n.waypoints))
    n.publish_catalog = lambda:None
    save_route(n.route_file, n.frame_id, n.waypoints, n.pass_radius)
    return n


def status(lifecycle, process='10:20', counter=0):
    lifecycle.observe_status({'localization_epoch': 'boot|' + process + ':' + str(counter)})


def grid(stamp=0, empty=False, width=2, frame='map'):
    message = OccupancyGrid(); message.header.frame_id = frame
    message.info.map_load_time.sec = stamp
    message.info.width = width; message.info.height = 2
    message.info.resolution = .1
    message.data = [] if empty else [0]*(width*2)
    return message


def test_initial_binding_does_not_clear_current_points(node):
    old = node.route_file.read_bytes(); lifecycle = MapLifecycle(node)
    status(lifecycle); lifecycle.observe_map(grid())
    assert node.route_file.read_bytes() == old and len(node.waypoints) == 1
    assert lifecycle.binding_file.exists() and not lifecycle.blocked


def test_initial_unbound_route_from_before_current_map_process_is_cleared(node, monkeypatch):
    monkeypatch.setattr(lifecycle_module, 'process_started_at', lambda _:node.route_file.stat().st_mtime + 10)
    lifecycle = MapLifecycle(node); status(lifecycle)
    assert node.waypoints == [] and load_route(node.route_file) == []


@pytest.mark.parametrize('event', ['restart', 'stopped', 'boot'])
def test_map_process_session_change_clears_file_and_display(node, event):
    lifecycle = MapLifecycle(node); status(lifecycle)
    if event == 'restart': status(lifecycle, '11:30')
    elif event == 'stopped': lifecycle.observe_status({'localization_epoch': ''})
    else: lifecycle.observe_status({'localization_epoch': 'newboot|10:20:0'})
    assert node.waypoints == [] and load_route(node.route_file) == []
    assert node.pending_name == '' and node.frames[-1] == []


def test_existing_route_does_not_return_after_waypoint_service_restart(node):
    first = MapLifecycle(node); status(first)
    second = MapLifecycle(node)
    status(second, '12:40')
    assert load_route(node.route_file) == []
    node.waypoints = load_route(node.route_file)
    third = MapLifecycle(node); status(third, '12:40')
    assert node.waypoints == []


def test_pose_jump_counter_and_normal_grid_updates_do_not_clear(node):
    lifecycle = MapLifecycle(node); status(lifecycle); lifecycle.observe_map(grid())
    old = node.route_file.read_bytes()
    status(lifecycle, counter=3)
    larger = grid(width=12); larger.info.origin.position.x = -5.; larger.data[3] = 100
    lifecycle.observe_map(larger)
    assert len(node.waypoints) == 1 and node.route_file.read_bytes() == old


def test_empty_map_clears_once_and_blocks_new_waypoint_operations(node):
    lifecycle = MapLifecycle(node); lifecycle.observe_map(grid())
    lifecycle.observe_map(grid(empty=True)); frame_count = len(node.frames)
    lifecycle.observe_map(grid(empty=True))
    assert lifecycle.blocked and node.waypoints == [] and len(node.frames) == frame_count
    lifecycle.observe_map(grid()); assert not lifecycle.blocked


@pytest.mark.parametrize('change', ['stamp', 'frame'])
def test_loaded_map_identity_change_clears_old_points(node, change):
    lifecycle = MapLifecycle(node); lifecycle.observe_map(grid(stamp=1))
    lifecycle.observe_map(grid(stamp=2) if change == 'stamp' else grid(stamp=1, frame='other_map'))
    assert node.waypoints == [] and load_route(node.route_file) == []


def test_explicit_map_invalidation_cancels_active_navigation_and_preview(node):
    lifecycle = MapLifecycle(node); node.edit_navigation_state['navigation_active'] = True
    canceled = []
    node.preview_goal_handle = SimpleNamespace(cancel_goal_async=lambda:canceled.append(True))
    assert lifecycle.invalidate('地图重置')
    assert len(node.stopped) == 1 and canceled and load_route(node.route_file) == []
    assert list(node.route_file.parent.glob('live.json.backup-*'))


def test_failed_clear_is_blocked_and_retried_after_service_restart(node, monkeypatch):
    from omnifleet_waypoint_ui import waypoint_ui_bridge as bridge
    lifecycle = MapLifecycle(node); status(lifecycle)
    original = bridge.save_route
    monkeypatch.setattr(bridge, 'save_route', lambda *a, **k:(_ for _ in ()).throw(OSError('disk error')))
    assert not lifecycle.invalidate('地图重置')
    assert lifecycle.blocked and node.waypoints == []
    node.waypoints = load_route(node.route_file)
    restarted = MapLifecycle(node); assert restarted.blocked
    monkeypatch.setattr(bridge, 'save_route', original)
    assert restarted.retry() and load_route(node.route_file) == [] and node.waypoints == []


def test_loading_new_map_preserves_its_restored_points(node):
    lifecycle = MapLifecycle(node); lifecycle.observe_map(grid(stamp=1))
    lifecycle.loading = True
    lifecycle.observe_map(grid(empty=True)); assert len(node.waypoints) == 1
    node.waypoints[0].name = '新地图配套航点'
    save_route(node.route_file, node.frame_id, node.waypoints, node.pass_radius)
    lifecycle.finish_map_load(True)
    lifecycle.observe_map(grid(empty=True)); lifecycle.observe_map(grid(stamp=2))
    assert len(node.waypoints) == 1 and node.waypoints[0].name == '新地图配套航点'
    lifecycle.observe_map(grid(stamp=3)); assert node.waypoints == []


def test_failed_map_load_releases_guard_without_losing_original_points(node):
    lifecycle = MapLifecycle(node); old = node.route_file.read_bytes()
    lifecycle.loading = True; lifecycle.finish_map_load(False)
    assert not lifecycle.blocked and node.route_file.read_bytes() == old


def test_corrupt_binding_invalidates_instead_of_reusing_unknown_route(node):
    lifecycle = MapLifecycle(node); lifecycle.binding_file.write_text('{')
    replacement = MapLifecycle(node)
    assert replacement.blocked and replacement.retry() and node.waypoints == []


def test_empty_route_readiness_does_not_invite_starting_navigation(node):
    from omnifleet_waypoint_ui.waypoint_ui_bridge import WaypointUiBridge
    node.waypoints = []; node.nav2_ready = False; node.preview_ready = False
    node.execution.navigator = SimpleNamespace(server_is_ready=lambda:True)
    node.execution.inputs_ready = lambda:True
    node.execution.health = SimpleNamespace(reason='定位就绪')
    node.preview_client = SimpleNamespace(server_is_ready=lambda:True)
    node.dispatch_route_preview = lambda:None
    WaypointUiBridge.refresh_nav2_ready(node)
    assert node.status and all('可以点击开始' not in x for x in node.status)


def test_map_reset_waits_for_waypoint_clear_before_resetting_mola():
    folder = Path('/home/iecme/omnifleet_ws/src/visualization/omnifleet_t2_ws/foxglove/nav2_permanent_panel')
    sys.path.insert(0, str(folder))
    store = candidate('_lifecycle_store', 'store-after.py')
    events = []
    def get(): return {'lidar_odom': {'reset_state': False, 'slice_z_min': -.03}}
    store.reset_mola_map(get, lambda _:events.append('reset'), before_reset=lambda:events.append('clear'))
    assert events == ['clear', 'reset', 'reset']
    events.clear()
    def fail():raise RuntimeError('clear not acknowledged')
    with pytest.raises(RuntimeError):store.reset_mola_map(get, lambda _:events.append('reset'), before_reset=fail)
    assert events == []
    with pytest.raises(ValueError):store.reset_mola_map(lambda:{}, lambda _:None, before_reset=lambda:events.append('clear'))
    assert events == []
