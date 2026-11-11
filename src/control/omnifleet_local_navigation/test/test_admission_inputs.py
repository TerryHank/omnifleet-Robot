"""TF diagnostics must not indirectly erase the cached planning pose."""
import ast
import unittest
from pathlib import Path
from types import SimpleNamespace

package = Path(__file__).resolve().parents[1]/'omnifleet_local_navigation'

def load_method(file, name, clock, extra=None):
    tree = ast.parse((package/file).read_text())
    method = next(item for cls in tree.body if isinstance(cls, ast.ClassDef)
                  for item in cls.body if isinstance(item, ast.FunctionDef) and item.name == name)
    values = {'time': SimpleNamespace(monotonic=lambda: clock[0], time=lambda: clock[0])}
    values.update(extra or {})
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(package/file), 'exec'), values)
    return values[name]

class AdmissionInputs(unittest.TestCase):
    def setUp(self):
        self.clock = [.6]
        self.inputs_ready = load_method('route_execution.py', 'inputs_ready', self.clock)
        header = SimpleNamespace(stamp=SimpleNamespace(sec=0, nanosec=0))
        self.route = SimpleNamespace(pose=(0., SimpleNamespace(header=header)), grid=(.5, object()),
            on_tf=lambda _: None, active=False, tf_stale_drop_count=0, tf_last_dropped_stamp=None,
            tf_check_count=0, tf_last_check_mono=None, tf_max_check_interval_ms=0., tf_max_age_ms=None,
            tf_over500_count=0, health=SimpleNamespace(trace=None, age_ms=600., check=lambda *_: False,
                reason='TF接收中断超过500 ms'))
        self.route.inputs_ready = lambda: self.inputs_ready(self.route)
        self.route.input_reason = lambda: load_method('route_execution.py', 'input_reason', self.clock)(self.route)

    def test_diagnostic_timeout_does_not_erase_last_planning_pose(self):
        self.assertTrue(self.inputs_ready(self.route))
        load_method('route_execution.py', 'tick', self.clock)(self.route)
        self.assertIsNotNone(self.route.pose)
        self.assertTrue(self.inputs_ready(self.route))

    def test_first_pose_and_map_are_still_required(self):
        self.route.pose = None
        self.assertFalse(self.inputs_ready(self.route))
        self.route.pose = (.5, object());self.route.grid = None
        self.assertFalse(self.inputs_ready(self.route))

    def test_stale_costmap_still_blocks_admission(self):
        self.clock[0] = 3.5
        self.assertFalse(self.inputs_ready(self.route))

    def test_missing_costmap_is_not_reported_as_tf_timeout(self):
        self.route.grid = None
        self.route.phase='idle';self.route.single=self.route.navigator=SimpleNamespace(server_is_ready=lambda: True)
        node = SimpleNamespace(estop=False, clearance_escape=None, policy=SimpleNamespace(canceling=False),
            execution=self.route, control_gate_ready=True, startup_done=True,
            state_clients=['controller'], states={'controller': (3,.6)})
        reason = load_method('runtime.py', 'readiness_reason', self.clock)(node)
        self.assertIn('全局代价地图', reason)
        self.assertNotIn('TF接收中断', reason)

    def test_rejected_goal_publishes_the_actual_reason(self):
        messages=[]
        class Action:
            Result=SimpleNamespace
        job=SimpleNamespace(done=SimpleNamespace(done=lambda:False,set_result=lambda _:None),
            handle=SimpleNamespace(is_active=False), action_type=Action, ticket='ticket')
        node=SimpleNamespace(current_job=None, completed={}, publish_status=messages.append)
        method=load_method('runtime.py','finish_job',self.clock,
            {'ExecuteNavigation':object(),'ExecuteFormation':object()})
        method(node,job,False,'NOT_READY','尚未收到全局代价地图')
        self.assertTrue(messages)
        self.assertIn('尚未收到全局代价地图',messages[-1])
