"""Publish a small visualization cloud while navigation keeps the source cloud."""
from array import array
import math
import struct
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2, PointField


def sample_cloud(message, limit=2000):
    result = PointCloud2()
    result.header = message.header
    result.height = 1
    result.fields = [PointField(name=name, offset=index * 4, datatype=PointField.FLOAT32, count=1)
                     for index, name in enumerate(('x', 'y', 'z'))]
    result.point_step = 12
    result.is_dense = True
    fields = {field.name: field for field in message.fields}
    payload = bytearray()
    if all(name in fields and fields[name].datatype in (PointField.FLOAT32, PointField.FLOAT64)
           for name in ('x', 'y', 'z')) and message.point_step:
        count = message.width * message.height
        stride = max(1, math.ceil(count / limit))
        data = bytes(message.data)
        for index in range(0, count, stride):
            base = (index // message.width) * message.row_step + (index % message.width) * message.point_step
            point = [struct.unpack_from(('>' if message.is_bigendian else '<') +
                     ('f' if fields[name].datatype == PointField.FLOAT32 else 'd'),
                     data, base + fields[name].offset)[0] for name in ('x', 'y', 'z')]
            if all(math.isfinite(value) for value in point):
                payload.extend(struct.pack('<fff', *point))
    result.width = len(payload) // result.point_step
    result.row_step = len(payload)
    result.data = array('B', payload)
    return result


class WebPointCloud(Node):
    def __init__(self):
        super().__init__('omnifleet_web_pointcloud')
        self.output = self.create_publisher(PointCloud2, '/visualization/points', qos_profile_sensor_data)
        self.last_publish = 0.
        self.subscription = self.create_subscription(PointCloud2, '/navigation/deskewed_points', self.receive, qos_profile_sensor_data)

    def receive(self, message):
        now = time.monotonic()
        if now - self.last_publish < 1. / 3.:
            return
        self.last_publish = now
        self.output.publish(sample_cloud(message, limit=12000))


def main():
    rclpy.init()
    node = WebPointCloud()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
