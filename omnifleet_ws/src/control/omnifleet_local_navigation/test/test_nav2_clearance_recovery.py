import ast
from pathlib import Path
from types import SimpleNamespace as NS
import unittest

from omnifleet_local_navigation.clearance_recovery import signed_clearance, recovery_config

SOURCE = Path(__file__).resolve().parents[1] / 'omnifleet_local_navigation'

def method(file, name):
    tree = ast.parse((SOURCE / file).read_text())
    fn = next(m for c in tree.body if isinstance(c, ast.ClassDef) for m in c.body
              if isinstance(m, ast.FunctionDef) and m.name == name)
    scope = {'time': NS(monotonic=lambda: 10.), 'signed_clearance': signed_clearance, 'recovery_config': recovery_config}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), name, 'exec'), scope)
    return scope[name]

class Nav2ClearanceRecoveryTests(unittest.TestCase):
    def node(self):
        events = []
        n = NS(current_job=NS(source='LOCAL'), mode='LOCAL', estop=False,
               execution=NS(active=True, phase='tracking', stop=lambda text: events.append('cancel_nav2')),
               policy=NS(canceling=False, cancel=lambda: events.append('cancel_owner')),
               clearance_escape=None, recovery_pending=None, local_pose=[0., 0., 0.],
               obstacles=[[0., .19]], obstacle_complete=True, obstacle_resolution=.02,
               config={'length': .5, 'width': .37}, runtime_parameters={},
               inhibited=False, armed=True)
        def prepare():
            events.append('prepare'); n.recovery_pending={'ticket': 'same-task'}
        n.prepare_clearance_recovery=prepare
        return n,events

    def test_nav2_failure_inside_lethal_cell_prepares_escape_and_keeps_job(self):
        n,events=self.node();job=n.current_job
        self.assertTrue(method('runtime.py','recover_from_nav2_failure')(n))
        self.assertEqual(events,['prepare','cancel_owner','cancel_nav2'])
        self.assertIs(n.current_job,job)
        self.assertTrue(n.inhibited);self.assertFalse(n.armed)
        self.assertEqual(n.cancel_deadline,15.)

    def test_point_model_does_not_use_full_body_as_an_extra_collision(self):
        n,events=self.node()
        n.runtime_parameters={'local_costmap/local_costmap':{'values':{'footprint':'[]','robot_radius':.1,'footprint_padding':0.}}}
        n.obstacles=[[0.,.17]]
        self.assertFalse(method('runtime.py','recover_from_nav2_failure')(n))
        self.assertEqual(events,[])

    def test_obstacle_ahead_outside_body_uses_normal_nav2_recovery(self):
        n,events=self.node();n.obstacles=[[.8,0.]]
        self.assertFalse(method('runtime.py','recover_from_nav2_failure')(n))
        self.assertEqual(events,[])

    def test_no_new_recovery_after_cancel_manual_fleet_or_estop(self):
        for field,value in [('mode','MANUAL'),('mode','FLEET'),('estop',True),
                            ('local_pose',None),('obstacle_complete',False)]:
            with self.subTest(field=field,value=value):
                n,events=self.node();setattr(n,field,value)
                self.assertFalse(method('runtime.py','recover_from_nav2_failure')(n))
                self.assertEqual(events,[])
        n,events=self.node();n.policy.canceling=True
        self.assertFalse(method('runtime.py','recover_from_nav2_failure')(n));self.assertEqual(events,[])

    def test_existing_recovery_switch_disabled_is_respected(self):
        n,events=self.node()
        n.runtime_parameters={'omnifleet_navigation_policy':{'values':{'automatic_recovery':False}}}
        self.assertFalse(method('runtime.py','recover_from_nav2_failure')(n));self.assertEqual(events,[])

    def test_exhausted_existing_attempt_budget_uses_normal_failure(self):
        n,events=self.node();n.prepare_clearance_recovery=lambda:None
        self.assertFalse(method('runtime.py','recover_from_nav2_failure')(n));self.assertEqual(events,[])

    def test_follow_path_abort_transition_triggers_once_not_retained_or_canceled(self):
        status=method('control.py','on_nav_status')
        gid=NS(goal_id=NS(uuid=[1]*16));key=bytes(gid.goal_id.uuid).hex()
        events=[];n=NS(active_goal_ids={'follow_path':{key}},nav_status={},mode='LOCAL',
                       recover_from_nav2_failure=lambda:events.append('escape'))
        msg=NS(status_list=[NS(goal_info=gid,status=6)])
        status(n,'follow_path',msg);status(n,'follow_path',msg)
        self.assertEqual(events,['escape'])
        for action,result in [('spin',6),('follow_path',5),('follow_path',4)]:
            n.active_goal_ids[action]={key}
            status(n,action,NS(status_list=[NS(goal_info=gid,status=result)]))
        self.assertEqual(events,['escape'])

    def test_outer_navigation_failure_uses_escape_but_preview_failure_does_not(self):
        failed=method('route_execution.py','request_failed')
        for role,eligible in [('navigation',True),('navigation',False),('plan',True)]:
            events=[]
            def recover():events.append('escape');return eligible
            n=NS(n=NS(recover_from_nav2_failure=recover),stop=lambda *a,**k:events.append('stop'))
            failed(n,role,'failure')
            self.assertEqual(events,['escape'] if role=='navigation' and eligible else
                             ['escape','stop'] if role=='navigation' else ['stop'])

if __name__ == '__main__': unittest.main()
