"""Publish bandwidth-limited display streams for the receiver."""

from array import array
from copy import deepcopy
import socket
import time

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import CompressedImage, PointCloud2


def thin_cloud(msg, byte_limit):
    """Sample complete point records, including any color and intensity fields."""
    width, height, step = msg.width, msg.height, msg.point_step
    count = width * height
    if count == 0:
        data = b""
    else:
        if (
            step == 0
            or step > byte_limit
            or msg.row_step < width * step
            or len(msg.data) < height * msg.row_step
        ):
            return None
        max_points = byte_limit // step
        stride = (count + max_points - 1) // max_points
        positions = np.arange(0, count, stride)
        records = np.ndarray(
            (height, width, step),
            dtype=np.uint8,
            buffer=memoryview(msg.data),
            strides=(msg.row_step, step, 1),
        )
        data = records[positions // width, positions % width].tobytes()
    return PointCloud2(
        header=msg.header,
        height=1,
        width=len(data) // step if step else 0,
        fields=msg.fields,
        is_bigendian=msg.is_bigendian,
        point_step=step,
        row_step=len(data),
        data=data,
        is_dense=msg.is_dense,
    )


# Limits apply to G20 display copies only. Each bulk slot can emit one sample.
GRID_BYTES = 24 * 1024
G20_SENDQ_BYTES = 32 * 1024
G20_ADDRESS_HEX = socket.inet_aton("192.168.144.11")[::-1].hex().upper()


def display_grid(msg, byte_limit=GRID_BYTES):
    """Preserve map coordinates; crop unknown margins and pool only oversized views."""
    width, height = msg.info.width, msg.info.height
    if not width or not height or len(msg.data) != width * height:
        return None
    source = np.frombuffer(msg.data, dtype=np.int8).reshape(height, width)
    known = source >= 0
    xs = np.flatnonzero(known.any(axis=0))
    ys = np.flatnonzero(known.any(axis=1))
    if xs.size:
        x, y = int(xs[0]), int(ys[0])
        cells = source[y:ys[-1]+1, x:xs[-1]+1]
    else:
        x = y = 0
        cells = source[:1, :1]
    h, w = cells.shape
    factor = 1
    while ((h + factor - 1) // factor) * ((w + factor - 1) // factor) > byte_limit:
        factor *= 2
    if factor > 1:
        padded = np.pad(cells, ((0, -h % factor), (0, -w % factor)),
                        constant_values=-1)
        blocks = padded.reshape(padded.shape[0] // factor, factor,
                                padded.shape[1] // factor, factor)
        cells = blocks.max(axis=(1, 3))
        # Show an obstacle even in a partly unknown block. Show free only if
        # every source cell in the block is known and free.
        cells[(cells == 0) & (blocks.min(axis=(1, 3)) < 0)] = -1
    info = deepcopy(msg.info)
    dx, dy = x * info.resolution, y * info.resolution
    q, pos = info.origin.orientation, info.origin.position
    pos.x += (1-2*(q.y*q.y+q.z*q.z))*dx + 2*(q.x*q.y-q.z*q.w)*dy
    pos.y += 2*(q.x*q.y+q.z*q.w)*dx + (1-2*(q.x*q.x+q.z*q.z))*dy
    pos.z += 2*(q.x*q.z-q.y*q.w)*dx + 2*(q.y*q.z+q.x*q.w)*dy
    info.height, info.width = cells.shape
    info.resolution *= factor
    payload = array("b")
    payload.frombytes(cells.tobytes())
    return OccupancyGrid(header=msg.header, info=info, data=payload)


def display_send_queue():
    """Largest unacknowledged/unsent byte count on the G20 display TCP connection."""
    largest = 0
    with open("/proc/net/tcp", encoding="ascii") as sockets:
        next(sockets)
        for line in sockets:
            fields = line.split()
            if (fields[3] == "01" and fields[1].endswith(":223D")
                    and fields[2].split(":")[0] == G20_ADDRESS_HEX):
                largest = max(largest, int(fields[4].split(":")[0], 16))
    return largest


class ReceiverDisplay(Node):
    def __init__(self):
        super().__init__("receiver_display_relay")
        self.camera = None
        self.follow_camera = None
        self.clouds = {}
        self.cloud_publishers = {}
        self.grids = {}
        self.sent_grids = {}
        self.grid_publishers = {}
        self.bulk_index = 0
        self.queue_checked = float("-inf")
        self.send_queue = 0
        sensor_qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.camera_pub = self.create_publisher(
            CompressedImage, "/camera/color/receiver_display/compressed", 1
        )
        self.follow_camera_pub = self.create_publisher(
            CompressedImage, "/camera/color/receiver_follow/compressed", 1
        )
        self.create_subscription(
            CompressedImage,
            "/camera/color/image_raw/compressed",
            self.on_camera,
            1,
        )
        for source, output, size in (
            ("slam_points_below_1m", "receiver_slam_points_1hz", 24 * 1024),
            ("local_obstacle_points", "receiver_obstacle_points_1hz", 12 * 1024),
        ):
            self.cloud_publishers[source] = (
                self.create_publisher(PointCloud2, f"/visualization/{output}", 1),
                size,
            )
            self.create_subscription(
                PointCloud2,
                f"/visualization/{source}",
                lambda msg, name=source: self.on_cloud(name, msg),
                sensor_qos,
            )
        self.create_timer(1.0 / 12, lambda: self.publish_camera(
            "camera", self.camera_pub, 480, 360, 16 * 1024, (55, 35)
        ))
        self.create_timer(1.0 / 18, lambda: self.publish_camera(
            "follow_camera", self.follow_camera_pub, 640, 480, 24 * 1024, (65, 55, 45, 35)
        ))
        grid_qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        for source, name in (
            ("/map", "map"),
            ("/global_costmap/costmap", "global_costmap"),
            ("/local_costmap/costmap", "local_costmap"),
        ):
            self.grid_publishers[name] = self.create_publisher(
                OccupancyGrid, f"/visualization/receiver_{name}", grid_qos
            )
            self.create_subscription(
                OccupancyGrid, source,
                lambda msg, name=name: self.grids.update({name: msg}),
                sensor_qos,
            )
        self.bulk_slots = ("map", "slam_points_below_1m", "global_costmap",
                           "local_obstacle_points", "local_costmap")
        self.create_timer(0.2, self.publish_bulk)

    def on_camera(self, msg):
        self.camera = self.follow_camera = msg

    def on_cloud(self, name, msg):
        self.clouds[name] = (time.monotonic(), msg)

    def display_busy(self):
        now = time.monotonic()
        if now - self.queue_checked >= 0.1:
            try:
                self.send_queue = display_send_queue()
            except OSError:
                # Size and slot limits still apply when procfs is unavailable.
                self.send_queue = 0
            self.queue_checked = now
        return self.send_queue >= G20_SENDQ_BYTES

    def publish_bulk(self):
        if self.display_busy():
            return
        name = self.bulk_slots[self.bulk_index]
        self.bulk_index = (self.bulk_index + 1) % len(self.bulk_slots)
        if name in self.cloud_publishers:
            publisher, limit = self.cloud_publishers[name]
            item = self.clouds.pop(name, None)
            if item and publisher.get_subscription_count() and time.monotonic() - item[0] <= 2.5:
                frame = thin_cloud(item[1], limit)
                if frame is not None:
                    publisher.publish(frame)
            return
        publisher = self.grid_publishers[name]
        if not publisher.get_subscription_count():
            return
        msg = self.grids.pop(name, None)
        if msg is None:
            return
        frame = display_grid(msg)
        if frame is None:
            return
        previous = self.sent_grids.get(name)
        if (previous is not None and frame.header.frame_id == previous.header.frame_id
                and frame.info.width == previous.info.width and frame.info.height == previous.info.height
                and frame.info.resolution == previous.info.resolution
                and frame.info.origin == previous.info.origin and frame.data == previous.data):
            return
        publisher.publish(frame)
        self.sent_grids[name] = frame

    def publish_camera(self, slot, publisher, max_width, max_height, byte_limit, qualities):
        msg = getattr(self, slot)
        setattr(self, slot, None)
        if msg is None or publisher.get_subscription_count() == 0 or self.display_busy():
            return
        frame = cv2.imdecode(np.frombuffer(msg.data, dtype=np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            return
        height, width = frame.shape[:2]
        scale = min(1, max_width / width, max_height / height)
        if scale < 1:
            frame = cv2.resize(
                frame, (round(width * scale), round(height * scale)), interpolation=cv2.INTER_AREA
            )
        for quality in qualities:
            ok, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
            if ok and jpeg.nbytes <= byte_limit:
                publisher.publish(
                    CompressedImage(header=msg.header, format="jpeg", data=jpeg.tobytes())
                )
                break


def main():
    cv2.setNumThreads(1)
    rclpy.init()
    node = ReceiverDisplay()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
