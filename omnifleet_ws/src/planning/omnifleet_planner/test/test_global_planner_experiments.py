from pathlib import Path

import yaml


CONFIG_DIR = Path(__file__).parents[1] / "config"


def _planner(name):
    config = yaml.safe_load((CONFIG_DIR / name).read_text(encoding="utf-8"))
    return config["planner_server"]["ros__parameters"]["GridBased"]


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


def test_default_profile_keeps_ackermann_reverse_capability():
    hybrid = _planner("planner_hybrid_astar.yaml")

    assert hybrid["plugin"] == "nav2_smac_planner/SmacPlannerHybrid"
    assert hybrid["motion_model_for_search"] == "REEDS_SHEPP"


def test_base_global_costmap_keeps_teaching_defaults():
    config = yaml.safe_load(
        (CONFIG_DIR / "nav2_glim.yaml").read_text(encoding="utf-8")
    )
    global_costmap = config["global_costmap"]["global_costmap"]["ros__parameters"]

    assert global_costmap["resolution"] == 0.05
    assert global_costmap["inflation_layer"]["inflation_radius"] == 0.22
    assert global_costmap["inflation_layer"]["cost_scaling_factor"] == 8.0
