import ast
import json
import math
from pathlib import Path
from types import SimpleNamespace as NS
import unittest

from omnifleet_local_navigation import clearance_recovery as recovery

SOURCE = Path(__file__).resolve().parents[1] / 'omnifleet_local_navigation'
VALUES = {'footprint': '[[0.25,0.185],[0.25,-0.185],[-0.25,-0.185],[-0.25,0.185]]',
          'footprint_padding': .02}
CONFIG = {'length': .5, 'width': .37, 'padding': .05}


def method(file, name, scope):
    tree = ast.parse((SOURCE / file).read_text())
    fn = next(n for c in tree.body if isinstance(c, ast.ClassDef)
              for n in c.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[fn], type_ignores=[]), name, 'exec'), scope)
    return scope[name]


def grid(cost=100):
    m = NS(info=NS(width=41, height=41, resolution=.1,
           origin=NS(position=NS(x=-2.05,y=-2.05), orientation=NS(x=0.,y=0.,z=0.,w=1.))),
           data=[0]*(41*41))
    m.data[20*41+20]=cost
    return m


def scope(now=0.):
    return {'time':NS(monotonic=lambda:now), 'signed_clearance':recovery.signed_clearance,
            'recovery_config':recovery.recovery_config, 'recovery_heading':recovery.recovery_heading,
            'grid_start_blocked':recovery.grid_start_blocked,
            'local_body_collision':getattr(recovery,'local_body_collision',None)}


