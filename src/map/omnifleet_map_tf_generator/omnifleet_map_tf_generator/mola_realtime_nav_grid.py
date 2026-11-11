#!/usr/bin/env python3
"""Build a transient local OccupancyGrid from the live MOLA deskewed cloud.

This is an experiment-only navigation bridge: Native GICP remains the pose/map
source, while Nav2 receives a continuously refreshed 2-D grid and the original
Deskewed PointCloud2 for obstacle marking. No saved .mm map is read.
"""
import os
import math
import json
from pathlib import Path
import numpy as np
from collections import deque
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from sensor_msgs.msg import PointCloud2
from std_srvs.srv import Trigger
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
    valid = (distance >= .12) & np.isfinite(distance)
    x, y, z, dx, dy, distance = [a[valid] for a in (x, y, z, dx, dy, distance)]
    band = (z >= -.03) & (z <= .5)
    hits = band & (distance <= 6.)
    cx = np.floor((x[hits] - origin_x) / res).astype(np.int64)
    cy = np.floor((y[hits] - origin_y) / res).astype(np.int64)
    inside = (cx >= 0) & (cx < width) & (cy >= 0) & (cy < height)
    occupied = np.unique(cy[inside] * width + cx[inside])

    # Retain every distinct raster ray. A one-degree bin can contain several
    # different cell paths; keeping only its nearest endpoint misses removals.
    rx, ry, ranges = dx[band], dy[band], distance[band]
    upper_x = np.nextafter(origin_x + width*res, origin_x)
    upper_y = np.nextafter(origin_y + height*res, origin_y)
    tx = np.divide(np.where(rx > 0, upper_x-sensor_x, origin_x-sensor_x), rx,
                   out=np.full_like(rx, np.inf), where=rx != 0)
    ty = np.divide(np.where(ry > 0, upper_y-sensor_y, origin_y-sensor_y), ry,
                   out=np.full_like(ry, np.inf), where=ry != 0)
    scale = np.minimum.reduce([np.ones_like(ranges), 8./ranges, tx, ty])
    cx = np.clip(np.floor((sensor_x+scale*rx-origin_x)/res).astype(np.int64), 0, width-1)
    cy = np.clip(np.floor((sensor_y+scale*ry-origin_y)/res).astype(np.int64), 0, height-1)
    endpoints = np.unique(cy*width+cx)
    return list(zip((endpoints % width).tolist(), (endpoints // width).tolist())), occupied


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
        boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        handoff = Path('/tmp') / f'omnifleet-nav-grid-handoff-{os.environ.get("ROS_DOMAIN_ID", "0")}-{boot}.json'
        if handoff.is_file():
            self.grid = json.loads(handoff.read_text())['data']
            handoff.unlink()
            self.get_logger().info(f'Restored live grid handoff: {self.grid.count(100)} occupied cells')
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
        self.create_service(Trigger, '/mola_realtime_nav_grid/clear', self.clear_grid)
        self.publish_grid()
        self.get_logger().info(f'publishing realtime grid {self.topic} from deskewed MOLA cloud; clearing all unique endpoint rays with current-hit occlusion')

    def clear_grid(self, request, response):
        occupied = self.grid.count(100)
        self.grid = [-1] * (self.width * self.height)
        self.pending_clouds.clear()
        self.have_pose = False
        self.last_points = 0
        self.publish_grid()
        response.success = True
        response.message = f'已清空当前二维导航栅格（原占用{occupied}格）；MOLA定位及已保存地图文件保留'
        return response

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
        self._current_occupied = set(occupied.tolist())
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
        occupied = getattr(self, '_current_occupied', ())
        while True:
            idx = y * self.width + x
            if idx in occupied or (x == end_x and y == end_y):
                break  # Foreground and return endpoints are not free-space evidence.
            # A current ray observation clears stale dynamic occupancy.
            # Current-frame hit cells are restored to occupied below.
            self.grid[idx] = 0
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

