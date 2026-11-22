from pathlib import Path

import pytest

from omnifleet_localization.node import SlamManagerNode


NODE_SOURCE = Path(__file__).parents[1] / "omnifleet_localization" / "node.py"


def test_runtime_ros_entities_are_retained_until_node_shutdown():
    source = NODE_SOURCE.read_text(encoding="utf-8")
    assert "self._health_subscriptions" in source
    assert "self._service_clients" in source
    assert "destroy_subscription(" not in source
    assert "destroy_client(" not in source


def test_glim_is_the_only_pose_owner():
    source = NODE_SOURCE.read_text(encoding="utf-8")
    assert 'self._finite_odom_events = {"/odom": threading.Event()}' in source
    assert '"odom", "base_link"' in source
    assert 'forbidden_pose_owners = {"ekf_filter_node", "map_odom_corrector"}' in source
    assert "state_estimation_unit" not in source
    assert "_set_state_estimation_active" not in source


def test_nav_startup_waits_for_smac_without_overlapping_resume():
    source = NODE_SOURCE.read_text(encoding="utf-8")
    assert "request.command = ManageLifecycleNodes.Request.STARTUP" in source
    assert "self._reconcile_navigation_active(60.0)" in source
    assert "LifecycleState.PRIMARY_STATE_ACTIVE" in source


def test_shutdown_always_stops_the_managed_backend_after_ros_context_shutdown():
    source = NODE_SOURCE.read_text(encoding="utf-8")
    destroy_source = source[source.index("    def destroy_node(self):") :]
    assert "if rclpy.ok(context=self.context):" in destroy_source
    assert "self.supervisor.stop(" in destroy_source
    assert "min(2.0, self._old_shutdown_timeout(self.current_mode))" in destroy_source
    assert "signal_handler_options=SignalHandlerOptions.NO" in source
    assert "except KeyboardInterrupt:" in source
    assert "signal.signal(signal.SIGINT, signal.SIG_IGN)" in source
    assert "if rclpy.ok():" in source


def test_slam_navigation_creates_a_new_online_mapping_session():
    manager = object.__new__(SlamManagerNode)

    map_id = manager._normalize_map_id("glim_cuda", "slam_navigation", "active")

    assert map_id.endswith("-active")
    assert map_id != "active"


def test_only_prior_map_localization_requires_an_existing_map_id():
    manager = object.__new__(SlamManagerNode)

    with pytest.raises(ValueError, match="map_id"):
        manager._normalize_map_id("glim_cuda", "localization", "")

    assert (
        manager._normalize_map_id(
            "glim_cuda", "localization", "20260723T010203Z-lab"
        )
        == "20260723T010203Z-lab"
    )
