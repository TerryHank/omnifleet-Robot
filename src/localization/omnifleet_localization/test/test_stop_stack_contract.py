from pathlib import Path


NODE_SOURCE = Path(__file__).parents[1] / "omnifleet_localization" / "node.py"


def test_manual_stop_service_uses_the_high_priority_shutdown_path():
    source = NODE_SOURCE.read_text(encoding="utf-8")

    assert '"/rrc_system/stop_manual_stack"' in source
    assert 'request.mode = "__stop__"' in source
    assert "self._switch_callback(request, SwitchMode.Response())" in source
    switch = source[source.index("    def _switch_callback(") :]
    stop_branch = switch.index(
        "if stop_only and self.shutdown_manual_stack_on_stop:"
    )
    transaction_lock = switch.index(
        "if not self._transaction_lock.acquire(blocking=False):"
    )
    assert stop_branch < transaction_lock


def test_manual_stack_stop_does_not_wait_for_stale_dds_node_names():
    source = NODE_SOURCE.read_text(encoding="utf-8")
    worker = source[source.index("    def _manual_stack_shutdown_worker(") :]

    cancel_navigation = worker.index("self._cancel_navigation()")
    exit_manager = worker.index("rclpy.shutdown(context=self.context)")

    assert cancel_navigation < exit_manager
    assert "_verify_old_owners_absent" not in worker[:exit_manager]


def test_manager_exit_still_stops_the_managed_backend_process_group():
    source = NODE_SOURCE.read_text(encoding="utf-8")
    destroy = source[source.index("    def destroy_node(self):") :]

    assert "self._set_zero_hold(True)" in destroy
    assert "self.supervisor.stop(" in destroy
