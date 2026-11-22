import json
import math
from pathlib import Path

import yaml


CONFIG = Path(__file__).parents[1] / "config" / "nav2_glim.yaml"
RPP_CONFIG = Path(__file__).parents[1] / "config" / "controller_rpp.yaml"
MPPI_CONFIG = Path(__file__).parents[1] / "config" / "controller_mppi.yaml"
DIMENSIONS = (
    Path(__file__).parents[2]
    / "omnifleet_a2_description"
    / "metadata"
    / "dimensions.json"
)
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


def test_glim_navigation_uses_rpp_and_hybrid_astar():
    config = yaml.safe_load(CONFIG.read_text())
    controller = yaml.safe_load(RPP_CONFIG.read_text())["controller_server"][
        "ros__parameters"
    ]["FollowPath"]
    goal_checker = config["controller_server"]["ros__parameters"][
        "general_goal_checker"
    ]
    planner = config["planner_server"]["ros__parameters"]["GridBased"]

    assert planner["plugin"] == "nav2_smac_planner/SmacPlannerHybrid"
    assert planner["minimum_turning_radius"] == 1.35
    assert planner["analytic_expansion_ratio"] == 5.0
    assert planner["analytic_expansion_max_length"] == 4.0
    assert planner["reverse_penalty"] == 4.0
    assert planner["change_penalty"] == 0.2
    assert planner["non_straight_penalty"] == 1.2
    assert planner["cost_penalty"] == 2.5
    assert planner["smooth_path"] is True
    assert planner["smoother"] == {
        "max_iterations": 1000,
        "w_smooth": 0.3,
        "w_data": 0.2,
        "tolerance": 1.0e-10,
        "do_refinement": True,
    }
    assert controller["plugin"] == (
        "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController"
    )
    assert controller["desired_linear_vel"] == 0.4
    assert controller["lookahead_dist"] == 0.45
    assert controller["min_lookahead_dist"] == 0.25
    assert controller["max_lookahead_dist"] == 0.60
    assert controller["lookahead_time"] == 1.0
    assert controller["use_collision_detection"] is True
    assert controller["max_allowed_time_to_collision_up_to_carrot"] == 1.0
    assert controller["use_cost_regulated_linear_velocity_scaling"] is True
    assert controller["cost_scaling_dist"] == 0.30
    assert controller["cost_scaling_gain"] == 1.0
    assert controller["inflation_cost_scaling_factor"] == 2.0
    assert controller["use_rotate_to_heading"] is False
    assert controller["allow_reversing"] is True
    assert controller["regulated_linear_scaling_min_radius"] == 1.35
    assert controller["regulated_linear_scaling_min_speed"] == 0.05
    assert planner["motion_model_for_search"] == "REEDS_SHEPP"
    assert goal_checker["plugin"] == "nav2_controller::SimpleGoalChecker"
    assert goal_checker["stateful"] is False
    assert goal_checker["xy_goal_tolerance"] == 0.20
    assert goal_checker["yaw_goal_tolerance"] == 0.25


def test_mppi_mode_preserves_ackermann_reverse_path_contract_with_bounded_load():
    mppi = yaml.safe_load(MPPI_CONFIG.read_text())["controller_server"][
        "ros__parameters"
    ]
    controller = mppi["FollowPath"]

    assert mppi["controller_frequency"] == 20.0
    assert controller["plugin"] == "nav2_mppi_controller::MPPIController"
    assert controller["motion_model"] == "Ackermann"
    assert controller["AckermannConstraints"]["min_turning_r"] == 1.35
    assert controller["vx_max"] == 0.40
    assert controller["vx_min"] == -0.40
    assert controller["wz_max"] == 0.64
    assert controller["enforce_path_inversion"] is True
    assert controller["PathAngleCritic"]["mode"] == 2
    assert "VelocityDeadbandCritic" not in controller["critics"]
    assert controller["batch_size"] <= 500
    assert controller["visualize"] is False


