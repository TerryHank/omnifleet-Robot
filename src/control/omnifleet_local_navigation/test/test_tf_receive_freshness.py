import ast
from pathlib import Path
import time
import unittest

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import Buffer, TransformListener, TransformBroadcaster


class TfReceiveFreshnessTests(unittest.TestCase):
    def test_busy_navigation_receives_latest_dynamic_tf_and_preserves_static_history(self):
        rclpy.init()
        publisher=Node('tf_freshness_publisher')
        old=Node('tf_freshness_old');old.tf=Buffer()
        old.listener=TransformListener(old.tf,old)
        current=Node('tf_freshness_current');current.tf=Buffer()
        source=Path(__file__).resolve().parents[1]/'omnifleet_local_navigation/control.py'
        tree=ast.parse(source.read_text())
        assign=next(n for n in ast.walk(tree) if isinstance(n,ast.Assign)
            and any(isinstance(t,ast.Attribute) and t.attr=='listener' for t in n.targets))
        exec(compile(ast.Module(body=[assign],type_ignores=[]),'production_tf_listener','exec'),
            {'self':current,'TransformListener':TransformListener})
        broadcaster=TransformBroadcaster(publisher)
        try:
            end=time.monotonic()+3.
            while publisher.count_subscribers('/tf')<2 and time.monotonic()<end:
                time.sleep(.02)
            self.assertGreaterEqual(publisher.count_subscribers('/tf'),2)
            # Simulate a busy navigation executor while TF continues to arrive.
            end=time.monotonic()+1.2
            while time.monotonic()<end:
                msg=TransformStamped();msg.header.frame_id='freshness_map'
                msg.child_frame_id='freshness_base';msg.header.stamp=publisher.get_clock().now().to_msg()
                msg.transform.rotation.w=1.;broadcaster.sendTransform(msg);time.sleep(.02)
            ages=[]
            for node in [old,current]:
                end=time.monotonic()+1.
                while not node.tf.can_transform('freshness_map','freshness_base',rclpy.time.Time()) and time.monotonic()<end:
                    rclpy.spin_once(node,timeout_sec=.05)
                tf=node.tf.lookup_transform('freshness_map','freshness_base',rclpy.time.Time())
                ages.append(time.time()-tf.header.stamp.sec-tf.header.stamp.nanosec/1e9)
            self.assertGreater(ages[0]-ages[1],.5)
            self.assertLess(ages[1],.8)
            self.assertEqual(current.listener.tf_static_sub.qos_profile.depth,100)
        finally:
            old.listener.unregister();current.listener.unregister()
            old.destroy_node();current.destroy_node();publisher.destroy_node();rclpy.shutdown()


if __name__=='__main__':
    unittest.main()
