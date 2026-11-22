import json
from pathlib import Path


PACKAGE_ROOT = Path(__file__).parents[1]
WORKSPACE_ROOT = PACKAGE_ROOT.parents[2]
PACKAGE_RVIZ = (PACKAGE_ROOT / "rviz" / "multi_robot.rviz").read_text(encoding="utf-8")
ROOT_RVIZ = (WORKSPACE_ROOT / "layouts" / "omnifleet_multi_robot.rviz").read_text(encoding="utf-8")
FOXGLOVE_PATH = WORKSPACE_ROOT / "layouts" / "omnifleet_multi_robot_foxglove.json"
FOXGLOVE_BYTES = FOXGLOVE_PATH.read_bytes()
FOXGLOVE = json.loads(FOXGLOVE_BYTES)
FOXGLOVE_ALIAS_BYTES = (WORKSPACE_ROOT / "OmniFleet Nav - Single & Multi.json").read_bytes()
FOXGLOVE_TEXT = json.dumps(FOXGLOVE, ensure_ascii=False)


def test_rviz_layouts_use_single_separator_and_current_topics():
    assert PACKAGE_RVIZ == ROOT_RVIZ
    assert "Fixed Frame: world" in PACKAGE_RVIZ
    assert "Class: rviz_default_plugins/TopDownOrtho" in PACKAGE_RVIZ
    assert "Topic: /fleet/goal" in PACKAGE_RVIZ
    for name in ("robot1", "robot2", "robot3"):
        assert f"TF Prefix: {name}\n" in PACKAGE_RVIZ
        assert f"TF Prefix: {name}/" not in PACKAGE_RVIZ
        assert f"{name}//" not in PACKAGE_RVIZ
        assert f"Value: /{name}/robot_description" in PACKAGE_RVIZ
        assert f"Value: /{name}/odom" in PACKAGE_RVIZ


def test_foxglove_layout_parses_and_uses_current_interfaces():
    assert FOXGLOVE_ALIAS_BYTES == FOXGLOVE_BYTES
    assert json.loads(FOXGLOVE_ALIAS_BYTES) == FOXGLOVE
    configs = FOXGLOVE["configById"]
    assert configs["3D!fleet"]["fixedFrame"] == "world"
    assert configs["RawMessages!status"]["topicPath"] == "/fleet/status"
    assert configs["RawMessages!events"]["topicPath"] == "/fleet/events"
    assert configs["Publish!goal"]["topicName"] == "/fleet/goal"
    assert configs["Publish!goal"]["datatype"] == "geometry_msgs/msg/PoseStamped"
    goal = json.loads(configs["Publish!goal"]["value"])
    assert goal["header"]["frame_id"] == "world"
    assert configs["Publish!robot1-route"]["topicName"] == "/robot1/waypoints"
    assert configs["Publish!robot1-route"]["datatype"] == "nav_msgs/msg/Path"
    route = json.loads(configs["Publish!robot1-route"]["value"])
    assert route["header"]["frame_id"] == "world"
    assert [pose["pose"]["position"]["x"] for pose in route["poses"]] == [
        -0.5,
        0.0,
        0.5,
        1.0,
        1.5,
    ]
    assert "Arbitrary waypoint route" in configs["Publish!robot1-route"]["foxglovePanelTitle"]
    assert configs["Publish!robot1-route"]["buttonText"] == "Publish all poses"
    for panel, service in (
        ("CallService!cancel-all", "/fleet/cancel_all"),
        ("CallService!clear-queue", "/fleet/clear_queue"),
    ):
        assert configs[panel]["serviceName"] == service
        assert configs[panel]["serviceType"] == "std_srvs/srv/Trigger"
        assert configs[panel]["requestPayload"] == "{}"
    for topic in ("/tf", "/tf_static", "/robot1/odom", "/robot2/odom", "/robot3/odom"):
        assert topic in FOXGLOVE_TEXT


def test_foxglove_layout_forbids_legacy_interfaces():
    for forbidden in (
        "/waypoint_status",
        "/waypoint_follow",
        "/waypoint_input",
        "/reset_waypoints",
        '"fixedFrame": "map"',
    ):
        assert forbidden not in FOXGLOVE_TEXT
