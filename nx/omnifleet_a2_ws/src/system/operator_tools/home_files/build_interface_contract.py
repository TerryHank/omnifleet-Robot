#!/usr/bin/env python3
import json
from pathlib import Path


backup = Path(Path("/home/iecme/robot_backups/mola_before_latest_CURRENT").read_text().strip())
interface = backup / "interface"
environment = {}
for line in (backup / "runtime/environment.txt").read_text().splitlines():
    if "=" in line:
        key, value = line.split("=", 1)
        environment[key] = value

topics = {}
for line in (interface / "topics.txt").read_text().splitlines():
    if " [" not in line:
        continue
    topic, type_name = line.rsplit(" [", 1)
    topics[topic] = type_name.rstrip("]")

services = []
for line in (interface / "services.txt").read_text().splitlines():
    if any(token in line for token in ("mola", "map_load", "map_save", "relocalize")):
        services.append(line)

actions = []
for line in (interface / "actions.txt").read_text().splitlines():
    if "mola" in line.lower() or "localiz" in line.lower():
        actions.append(line)

contract = {
    "namespace": "",
    "ros_domain_id": environment.get("ROS_DOMAIN_ID"),
    "rmw_implementation": environment.get("RMW_IMPLEMENTATION"),
    "node": "/mola_bridge_ros2",
    "subscriptions": {
        "/rslidar_points": {
            "type": "sensor_msgs/msg/PointCloud2",
            "reliability": "BEST_EFFORT",
            "durability": "VOLATILE",
            "depth": 20,
        },
        "/omnifleet_t2/experiments/rslidar_imu_corrected": {
            "type": "sensor_msgs/msg/Imu",
            "reliability": "BEST_EFFORT",
            "durability": "VOLATILE",
            "depth": 1000,
        },
    },
    "publishers": {
        "/lidar_odometry/pose": {
            "type": "nav_msgs/msg/Odometry",
            "reliability": "RELIABLE",
            "durability": "VOLATILE",
            "depth": 42,
        },
        "/lidar_odometry/pose_quality": {
            "type": "std_msgs/msg/Float32",
        },
        "/lidar_odometry/nav_odom": {
            "type": "nav_msgs/msg/Odometry",
        },
        "/lidar_odometry/localmap_points": {
            "type": "sensor_msgs/msg/PointCloud2",
        },
        "/lidar_odometry/nav_voxelmap_points": {
            "type": "sensor_msgs/msg/PointCloud2",
        },
        "/map": {
            "type": "nav_msgs/msg/OccupancyGrid",
            "reliability": "RELIABLE",
            "durability": "TRANSIENT_LOCAL",
            "depth": 1,
        },
        "/tf": {
            "type": "tf2_msgs/msg/TFMessage",
            "reliability": "RELIABLE",
            "durability": "VOLATILE",
            "depth": 100,
        },
    },
    "frames": {
        "reference": environment.get("MOLA_TF_MAP"),
        "vehicle": environment.get("MOLA_TF_BASE_LINK"),
        "odom": environment.get("MOLA_TF_ESTIMATED_ODOMETRY"),
        "lidar": "rslidar",
        "tf_mode": "simple_direct",
        "required_tf": "map -> base_link",
        "rep105": environment.get("MOLA_LOCALIZ_USE_REP105") == "True",
    },
    "timestamp": {
        "use_sim_time": False,
        "publish_original_sensor_time": environment.get("MOLA_ROS2_PUBLISH_IN_SIM_TIME") == "true",
        "transform_tolerance_seconds": float(environment.get("MOLA_ROS2_TRANSFORM_TOLERANCE", "0")),
        "semantic": "LiDAR acquisition timestamp preserved through pose and TF; no wall-clock restamp",
    },
    "configured_rates": {
        "lidar_input_hz": 10.0,
        "bridge_execution_hz": 20.0,
        "tf_rebroadcast_hz": 20.0,
        "map_check_hz": 2.0,
    },
    "services": services,
    "actions": actions,
    "all_mola_topics_seen": {
        key: value for key, value in sorted(topics.items())
        if any(token in key for token in ("lidar_odometry", "/map", "mola_"))
    },
    "raw_evidence": {
        "nodes": "interface/nodes.txt",
        "topics": "interface/topics.txt",
        "services": "interface/services.txt",
        "actions": "interface/actions.txt",
        "node_info": "interface/node__robot_113_mola_bridge_ros2.txt",
    },
}

(backup / "MOLA_NAV_INTERFACE_CONTRACT.json").write_text(
    json.dumps(contract, indent=2), encoding="utf-8"
)

lines = [
    "# MOLA NAV INTERFACE CONTRACT",
    "",
    "This contract was captured from the running original MOLA process and ROS graph.",
    "",
    f"- Namespace: `{contract['namespace']}`",
    f"- ROS_DOMAIN_ID: `{contract['ros_domain_id']}`",
    f"- RMW: `{contract['rmw_implementation']}`",
    f"- TF: `{contract['frames']['required_tf']}`",
    f"- TF mode: `{contract['frames']['tf_mode']}`",
    f"- Timestamp: {contract['timestamp']['semantic']}",
    "",
    "## Required publishers",
    "",
]
for topic, details in contract["publishers"].items():
    qos = ", ".join(
        str(details[key]) for key in ("reliability", "durability", "depth")
        if key in details
    )
    lines.append(f"- `{topic}` `{details['type']}` {qos}".rstrip())
lines += ["", "## Required sensor subscriptions", ""]
for topic, details in contract["subscriptions"].items():
    lines.append(
        f"- `{topic}` `{details['type']}` {details['reliability']} depth={details['depth']}"
    )
lines += [
    "",
    "The latest MOLA must satisfy this contract without Nav2 changes.",
]
(backup / "MOLA_NAV_INTERFACE_CONTRACT.md").write_text(
    "\n".join(lines) + "\n", encoding="utf-8"
)
print(backup)
