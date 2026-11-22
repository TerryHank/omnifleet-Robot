import rclpy
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
from PIL import Image
import sys, json, os, time

os.environ.setdefault('ROS_LOG_DIR', '/tmp/ros-logs')
os.makedirs('/tmp/ros-logs', exist_ok=True)

rclpy.init()
n = Node('grab_map')
qos = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=1,
    durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
)
got = []
def cb(m):
    got.append(m)
sub = n.create_subscription(OccupancyGrid, '/map', cb, qos)
deadline = time.time() + 20.0
while not got and time.time() < deadline and rclpy.ok():
    rclpy.spin_once(n, timeout_sec=0.2)
if not got:
    print('NO_MAP')
    sys.exit(2)
m = got[-1]
info = m.info
w, h = info.width, info.height
print(json.dumps({
    'frame_id': m.header.frame_id,
    'stamp': m.header.stamp.sec + m.header.stamp.nanosec * 1e-9,
    'width': w, 'height': h,
    'resolution': info.resolution,
    'origin_xy': [info.origin.position.x, info.origin.position.y],
}))
data = list(m.data)
img = Image.new('L', (w, h), 205)
px = img.load()
for i, v in enumerate(data):
    x = i % w
    y = h - 1 - (i // w)
    if v < 0:
        px[x, y] = 205
    elif v == 0:
        px[x, y] = 255
    else:
        px[x, y] = 0
img.save('/home/iecme/omnifleet_a2_ws/map_snapshot.png')
print('saved map_snapshot.png size', img.size)