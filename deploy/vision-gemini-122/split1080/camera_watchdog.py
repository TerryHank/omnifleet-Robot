"""End the camera launch when a Gemini Pro stream stops advancing."""

import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CameraInfo


def stale_streams(progress, started, now):
    return [
        name for name, seen in progress.items()
        if (seen is None and now - started > 18.0)
        or (seen is not None and now - seen > 8.0)
    ]


def main():
    rclpy.init()
    node = rclpy.create_node("gemini_pro_stream_watchdog")
    started = time.monotonic()
    progress = dict(color=None, depth=None)
    stamps = {}

    def observe(message, name):
        stamp = (message.header.stamp.sec, message.header.stamp.nanosec)
        if message.width > 0 and message.height > 0 and stamp != stamps.get(name):
            stamps[name] = stamp
            progress[name] = time.monotonic()

    for name in progress:
        node.create_subscription(CameraInfo, f"/camera/{name}/camera_info",
                                 lambda msg, stream=name: observe(msg, stream),
                                 qos_profile_sensor_data)
    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.25)
            stale = stale_streams(progress, started, time.monotonic())
            if stale:
                node.get_logger().error("Gemini Pro streams stopped advancing: " + ", ".join(stale))
                return 1
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
