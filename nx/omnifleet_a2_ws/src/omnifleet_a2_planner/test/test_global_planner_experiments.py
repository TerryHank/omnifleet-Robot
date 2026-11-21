from pathlib import Path

import yaml


CONFIG_DIR = Path(__file__).parents[1] / "config"


def _planner(name, planner_id="GridBased"):
    config = yaml.safe_load((CONFIG_DIR / name).read_text(encoding="utf-8"))
    return config["planner_server"]["ros__parameters"][planner_id]


def test_navfn_profiles_change_only_the_search_algorithm():
    astar = _planner("planner_navfn_astar.yaml")
    dijkstra = _planner("planner_navfn_dijkstra.yaml")

    assert astar["plugin"] == "nav2_navfn_planner/NavfnPlanner"
    assert dijkstra["plugin"] == astar["plugin"]
    assert astar["use_astar"] is True
    assert dijkstra["use_astar"] is False
    for parameter in (
        "allow_unknown",
        "tolerance",
        "use_final_approach_orientation",
    ):
        assert astar[parameter] == dijkstra[parameter]


def test_default_profile_tries_forward_before_reverse_fallback():
    config = yaml.safe_load(
        (CONFIG_DIR / "planner_hybrid_astar.yaml").read_text(encoding="utf-8")
    )["planner_server"]["ros__parameters"]
    forward = config["ForwardGrid"]
    reverse = config["GridBased"]

    assert config["planner_plugins"] == ["ForwardGrid", "GridBased"]
    assert forward["plugin"] == "nav2_smac_planner/SmacPlannerHybrid"
    assert forward["motion_model_for_search"] == "DUBIN"
    assert forward["minimum_turning_radius"] == 1.35
    assert forward["smooth_path"] is True
    assert reverse["plugin"] == "nav2_smac_planner/SmacPlannerHybrid"
    assert reverse["motion_model_for_search"] == "REEDS_SHEPP"


def test_base_global_costmap_keeps_teaching_defaults():
    config = yaml.safe_load(
        (CONFIG_DIR / "nav2_glim.yaml").read_text(encoding="utf-8")
    )
    global_costmap = config["global_costmap"]["global_costmap"]["ros__parameters"]

    assert global_costmap["resolution"] == 0.05
    assert global_costmap["plugins"] == [
        "static_layer",
        "obstacle_layer",
        "inflation_layer",
    ]
    assert global_costmap["obstacle_layer"]["lidar"]["topic"] == "/rslidar_points"
    assert global_costmap["inflation_layer"]["inflation_radius"] == 0.45
    assert global_costmap["inflation_layer"]["cost_scaling_factor"] == 2.0
