import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from pose_compensation import PoseCompensator

def pose(x=0,y=0,yaw=0):
 return np.array([x,y,0,*Rotation.from_euler('z',yaw).as_quat()])

class CompensationTest(unittest.TestCase):
 def test_delayed_straight_pose(self):
  c=PoseCompensator(.75)
  c.add_wheel(10,pose(0));c.add_wheel(10.5,pose(.5))
  c.add_lidar(10.2,pose(3.2))
  stamp,p=c.current()
  self.assertEqual(stamp,10.5)
  np.testing.assert_allclose(p[:3],[3.5,0,0],atol=1e-9)
 def test_turn_and_map_rotation(self):
  c=PoseCompensator(.75)
  c.add_wheel(1,pose());c.add_wheel(1.5,pose(1,0,np.pi/2))
  c.add_lidar(1,pose(5,6,np.pi/2))
  _,p=c.current()
  np.testing.assert_allclose(p[:2],[5,7],atol=1e-9)
  self.assertAlmostEqual(abs(Rotation.from_quat(p[3:]).as_euler('xyz')[2]),np.pi)
 def test_missing_history_and_stale_anchor(self):
  c=PoseCompensator(.75)
  c.add_wheel(2,pose());c.add_lidar(1,pose())
  self.assertIsNone(c.current())
  c.add_lidar(2,pose());c.add_wheel(3,pose(1))
  np.testing.assert_allclose(c.current()[1][:3],[1,0,0],atol=1e-9)
  c.add_wheel(6,pose(4))
  self.assertIsNone(c.current())
 def test_old_inputs_and_stationary(self):
  c=PoseCompensator(.75)
  c.add_wheel(1,pose(8));c.add_wheel(1.1,pose(8))
  c.add_lidar(1,pose(2,3))
  c.add_wheel(.9,pose(99));c.add_lidar(.9,pose(99))
  _,p=c.current()
  np.testing.assert_allclose(p[:3],pose(2,3)[:3],atol=1e-9)
  self.assertAlmostEqual(Rotation.from_quat(p[3:]).magnitude(),0)

if __name__=='__main__':unittest.main()
