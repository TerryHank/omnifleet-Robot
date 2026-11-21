#!/usr/bin/env python3

from math import floor

import rclpy
from nav_msgs.msg import OccupancyGrid
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy


class TrafficMapPublisher(Node):
    RESOLUTION = 0.05
    SIZE = 12.0
    ORIGIN = -6.0

    def __init__(self):
        super().__init__('omnifleet_a2_traffic_map')
        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.publisher = self.create_publisher(OccupancyGrid, '/map', qos)
        self.map_message = self._build_map()
        self.timer = self.create_timer(2.0, self.publish_map)
        self.publish_map()

    def _cell(self, coordinate):
        return int(floor((coordinate - self.ORIGIN) / self.RESOLUTION))

    def _mark_box(self, data, width, cx, cy, sx, sy):
        x0 = max(0, self._cell(cx - sx / 2.0))
        x1 = min(width - 1, self._cell(cx + sx / 2.0))
        y0 = max(0, self._cell(cy - sy / 2.0))
        y1 = min(width - 1, self._cell(cy + sy / 2.0))
        for y_index in range(y0, y1 + 1):
            row = y_index * width
            for x_index in range(x0, x1 + 1):
                data[row + x_index] = 100

    def _build_map(self):
        cells = int(self.SIZE / self.RESOLUTION)
        data = [0] * (cells * cells)

        # These boxes match the collision geometry in the Gazebo world.
        obstacles = [
            (0.0, 5.95, 12.0, 0.10),
            (0.0, -5.95, 12.0, 0.10),
            (5.95, 0.0, 0.10, 12.0),
            (-5.95, 0.0, 0.10, 12.0),
            (-4.76, 0.0, 0.12, 3.0),
            (-3.44, 0.0, 0.12, 3.0),
            (1.55, 4.55, 0.72, 0.38),
            (2.55, 4.55, 0.72, 0.38),
            (2.40, 0.10, 0.24, 0.24),
            (3.05, 0.45, 0.24, 0.24),
        ]
        for box in obstacles:
            self._mark_box(data, cells, *box)

        message = OccupancyGrid()
        message.header.frame_id = 'map'
        message.info.resolution = self.RESOLUTION
        message.info.width = cells
        message.info.height = cells
        message.info.origin.position.x = self.ORIGIN
        message.info.origin.position.y = self.ORIGIN
        message.info.origin.orientation.w = 1.0
        message.data = data
        return message

    def publish_map(self):
        self.map_message.header.stamp = self.get_clock().now().to_msg()
        self.publisher.publish(self.map_message)


def main():
    rclpy.init()
    node = TrafficMapPublisher()
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
