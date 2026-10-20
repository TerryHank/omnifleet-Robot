#!/usr/bin/env python3
"""Publish a V4L2 USB camera as sensor_msgs/CompressedImage."""
import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, Image


class UsbCameraPublisher(Node):
    def __init__(self):
        super().__init__('usb_camera_publisher')
        self.declare_parameter('device', '/dev/video0')
        self.declare_parameter('topic', '/camera/image/compressed')
        self.declare_parameter('frame_id', 'camera_link')
        self.declare_parameter('fps', 15.0)
        self.declare_parameter('jpeg_quality', 75)
        device = str(self.get_parameter('device').value)
        self.frame_id = str(self.get_parameter('frame_id').value)
        self.quality = int(self.get_parameter('jpeg_quality').value)
        self.publisher = self.create_publisher(
            CompressedImage, str(self.get_parameter('topic').value), 5)
        raw_topic = str(self.get_parameter('topic').value)
        if raw_topic.endswith('/compressed'):
            raw_topic = raw_topic[:-len('/compressed')]
        self.raw_publisher = self.create_publisher(Image, raw_topic, 5)
        self.camera = cv2.VideoCapture(device, cv2.CAP_V4L2)
        if not self.camera.isOpened():
            raise RuntimeError('cannot open USB camera ' + device)
        self.timer = self.create_timer(1.0 / max(1.0, float(self.get_parameter('fps').value)),
                                       self.publish_frame)
        self.get_logger().info('USB camera opened: %s' % device)

    def publish_frame(self):
        ok, frame = self.camera.read()
        if not ok:
            self.get_logger().warning('USB camera frame read failed')
            return
        ok, encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
        if not ok:
            return
        message = CompressedImage()
        message.header.stamp = self.get_clock().now().to_msg()
        message.header.frame_id = self.frame_id
        message.format = 'jpeg'
        message.data = encoded.tobytes()
        self.publisher.publish(message)
        raw = Image()
        raw.header = message.header
        raw.height, raw.width = frame.shape[:2]
        raw.encoding = 'bgr8'
        raw.is_bigendian = False
        raw.step = int(frame.strides[0])
        raw.data = frame.tobytes()
        self.raw_publisher.publish(raw)

    def destroy_node(self):
        if self.camera:
            self.camera.release()
        super().destroy_node()


def main():
    rclpy.init()
    node = UsbCameraPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
