from pathlib import Path
import xml.etree.ElementTree as ET

import yaml


PACKAGE = Path(__file__).resolve().parents[1]
ROBOT_LAUNCH = PACKAGE.parent / "omnifleet_a2_bringup" / "launch" / "robot.launch.py"


def test_nav_launch_has_one_ordered_lifecycle_manager_and_no_legacy_localizer():
    source = (PACKAGE / "launch" / "navigation.launch.py").read_text(encoding="utf-8")
    assert source.count('package="nav2_lifecycle_manager"') == 1
    assert 'package="nav2_amcl"' not in source
    assert 'executable="map_server"' not in source
    assert "localization_provider" not in source
    assert source.count('remappings=[("cmd_vel", "/cmd_vel")]') == 1
    for removed in ("smoother_server", "behavior_server", "waypoint_follower"):
        assert removed not in source
    assert "nav2_bt_navigator" in source
    assert "navigate_w_replanning_only_if_path_becomes_invalid.xml" in source
    assert "navigate_to_pose_ackermann.xml" not in source
    assert "navigate_to_pose_ackermann_hybrid.xml" in source
    assert "navigate_through_poses_ackermann_hybrid.xml" in source


def test_multi_pose_tree_keeps_valid_path_with_official_local_clear_only():
    through_poses = (
        PACKAGE / "behavior_trees" / "navigate_through_poses_ackermann.xml"
    ).read_text(encoding="utf-8")
    ET.fromstring(through_poses)
    assert '<PipelineSequence name="NavigateWithReplanning">' in through_poses
    assert '<RateController hz="1.0">' in through_poses
    assert '<Fallback name="KeepValidPath">' in through_poses
    assert '<IsPathValid path="{path}"/>' in through_poses
    assert 'RemovePassedGoals input_goals="{goals}" output_goals="{goals}" radius="0.20"' in through_poses
    assert '<ComputePathThroughPoses goals="{goals}" path="{path}" planner_id="GridBased"/>' in through_poses
    assert '<FollowPath path="{path}" controller_id="FollowPath"/>' in through_poses
    assert '<RecoveryNode number_of_retries="1" name="FollowPathWithLocalCostmapClear">' in through_poses
    assert 'service_name="local_costmap/clear_entirely_local_costmap"' in through_poses
    assert through_poses.index("<ComputePathThroughPoses") < through_poses.index("<FollowPath")
    for removed_node in (
        "<Wait",
        "<BackUp",
        "<Spin",
        "<SmoothPath",
    ):
        assert removed_node not in through_poses


def test_hybrid_trees_try_forward_before_reverse_with_local_clear_only():
    tree_specs = (
        ("navigate_to_pose_ackermann_hybrid.xml", "ComputePathToPose"),
        ("navigate_through_poses_ackermann_hybrid.xml", "ComputePathThroughPoses"),
    )
    for name, node_name in tree_specs:
        tree = (PACKAGE / "behavior_trees" / name).read_text(encoding="utf-8")
        ET.fromstring(tree)
        assert '<Fallback name="PlanForwardThenReverse">' in tree
        assert '<Sequence name="PlanAndValidateForward">' in tree
        assert '<Sequence name="PlanAndValidateReverse">' in tree
        forward = f'<{node_name} '
        assert tree.count(forward) == 2
        assert tree.index('planner_id="ForwardGrid"') < tree.index(
            'planner_id="GridBased"'
        )
        assert tree.count('<IsPathValid path="{path}"/>') == 3
        assert tree.count('<RecoveryNode number_of_retries="1" name="FollowPathWithLocalCostmapClear">') == 1
        assert tree.count('service_name="local_costmap/clear_entirely_local_costmap"') == 1
        for removed_node in (
            "<Wait",
            "<BackUp",
            "<Spin",
        ):
            assert removed_node not in tree


def test_production_launch_exposes_independent_cold_switch_contract():
    source = (PACKAGE / "launch" / "navigation.launch.py").read_text(encoding="utf-8")
    robot_source = ROBOT_LAUNCH.read_text(encoding="utf-8")

    assert '"terrain_mode"' in source
    assert '"local_obstacle_mode"' in source
    assert 'default_value="2d"' in source
    assert 'default_value="obstacle"' in source
    assert 'executable="terrain_mapper"' in source
    assert "global_costmap_terrain.yaml" in source
    assert "terrain_mode=2_5d尚未启用" not in source
    assert "spatio_temporal_voxel_layer" in source

    assert '"terrain_mode", default_value="2d"' in robot_source
    assert '"local_obstacle_mode", default_value="obstacle"' in robot_source
    assert '"terrain_mode": LaunchConfiguration("terrain_mode")' in robot_source
    assert (
        '"local_obstacle_mode": LaunchConfiguration("local_obstacle_mode")'
        in robot_source
    )


