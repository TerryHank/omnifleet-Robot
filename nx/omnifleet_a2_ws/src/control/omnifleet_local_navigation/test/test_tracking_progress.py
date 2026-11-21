"""A slow curve can make position progress without enough yaw change."""
import importlib.util
from pathlib import Path
import unittest

source=Path(__file__).resolve().parents[1]/'omnifleet_local_navigation/tracking_guard.py'
spec=importlib.util.spec_from_file_location('guard',source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class TrackingProgress(unittest.TestCase):
    def test_path_offset_and_heading_do_not_cancel_collision_free_motion(self):
        guard=module.TrackingGuard(.5,.37,.05)
        for now in [0.,.2,.4]:
            reason,latch=guard.evaluate(now,[0.,.25,1.2],now,[-.05,.1],
                [[-2.,0.],[2.,0.]],[[10.,10.]],.02,0.,0.,True)
            self.assertEqual((reason,latch),('',False))

    def test_output_supervisor_does_not_intercept_collision_free_or_near_obstacle_motion(self):
        guard=module.TrackingGuard(.5,.37,.05)
        reason,latch=guard.evaluate(0.,[0.,.25,0.],0.,[-.05,.1],
            [[-2.,0.],[2.,0.]],[[0.,.25]],.02,0.,0.,True)
        self.assertEqual((reason,latch),('',False))

    def evaluate(self,guard,now,pose,command):
        return guard.evaluate(now,pose,now,command,[],[[10.,10.]],.02,0.,0.,True,require_path=False)[0]

    def test_slow_forward_and_reverse_curves_accept_position_progress(self):
        for direction in [-1.,1.]:
            guard=module.TrackingGuard(.5,.37,.05);command=[direction*.03,.15]
            self.assertEqual(self.evaluate(guard,0.,[0.,0.,0.],command),'')
            self.assertEqual(self.evaluate(guard,1.21,[direction*.04,0.,0.],command),'')

    def test_stalled_curve_is_not_intercepted(self):
        guard=module.TrackingGuard(.5,.37,.05);command=[.03,.15]
        self.evaluate(guard,0.,[0.,0.,0.],command)
        self.assertEqual(self.evaluate(guard,1.21,[0.,0.,0.],command),'')

    def test_pure_turn_is_not_intercepted(self):
        guard=module.TrackingGuard(.5,.37,.05);command=[0.,.15]
        self.evaluate(guard,0.,[0.,0.,0.],command)
        self.assertEqual(self.evaluate(guard,1.21,[.04,0.,0.],command),'')

    def test_forward_command_is_not_intercepted(self):
        guard=module.TrackingGuard(.5,.37,.05);command=[.15,.05]
        self.evaluate(guard,0.,[0.,0.,0.],command)
        self.assertEqual(self.evaluate(guard,1.21,[0.,0.,.1],command),'')

    def test_recorded_curve_to_spin_window_keeps_prior_commanded_translation(self):
        guard=module.TrackingGuard(.5,.37,.05)
        samples=[(0.,[-2.5759,-.00645,.24009],[-.0486435,.2430839]),
                 (.629,[-2.61951,-.00948,.3856],[0.,-.35]),
                 (1.223,[-2.60285,.00491,.22014],[0.,-.35])]
        for now,pose,command in samples:self.assertEqual(self.evaluate(guard,now,pose,command),'')
        # The next pure-turn window must not inherit the earlier translation.
        self.assertEqual(self.evaluate(guard,2.5,[-2.56285,.00491,.22014],[0.,-.35]),'')
