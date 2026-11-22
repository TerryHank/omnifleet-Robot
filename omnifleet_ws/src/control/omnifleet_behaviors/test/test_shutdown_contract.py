from pathlib import Path


NODE_SOURCE = Path(__file__).parents[1] / "omnifleet_behaviors" / "mission_manager.py"


def test_ros_shutdown_does_not_call_shutdown_twice():
    source = NODE_SOURCE.read_text(encoding="utf-8")
    assert "except (KeyboardInterrupt, ExternalShutdownException):" in source
    assert "signal.signal(signal.SIGINT, signal.SIG_IGN)" in source
    assert "if rclpy.ok():" in source
