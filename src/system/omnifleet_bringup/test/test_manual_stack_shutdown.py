from pathlib import Path


LAUNCH_SOURCE = Path(__file__).parents[1] / "launch" / "robot.launch.py"


def test_glim_manager_exit_closes_the_complete_manual_launch():
    source = LAUNCH_SOURCE.read_text(encoding="utf-8")

    assert "OnProcessExit(" in source
    assert "target_action=slam_manager" in source
    assert "event=Shutdown(" in source
    assert "关闭全部手动启动节点" in source


def test_launch_adds_one_ground_aligned_navigation_parent_frame():
    source = LAUNCH_SOURCE.read_text(encoding="utf-8")

    assert 'name="navigation_ground_frame"' in source
    assert '"--frame-id", "nav_map"' in source
    assert '"--child-frame-id", "map"' in source
    assert '"navigation_ground_offset_z", default_value="0.374553341297"' in source


def test_mapping_does_not_create_nav2_but_localization_does():
    source = LAUNCH_SOURCE.read_text(encoding="utf-8")

    assert '"operation", default_value="mapping"' in source
    assert '"omnifleet_planner", "navigation.launch.py"' in source
    assert 'LaunchConfiguration("operation"), "\' != \'mapping\'"' in source
