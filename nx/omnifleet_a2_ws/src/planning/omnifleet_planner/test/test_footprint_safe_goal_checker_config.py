from pathlib import Path

import yaml


PACKAGE = Path(__file__).resolve().parents[1]
CONFIG = yaml.safe_load((PACKAGE / "config" / "nav2_t2.yaml").read_text())


def test_goal_checker_requires_stable_safe_footprint():
    checker = CONFIG["controller_server"]["ros__parameters"]["general_goal_checker"]
    assert checker["plugin"] == "omnifleet_planner::FootprintSafeGoalChecker"
    assert checker["stateful"] is False
    assert checker["safe_hold_time"] >= 0.3