def test_glim_navigation_constrains_path_and_routes_directly_to_chassis_driver():
    config = yaml.safe_load(CONFIG.read_text())
    controller = config["controller_server"]["ros__parameters"]
    launch_source = NAV_LAUNCH.read_text()

    for removed in ("smoother_server", "behavior_server", "waypoint_follower"):
        assert removed not in config
        assert removed not in launch_source
    assert controller["controller_frequency"] == 10.0
    assert controller["controller_server.verbose"] is False
    assert "velocity_smoother" not in config
    assert 'remappings=[("cmd_vel", "/cmd_vel")]' in launch_source
    assert 'package="nav2_velocity_smoother"' not in launch_source
    assert '"velocity_smoother",' not in launch_source
    assert "collision_monitor" not in config
    assert 'package="nav2_collision_monitor"' not in launch_source
    assert '"collision_monitor",' not in launch_source

    local = config["local_costmap"]["local_costmap"]["ros__parameters"]
    global_costmap = config["global_costmap"]["global_costmap"]["ros__parameters"]
    assert local["robot_base_frame"] == "base_link"
    assert global_costmap["robot_base_frame"] == "base_link"
    measured_footprint = "[[-0.09, -0.16], [-0.09, 0.16], [0.42, 0.16], [0.42, -0.16]]"
    assert local["footprint"] == measured_footprint
    assert global_costmap["footprint"] == measured_footprint
    assert local["footprint_padding"] == 0.0
    assert global_costmap["footprint_padding"] == 0.0
    assert local["plugins"] == ["obstacle_layer", "inflation_layer"]
    assert local["obstacle_layer"]["plugin"] == "nav2_costmap_2d::ObstacleLayer"
    assert local["obstacle_layer"]["footprint_clearing_enabled"] is True
    assert local["obstacle_layer"]["observation_sources"] == "lidar"
    assert local["global_frame"] == "odom"
    assert local["obstacle_layer"]["lidar"]["topic"] == "/rslidar_points"
    assert local["obstacle_layer"]["lidar"]["observation_persistence"] == 0.0
    assert "voxel_layer" not in local
    assert global_costmap["plugins"] == [
        "static_layer",
        "obstacle_layer",
        "inflation_layer",
    ]
    assert global_costmap["obstacle_layer"]["plugin"] == "nav2_costmap_2d::ObstacleLayer"
    assert global_costmap["obstacle_layer"]["footprint_clearing_enabled"] is True
    assert global_costmap["obstacle_layer"]["lidar"]["topic"] == "/rslidar_points"
    assert global_costmap["obstacle_layer"]["lidar"]["observation_persistence"] == 0.0
    assert local["inflation_layer"]["inflation_radius"] == 0.45
    assert local["inflation_layer"]["cost_scaling_factor"] == 2.0
    assert global_costmap["inflation_layer"]["inflation_radius"] == 0.45
    assert global_costmap["inflation_layer"]["cost_scaling_factor"] == 2.0


def test_ackermann_geometry_and_turning_radius_share_one_contract():
    config = yaml.safe_load(CONFIG.read_text())
    dimensions = json.loads(DIMENSIONS.read_text())
    controller = yaml.safe_load(RPP_CONFIG.read_text())["controller_server"][
        "ros__parameters"
    ]["FollowPath"]
    planner = config["planner_server"]["ros__parameters"]["GridBased"]

    radii = {
        planner["minimum_turning_radius"],
        controller["regulated_linear_scaling_min_radius"],
    }
    assert radii == {1.35}
    geometric_radius = dimensions["wheelbase_m"] / math.tan(
        math.radians(25.0)
    )
    configured_radius = radii.pop()
    # Keep the configured radius at or above the 25-degree geometric limit.
    assert configured_radius >= geometric_radius


def test_terrain_2_5d_configuration_is_active_and_additive():
    terrain = yaml.safe_load(TERRAIN_CONFIG.read_text())["terrain_mapper"][
        "ros__parameters"
    ]
    global_costmap = yaml.safe_load(GLOBAL_TERRAIN.read_text())[
        "global_costmap"
    ]["global_costmap"]["ros__parameters"]

    assert terrain["input_cloud_topic"] == "/glim_ros/map"
    assert terrain["static_map_topic"] == "/map"
    assert terrain["output_grid_map_topic"] == "/omnifleet_a2/terrain/grid_map"
    assert terrain["output_costmap_topic"] == "/omnifleet_a2/terrain/costmap"
    assert global_costmap["plugins"] == [
        "static_layer",
        "traversability_layer",
        "inflation_layer",
    ]
    traversability = global_costmap["traversability_layer"]
    assert traversability["plugin"] == "nav2_costmap_2d::StaticLayer"
    assert traversability["map_topic"] == "/omnifleet_a2/terrain/costmap"
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
        assert local[layer][source]["topic"] == "/rslidar_points"
