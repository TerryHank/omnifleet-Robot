import ast
import json
from pathlib import Path
from types import SimpleNamespace as NS
import unittest

from omnifleet_local_navigation.clearance_recovery import ClearanceEscape, recovery_config, recovery_heading, local_body_collision
from omnifleet_local_navigation.task_policy import TaskPolicy, Ticket

SOURCE = Path(__file__).resolve().parents[1] / 'omnifleet_local_navigation'


def method(file, name, scope):
    tree = ast.parse((SOURCE / file).read_text())
    fn = next(m for c in tree.body if isinstance(c, ast.ClassDef)
              for m in c.body if isinstance(m, ast.FunctionDef) and m.name == name)
    exec(compile(ast.Module(body=[fn], type_ignores=[]), name, 'exec'), scope)
    return scope[name]


def escape(now=0., timeout=1.):
    result = ClearanceEscape.__new__(ClearanceEscape)
    result.state = 'moving'
    result.started, result.timeout, result.epoch = now, timeout, 'epoch'
    result.reason, result.diagnostic, result.replan_allowed = '', {}, False
    return result


class TimeoutReplanTests(unittest.TestCase):
    def runtime(self):
        now, stopped, created, sent, completed = [2.], [False], [], [], []
        policy = TaskPolicy()
        ticket = Ticket('original-route', 'LOCAL')
        policy.request(ticket)
        points = [object(), object(), object()]
        job = NS(ticket=ticket, source='LOCAL', single=False, points=points,
                 clearance_attempts=2, clearance_block=0)
        execution = NS(active=True, phase='recovering', requests={}, block=0,
                       blocks=[(0, 3)], points=points, states=['已通过', '正在通过', '待通过'],
                       epoch=7, failed=False)
        n = NS(clearance_escape=escape(), mode='LOCAL', estop=False, epoch='epoch',
               current_job=job, pending_job=None, recovery_pending=None, execution=execution,
               policy=policy, goal=[5., 6., .7], local_pose=[1., 2., .3], nav=[0., 0.],
               config={'length': .5, 'width': .37, 'padding': .05}, obstacles=[[.944,2.182]],
               obstacle_resolution=.05, runtime_parameters={}, selection={},
               stationary=lambda: stopped[0], get_logger=lambda: NS(warning=lambda *_: None, info=lambda *_: None),
               publish_catalog=lambda: None, recovery_unknown=lambda: [],
               finish_job=lambda *args: completed.append(args),
               tracking_guard=NS(reset=lambda: None), tracking_stop_reason='', goal_error='')
        execution.n = n

        def finish(phase, _text):
            execution.active, execution.phase = False, phase

        execution.finish = finish
        execution.set_phase = lambda phase, _text: setattr(execution, 'phase', phase)
        execution.send_block = lambda: sent.append(execution.points[execution.blocks[0][0]:execution.blocks[0][1]])
        execution.resume_after_clearance = lambda: method('route_execution.py', 'resume_after_clearance', {})(execution)
        prepare = method('runtime.py', 'prepare_clearance_recovery', {'recovery_heading': recovery_heading})
        n.prepare_clearance_recovery = lambda **kwargs: prepare(n, **kwargs)
        update = method('runtime.py', 'update_clearance_recovery', {'time': NS(monotonic=lambda: now[0]), 'json': json})
        n.update_clearance_recovery = lambda: update(n)

        def create(*args, **_kwargs):
            created.append(list(args[0]))
            r = escape(now[0], 30.)
            r.distance, r.direction, r.curvature, r.speed = .2, -1, 0., .05
            return r

        jobs = method('runtime.py', 'update_jobs', {'time': NS(monotonic=lambda: now[0]),
                      'ClearanceEscape': create, 'recovery_config': recovery_config, 'local_body_collision': local_body_collision, 'json': json})
        return n, now, stopped, created, sent, completed, update, jobs

    def test_command_timeout_requests_replanning_but_epoch_change_does_not(self):
        for epoch, retry in [('epoch', True), ('changed', False)]:
            r = escape()
            self.assertEqual(r.command(2., None, [], [], [0., 0.], True, epoch), [0., 0.])
            self.assertEqual(r.replan_allowed, retry)
            self.assertEqual(getattr(r, 'timed_out', False), retry)

    def test_runtime_timeout_retains_route_and_resumes_remaining_original_points(self):
        n, now, stopped, created, sent, completed, update, jobs = self.runtime()
        job, points, goal = n.current_job, n.execution.points, n.goal
        self.assertFalse(update(n))
        self.assertIsNotNone(n.recovery_pending)
        self.assertEqual(n.execution.phase, 'canceled')
        self.assertIs(n.current_job, job)
        self.assertEqual(n.current_job.clearance_attempts, 2)
        jobs(n)
        self.assertEqual(created, [])
        stopped[0] = True
        n.local_pose = [1.1, 2.1, .4]
        jobs(n)
        self.assertEqual(created, [[1.1, 2.1, .4]])
        self.assertEqual(n.execution.phase, 'recovering')
        self.assertIs(n.current_job, job)
        self.assertIs(n.execution.points, points)
        self.assertIs(n.goal, goal)
        n.clearance_escape.state = 'stopping'
        self.assertTrue(update(n))
        self.assertEqual(n.execution.blocks, [(1, 3)])
        self.assertEqual(sent, [points[1:]])
        self.assertIs(sent[0][-1], points[-1])
        self.assertEqual(completed, [])

    def test_repeated_timeouts_do_not_hit_the_non_timeout_attempt_limit(self):
        n, now, stopped, created, _sent, completed, update, jobs = self.runtime()
        original = n.current_job
        stopped[0] = True
        for _ in range(4):
            update(n)
            self.assertIsNotNone(n.recovery_pending)
            jobs(n)
            self.assertIs(n.current_job, original)
            self.assertEqual(original.clearance_attempts, 2)
            now[0] += 31.
        self.assertEqual(len(created), 4)
        self.assertEqual(completed, [])

    def test_existing_terminal_failure_is_not_reclassified_after_deadline(self):
        n, _now, _stopped, _created, _sent, _completed, update, _jobs = self.runtime()
        n.clearance_escape.abort('original terminal failure')
        update(n)
        self.assertIsNone(n.recovery_pending)
        self.assertEqual(n.execution.phase, 'failed')


if __name__ == '__main__':
    unittest.main()
