#!/usr/bin/env python3
"""Build a transient local OccupancyGrid from the live MOLA deskewed cloud.

This is an experiment-only navigation bridge: Native GICP remains the pose/map
source, while Nav2 receives a continuously refreshed 2-D grid and the original
Deskewed PointCloud2 for obstacle marking. No saved .mm map is read.
"""
import os
import math
import numpy as np
from collections import deque
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid, Odometry
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener
from tf2_ros import TransformException

def select_grid_points(msg, sensor_x, sensor_y, origin_x, origin_y, res, width, height):
    field_types = {1: 'i1', 2: 'u1', 3: 'i2', 4: 'u2', 5: 'i4', 6: 'u4', 7: 'f4', 8: 'f8'}
    fields = {f.name: f for f in msg.fields}
    endian = '>' if msg.is_bigendian else '<'
    dtype = np.dtype({'names': ['x', 'y', 'z'],
                      'formats': [endian + field_types[fields[k].datatype] for k in ('x', 'y', 'z')],
                      'offsets': [fields[k].offset for k in ('x', 'y', 'z')],
                      'itemsize': msg.point_step})
    cloud = np.ndarray((msg.height, msg.width), dtype=dtype, buffer=msg.data,
                       strides=(msg.row_step, msg.point_step))
    x, y, z = [cloud[k].ravel().astype(np.float64) for k in ('x', 'y', 'z')]
    finite = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
    x, y, z = x[finite], y[finite], z[finite]
    dx, dy = x - sensor_x, y - sensor_y
    distance = np.hypot(dx, dy)
    # Keep libm's original decision at range boundaries.
    boundary = np.any(np.abs(distance[:, None] - np.array([.12, 6., 8.])) < 1e-12, axis=1)
    for i in np.flatnonzero(boundary):
        distance[i] = math.hypot(float(dx[i]), float(dy[i]))
    valid = (distance >= .12) & (distance <= 8.)
    x, y, z, dx, dy, distance = [a[valid] for a in (x, y, z, dx, dy, distance)]
    cx = np.floor((x - origin_x) / res).astype(np.int64)
    cy = np.floor((y - origin_y) / res).astype(np.int64)
    valid = (cx >= 0) & (cx < width) & (cy >= 0) & (cy < height)
    z, dx, dy, distance, cx, cy = [a[valid] for a in (z, dx, dy, distance, cx, cy)]
    angles = (np.arctan2(dy, dx) + math.pi) * 180. / math.pi
    boundary = np.abs(angles - np.rint(angles)) < 1e-10
    for i in np.flatnonzero(boundary):
        angles[i] = (math.atan2(float(dy[i]), float(dx[i])) + math.pi) * 180. / math.pi
    bins = angles.astype(np.int64)
    hits = (z >= -.03) & (z <= .5) & (distance <= 6.)

    def select(mask, farthest):
        indices = np.flatnonzero(mask)
        signed = -distance[indices] if farthest else distance[indices]
        order = indices[np.lexsort((indices, signed, bins[indices]))]
        first = np.r_[True, bins[order[1:]] != bins[order[:-1]]] if len(order) else np.array([], dtype=bool)
        starts = np.flatnonzero(first)
        ends = np.r_[starts[1:], len(order)]
        result = {}
        for start, end in zip(starts, ends):
            group = order[start:end]
            i = group[0]
            # Recheck ties with the scalar implementation; retain the first
            # input point on equality, as the original dictionaries did.
            tied = group[np.abs(distance[group] - distance[i]) < 1e-12]
            chosen = min(tied, key=lambda j: ((-1 if farthest else 1) * math.hypot(float(dx[j]), float(dy[j])), j))
            result[int(bins[i])] = (int(cx[chosen]), int(cy[chosen]))
        return result

    # A return above or below the obstacle band cannot prove that a low
    # obstacle disappeared. Clear only toward the nearest return in the band.
    clearing = (z >= -.03) & (z <= .5)
    rays = select(clearing, False)
    occupied = np.unique(cy[hits] * width + cx[hits])
    return list(rays.values()), occupied


