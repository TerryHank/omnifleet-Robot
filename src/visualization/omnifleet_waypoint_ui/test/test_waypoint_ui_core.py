import json
import math
from pathlib import Path
from types import SimpleNamespace

import pytest
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import Pose

from omnifleet_waypoint_ui.waypoint_ui_bridge import (
    SemanticWaypoint,
    WaypointUiBridge,
    load_route,
    map_sidecar_path,
    normalized_pose,
    resolve_waypoint,
    save_route,
    waypoint_name,
)


def test_map_sidecar_path_uses_map_prefix_without_extension():
    assert map_sidecar_path("/maps/site_01.mm") == Path(
        "/maps/site_01.waypoints.json"
    )
    assert map_sidecar_path("/maps/site_01.simplemap") == Path(
        "/maps/site_01.waypoints.json"
    )


def test_ui_owns_nav2_action_and_has_no_manager_readiness_dependency():
    source = (
        Path(__file__).parents[1]
        / "omnifleet_waypoint_ui"
        / "waypoint_ui_bridge.py"
    ).read_text(encoding="utf-8")

    assert 'ActionClient(\n            self, NavigateToPose, "navigate_to_pose"' in source
    assert 'ActionClient(\n            self, ComputePathThroughPoses, "compute_path_through_poses"' in source
    assert "NavigateThroughPoses.Goal()" not in source
    assert '"/omnifleet_t2/system/localization_ready"' not in source
    assert '"/omnifleet_t2/system/lifecycle_ready"' not in source
    assert 'PoseArray, "/omnifleet_t2/nav/waypoint_poses"' not in source


def test_route_preview_comes_from_global_planner_instead_of_waypoint_polyline():
    source = (
        Path(__file__).parents[1]
        / "omnifleet_waypoint_ui"
        / "waypoint_ui_bridge.py"
    ).read_text(encoding="utf-8")

    preview = source.split("    def dispatch_route_preview", 1)[1].split(
        "    def on_preview_goal_response", 1
    )[0]
    visuals = source.split("    def publish_visuals", 1)[1].split(
        "    def publish_empty_preview", 1
    )[0]
    assert "ComputePathThroughPoses.Goal()" in preview
    assert "goal.goals.append(pose)" in preview
    assert "goal.planner_id = planner_id" in preview
    assert "goal.use_start = False" in preview
    assert "path.poses.append" not in visuals
    assert "self.request_route_preview()" in visuals


def test_stop_button_cancels_single_and_multi_navigation_actions():
    source = (
        Path(__file__).parents[1]
        / "omnifleet_waypoint_ui"
        / "waypoint_ui_bridge.py"
    ).read_text(encoding="utf-8")

    assert "from action_msgs.srv import CancelGoal" in source
    assert '"/navigate_to_pose/_action/cancel_goal"' in source
    assert '"/navigate_through_poses/_action/cancel_goal"' in source
    stop_handler = source.split("    def on_stop", 1)[1].split(
        "    def on_cancel_all_response", 1
    )[0]
    assert "if not self.navigation_active" not in stop_handler
    assert "CancelGoal.Request()" in stop_handler


class CompletedFuture:
    def __init__(self, status):
        self.status = status

    def result(self):
        return SimpleNamespace(status=self.status, result="result")


def route_state(status):
    events = []
    state = SimpleNamespace(
        active_route_names=["航点1", "航点2"],
        active_route_index=0,
        active_goal_handle=object(),
        last_remaining=None,
        stop_requested=False,
    )
    state.publish_status = lambda text: events.append(("status", text))
    state.send_current_waypoint = lambda: events.append(("send", state.active_route_index))
    state.finish_navigation = lambda text: events.append(("finish", text))
    WaypointUiBridge.on_action_result(state, CompletedFuture(status))
    return state, events


def test_next_waypoint_is_sent_only_after_current_waypoint_succeeds():
    state, events = route_state(GoalStatus.STATUS_SUCCEEDED)
    assert state.active_route_index == 1
    assert events[-1] == ("send", 1)
    assert "航点1“航点1”成功" in events[0][1]


