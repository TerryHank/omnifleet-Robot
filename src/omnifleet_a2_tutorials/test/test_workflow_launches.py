from pathlib import Path
import re


PACKAGE = Path(__file__).resolve().parents[1]


def test_all_user_workflow_launches_are_installed_sources():
    launch = PACKAGE / "launch"
    expected = {
        "mapping_keyboard.launch.py",
        "mapping_save_view_stop.launch.py",
        "waypoint_navigation.launch.py",
        "waypoint_save_view_stop.launch.py",
    }
    assert expected <= {path.name for path in launch.glob("*.launch.py")}


def test_mapping_keyboard_starts_fresh_online_mapping_with_navigation():
    source = (PACKAGE / "launch" / "mapping_keyboard.launch.py").read_text()
    assert "ros2 run omnifleet_a2_bringup keyboard_teleop" in source
    assert '"operation": "slam_navigation"' in source
    assert "/omnifleet_a2/system/stop_manual_stack" in source
    assert '"lidar_range_max": LaunchConfiguration("lidar_range_max")' in source


def test_mapping_keyboard_exposes_teaching_parameters():
    source = (PACKAGE / "launch" / "mapping_keyboard.launch.py").read_text()
    for argument in (
        "terrain_mode",
        "local_obstacle_mode",
        "local_inflation_radius",
        "local_cost_scaling_factor",
        "global_inflation_radius",
        "global_cost_scaling_factor",
        "global_costmap_resolution",
        "planner_mode",
        "local_controller_plugin",
    ):
        assert re.search(
            rf'DeclareLaunchArgument\(\s*"{re.escape(argument)}"', source
        )
        assert re.search(
            rf'LaunchConfiguration\(\s*"{re.escape(argument)}"\s*\)', source
        )


def test_waypoint_workflow_loads_a_saved_map_for_navigation():
    source = (PACKAGE / "launch" / "waypoint_navigation.launch.py").read_text()
    assert '"operation": "localization"' in source
    assert '"map_id": LaunchConfiguration("map_id")' in source
    declaration = re.search(
        r'DeclareLaunchArgument\(\s*"map_id"(?P<body>.*?)\)',
        source,
        flags=re.DOTALL,
    )
    assert declaration is not None
    assert "default_value" not in declaration.group("body")


def test_waypoint_workflow_exposes_teaching_parameters():
    source = (PACKAGE / "launch" / "waypoint_navigation.launch.py").read_text()
    for argument in (
        "terrain_mode",
        "local_obstacle_mode",
        "local_inflation_radius",
        "local_cost_scaling_factor",
        "global_inflation_radius",
        "global_cost_scaling_factor",
        "global_costmap_resolution",
        "planner_mode",
        "local_controller_plugin",
    ):
        assert re.search(
            rf'DeclareLaunchArgument\(\s*"{re.escape(argument)}"', source
        )
        assert re.search(
            rf'LaunchConfiguration\(\s*"{re.escape(argument)}"\s*\)', source
        )


def test_finalizer_launches_the_behavior_transaction():
    source = (PACKAGE / "launch" / "mapping_save_view_stop.launch.py").read_text()
    assert 'package="omnifleet_a2_behaviors"' in source
    assert 'executable="map_save_view_stop"' in source


def test_waypoint_finalizer_only_stops_the_localization_navigation_stack():
    source = (PACKAGE / "launch" / "waypoint_save_view_stop.launch.py").read_text()
    assert "/omnifleet_a2/system/stop_manual_stack" in source
    assert "/omnifleet_a2/slam/save_map" not in source
    assert "map_save_view_stop" not in source
