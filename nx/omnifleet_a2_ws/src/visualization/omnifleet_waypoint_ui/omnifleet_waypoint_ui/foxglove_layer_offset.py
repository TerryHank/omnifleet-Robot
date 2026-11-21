# SPDX-License-Identifier: Apache-2.0
# Moved from the retired omnifleet_t2_mola_experiments package.
#!/usr/bin/env python3
import copy
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from nav_msgs.msg import OccupancyGrid, Path


class FoxgloveLayerOffset(Node):
    def __init__(self):
        super().__init__('foxglove_layer_offset')
        map_qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                             durability=DurabilityPolicy.TRANSIENT_LOCAL)
        path_qos = QoSProfile(depth=5, reliability=ReliabilityPolicy.RELIABLE,
                              durability=DurabilityPolicy.VOLATILE)
        self.map_offsets = {
            '/map': ('/foxglove/map', 0.00),
            '/global_costmap/costmap': ('/foxglove/global_costmap/costmap', 0.06),
            '/local_costmap/costmap': ('/foxglove/local_costmap/costmap', 0.12),
        }
        self.path_offsets = {
            '/plan': ('/foxglove/plan', 0.18),
            '/local_plan': ('/foxglove/local_plan', 0.18),
            '/received_global_plan': ('/foxglove/received_global_plan', 0.18),
            '/unsmoothed_plan': ('/foxglove/unsmoothed_plan', 0.18),
            '/omnifleet_t2/waypoints/path': ('/foxglove/omnifleet_t2/waypoints/path', 0.18),
        }
        for source, (target, _) in self.map_offsets.items():
            pub = self.create_publisher(OccupancyGrid, target, map_qos)
            self.create_subscription(OccupancyGrid, source, lambda msg, p=pub, s=source: self.on_map(msg, p, s), map_qos)
        for source, (target, _) in self.path_offsets.items():
            pub = self.create_publisher(Path, target, path_qos)
            self.create_subscription(Path, source, lambda msg, p=pub, s=source: self.on_path(msg, p, s), path_qos)

    def on_map(self, msg, pub, source):
        out = copy.deepcopy(msg)
        out.info.origin.position.z += self.map_offsets[source][1]
        pub.publish(out)

    def on_path(self, msg, pub, source):
        out = copy.deepcopy(msg)
        offset = self.path_offsets[source][1]
        for pose in out.poses:
            pose.pose.position.z += offset
        pub.publish(out)


def main():
    rclpy.init()
    node = FoxgloveLayerOffset()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
