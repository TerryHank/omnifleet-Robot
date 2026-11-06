"""Position-only map goals reuse the onboard navigation owner."""
import ast
import copy
import math
import unittest
from pathlib import Path
from types import SimpleNamespace
from geometry_msgs.msg import PointStamped, PoseStamped, TransformStamped
from rclpy.time import Time
from tf2_ros import TransformException
from tf2_geometry_msgs import do_transform_point

runtime = Path(__file__).resolve().parents[1]/'omnifleet_local_navigation/runtime.py'
module = ast.parse(runtime.read_text())
method = next(item for cls in module.body if isinstance(cls, ast.ClassDef)
              for item in cls.body if isinstance(item, ast.FunctionDef) and item.name == 'goal_point')
scope = dict(copy=copy, math=math, PoseStamped=PoseStamped, Time=Time,
             TransformException=TransformException, do_transform_point=do_transform_point)
exec(compile(ast.Module(body=[method], type_ignores=[]), str(runtime), 'exec'), scope)

class PointGoal(unittest.TestCase):
    def setUp(self):
        self.received=[];self.status=[]
        self.node=SimpleNamespace(frame_id='map',local_pose=[1.,2.,.7],
                                  goal_pose=self.received.append,publish_status=self.status.append)
        self.message=PointStamped();self.message.header.frame_id='map'
        self.message.point.x=4.;self.message.point.y=6.

    def submit(self):
        scope['goal_point'](self.node,self.message)

    def test_map_point_uses_automatic_bearing_and_existing_goal_path(self):
        self.submit()
        self.assertEqual(len(self.received),1)
        target=self.received[0]
        self.assertEqual(target.header.frame_id,'map')
        self.assertEqual((target.pose.position.x,target.pose.position.y),(4.,6.))
        self.assertAlmostEqual(2*math.atan2(target.pose.orientation.z,target.pose.orientation.w),math.atan2(4.,3.))
        self.assertEqual(self.message.point.x,4.)

    def test_vehicle_relative_point_is_transformed_to_map(self):
        transform=TransformStamped();transform.header.frame_id='map';transform.child_frame_id='base_link'
        transform.transform.translation.x=10.;transform.transform.translation.y=-3.
        transform.transform.rotation.z=math.sin(math.pi/4);transform.transform.rotation.w=math.cos(math.pi/4)
        lookups=[]
        self.node.tf=SimpleNamespace(lookup_transform=lambda target,source,stamp:(lookups.append((target,source)) or transform))
        self.node.local_pose=[10.,-3.,0.]
        self.message.header.frame_id='base_link';self.message.point.x=1.;self.message.point.y=0.
        self.submit()
        point=self.received[0].pose.position
        self.assertAlmostEqual(point.x,10.);self.assertAlmostEqual(point.y,-2.)
        self.assertEqual(lookups,[('map','base_link')])
        q=self.received[0].pose.orientation
        self.assertAlmostEqual(2*math.atan2(q.z,q.w),math.pi/2)

    def test_same_position_retains_current_heading(self):
        self.message.point.x=1.;self.message.point.y=2.
        self.submit();q=self.received[0].pose.orientation
        self.assertAlmostEqual(2*math.atan2(q.z,q.w),.7)

    def test_missing_pose_still_uses_existing_navigation_admission(self):
        self.node.local_pose=None
        self.submit()
        self.assertEqual(len(self.received),1)
        self.assertEqual(self.received[0].pose.orientation.w,1.)

    def test_unavailable_frame_reports_error_without_submitting_wrong_coordinates(self):
        def lookup(*args):raise TransformException('missing frame')
        self.node.tf=SimpleNamespace(lookup_transform=lookup)
        self.message.header.frame_id='missing'
        self.submit()
        self.assertFalse(self.received)
        self.assertIn('missing frame',self.status[0])

if __name__=='__main__':unittest.main()