def test_production_launch_exposes_beginner_global_planning_experiments():
    source = (PACKAGE / "launch" / "navigation.launch.py").read_text(
        encoding="utf-8"
    )
    robot_source = ROBOT_LAUNCH.read_text(encoding="utf-8")

    assert '"planner_mode", default_value="hybrid_astar"' in robot_source
    assert '"global_costmap_resolution", default_value="0.05"' in robot_source
    assert '"planner_mode": LaunchConfiguration("planner_mode")' in robot_source
    assert (
        '"global_costmap_resolution": '
        'LaunchConfiguration("global_costmap_resolution")'
    ) in robot_source
    assert '"hybrid_astar": "planner_hybrid_astar.yaml"' in source
    assert '"astar": "planner_navfn_astar.yaml"' in source
    assert '"dijkstra": "planner_navfn_dijkstra.yaml"' in source
    assert "global_costmap.global_costmap.ros__parameters.resolution" in source


def test_production_launch_exposes_rpp_mppi_cold_switch():
    source = (PACKAGE / "launch" / "navigation.launch.py").read_text(
        encoding="utf-8"
    )
    robot_source = ROBOT_LAUNCH.read_text(encoding="utf-8")

    assert '"rpp": "controller_rpp.yaml"' in source
    assert '"mppi": "controller_mppi.yaml"' in source
    assert '"controller_mode",\n                default_value="rpp"' in source
    assert '"controller_mode", default_value="rpp"' in robot_source
    assert '"controller_mode": LaunchConfiguration("controller_mode")' in robot_source
    assert 'default_value=""' in robot_source


def test_nav2_uses_standard_global_and_local_frames():
    source = (PACKAGE / "config" / "nav2_glim.yaml").read_text(encoding="utf-8")
    params = yaml.safe_load(source)

    bt_params = params["bt_navigator"]["ros__parameters"]
    assert bt_params["global_frame"] == "map"
    assert bt_params["always_reload_bt_xml"] is True
    assert "nav2_rate_controller_bt_node" in bt_params["plugin_lib_names"]
    assert "nav2_pipeline_sequence_bt_node" in bt_params["plugin_lib_names"]
    assert "nav2_is_path_valid_condition_bt_node" in bt_params["plugin_lib_names"]
    assert "nav2_globally_updated_goal_condition_bt_node" in bt_params["plugin_lib_names"]
    assert "nav2_recovery_node_bt_node" in bt_params["plugin_lib_names"]
    assert "nav2_clear_costmap_service_bt_node" in bt_params["plugin_lib_names"]
    assert (
        params["global_costmap"]["global_costmap"]["ros__parameters"][
            "global_frame"
        ]
        == "map"
    )
    assert (
        params["local_costmap"]["local_costmap"]["ros__parameters"][
            "global_frame"
        ]
        == "odom"
    )
    for removed in ("smoother_server", "behavior_server", "waypoint_follower"):
        assert removed not in params
    assert (
        params["global_costmap"]["global_costmap"]["ros__parameters"][
            "update_frequency"
        ]
        == 10.0
    )
    assert (
        params["planner_server"]["ros__parameters"]["GridBased"][
            "change_penalty"
        ]
        == 0.2
    )
    for costmap_name in ("local_costmap", "global_costmap"):
        costmap_params = params[costmap_name][costmap_name]["ros__parameters"]
        assert costmap_params["always_send_full_costmap"] is True
        obstacle_layer = costmap_params["obstacle_layer"]
        assert obstacle_layer["max_obstacle_height"] == 2.0
        assert obstacle_layer["lidar"]["max_obstacle_height"] == 2.0

    local_overlay = yaml.safe_load(
        (PACKAGE / "config" / "local_costmap_obstacle.yaml").read_text()
    )["local_costmap"]["local_costmap"]["ros__parameters"]["obstacle_layer"]
    assert local_overlay["max_obstacle_height"] == 2.0
    assert local_overlay["lidar"]["max_obstacle_height"] == 2.0
