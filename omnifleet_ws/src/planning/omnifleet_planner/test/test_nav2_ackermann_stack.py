from pathlib import Path

import yaml


CONFIG = Path(__file__).parents[1] / "config" / "nav2_glim.yaml"
NAV_LAUNCH = Path(__file__).parents[1] / "launch" / "navigation.launch.py"
TERRAIN_CONFIG = Path(__file__).parents[1] / "config" / "terrain_2_5d.yaml"
GLOBAL_TERRAIN = (
    Path(__file__).parents[1] / "config" / "global_costmap_terrain.yaml"
)
LOCAL_OBSTACLE_CONFIGS = {
    "obstacle": Path(__file__).parents[1] / "config" / "local_costmap_obstacle.yaml",
    "voxel": Path(__file__).parents[1] / "config" / "local_costmap_voxel.yaml",
    "stvl": Path(__file__).parents[1] / "config" / "local_costmap_stvl.yaml",
}


def test_glim_navigation_uses_ackermann_mppi_and_hybrid_astar():
    config = yaml.safe_load(CONFIG.read_text())
    controller = config["controller_server"]["ros__parameters"]["FollowPath"]
    goal_checker = config["controller_server"]["ros__parameters"][
        "general_goal_checker"
    ]
    progress_checker = config["controller_server"]["ros__parameters"][
        "progress_checker"
    ]
    planner = config["planner_server"]["ros__parameters"]["GridBased"]
    bridge = config["foxglove_nav_bridge"]["ros__parameters"]

    assert planner["plugin"] == "nav2_smac_planner/SmacPlannerHybrid"
    assert planner["minimum_turning_radius"] == 0.63
    assert planner["smooth_path"] is False
    assert controller["plugin"] == "nav2_mppi_controller::MPPIController"
    assert controller["motion_model"] == "Ackermann"
    assert controller["AckermannConstraints"]["min_turning_r"] == 0.63
    assert controller["vx_min"] == -0.4
    assert controller["vx_max"] == 0.4
    assert controller["wz_max"] == 0.3
    assert "VelocityDeadbandCritic" in controller["critics"]
    assert controller["VelocityDeadbandCritic"]["deadband_velocities"] == [0.3, 0.0, 0.0]
    assert controller["enforce_path_inversion"] is True
    assert planner["motion_model_for_search"] == "REEDS_SHEPP"
    assert controller["retry_attempt_limit"] == 3
    assert goal_checker["plugin"] == "nav2_controller::SimpleGoalChecker"
    assert goal_checker["stateful"] is False
    assert goal_checker["xy_goal_tolerance"] == 0.15
    assert goal_checker["yaw_goal_tolerance"] == 0.12
    assert progress_checker["required_movement_radius"] == 0.10
    assert bridge["goal_approach_distance"] == 2.0 * planner[
        "minimum_turning_radius"
    ]


def test_glim_navigation_constrains_path_and_uses_chassis_collision_safety():
    config = yaml.safe_load(CONFIG.read_text())
    smoother = config["smoother_server"]["ros__parameters"]["SmoothPath"]
    velocity_smoother = config["velocity_smoother"]["ros__parameters"]
    steering = config["nav_steering_adapter"]["ros__parameters"]
    controller = config["controller_server"]["ros__parameters"]
    launch_source = NAV_LAUNCH.read_text()

    assert smoother["plugin"] == "nav2_constrained_smoother/ConstrainedSmoother"
    assert smoother["minimum_turning_radius"] == 0.63
    assert smoother["reversing_enabled"] is True
    assert controller["controller_frequency"] == 10.0
    assert velocity_smoother["smoothing_frequency"] == 20.0
    assert velocity_smoother["feedback"] == "OPEN_LOOP"
    assert velocity_smoother["velocity_timeout"] == 1.0
    assert velocity_smoother["max_velocity"] == [0.4, 0.0, 0.3]
    assert velocity_smoother["min_velocity"] == [-0.4, 0.0, -0.3]
    assert velocity_smoother["max_decel"] == [-2.0, 0.0, -2.0]
    assert steering["input_topic"] == "/cmd_vel_nav_smoothed"
    assert steering["output_topic"] == "/cmd_vel_nav_adjusted"
    assert steering["angular_scale"] == -1.0
    assert steering["minimum_linear_speed"] == 0.31
    assert steering["maximum_angular_speed"] == 0.30
    assert "collision_monitor" not in config
    assert 'package="nav2_collision_monitor"' not in launch_source
    assert '"collision_monitor",' not in launch_source

    local = config["local_costmap"]["local_costmap"]["ros__parameters"]
    global_costmap = config["global_costmap"]["global_costmap"]["ros__parameters"]
    assert local["robot_base_frame"] == "base_link"
    assert global_costmap["robot_base_frame"] == "base_link"
    assert local["footprint"] == "[[-0.06, -0.16], [-0.06, 0.16], [0.42, 0.16], [0.42, -0.16]]"
    assert local["plugins"] == ["obstacle_layer", "inflation_layer"]
    assert local["obstacle_layer"]["plugin"] == "nav2_costmap_2d::ObstacleLayer"
    assert local["obstacle_layer"]["observation_sources"] == "lidar"
    assert local["obstacle_layer"]["lidar"]["topic"] == "/lidar/obstacles"
    assert "voxel_layer" not in local
    assert global_costmap["plugins"] == ["static_layer", "inflation_layer"]
    assert local["inflation_layer"]["inflation_radius"] == 0.22
    assert global_costmap["inflation_layer"]["inflation_radius"] == 0.22


def test_terrain_2_5d_configuration_is_active_and_additive():
    terrain = yaml.safe_load(TERRAIN_CONFIG.read_text())["terrain_mapper"][
        "ros__parameters"
    ]
    global_costmap = yaml.safe_load(GLOBAL_TERRAIN.read_text())[
        "global_costmap"
    ]["global_costmap"]["ros__parameters"]

    assert terrain["input_cloud_topic"] == "/glim_ros/map"
    assert terrain["static_map_topic"] == "/map"
    assert terrain["output_grid_map_topic"] == "/terrain/grid_map"
    assert terrain["output_costmap_topic"] == "/terrain/costmap"
    assert global_costmap["plugins"] == [
        "static_layer",
        "traversability_layer",
        "inflation_layer",
    ]
    traversability = global_costmap["traversability_layer"]
    assert traversability["plugin"] == "nav2_costmap_2d::StaticLayer"
    assert traversability["map_topic"] == "/terrain/costmap"
    assert traversability["trinary_costmap"] is False
    assert traversability["use_maximum"] is True


def test_local_obstacle_modes_are_independent_from_terrain_mode():
    expected = {
        "obstacle": ("obstacle_layer", "nav2_costmap_2d::ObstacleLayer"),
        "voxel": ("voxel_layer", "nav2_costmap_2d::VoxelLayer"),
        "stvl": (
            "stvl_layer",
            "spatio_temporal_voxel_layer/SpatioTemporalVoxelLayer",
        ),
    }
    for mode, path in LOCAL_OBSTACLE_CONFIGS.items():
        config = yaml.safe_load(path.read_text())
        local = config["local_costmap"]["local_costmap"]["ros__parameters"]
        layer, plugin = expected[mode]
        assert local["plugins"] == [layer, "inflation_layer"]
        assert local[layer]["plugin"] == plugin
        source = "lidar_mark" if mode == "stvl" else "lidar"
        assert local[layer][source]["topic"] == "/lidar/obstacles"
