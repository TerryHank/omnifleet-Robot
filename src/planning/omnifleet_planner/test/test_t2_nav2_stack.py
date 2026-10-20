from pathlib import Path

import yaml


PACKAGE = Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load((PACKAGE / "config" / "nav2_t2.yaml").read_text())
LAUNCH = (PACKAGE / "launch" / "navigation.launch.py").read_text()


def test_t2_geometry_and_official_plugins():
    controller = CONFIG["controller_server"]["ros__parameters"]["FollowPath"]
    planner = CONFIG["planner_server"]["ros__parameters"]["GridBased"]
    local = CONFIG["local_costmap"]["local_costmap"]["ros__parameters"]
    global_costmap = CONFIG["global_costmap"]["global_costmap"]["ros__parameters"]
    footprint = "[[0.25, 0.185], [0.25, -0.185], [-0.25, -0.185], [-0.25, 0.185]]"
    assert planner["plugin"] == "nav2_smac_planner/SmacPlanner2D"
    assert controller["plugin"] == "omnifleet_dwb_hot::HotDWBLocalPlanner"
    assert controller["max_vel_y"] == 0.0
    assert controller["vtheta_samples"] > 1
    assert local["footprint"] == footprint
    assert global_costmap["footprint"] == footprint
    assert local["global_frame"] == "map"
    assert global_costmap["global_frame"] == "map"
    assert CONFIG["behavior_server"]["ros__parameters"]["global_frame"] == "map"


def test_direct_standard_command_chain():
    assert LAUNCH.count('remappings=[("cmd_vel", "/msc/nav_cmd_vel")]') == 2
    assert 'remappings=[("/cmd_vel", "/msc/nav_cmd_vel")' in LAUNCH
    assert "/cmd_vel_nav_raw" not in LAUNCH
    assert "nav_steering_adapter" not in LAUNCH
    assert "velocity_smoother" not in LAUNCH
    assert "collision_monitor" not in LAUNCH


def test_raw_airy_points_feed_official_local_obstacle_layer():
    costmap = CONFIG["local_costmap"]["local_costmap"]["ros__parameters"]
    lidar = costmap["obstacle_layer"]["lidar"]
    assert costmap["plugins"] == ["obstacle_layer", "inflation_layer"]
    assert costmap["obstacle_layer"]["plugin"] == "nav2_costmap_2d::VoxelLayer"
    assert lidar["topic"] == "/rslidar_points"
    assert lidar["marking"] is True
    assert lidar["clearing"] is False
    assert lidar["observation_persistence"] == 0.0


def test_global_costmap_combines_mola_map_and_live_lidar_obstacles():
    costmap = CONFIG["global_costmap"]["global_costmap"]["ros__parameters"]
    assert costmap["plugins"] == ["static_layer", "peer_layer", "obstacle_layer", "inflation_layer"]
    assert costmap["peer_layer"]["plugin"] == "nav2_costmap_2d::StaticLayer"
    assert costmap["peer_layer"]["map_topic"] == "/msc/peer_map"
    assert costmap["static_layer"]["plugin"] == "nav2_costmap_2d::StaticLayer"
    assert costmap["obstacle_layer"]["plugin"] == "nav2_costmap_2d::VoxelLayer"
    assert costmap["obstacle_layer"]["lidar"]["topic"] == "/rslidar_points"
    assert costmap["obstacle_layer"]["lidar"]["marking"] is True
    assert costmap["obstacle_layer"]["lidar"]["clearing"] is False
    assert costmap["obstacle_layer"]["lidar_clearing"]["marking"] is False
    assert costmap["obstacle_layer"]["lidar_clearing"]["clearing"] is True
    assert costmap["inflation_layer"]["inflation_radius"] == 0.1
    assert costmap["inflation_layer"]["cost_scaling_factor"] == 10.0