class GlobalStartRecoveryTests(unittest.TestCase):
    def node(self, cost=100, phase='tracking'):
        import test_clearance_timeout_replan as timeout_tests
        n, now, stopped, created, sent, completed, update, jobs = timeout_tests.TimeoutReplanTests().runtime()
        n.clearance_escape=None; n.grid=grid(cost); n.local_pose=[0.,0.,0.]
        n.obstacles=[[.8,0.]]; n.obstacle_complete=True; n.obstacle_resolution=.01
        n.runtime_parameters={'local_costmap/local_costmap':{'values':dict(VALUES)}}
        n.execution.phase=phase; n.execution.preflight_only=False
        n.execution.stop=lambda text,failed=False:n.execution.finish('failed' if failed else 'canceled',text)
        n.recover_from_nav2_failure=lambda:method('runtime.py','recover_from_nav2_failure',scope(now[0]))(n)
        jobs.__globals__['local_body_collision']=getattr(recovery,'local_body_collision',None)
        return n, stopped, created, sent, completed, jobs

    def test_global_99_and_100_replan_without_physical_escape(self):
        for cost in [99,100]:
            for phase in ['tracking','preplanning','replanning']:
                n, stopped, created, sent, completed, jobs=self.node(cost,phase)
                job,points,goal=n.current_job,n.execution.points,n.goal
                self.assertTrue(n.recover_from_nav2_failure())
                self.assertFalse(getattr(job,'clearance_global_start',False))
                self.assertIsNotNone(n.recovery_pending)
                stopped[0]=True; jobs(n)
                self.assertEqual(created,[])
                self.assertIsNone(n.clearance_escape)
                self.assertEqual(sent,[points[1:]])
                self.assertEqual(completed,[])
                self.assertIs(n.current_job,job); self.assertIs(n.execution.points,points); self.assertIs(n.goal,goal)
                self.assertTrue(recovery.grid_start_blocked(n.grid,n.local_pose))

    def test_repeated_global_only_failures_keep_original_remaining_route_and_target(self):
        n, stopped, created, sent, completed, jobs=self.node(); stopped[0]=True
        job,points,goal=n.current_job,n.execution.points,n.goal
        for _ in range(4):
            n.execution.phase='tracking'
            self.assertTrue(n.recover_from_nav2_failure()); jobs(n)
            self.assertIs(n.current_job,job); self.assertIs(n.execution.points,points); self.assertIs(n.goal,goal)
            self.assertTrue(n.execution.active)
        self.assertEqual(sent,[points[1:]]*4); self.assertEqual(created,[]); self.assertEqual(completed,[])

    def test_local_corner_overlap_enters_escape_with_global_free_or_blocked(self):
        for cost in [0,100]:
            n, stopped, created, sent, completed, jobs=self.node(cost)
            n.current_job.clearance_attempts=0; n.obstacles=[[.265,.199]]
            self.assertTrue(n.recover_from_nav2_failure()); stopped[0]=True; jobs(n)
            self.assertEqual(len(created),1); self.assertIsNotNone(n.clearance_escape)
            self.assertEqual(sent,[]); self.assertEqual(completed,[])

    def test_local_clear_after_cancel_resumes_without_an_escape(self):
        n, stopped, created, sent, completed, jobs=self.node()
        n.obstacles=[[.265,.199]]
        self.assertTrue(n.recover_from_nav2_failure())
        n.obstacles=[[.8,0.]]; stopped[0]=True; jobs(n)
        self.assertEqual(created,[]); self.assertEqual(len(sent),1); self.assertEqual(completed,[])

    def test_new_local_overlap_before_dispatch_uses_current_local_map(self):
        n, stopped, created, sent, _completed, jobs=self.node()
        self.assertTrue(n.recover_from_nav2_failure())
        n.obstacles=[[.265,.199]]; stopped[0]=True; jobs(n)
        self.assertEqual(len(created),1); self.assertEqual(sent,[])

    def test_global_grid_is_not_an_escape_exit_requirement(self):
        n, stopped, _created, _sent, _completed, jobs=self.node()
        n.obstacles=[[.265,.199]]; observed=[]
        self.assertTrue(n.recover_from_nav2_failure())
        factory=jobs.__globals__['ClearanceEscape']
        def create(*args,**kwargs):
            observed.append(kwargs.get('start_blocked')); return factory(*args,**kwargs)
        jobs.__globals__['ClearanceEscape']=create
        n.current_job.clearance_global_start=True
        stopped[0]=True; jobs(n)
        self.assertEqual(observed,[None])

    def test_continuous_replanning_failure_uses_same_local_body_classification(self):
        n, stopped, created, sent, completed, jobs=self.node(100,'replanning')
        n.execution.strategy='continuous'; n.execution.run_id='original'
        failed=method('route_execution.py','request_failed',{})
        n.execution.request_failed=lambda role,reason:failed(n.execution,role,reason)
        observe=method('route_execution.py','on_execution_state',{'json':json})
        observe(n.execution,NS(data=json.dumps({'run_id':'original-0','state':'failed',
                                              'reason':'Starting point in lethal space'})))
        self.assertIsNotNone(n.recovery_pending)
        stopped[0]=True; jobs(n)
        self.assertEqual(created,[]); self.assertEqual(len(sent),1); self.assertEqual(completed,[])

    def test_preview_failure_is_nonmoving_and_unrelated_free_start_failure_is_unchanged(self):
        failed=method('route_execution.py','request_failed',{})
        n, _stopped, _created, _sent, _completed, _jobs=self.node(100,'preplanning')
        n.execution.preflight_only=True
        failed(n.execution,'plan','Starting point in lethal space')
        self.assertIsNone(n.recovery_pending); self.assertEqual(n.execution.phase,'failed')
        for cost in [0,98,-1]:
            n,*_=self.node(cost)
            self.assertFalse(n.recover_from_nav2_failure()); self.assertIsNone(n.recovery_pending)

    def test_local_body_check_includes_interior_and_corner_with_zero_center(self):
        check=getattr(recovery,'local_body_collision',None); self.assertTrue(callable(check))
        for point in [[.1,.1],[.265,.199]]:
            self.assertTrue(check([0.,0.,0.],[point],CONFIG,.01,VALUES))
        self.assertFalse(check([0.,0.,0.],[[.28,0.]],CONFIG,.01,VALUES))
        self.assertFalse(check([0.,0.,0.],[],CONFIG,.01,VALUES))

    def test_exact_cell_intersection_rejects_a_corner_gap_inside_circumscribed_circle(self):
        check=getattr(recovery,'local_body_collision',None); self.assertTrue(callable(check))
        self.assertFalse(check([0.,0.,0.],[[.26,.23]],CONFIG,.01,VALUES))
        self.assertTrue(check([0.,0.,0.],[[.274,.209]],CONFIG,.01,VALUES))

    def test_body_and_grid_rotation_preserve_cell_overlap(self):
        check=getattr(recovery,'local_body_collision',None); self.assertTrue(callable(check))
        for a in [0.,.7,math.pi/2,-2.]:
            c,s=math.cos(a),math.sin(a)
            for point,expected in [([.265,.199],True),([.28,0.],False)]:
                world=[1+c*point[0]-s*point[1],2+s*point[0]+c*point[1]]
                self.assertEqual(check([1.,2.,a],[world],CONFIG,.01,VALUES,a),expected)

    def test_rotated_cell_corner_requires_the_cell_axes_too(self):
        check=getattr(recovery,'local_body_collision',None); self.assertTrue(callable(check))
        self.assertTrue(check([0.,0.,0.],[[.273,.208]],CONFIG,.01,VALUES,math.pi/4))
        self.assertFalse(check([0.,0.,0.],[[.274,.209]],CONFIG,.01,VALUES,math.pi/4))

    def test_actual_local_grid_callback_uses_lethal_cells_and_not_the_global_grid(self):
        from omnifleet_local_navigation.geometry import compose
        observe=method('control.py','on_obstacle_grid',{'math':math,'compose':compose,
            'yaw':lambda _q:0.,'frame':lambda value:value,'time':NS(monotonic=lambda:1.)})
        for cost in [99,100]:
            n,stopped,created,sent,_completed,jobs=self.node()
            n.current_job.clearance_attempts=0
            local=NS(header=NS(frame_id='map'),data=[0]*10000,
                info=NS(width=100,height=100,resolution=.01,origin=NS(
                    position=NS(x=-.5,y=-.5),orientation=NS(x=0.,y=0.,z=0.,w=1.))))
            local.data[69*100+76]=cost
            observe(n,local)
            self.assertEqual(local.data[50*100+50],0)
            self.assertTrue(n.recover_from_nav2_failure())
            stopped[0]=True; jobs(n)
            self.assertEqual(len(created),int(cost==100))
            self.assertEqual(len(sent),int(cost==99))

    def test_selected_radius_model_still_uses_its_configured_shape(self):
        check=getattr(recovery,'local_body_collision',None); self.assertTrue(callable(check))
        values={'footprint':'[]','robot_radius':.1,'footprint_padding':0.}
        self.assertTrue(check([0.,0.,0.],[[.104,0.]],CONFIG,.01,values))
        self.assertFalse(check([0.,0.,0.],[[.17,0.]],CONFIG,.01,values))


if __name__=='__main__':unittest.main()