class RealtimeNavGrid(Node):
    def __init__(self):
        super().__init__('mola_realtime_nav_grid')
        robot = os.environ.get('OMNIFLEET_ROBOT_ID', 'robot_113')
        self.topic = f'/map'
        self.frame = f'map'
        self.res = 0.10
        self.width = 500
        self.height = 500
        self.origin_x = -25.0
        self.origin_y = -25.0
        self.grid = [-1] * (self.width * self.height)
        self.sensor_frame = f'rslidar'
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.pending_clouds = deque(maxlen=3)
        self.pose_x = 0.0
        self.pose_y = 0.0
        self.have_pose = False
        qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.RELIABLE,
                         durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.pub = self.create_publisher(OccupancyGrid, self.topic, qos)
        cloud_qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.sub = self.create_subscription(
            PointCloud2, f'/navigation/deskewed_points', self.cloud_cb, cloud_qos)
        self.pose_sub = self.create_subscription(
            Odometry, f'/lidar_odometry/pose', self.pose_cb, 10)
        self.update_timer = self.create_timer(0.05, self.process_pending)
        self.timer = self.create_timer(1.0, self.publish_grid)
        self.last_points = 0
        self.publish_grid()
        self.get_logger().info(f'publishing realtime grid {self.topic} from deskewed MOLA cloud')

    def cloud_cb(self, msg):
        self.pending_clouds.append(msg)

    def pose_cb(self, msg):
        frame_id = msg.header.frame_id.lstrip('/')
        if frame_id != self.frame:
            return
        self.pose_x = float(msg.pose.pose.position.x)
        self.pose_y = float(msg.pose.pose.position.y)
        self.have_pose = True

    def process_pending(self):
        if not self.pending_clouds:
            return
        msg = self.pending_clouds[0]
        frame_id = msg.header.frame_id.lstrip('/')
        if frame_id not in (self.frame, self.sensor_frame):
            self.pending_clouds.popleft()
            return
        if frame_id == self.frame:
            # MOLA's deskewed output is already expressed in map coordinates.
            # The old code nevertheless required a map->rslidar TF at the
            # sensor timestamp; that frame is not published in this setup, so
            # every cloud was silently discarded and the grid stayed unknown.
            if not self.have_pose:
                return
            sensor_x, sensor_y = self.pose_x, self.pose_y
        else:
            try:
                tf = self.tf_buffer.lookup_transform(
                    self.frame, self.sensor_frame, Time.from_msg(msg.header.stamp))
            except TransformException:
                return
            sensor_x = tf.transform.translation.x
            sensor_y = tf.transform.translation.y
        self.pending_clouds.popleft()
        origin = self.cell(sensor_x, sensor_y)
        if origin is None:
            return
        updated = 0
        rays, occupied = select_grid_points(
            msg, sensor_x, sensor_y, self.origin_x, self.origin_y,
            self.res, self.width, self.height)
        for cell in rays:
            self.mark_free_ray(origin, cell)
        for idx in occupied:
            if self.grid[idx] != 100:
                self.grid[idx] = 100
                updated += 1
        self.last_points = updated
        # Keep point-cloud rasterization off the costmap publisher path.  The
        # 1 Hz timer below is the single publication cadence; publishing the
        # full 500x500 grid for every processed cloud caused redundant
        # serialization and competed with the navigation controller.

    def cell(self, x, y):
        ix = int(math.floor((x - self.origin_x) / self.res))
        iy = int(math.floor((y - self.origin_y) / self.res))
        return (ix, iy) if 0 <= ix < self.width and 0 <= iy < self.height else None

    def mark_free_ray(self, origin, end):
        x, y = origin
        end_x, end_y = end
        dx, dy = abs(end_x - x), abs(end_y - y)
        step_x = 1 if x < end_x else -1
        step_y = 1 if y < end_y else -1
        error = dx - dy
        while True:
            idx = y * self.width + x
            # A current ray observation clears stale dynamic occupancy.
            # Current-frame hit cells are restored to occupied below.
            self.grid[idx] = 0
            if x == end_x and y == end_y:
                break
            twice = 2 * error
            if twice > -dy:
                error -= dy
                x += step_x
            if twice < dx:
                error += dx
                y += step_y

    def publish_grid(self):
        msg = OccupancyGrid()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame
        msg.info.resolution = self.res
        msg.info.width = self.width
        msg.info.height = self.height
        msg.info.origin.position.x = self.origin_x
        msg.info.origin.position.y = self.origin_y
        msg.info.origin.orientation.w = 1.0
        msg.data = self.grid
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = RealtimeNavGrid()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
