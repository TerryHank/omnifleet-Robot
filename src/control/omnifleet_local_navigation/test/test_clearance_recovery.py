import ast
import importlib.util
import json
import math
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
import numpy as np
from omnifleet_local_navigation.bounded_turn import BoundedTurn,body_velocity

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'omnifleet_local_navigation'
spec = importlib.util.spec_from_file_location('escape', SOURCE / 'clearance_recovery.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
FIXTURE = json.loads((ROOT / 'test/data/near-obstacle-fixture.json').read_text())
CONFIG = dict(length=.5, width=.37, padding=.05)


class BoundedTurnTests(unittest.TestCase):
    def fixture(self):return json.loads((ROOT/'test/data/fine-grid-turn-fixture.json').read_text())

    def test_requested_longitudinal_correction_keeps_its_direction(self):
        f=self.fixture();p=f['pose'];far=[[p[0]+1.,p[1]+1.]]
        for v in [-.015,.015]:
            r=BoundedTurn(p,CONFIG,f['resolution'],0.,'e')
            cmd=r.command(0.,p,[v,.03],far,[],[0.,0.],True,'e')
            self.assertEqual(cmd,[math.copysign(.01,v),.03])

    def test_recorded_turn_with_measured_drift_stays_outside_body_envelope(self):
        f=self.fixture();p=list(f['pose']);r=BoundedTurn(p,CONFIG,f['resolution'],0.,'e')
        now=v=w=0.;target=3.0912796384470336;minimum=1.
        while now<90.:
            error=math.atan2(math.sin(target-p[2]),math.cos(target-p[2]))
            if abs(error)<.06:break
            cmd=r.command(now,p,[0.,math.copysign(.35,error)],f['obstacles'],f['unknown'],[math.hypot(v,.05*w),w],True,'e')
            self.assertIsNotNone(cmd,r.diagnostic)
            self.assertLessEqual(abs(cmd[0]),.01);self.assertLessEqual(abs(cmd[1]),.08)
            v,w=1.3*cmd[0],cmd[1];lateral=-.06*v+.05*w
            p[0]+=.1*(v*math.cos(p[2])-lateral*math.sin(p[2]))
            p[1]+=.1*(v*math.sin(p[2])+lateral*math.cos(p[2]));p[2]+=.1*w;now+=.1
            minimum=min(minimum,float(module.signed_clearance(p,f['obstacles'],.5,.37).min()))
        self.assertLess(abs(error),.06);self.assertGreaterEqual(minimum,f['resolution']*.71+.005)

    def test_unknown_and_stale_input_hold_zero_then_decline_override(self):
        f=self.fixture();p=f['pose']
        for unknown,fresh in [(f['unknown']+[p[:2]],True),(f['unknown'],False)]:
            r=BoundedTurn(p,CONFIG,f['resolution'],0.,'e')
            self.assertEqual(r.command(0.,p,[0.,.35],f['obstacles'],unknown,[0.,0.],fresh,'e'),[0.,0.])
            self.assertIsNone(r.command(1.1,p,[0.,.35],f['obstacles'],unknown,[0.,0.],fresh,'e'))

    def test_epoch_and_motion_budgets_decline_override(self):
        f=self.fixture();p=f['pose']
        for now,pose,epoch in [(91.,p,'e'),(0.,p,'new'),(0.,[p[0]+.16,p[1],p[2]],'e'),(0.,p,'e')]:
            r=BoundedTurn(p,CONFIG,f['resolution'],0.,'e')
            if now==0. and pose is p and epoch=='e':r.angle=7.1
            self.assertIsNone(r.command(now,pose,[0.,.35],f['obstacles'],f['unknown'],[0.,0.],True,epoch))


class EscapeTests(unittest.TestCase):
    def test_recovery_keeps_nav2_final_rotation_intent(self):
        goal=[2.49,-.087,3.091]
        p=[2.39,-.076,.53]
        self.assertEqual(module.recovery_heading(p,goal,[0.,.35]),goal[2])
        self.assertLess(abs(module.recovery_heading(p,goal,[0.,-.35])),.2)
        self.assertLess(abs(module.recovery_heading([1.5,-.076,.53],goal,[0.,.35])),.2)
        self.assertEqual(module.recovery_heading([2.45,-.087,.53],goal,[0.,0.]),goal[2])

    def test_recorded_partial_turn_with_rotation_center_drift(self):
        f=json.loads((ROOT/'test/data/partial-turn-fixture.json').read_text())
        p=list(f['pose']);target=math.pi;now=0.;state='failed'
        for attempt in range(2):
            r=module.ClearanceEscape(p,f['obstacles'],f['unknown'],CONFIG,.05,now,'epoch',target_heading=target)
            w=0.
            while r.state=='moving' and now<100.:
                cmd=r.command(now,p,f['obstacles'],f['unknown'],[.05*abs(w),w],True,'epoch')
                w=cmd[1];angle=p[2]+w*.1
                p[0]+=.1*cmd[0]*math.cos(p[2]);p[1]+=.1*cmd[0]*math.sin(p[2])
                p[0]+=.05*(math.cos(angle)-math.cos(p[2]))
                p[1]+=.05*(math.sin(angle)-math.sin(p[2]))
                p[2]=angle;now+=.1
                blocked=np.concatenate((np.asarray(f['obstacles']).reshape((-1,2)),np.asarray(f['unknown']).reshape((-1,2))))
                self.assertGreaterEqual(r.distances(p,blocked).min(),r.physical)
            state=r.state
            if state=='stopping' and r.turn_target is not None:break
            if state=='stopping':continue
            self.assertTrue(r.replan_allowed,r.reason)
        self.assertEqual(state,'stopping',r.reason)

    def test_recorded_narrow_corridor_turns_without_body_collision(self):
        f=json.loads((ROOT/'test/data/narrow-corridor-fixture.json').read_text())
        r=module.ClearanceEscape(f['pose'],f['obstacles'],f['unknown'],CONFIG,.05,0.,'epoch',target_heading=math.pi)
        self.assertEqual(r.distance,0.);self.assertIsNotNone(r.turn_target)
        p=list(f['pose']);now=0.;w=0.
        while r.state=='moving' and now<r.timeout:
            command=r.command(now,p,f['obstacles'],f['unknown'],[0.,w],True,'epoch')
            self.assertEqual(command[0],0.);self.assertLessEqual(abs(command[1]),.10)
            self.assertTrue(r.certified(p,command,f['obstacles'],f['unknown']))
            w=command[1];p[2]+=.1*w;now+=.1
        self.assertEqual(r.state,'stopping',r.reason)
        r=module.ClearanceEscape(f['pose'],f['obstacles'],f['unknown'],CONFIG,.05,0.,'epoch',target_heading=math.pi)
        self.assertEqual(r.command(0.,f['pose'],f['obstacles']+[f['pose'][:2]],f['unknown'],[0.,0.],True,'epoch'),[0.,0.])
        self.assertEqual(r.state,'failed')

    def test_recorded_tight_curve_is_slow_and_reaches_turn_space(self):
        f=json.loads((ROOT/'test/data/tight-turn-fixture.json').read_text())
        r=module.ClearanceEscape(f['local_pose'],f['obstacles'],[],CONFIG,.05,0.,'epoch')
        self.assertLessEqual(r.speed,.05)
        self.assertLessEqual(r.distance,.8)
        self.assertLessEqual(r.timeout,35.)
        for i,pose in enumerate(r.path):
            command=r.command(i*.01/r.speed,pose,f['obstacles'],[],[r.direction*r.speed,r.direction*r.speed*r.curvature],True,'epoch')
            self.assertNotEqual(r.state,'failed',r.reason)
        self.assertEqual(r.state,'stopping');self.assertEqual(command,[0.,0.])

    def test_recorded_curves_tolerate_measured_lateral_motion(self):
        for name in ['tight-turn-fixture.json','curved-near-obstacle-fixture.json']:
            f=json.loads((ROOT/'test/data'/name).read_text())
            p=list(f.get('pose',f.get('local_pose')));unknown=f.get('unknown',[])
            r=module.ClearanceEscape(p,f['obstacles'],unknown,CONFIG,.05,0.,'epoch')
            v=w=now=0.
            while r.state=='moving' and now<36.:
                command=r.command(now,p,f['obstacles'],unknown,[v,w],True,'epoch')
                v,w=command[0]*1.3,command[1]
                # Approximate the cross-track motion observed in both recordings.
                lateral=-.06*v+.03*w
                p[0]+=.05*(v*math.cos(p[2])-lateral*math.sin(p[2]))
                p[1]+=.05*(v*math.sin(p[2])+lateral*math.cos(p[2]))
                p[2]+=.05*w;now+=.05
            self.assertEqual(r.state,'stopping',r.reason)

    def test_faster_straight_exit_profile(self):
        r=self.make()
        self.assertAlmostEqual(r.speed,.10)
        self.assertAlmostEqual(r.command(0.,FIXTURE['pose'],FIXTURE['obstacles'],[],[0.,0.],True,'epoch')[0],.10)
        self.assertLess(r.distance/r.speed,r.distance/.03)

    def test_faster_clearance_turn_profile(self):
        f=json.loads((ROOT/'test/data/narrow-corridor-fixture.json').read_text())
        r=module.ClearanceEscape(f['pose'],f['obstacles'],f['unknown'],CONFIG,.05,0.,'epoch',target_heading=math.pi)
        cmd=r.command(0.,f['pose'],f['obstacles'],f['unknown'],[0.,0.],True,'epoch')
        self.assertAlmostEqual(abs(cmd[1]),.10)
        self.assertTrue(r.certified(f['pose'],cmd,f['obstacles'],f['unknown']))

    def test_selected_circle_geometry_preserves_existing_deviation_allowance(self):
        config=module.recovery_config(CONFIG,{'footprint':'[]','robot_radius':.1,'footprint_padding':.02})
        self.assertAlmostEqual(config['robot_radius'],.12)
        self.assertEqual(config['padding'],CONFIG['padding'])
        self.assertEqual(module.recovery_config(CONFIG,{'footprint':'[[0.25,0.185],[-0.25,0.185],[-0.25,-0.185]]'}),CONFIG)

    def test_point_model_can_exit_existing_lethal_cell_overlap(self):
        config={**CONFIG,'robot_radius':.1}
        r=module.ClearanceEscape([0.,0.,0.],[[0.,0.]],[],config,.02,0.,'epoch')
        before=r.distances(r.start,[[0.,0.]])[0]
        self.assertLess(before,-.02*.71)
        for i,p in enumerate(r.path):
            self.assertGreaterEqual(r.distances(p,[[0.,0.]])[0],before-1e-7)
            command=r.command(i*.01/r.speed,p,[[0.,0.]],[],[r.direction*r.speed,0.],True,'epoch')
            self.assertNotEqual(r.state,'failed',r.reason)
        self.assertEqual(r.state,'stopping');self.assertEqual(command,[0.,0.])
        self.assertGreaterEqual(r.distances(r.path[-1],[[0.,0.]])[0],r.physical)

    def test_circle_clearance_and_new_collision_are_not_rectangular(self):
        values=module.signed_clearance([0.,0.,0.],[[.2,0.]],.5,.37,radius=.1)
        self.assertAlmostEqual(values[0],.1)
        r=module.ClearanceEscape([0.,0.,0.],[[0.,0.]],[],{**CONFIG,'robot_radius':.1},.02,0.,'epoch')
        self.assertFalse(r.certified(r.start,[.05,0.],[[0.,0.],[.13,0.]],[]))

    def make(self):
        return module.ClearanceEscape(FIXTURE['pose'], FIXTURE['obstacles'], FIXTURE['unknown'], CONFIG, .05, 0., 'epoch')

    def test_recorded_exit_is_bounded_and_preserves_clearance(self):
        r = self.make(); self.assertEqual(r.direction, 1)
        self.assertLessEqual(r.distance, .8)
        p = FIXTURE['pose']; obstacles = np.asarray(FIXTURE['obstacles'])
        initial = r.distances(p, obstacles)
        for distance in np.linspace(0, r.distance, 101):
            pose = [p[0]+distance*math.cos(p[2]), p[1]+distance*math.sin(p[2]), p[2]]
            self.assertTrue(np.all(r.distances(pose, obstacles) >= np.minimum(initial, r.physical)-1e-6))
        command = r.command(r.distance/r.speed, pose, obstacles, [], [0., 0.], True, 'epoch')
        self.assertEqual(command, [0., 0.]); self.assertEqual(r.state, 'stopping')
        self.assertGreaterEqual(np.linalg.norm(obstacles-np.array(pose[:2]), axis=1).min()-r.radius, r.exit_clearance)

    def test_new_obstacle_cannot_use_initial_contact_exception(self):
        r = self.make(); p = FIXTURE['pose']; obstacles = FIXTURE['obstacles']+[[p[0], p[1]]]
        self.assertEqual(r.command(0., p, obstacles, [], [0., 0.], True, 'epoch'), [0., 0.])
        self.assertEqual(r.command(1.1, p, obstacles, [], [0., 0.], True, 'epoch'), [0., 0.])
        self.assertEqual(r.state, 'failed')

    def test_collision_diagnostic_can_be_serialized(self):
        r=self.make();p=FIXTURE['pose']
        r.command(0.,p,FIXTURE['obstacles']+[p[:2]],[],[0.,0.],True,'epoch')
        data=json.loads(json.dumps(r.diagnostic))
        self.assertIsInstance(data['initial_contact'],bool)

    def test_environment_change_requests_bounded_replan(self):
        r=self.make();r.abort('changed',replan=True)
        self.assertTrue(r.replan_allowed)
        r=self.make();r.abort('unsafe speed')
        self.assertFalse(r.replan_allowed)

    def test_unknown_cells_are_never_ignored(self):
        r = self.make(); p = FIXTURE['pose']
        self.assertEqual(r.command(0., p, FIXTURE['obstacles'], [p[:2]], [0., 0.], True, 'epoch'), [0., 0.])
        self.assertEqual(r.command(1.1, p, FIXTURE['obstacles'], [p[:2]], [0., 0.], True, 'epoch'), [0., 0.])
        self.assertEqual(r.state, 'failed')

    def test_transient_veto_holds_zero_then_revalidates(self):
        r=self.make();p=FIXTURE['pose']
        self.assertEqual(r.command(0.,p,FIXTURE['obstacles'],[p[:2]],[0.,0.],True,'epoch'),[0.,0.])
        self.assertEqual(r.state,'moving')
        self.assertGreater(r.command(.2,p,FIXTURE['obstacles'],[],[0.,0.],True,'epoch')[0],0.)
        self.assertIsNone(r.blocked_since)

    def test_grid_cell_identity_is_stable_at_half_cell_centers(self):
        r=self.make()
        self.assertEqual(r.key([2.175-1e-8,.225]),r.key([2.175+1e-8,.225]))
        self.assertNotEqual(r.key([2.175,.225]),r.key([2.225,.225]))

    def test_adjacent_wall_return_uses_start_pose_clearance(self):
        r=self.make();point=[2.2250000298023234,.22500003203749674]
        expected=float(r.distances(r.start,[point])[0])
        self.assertAlmostEqual(r.contact_floor(point),expected)
        self.assertLess(expected,r.physical)
        self.assertEqual(r.contact_floor(r.start[:2]),r.physical)
        original=r.contact_surface.copy()
        r.contact_floor(point)
        self.assertTrue(np.array_equal(r.contact_surface,original))

    def test_safe_straight_motion_is_used_when_heading_correction_is_blocked(self):
        r=self.make();p=list(FIXTURE['pose']);p[2]+=.01
        r.certified=lambda pose,command,*args:command[1]==0.
        self.assertEqual(r.command(0.,p,FIXTURE['obstacles'],[],[0.,0.],True,'epoch'),[.10,0.])
        self.assertEqual(r.state,'moving')

    def test_safe_away_deviation_is_certified_but_stays_bounded(self):
        r=self.make();p=FIXTURE['pose'];pose=[p[0]+.3*math.cos(p[2]),p[1]+.3*math.sin(p[2])-.03,p[2]]
        self.assertGreater(r.command(10.,pose,FIXTURE['obstacles'],[],[.03,0.],True,'epoch')[0],0.)
        self.assertEqual(r.state,'moving')
        pose[1]-=.04
        self.assertEqual(r.command(10.1,pose,FIXTURE['obstacles'],[],[.03,0.],True,'epoch'),[0.,0.])
        self.assertEqual(r.state,'failed')
        self.assertTrue(r.replan_allowed)

    def test_recorded_curved_retreat_reaches_turn_space(self):
        f=json.loads((ROOT/'test/data/curved-near-obstacle-fixture.json').read_text())
        r=module.ClearanceEscape(f['pose'],f['obstacles'],f['unknown'],CONFIG,.05,0.,'epoch')
        self.assertIn(r.direction,[-1,1]);self.assertNotEqual(r.curvature,0.)
        self.assertLessEqual(r.distance,.8);self.assertLessEqual(r.timeout,35.)
        for i,p in enumerate(r.path):
            command=r.command(i*.01/r.speed,p,f['obstacles'],f['unknown'],[r.speed,r.direction*r.speed*r.curvature],True,'epoch')
            self.assertNotEqual(r.state,'failed',r.reason)
        self.assertEqual(r.state,'stopping');self.assertEqual(command,[0.,0.])

    def test_deep_body_collision_is_not_an_escape_exception(self):
        with self.assertRaises(ValueError):
            module.ClearanceEscape([0., 0., 0.], [[0., 0.]], [], CONFIG, .05, 0., 'epoch')

    def test_stale_input_holds_zero(self):
        r = self.make()
        self.assertEqual(r.command(0., FIXTURE['pose'], FIXTURE['obstacles'], [], [0., 0.], False, 'epoch'), [0., 0.])
        self.assertEqual(r.state, 'moving')

    def test_changed_localization_and_timeout_abort(self):
        for now, epoch in [(0., 'new'), (self.make().timeout+1, 'epoch')]:
            r = self.make()
            self.assertEqual(r.command(now, FIXTURE['pose'], FIXTURE['obstacles'], [], [0., 0.], True, epoch), [0., 0.])
            self.assertEqual(r.state, 'failed')

    def test_stall_and_overspeed_abort(self):
        for now, velocity in [(4.1, [0., 0.]), (0., [.2, 0.]), (0., [0., .2])]:
            r = self.make()
            self.assertEqual(r.command(now, FIXTURE['pose'], FIXTURE['obstacles'], [], velocity, True, 'epoch'), [0., 0.])
            if now==0.:
                self.assertEqual(r.command(1.1,FIXTURE['pose'],FIXTURE['obstacles'],[],velocity,True,'epoch'),[0.,0.])
            self.assertEqual(r.state, 'failed')

    def test_transient_speed_peak_holds_then_resumes_with_governor(self):
        r=self.make();p=FIXTURE['pose']
        self.assertEqual(r.command(0.,p,FIXTURE['obstacles'],[],[.16,0.],True,'epoch'),[0.,0.])
        self.assertEqual(r.state,'moving')
        self.assertGreater(r.command(.2,p,FIXTURE['obstacles'],[],[.04,0.],True,'epoch')[0],0.)
        self.assertIsNone(r.speed_limited_since)
        speed=r.command(.3,p,FIXTURE['obstacles'],[],[.12,0.],True,'epoch')[0]
        self.assertGreater(speed,0.);self.assertAlmostEqual(speed,r.speed*r.speed/.12)


def method(file, name, environment):
    tree = ast.parse((SOURCE / file).read_text())
    fn = next(m for c in tree.body if isinstance(c, ast.ClassDef) for m in c.body
              if isinstance(m, ast.FunctionDef) and m.name == name)
    exec(compile(ast.Module(body=[fn], type_ignores=[]), name, 'exec'), environment)
    return environment[name]


class LifecycleTests(unittest.TestCase):
    def test_low_speed_turn_keeps_native_job_and_physical_estop_priority(self):
        for estop in [False,True]:
            sent=[];canceled=[];job=object()
            class Twist:
                def __init__(self):self.linear=NS(x=0.);self.angular=NS(z=0.)
            tick=method('control.py','control_tick',{'time':NS(monotonic=lambda:1.),'math':math,'Twist':Twist})
            n=NS(control_gate_ready=True,mode='LOCAL',current_job=job,nav=[0.,.35],nav_time=1.,
                 output_permitted=lambda:True,estop=estop,local_pose=[0.,0.,0.],pose_stamp_ns=1,
                 planned_path=[],obstacles=[],obstacle_resolution=.02,pose_age=0.,obstacle_stamp=1.,obstacle_complete=True,
                 tracking_guard=NS(evaluate=lambda *a,**k:('predicted_body_clearance',True),reset=lambda:None),
                 bounded_turn_command=lambda now,command,start=False:[0.,.08] if start else None,
                 cancel_all=lambda:canceled.append(True),output=NS(publish=lambda m:sent.append([m.linear.x,m.angular.z])))
            tick(n);self.assertEqual(sent,[[0.,0. if estop else .08]])
            self.assertEqual(canceled,[]);self.assertIs(n.current_job,job)

    def test_new_waypoint_restores_its_own_recovery_attempts(self):
        prepare=method('runtime.py','prepare_clearance_recovery',{'recovery_heading':module.recovery_heading})
        for block in [0,1]:
            job=NS(single=False,source='LOCAL',ticket='t',clearance_attempts=2,clearance_block=0)
            n=NS(current_job=job,mode='LOCAL',clearance_escape=None,recovery_pending=None,
                 epoch='e',execution=NS(block=block))
            prepare(n)
            self.assertEqual(n.recovery_pending is not None,block==1)
            self.assertEqual(job.clearance_attempts,1 if block==1 else 2)

    def test_environment_replan_preserves_final_heading_after_nav2_zero(self):
        prepare=method('runtime.py','prepare_clearance_recovery',{'recovery_heading':module.recovery_heading})
        n=NS(current_job=NS(single=True,source='LOCAL',ticket='t'),mode='LOCAL',clearance_escape=None,
             recovery_pending=None,epoch='e',local_pose=[2.39,-.076,.53],goal=[2.49,-.087,3.091],nav=[0.,.35])
        prepare(n);self.assertEqual(n.recovery_pending['heading'],3.091)
        n.recovery_pending=None;n.nav=[0.,0.]
        prepare(n);self.assertEqual(n.recovery_pending['heading'],3.091)

    def test_environment_replan_keeps_original_job_and_waits_stopped(self):
        prepared=[];finished=[];job=NS(clearance_attempts=1)
        recovery=NS(state='failed',reason='changed',diagnostic={'initial_contact':False},replan_allowed=True,
                    started=0.,timeout=30.,epoch='e')
        n=NS(clearance_escape=recovery,mode='LOCAL',estop=False,epoch='e',current_job=job,
             get_logger=lambda:NS(warning=lambda *args:None),prepare_clearance_recovery=lambda:prepared.append(True),
             policy=NS(cancel=lambda:None),execution=NS(finish=lambda *args:finished.append(args)))
        update=method('runtime.py','update_clearance_recovery',{'time':NS(monotonic=lambda:1.),'json':json})
        self.assertFalse(update(n));self.assertEqual(prepared,[True])
        self.assertIs(n.current_job,job);self.assertIsNone(n.clearance_escape)
        self.assertTrue(n.inhibited);self.assertFalse(n.armed)
        self.assertEqual(finished[0][0],'canceled')

    def test_recovery_speed_uses_body_pose_not_wheel_rotation(self):
        observed=[]
        def command(now,pose,obstacles,unknown,velocity,fresh,epoch):
            observed.append((velocity,fresh));return [0.,0.]
        read=method('runtime.py','recovery_command',{'math':math,'body_velocity':body_velocity})
        n=NS(clearance_escape=NS(command=command),control_gate_ready=True,obstacle_complete=True,
             pose_age=.02,local_pose=[0.,0.,0.],obstacles=[],velocity=[.02,.155],epoch='epoch',
             recovery_pose_history=[],recovery_unknown=lambda:[],execution=NS(pose=None))
        for i in range(3):
            now=1.+i*.1;stamp=100000000+i*100000000
            m=NS(header=NS(stamp=NS(sec=0,nanosec=stamp)),pose=NS(pose=NS(
                position=NS(x=i*.003,y=0.),orientation=NS(x=0.,y=0.,z=0.,w=1.))))
            n.execution.pose=(now,m);n.pose_time=n.obstacle_stamp=n.velocity_time=now
            read(n,now)
        self.assertTrue(observed[-1][1]);self.assertAlmostEqual(observed[-1][0][0],.03)
        self.assertAlmostEqual(observed[-1][0][1],0.)

    def test_recovery_waits_for_all_old_requests_and_stopped_feedback(self):
        spec = importlib.util.spec_from_file_location('policy', SOURCE / 'task_policy.py')
        policy_module = importlib.util.module_from_spec(spec); spec.loader.exec_module(policy_module)
        policy = policy_module.TaskPolicy(); ticket = policy_module.Ticket('test', 'LOCAL')
        policy.request(ticket); policy.cancel()
        started = []; stopped = [False]
        def create(*args,**kwargs):
            started.append(True); return NS(distance=.51,direction=1,curvature=0.,timeout=25.,speed=.03)
        update = method('runtime.py', 'update_jobs', {'time': NS(monotonic=lambda: 1.), 'ClearanceEscape': create, 'json': json, 'recovery_config': module.recovery_config})
        n = NS(update_clearance_recovery=lambda: False, current_job=NS(ticket=ticket),
               policy=policy, execution=NS(phase='canceling', active=True, requests={'old': 1}, set_phase=lambda *args: None),
               pending_job=None, recovery_pending={'ticket': ticket, 'epoch': 'epoch'}, epoch='epoch',
               stationary=lambda: stopped[0], cancel_deadline=10., publish_catalog=lambda: None,
               estop=False, mode='LOCAL', local_pose=[0., 0., 0.], obstacles=[], config=CONFIG,
               recovery_unknown=lambda: [], obstacle_resolution=.05,runtime_parameters={},selection={},
               get_logger=lambda:NS(info=lambda *args:None))
        update(n); n.execution.active=False; update(n)
        n.execution.requests={}; update(n)
        self.assertEqual(started, [])
        stopped[0]=True; update(n)
        self.assertEqual(started, [True]); self.assertTrue(n.inhibited)
        self.assertFalse(n.armed)

    def test_resume_keeps_passed_points_and_refuses_pending_requests(self):
        sent = []; n = NS(requests={'old': 1}, active=False, blocks=[(0, 3)], block=0,
                          states=['已通过', '正在通过', '待通过'], epoch=2, failed=True,
                          n=NS(navigation_active=False), send_block=lambda: sent.append(True))
        resume = method('route_execution.py', 'resume_after_clearance', {})
        with self.assertRaises(RuntimeError): resume(n)
        self.assertEqual(sent, [])
        n.requests = {}; resume(n)
        self.assertEqual(n.blocks, [(1, 3)]); self.assertEqual(sent, [True])

    def test_physical_estop_overrides_recovery_output(self):
        sent = []
        class Twist:
            def __init__(self): self.linear=NS(x=0.); self.angular=NS(z=0.)
        tick = method('control.py', 'control_tick', {'time': NS(monotonic=lambda: 1.), 'math': math, 'Twist': Twist})
        n = NS(clearance_escape=object(), control_gate_ready=True, mode='LOCAL',
               recovery_command=lambda now: [.03, 0.], tracking_guard=NS(reset=lambda: None),
               estop=True, output=NS(publish=lambda m: sent.append([m.linear.x, m.angular.z])))
        tick(n); self.assertEqual(sent, [[0., 0.]])


if __name__ == '__main__': unittest.main()