@pytest.mark.parametrize("status", [GoalStatus.STATUS_ABORTED, GoalStatus.STATUS_CANCELED])
def test_failed_or_canceled_waypoint_stops_sequence(status):
    state, events = route_state(status)
    assert state.active_route_index == 0
    assert not any(event[0] == "send" for event in events)
    assert events[-1][0] == "finish"


def make_pose(x=1.0, y=2.0, z=0.0, qz=0.0, qw=1.0):
    pose = Pose()
    pose.position.x = x
    pose.position.y = y
    pose.position.z = z
    pose.orientation.z = qz
    pose.orientation.w = qw
    return pose


def test_zero_quaternion_becomes_identity():
    pose = make_pose(qw=0.0)
    result = normalized_pose(pose)
    assert result.orientation.w == pytest.approx(1.0)
    assert result.orientation.z == pytest.approx(0.0)


def test_quaternion_is_normalized():
    result = normalized_pose(make_pose(qz=1.0, qw=1.0))
    assert result.orientation.z == pytest.approx(math.sqrt(0.5))
    assert result.orientation.w == pytest.approx(math.sqrt(0.5))


def test_non_finite_coordinate_is_rejected():
    with pytest.raises(ValueError, match="无效数字"):
        normalized_pose(make_pose(x=float("nan")))


def test_route_round_trip(tmp_path):
    path = tmp_path / "route.json"
    waypoints = [
        SemanticWaypoint(name="装货区", pose=make_pose(x=-0.5)),
        SemanticWaypoint(name="2号仓库", pose=make_pose(x=0.75, y=0.2)),
    ]
    save_route(path, "map", waypoints)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["frame_id"] == "map"
    assert saved["version"] == 2
    assert [item["name"] for item in saved["waypoints"]] == ["装货区", "2号仓库"]
    loaded = load_route(path)
    assert [item.name for item in loaded] == ["装货区", "2号仓库"]
    assert [item.pose.position.x for item in loaded] == pytest.approx([-0.5, 0.75])
    assert loaded[1].pose.position.y == pytest.approx(0.2)


def test_missing_route_is_empty(tmp_path):
    assert load_route(tmp_path / "missing.json") == []


def test_blank_name_uses_sequence_and_chinese_is_preserved():
    assert waypoint_name("", 3) == "航点3"
    assert waypoint_name("  原料 仓库  ", 1) == "原料 仓库"


def test_semantic_waypoint_can_be_selected_by_index_or_chinese_name():
    waypoints = [
        SemanticWaypoint(name="装货区", pose=make_pose(x=-0.5)),
        SemanticWaypoint(name="充电站", pose=make_pose(x=0.75)),
    ]
    index, waypoint = resolve_waypoint(waypoints, json.dumps({"index": 2}))
    assert index == 2
    assert waypoint.name == "充电站"
    assert waypoint.pose.position.x == pytest.approx(0.75)

    index, waypoint = resolve_waypoint(waypoints, "  装货区  ")
    assert index == 1
    assert waypoint.name == "装货区"


def test_missing_or_duplicate_semantic_waypoint_is_rejected():
    waypoints = [
        SemanticWaypoint(name="充电站", pose=make_pose(x=1.0)),
        SemanticWaypoint(name="充电站", pose=make_pose(x=2.0)),
    ]
    with pytest.raises(ValueError, match="多个同名"):
        resolve_waypoint(waypoints, "充电站")
    with pytest.raises(ValueError, match="序号不存在"):
        resolve_waypoint(waypoints, json.dumps({"index": 3}))


def test_old_pose_only_route_is_migrated(tmp_path):
    path = tmp_path / "old-route.json"
    path.write_text(
        json.dumps({"frame_id": "map", "poses": [{"position": {"x": 1.5}}]}),
        encoding="utf-8",
    )
    loaded = load_route(path)
    assert loaded[0].name == "航点1"
    assert loaded[0].pose.position.x == pytest.approx(1.5)
