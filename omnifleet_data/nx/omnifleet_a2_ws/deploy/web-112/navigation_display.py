"""Bandwidth-limited Foxglove copies of the live maps and deskewed cloud."""

from array import array
from copy import deepcopy
import math
import time

import numpy as np
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import PointCloud2
from rclpy.qos import DurabilityPolicy, QoSProfile, qos_profile_sensor_data


DISPLAY_MAP = '/visualization/foxglove_map'
DISPLAY_GLOBAL_COSTMAP = '/visualization/foxglove_global_costmap'
DISPLAY_CLOUD = '/visualization/foxglove_deskewed_points'


def cropped_grid(message):
    info = deepcopy(message.info)
    grid = np.asarray(message.data, dtype=np.int8).reshape(info.height, info.width)
    rows = np.flatnonzero(np.any(grid != -1, axis=1))
    cols = np.flatnonzero(np.any(grid != -1, axis=0))
    if rows.size and cols.size:
        y0, y1 = max(0, int(rows[0])-2), min(info.height, int(rows[-1])+3)
        x0, x1 = max(0, int(cols[0])-2), min(info.width, int(cols[-1])+3)
    else:
        y0, y1, x0, x1 = 0, 1, 0, 1
    q = info.origin.orientation
    yaw = math.atan2(2*(q.w*q.z+q.x*q.y), 1-2*(q.y*q.y+q.z*q.z))
    pos = info.origin.position
    pos.x += info.resolution*(x0*math.cos(yaw)-y0*math.sin(yaw))
    pos.y += info.resolution*(x0*math.sin(yaw)+y0*math.cos(yaw))
    info.width = x1-x0
    info.height = y1-y0
    return OccupancyGrid(header=message.header, info=info,
                         data=array('b', grid[y0:y1,x0:x1].tobytes()))


class NavigationDisplay:
    def __init__(self, node):
        grid_qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.map = node.create_publisher(OccupancyGrid, DISPLAY_MAP, grid_qos)
        self.costmap = node.create_publisher(OccupancyGrid, DISPLAY_GLOBAL_COSTMAP, grid_qos)
        self.cloud = node.create_publisher(PointCloud2, DISPLAY_CLOUD, qos_profile_sensor_data)
        self.last_cloud = 0.0
        node.create_subscription(OccupancyGrid, '/map',
                                 lambda msg: self.grid(msg,self.map), qos_profile_sensor_data)
        node.create_subscription(OccupancyGrid, '/global_costmap/costmap',
                                 lambda msg: self.grid(msg,self.costmap), qos_profile_sensor_data)
        node.create_subscription(PointCloud2, '/navigation/deskewed_points',
                                 self.sample_cloud, qos_profile_sensor_data)

    @staticmethod
    def grid(message, publisher):
        if message.info.width and message.info.height:
            publisher.publish(cropped_grid(message))

    def sample_cloud(self, message):
        now = time.monotonic()
        count = message.width * message.height
        if now-self.last_cloud < 1/3 or not count or not message.point_step:
            return
        self.last_cloud = now
        packed = np.ndarray((message.height,message.width,message.point_step), dtype=np.uint8,
                            buffer=message.data, strides=(message.row_step,message.point_step,1))
        indices = np.linspace(0,count-1,min(2400,count),dtype=np.intp)
        row,col = np.divmod(indices,message.width)
        data = packed[row,col].tobytes()
        self.cloud.publish(PointCloud2(header=message.header,height=1,width=len(indices),
            fields=message.fields,is_bigendian=message.is_bigendian,point_step=message.point_step,
            row_step=len(data),data=array('B',data),is_dense=message.is_dense))
