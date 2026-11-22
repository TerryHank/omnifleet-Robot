#!/usr/bin/env python3
import json, struct, sys, time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2


class Capture(Node):
    def __init__(self, topic, output):
        super().__init__("mola_auto_cloud_capture")
        self.output, self.msg = output, None
        self.create_subscription(PointCloud2, topic, self.cb, 10)

    def cb(self, msg):
        if msg.width * msg.height:
            self.msg = msg


def main():
    if len(sys.argv) != 3:
        raise SystemExit("capture_cloud.py TOPIC OUTPUT.pcd")
    rclpy.init()
    node = Capture(sys.argv[1], sys.argv[2])
    deadline = time.monotonic() + 12.0
    while rclpy.ok() and node.msg is None and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.2)
    if node.msg is None:
        raise SystemExit("no nonempty pointcloud received")
    msg = node.msg
    fields = {f.name: (f.offset, f.datatype) for f in msg.fields}
    if not all(k in fields for k in ("x", "y", "z")):
        raise SystemExit("pointcloud has no xyz fields")

    def value(row, name):
        off, datatype = fields[name]
        fmt = {7: "f", 8: "d"}.get(datatype)
        if fmt is None:
            raise RuntimeError(f"unsupported PointCloud2 datatype {datatype}")
        return struct.unpack_from("<" + fmt, row, off)[0]

    points = []
    for i in range(0, len(msg.data), msg.point_step):
        row = msg.data[i : i + msg.point_step]
        xyz = (value(row, "x"), value(row, "y"), value(row, "z"))
        if all(v == v and abs(v) < 1e4 for v in xyz):
            points.append(xyz)
    with open(sys.argv[2], "w", encoding="ascii") as f:
        f.write("# .PCD v0.7 - Point Cloud Data file format\nVERSION 0.7\n")
        f.write("FIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1\n")
        f.write(f"WIDTH {len(points)}\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0\nPOINTS {len(points)}\nDATA ascii\n")
        for x, y, z in points:
            f.write(f"{x:.6f} {y:.6f} {z:.6f}\n")
    print(json.dumps({"topic": sys.argv[1], "points": len(points), "output": sys.argv[2]}), flush=True)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
