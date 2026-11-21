from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
ROBOT_LAUNCH = PACKAGE.parent / "omnifleet_bringup" / "launch" / "robot.launch.py"


def test_nav_launch_has_one_ordered_lifecycle_manager_and_no_legacy_localizer():
    source = (PACKAGE / "launch" / "navigation.launch.py").read_text(encoding="utf-8")
    assert source.count('package="nav2_lifecycle_manager"') == 1
    assert 'package="nav2_amcl"' not in source
    assert 'executable="map_server"' not in source
    assert "localization_provider" not in source
    assert 'remappings=[("cmd_vel", "/cmd_vel_nav_raw")]' in source
    assert 'executable="nav_steering_adapter"' in source
    assert "navigate_to_pose_ackermann.xml" in source


def test_ackermann_behavior_tree_never_requests_spin():
    for name in ("navigate_to_pose_ackermann.xml", "navigate_through_poses_ackermann.xml"):
        tree = (PACKAGE / "behavior_trees" / name).read_text(encoding="utf-8")
        assert "<Spin" not in tree
        assert "BackUp" in tree
    to_pose = (
        PACKAGE / "behavior_trees" / "navigate_to_pose_ackermann.xml"
    ).read_text(encoding="utf-8")
    assert '<IsPathValid path="{path}"/>' in to_pose
    assert 'smoothed_path="{path}"' in to_pose
    assert '<FollowPath path="{path}" controller_id="FollowPath"/>' in to_pose
    assert "{smoothed_path}" not in to_pose
    through_poses = (
        PACKAGE / "behavior_trees" / "navigate_through_poses_ackermann.xml"
    ).read_text(encoding="utf-8")
    assert 'RemovePassedGoals input_goals="{goals}" output_goals="{goals}" radius="0.20"' in through_poses
    assert "<SmoothPath" in through_poses
    assert 'smoother_id="SmoothPath"' in through_poses


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


def test_signed_mppi_velocity_range_cannot_be_overridden_from_launch():
    source = (PACKAGE / "launch" / "navigation.launch.py").read_text(
        encoding="utf-8"
    )
    robot_source = ROBOT_LAUNCH.read_text(encoding="utf-8")

    assert "mppi_vx_min" not in source
    assert "mppi_vx_min" not in robot_source


def test_nav2_uses_one_ground_aligned_global_frame():
    params = (PACKAGE / "config" / "nav2_glim.yaml").read_text(encoding="utf-8")
    assert params.count("global_frame: nav_map") == 4
    assert "global_frame: map" not in params
    assert "global_frame: odom" not in params
