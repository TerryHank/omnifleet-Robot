import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo, Image


def main():
    rclpy.init()
    node = Node('gemini345lg_aligned_depth_alias')
    for suffix, message_type in (('image_raw', Image), ('camera_info', CameraInfo)):
        publisher = node.create_publisher(
            message_type, '/camera/aligned_depth_to_color/' + suffix, 2)
        node.create_subscription(
            message_type, '/camera/depth/' + suffix, publisher.publish,
            qos_profile_sensor_data)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
