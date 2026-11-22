import ast
import importlib.util
import math
from pathlib import Path
from types import SimpleNamespace as NS
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'omnifleet_local_navigation'
spec = importlib.util.spec_from_file_location('tracking_guard_under_test', SOURCE / 'tracking_guard.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class Twist:
    def __init__(self):
        self.linear = NS(x=0.)
        self.angular = NS(z=0.)


class TrackingStopMode(unittest.TestCase):
    def setUp(self):
        methods = ast.parse((SOURCE / 'control.py').read_text())
        selected = [m for c in methods.body if isinstance(c, ast.ClassDef)
                    for m in c.body if isinstance(m, ast.FunctionDef)
                    and m.name in ('control_tick', 'on_estop', 'on_contact')]
        self.saved, self.sent, self.cancelled, self.revoked = [], [], [], []
        self.methods = {'time': NS(monotonic=lambda: 10.), 'math': math, 'Twist': Twist,
                        'save': lambda p, value: self.saved.append(value)}
        exec(compile(ast.Module(body=selected, type_ignores=[]), 'control_methods', 'exec'), self.methods)
        self.node = NS(control_gate_ready=True, mode='LOCAL', manual_time=10., manual=[.15, 0.],
                       nav_time=10., nav=[.15, 0.], output_permitted=lambda: True,
                       tracking_guard=guard.TrackingGuard(.5, .37, .05), local_pose=[0., 0., 0.],
                       pose_stamp_ns=10000000000, planned_path=[[0., 0.], [1., 0.]],
                       obstacles=[[.2, 0.]], obstacle_resolution=.05, pose_age=0.,
                       obstacle_stamp=10., obstacle_complete=True, estop=False,
                       safety_latched=False, tracking_stop_reason='',
                       fleet_enabled=True, state_path='unused',
                       active_goal_ids={}, fleet_localization_epoch='test', epoch='test', current_job=NS(ticket='test'),
                       fleet_lease=NS(revoke=lambda: self.revoked.append(True), fresh=lambda now: True,
                                      matches=lambda ticket, now: True),
                       cancel_all=lambda: self.cancelled.append(True),
                       output=NS(publish=lambda m: self.sent.append([m.linear.x, m.angular.z])))

    def test_local_navigation_skips_predicted_collision_gate(self):
        self.methods['control_tick'](self.node)
        self.assertEqual(self.sent, [[.15, 0.]])
        self.assertEqual(self.cancelled, [])
        self.assertEqual(self.revoked, [])
        self.assertFalse(self.node.estop or self.node.safety_latched)

    def test_local_navigation_does_not_stop_for_stale_inputs(self):
        self.node.pose_age = .6
        self.methods['control_tick'](self.node)
        self.assertEqual(self.sent, [[.15, 0.]])
        self.assertEqual(self.node.safety_reason, '')
        self.assertEqual(self.cancelled, [])

    def test_manual_directions_skip_predicted_body_clearance(self):
        for command in [[.15, 0.], [-.15, 0.], [0., 1.], [0., -1.]]:
            with self.subTest(command=command):
                self.setUp()
                self.node.mode = 'MANUAL'
                self.node.manual = command
                self.node.obstacles = [[.2704, -.0702], [.2304, -.2102]]
                self.methods['control_tick'](self.node)
                self.assertEqual(self.sent, [command])
                self.assertEqual(self.node.safety_reason, '')
                self.assertEqual(self.cancelled, [])
                self.assertEqual(self.revoked, [])
                self.assertFalse(self.node.estop or self.node.safety_latched)

    def test_fleet_output_is_not_intercepted_by_secondary_guard(self):
        self.node.mode = 'FLEET'
        self.methods['control_tick'](self.node)
        self.assertEqual(self.sent, [[.15, 0.]])
        self.assertEqual(self.node.tracking_stop_reason, '')
        self.assertFalse(self.node.estop or self.node.safety_latched)
        self.assertTrue(self.node.fleet_enabled)
        self.assertEqual(self.cancelled, [])
        self.assertEqual(self.revoked, [])
        self.assertEqual(self.saved, [])

    def test_physical_estop_still_latches_and_cancels(self):
        self.methods['on_estop'](self.node, NS(data=True))
        self.assertTrue(self.node.estop and self.node.safety_latched)
        self.assertEqual(self.node.manual, [0., 0.])
        self.assertEqual(self.saved, [{'safety_latched': True}])
        self.assertEqual(self.cancelled, [True])

    def test_contact_still_latches_and_cancels(self):
        self.methods['on_contact'](self.node, NS(data=True))
        self.assertTrue(self.node.estop and self.node.safety_latched)
        self.assertEqual(self.saved, [{'safety_latched': True}])
        self.assertEqual(self.cancelled, [True])


if __name__ == '__main__':
    unittest.main()
