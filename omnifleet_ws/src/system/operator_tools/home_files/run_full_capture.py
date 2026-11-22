import subprocess
import os
import sys
import time
import json
import signal
import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Empty, String
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry

root = "/home/iecme/mola_latest_20260917_ws/reports/gicp_full_capture_20260917_120622"
bag_root = os.path.join(root, "bag")
os.makedirs(bag_root, exist_ok=True)

print("======================================================================")
print("[Full Capture] Starting Mission Orchestrator")
print("======================================================================")

# 1. Start bag recording subprocess
rec_cmd = ["/home/iecme/omnifleet_a2_ws/src/system/operator_tools/home_files/record_gicp_mapping_bag.sh"]
env = os.environ.copy()
env["GICP_BAG_DIR"] = bag_root

print("[Full Capture] Launching recording script...")
proc_rec = subprocess.Popen(rec_cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# Wait for bag to initialize
bag_dir = None
for _ in range(15):
    time.sleep(1.0)
    subdirs = [os.path.join(bag_root, d) for d in os.listdir(bag_root) if os.path.isdir(os.path.join(bag_root, d))]
    if subdirs:
        bag_dir = subdirs[0]
        db3_files = [f for f in os.listdir(bag_dir) if f.endswith(".db3")]
        if db3_files:
            print(f"[Full Capture] Bag active: {bag_dir}")
            break

if not bag_dir:
    print("ERROR: Bag directory was not initialized within 15s!")
    proc_rec.terminate()
    sys.exit(1)

# 2. Initial static hold for 8 seconds
print("[Full Capture] Initial static recording: holding for 8 seconds...")
time.sleep(8.0)

# 3. Initialize ROS node to command and monitor
rclpy.init()
node = Node("full_capture_orchestrator")
pub_start = node.create_publisher(Empty, "/omnifleet_t2/waypoints/start", 10)
pub_stop = node.create_publisher(Empty, "/omnifleet_t2/waypoints/stop", 10)

wp_status_list = []
def wp_status_cb(msg):
    wp_status_list.append((time.time(), msg.data))
sub_wp_status = node.create_subscription(String, "/omnifleet_t2/waypoints/status", wp_status_cb, 10)

odom_speeds = []
def odom_cb(msg):
    vx = msg.twist.twist.linear.x
    wz = msg.twist.twist.angular.z
    odom_speeds.append((time.time(), vx, wz))
sub_odom = node.create_subscription(Odometry, "/odom", odom_cb, 10)

# Start motion
motion_start_time = time.time()
print(f"[Full Capture] Sending START command at {time.strftime('%H:%M:%S', time.localtime(motion_start_time))}...")
for _ in range(3):
    pub_start.publish(Empty())
    time.sleep(0.1)

# 4. Monitoring loop
monitor_log = []
max_linear_cmd = 0.0
max_angular_cmd = 0.0
consecutive_high_tf = 0
abort_triggered = False
abort_reason = ""
route_completed = False

status_file = "/home/iecme/.local/share/omnifleet_t2/navigation-stack/status.json"

start_loop = time.time()
max_mission_duration = 180.0 # 3 minutes maximum timeout

print("[Full Capture] Monitoring vehicle navigation...")

while time.time() - start_loop < max_mission_duration:
    rclpy.spin_once(node, timeout_sec=0.5)
    now = time.time()

    # Read status.json for live TF age and localization state
    tf_age = -1.0
    loc_status = ""
    if os.path.exists(status_file):
        try:
            with open(status_file) as f:
                st_data = json.load(f)
                tf_age = st_data.get("tf_age_ms", -1.0)
                loc_status = st_data.get("localization_status", "")
        except Exception:
            pass

    # Read latest waypoint status
    latest_wp = wp_status_list[-1][1] if wp_status_list else ""
    
    # Read latest speed
    cur_vx, cur_wz = (odom_speeds[-1][1], odom_speeds[-1][2]) if odom_speeds else (0.0, 0.0)
    if abs(cur_vx) > max_linear_cmd: max_linear_cmd = abs(cur_vx)
    if abs(cur_wz) > max_angular_cmd: max_angular_cmd = abs(cur_wz)

    record_entry = {
        "time": now,
        "elapsed": now - motion_start_time,
        "tf_age_ms": tf_age,
        "loc_status": loc_status,
        "wp_status": latest_wp,
        "vx": cur_vx,
        "wz": cur_wz
    }
    monitor_log.append(record_entry)

    # Check for completion
    if "已完成" in latest_wp or "完成整条路线" in latest_wp or "到达最终航点" in latest_wp:
        print(f"[Full Capture] Route completed successfully! ({latest_wp})")
        route_completed = True
        break

    # Safety checks
    if tf_age >= 300.0:
        print(f"[Full Capture][WARN] High TF age: {tf_age:.1f} ms")
    if tf_age >= 350.0:
        consecutive_high_tf += 1
    else:
        consecutive_high_tf = 0

    if tf_age >= 400.0 or consecutive_high_tf >= 2:
        abort_triggered = True
        abort_reason = f"TF age threshold exceeded (tf_age={tf_age:.1f} ms, consecutive={consecutive_high_tf})"
        print(f"[Full Capture][ABORT] {abort_reason}")
        break

    if "失败" in latest_wp or "中止" in latest_wp or "error" in latest_wp.lower():
        abort_triggered = True
        abort_reason = f"Waypoint navigation reported error: {latest_wp}"
        print(f"[Full Capture][ABORT] {abort_reason}")
        break

# Stop vehicle
print("[Full Capture] Sending STOP command...")
for _ in range(5):
    pub_stop.publish(Empty())
    time.sleep(0.1)

# Spin to process stop
t_stop_wait = time.time()
while time.time() - t_stop_wait < 3.0:
    rclpy.spin_once(node, timeout_sec=0.2)

motion_end_time = time.time()
print(f"[Full Capture] Motion phase ended at {time.strftime('%H:%M:%S', time.localtime(motion_end_time))}.")

# 5. Final static hold for 8 seconds
print("[Full Capture] Final static recording: holding for 8 seconds...")
time.sleep(8.0)

# 6. Stop bag recording cleanly via SIGINT
print("[Full Capture] Stopping rosbag recording (sending SIGINT)...")
proc_rec.send_signal(signal.SIGINT)
try:
    stdout_rec, _ = proc_rec.communicate(timeout=15)
    print(stdout_rec)
except Exception as e:
    print("Recording communicate timeout, killing...")
    proc_rec.terminate()

node.destroy_node()
rclpy.shutdown()

# Save monitor log
mon_path = os.path.join(root, "results", "motion_health_monitor.json")
with open(mon_path, "w") as f:
    json.dump({
        "motion_start_epoch": motion_start_time,
        "motion_end_epoch": motion_end_time,
        "motion_duration_s": motion_end_time - motion_start_time,
        "max_linear_speed_mps": max_linear_cmd,
        "max_angular_speed_radps": max_angular_cmd,
        "route_completed": route_completed,
        "abort_triggered": abort_triggered,
        "abort_reason": abort_reason,
        "monitor_samples": monitor_log
    }, f, indent=2)
print("Saved:", mon_path)

