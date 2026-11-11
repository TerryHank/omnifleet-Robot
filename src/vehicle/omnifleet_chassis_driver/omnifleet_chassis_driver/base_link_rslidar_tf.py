#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

class BaseLinkRslidarTF(Node):
    def __init__(self):
        super().__init__('base_link_rslidar_tf')
        self.br = TransformBroadcaster(self)
        self.create_timer(0.05, self.publish_tf)

    def publish_tf(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'base_link'
        t.child_frame_id = 'rslidar'
        t.transform.translation.x = -0.041
        t.transform.translation.z = 0.150
        t.transform.rotation.w = 1.0
        self.br.sendTransform(t)

def main():
    rclpy.init()
    node = BaseLinkRslidarTF()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node(); rclpy.shutdown()

if __name__ == '__main__':
    main()
