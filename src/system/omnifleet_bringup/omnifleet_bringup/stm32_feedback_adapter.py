import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node


class Stm32FeedbackAdapter(Node):
    """Wrap STM32 body feedback without performing kinematics or integration."""

    def __init__(self):
        super().__init__("stm32_feedback_adapter")
        self.declare_parameter("odom_frame", "odom")
        self.declare_parameter("base_frame", "base_link")
        self.odom_frame = self.get_parameter("odom_frame").value
        self.base_frame = self.get_parameter("base_frame").value
        self.publisher = self.create_publisher(Odometry, "/wheel/odometry", 50)
        self.subscription = self.create_subscription(
            Twist, "/vel_raw", self.feedback_callback, 50
        )

    def feedback_callback(self, feedback):
        odometry = Odometry()
        odometry.header.stamp = self.get_clock().now().to_msg()
        odometry.header.frame_id = self.odom_frame
        odometry.child_frame_id = self.base_frame
        odometry.pose.pose.orientation.w = 1.0
        for index in (0, 7, 14, 21, 28, 35):
            odometry.pose.covariance[index] = 1.0e6
        odometry.twist.twist.linear.x = feedback.linear.x
        odometry.twist.twist.angular.z = feedback.angular.z
        odometry.twist.covariance[0] = 0.01
        odometry.twist.covariance[35] = 0.04
        self.publisher.publish(odometry)


def main():
    rclpy.init()
    node = Stm32FeedbackAdapter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
