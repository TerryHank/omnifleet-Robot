#!/usr/bin/env python3
"""Low-bandwidth Foxglove copy; navigation and SLAM keep the source cloud."""

import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2


def display_copy(cloud):
    total = cloud.height * cloud.width
    points = np.ndarray(
        (cloud.height, cloud.width),
        dtype=np.dtype((np.void, cloud.point_step)),
        buffer=cloud.data,
        strides=(cloud.row_step, cloud.point_step),
    )
    count = min(total, 8000)
    if total > count:
        indices = np.linspace(0, total - 1, count, dtype=np.int64)
        data = points[indices // cloud.width, indices % cloud.width].tobytes()
    else:
        data = points.tobytes()
    return PointCloud2(
        header=cloud.header,
        height=1,
        width=count,
        fields=cloud.fields,
        is_bigendian=cloud.is_bigendian,
        point_step=cloud.point_step,
        row_step=count * cloud.point_step,
        data=data,
        is_dense=cloud.is_dense,
    )


class DisplayCloud(Node):
    def __init__(self):
        super().__init__("omnifleet_display_cloud")
        self.latest = None
        qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.publisher = self.create_publisher(
            PointCloud2, "/visualization/deskewed_points", qos
        )
        self.subscription = self.create_subscription(
            PointCloud2, "/navigation/deskewed_points", self.receive, qos
        )
        self.timer = self.create_timer(1.0, self.publish_latest)

    def receive(self, cloud):
        self.latest = cloud

    def publish_latest(self):
        cloud, self.latest = self.latest, None
        if cloud is not None:
            self.publisher.publish(display_copy(cloud))


def main():
    rclpy.init()
    node = DisplayCloud()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()

