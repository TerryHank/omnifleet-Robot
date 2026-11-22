#!/usr/bin/env python3
"""Publish compact viewer clouds and serve read-only dashboard telemetry."""

import json
import math
import socket
import threading
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np
import rclpy
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Float32


CLOUDS = (
    ("/navigation/deskewed_points", "/visualization/web/deskewed_points", 20_000, 5),
    ("/visualization/slam_points_below_1m", "/visualization/web/slam_points_below_1m", 20_000, 1),
    ("/visualization/local_obstacle_points", "/visualization/web/local_obstacle_points", 12_000, 5),
)
POINT_TYPES = {
    PointField.INT8: "i1",
    PointField.UINT8: "u1",
    PointField.INT16: "i2",
    PointField.UINT16: "u2",
    PointField.INT32: "i4",
    PointField.UINT32: "u4",
    PointField.FLOAT32: "f4",
    PointField.FLOAT64: "f8",
}


def display_copy(cloud, limit):
    fields = {field.name: field for field in cloud.fields}
    names = ["x", "y", "z"]
    if "intensity" in fields:
        names.append("intensity")
    endian = ">" if cloud.is_bigendian else "<"
    source_type = np.dtype({
        "names": names,
        "formats": [endian + POINT_TYPES[fields[name].datatype] for name in names],
        "offsets": [fields[name].offset for name in names],
        "itemsize": cloud.point_step,
    })
    count = min(cloud.height * cloud.width, limit)
    packed = np.empty((count, len(names)), dtype="<f4")
    if count:
        points = np.ndarray(
            (cloud.height, cloud.width),
            dtype=source_type,
            buffer=cloud.data,
            strides=(cloud.row_step, cloud.point_step),
        )
        indices = np.linspace(0, cloud.height * cloud.width, count, endpoint=False, dtype=np.int64)
        sample = points[indices // cloud.width, indices % cloud.width]
        for index, name in enumerate(names):
            packed[:, index] = sample[name]
    step = len(names) * 4
    return PointCloud2(
        header=cloud.header,
        height=1,
        width=count,
        fields=[
            PointField(name=name, offset=index * 4, datatype=PointField.FLOAT32, count=1)
            for index, name in enumerate(names)
        ],
        is_bigendian=False,
        point_step=step,
        row_step=count * step,
        data=packed.tobytes(),
        is_dense=cloud.is_dense,
    )


class CloudSampler:
    def __init__(self, node, qos, source, target, limit, hz):
        self.node = node
        self.limit = limit
        self.latest = None
        self.reported_invalid = False
        self.publisher = node.create_publisher(PointCloud2, target, qos)
        self.subscription = node.create_subscription(PointCloud2, source, self.receive, qos)
        self.timer = node.create_timer(1.0 / hz, self.publish_latest)

    def receive(self, cloud):
        self.latest = cloud

    def publish_latest(self):
        cloud, self.latest = self.latest, None
        if cloud is None:
            return
        try:
            self.publisher.publish(display_copy(cloud, self.limit))
        except (ValueError, TypeError, KeyError) as error:
            if not self.reported_invalid:
                self.node.get_logger().warning(f"Display cloud {self.publisher.topic_name}: {error}")
                self.reported_invalid = True


class Telemetry:
    def __init__(self):
        self.condition = threading.Condition()
        self.latest = {}
        self.version = 0

    def publish(self, event, sample):
        payload = f"event: {event}\ndata: {json.dumps(sample, separators=(',', ':'))}\n\n".encode()
        with self.condition:
            self.version += 1
            self.latest[event] = (self.version, payload)
            self.condition.notify_all()

    def speed(self, odom):
        linear = odom.twist.twist.linear.x
        if math.isfinite(linear):
            stamp = odom.header.stamp
            self.publish("speed", {"value": linear, "stamp": {"sec": stamp.sec, "nanosec": stamp.nanosec}})

    def voltage(self, message):
        if math.isfinite(message.data):
            self.publish("voltage", {"value": message.data})


class TelemetryHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, telemetry, **kwargs):
        self.telemetry = telemetry
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path != "/telemetry":
            self.send_error(404)
            return
        origin = self.headers.get("Origin")
        host = self.headers.get("Host", "").rsplit(":", 1)[0]
        if origin and origin != f"http://{host}":
            self.send_error(403)
            return
        self.connection.settimeout(2.0)
        self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.send_response(200)
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()

        version = -1
        try:
            while True:
                with self.telemetry.condition:
                    self.telemetry.condition.wait_for(lambda: version != self.telemetry.version, timeout=3)
                    messages = [payload for number, payload in self.telemetry.latest.values() if number > version]
                    version = self.telemetry.version
                self.wfile.write(b"".join(messages) if messages else b": keepalive\n\n")
        except OSError:
            return


def main():
    rclpy.init()
    node = Node("omnifleet_web_display")
    qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)
    samplers = [CloudSampler(node, qos, *specification) for specification in CLOUDS]
    telemetry = Telemetry()
    node.create_subscription(Odometry, "/odom", telemetry.speed, qos)
    node.create_subscription(Float32, "/voltage", telemetry.voltage, qos)
    handler = partial(TelemetryHandler, telemetry=telemetry)
    with ThreadingHTTPServer(("0.0.0.0", 8767), handler) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            rclpy.spin(node)
        except (KeyboardInterrupt, ExternalShutdownException):
            pass
        finally:
            server.shutdown()
            node.destroy_node()
            if rclpy.ok():
                rclpy.shutdown()


if __name__ == "__main__":
    main()
