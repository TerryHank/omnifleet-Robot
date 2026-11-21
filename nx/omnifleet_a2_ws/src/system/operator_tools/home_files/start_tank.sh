#!/bin/bash
# === IECME Tank Airy GLIM + Nav2 启动脚本 ===
set -e

CFG=/home/iecme/文档/omnifleet_preserved_projects/ros2humble_ws/src/rrc_slam_bringup/config/glim_cuda
NAV=/home/iecme/文档/omnifleet_preserved_projects/ros2humble_ws/src/rrc_slam_bringup/config/nav2_glim.yaml

echo "=== Step 1: 配置修复 ==="

# CT odometry model (bypass GTSAM crash)
sed -i 's/"config_odometry": "config_odometry_gpu.json"/"config_odometry": "config_odometry_ct.json"/' $CFG/config.json

# Disable IMU in sub/global mapping
sed -i 's/"enable_imu": true/"enable_imu": false/' $CFG/config_sub_mapping_gpu.json $CFG/config_global_mapping_gpu.json 2>/dev/null

# NAIVE init (no IMU needed)
sed -i 's/"initialization_mode": "LOOSE"/"initialization_mode": "NAIVE"/' $CFG/config_odometry_ct.json 2>/dev/null

# TF tolerance
sed -i 's/transform_tolerance: 0.2/transform_tolerance: 2.0/' $NAV

# Deadband to zero
sed -i 's/deadband_velocity: \[1.0, 0.0, 0.5\]/deadband_velocity: [0.0, 0.0, 0.0]/' $NAV 2>/dev/null

echo "=== Step 2: 编译 ==="
source /opt/ros/humble/setup.bash
cd /home/iecme/文档/omnifleet_preserved_projects/ros2humble_ws && colcon build --packages-select rrc_slam_bringup 2>&1 | tail -1

echo "=== Step 3: 清理旧数据 ==="
rm -rf ~/robot_maps/glim_cuda/airy_active

echo "=== Step 4: 创建简单 BT ==="
cat > /tmp/simple_bt.xml << 'BTEOF'
<root main_tree_to_execute="MainTree">
  <BehaviorTree ID="MainTree">
    <PipelineSequence>
      <ComputePathToPose goal="{goal}" path="{path}" planner_id="GridBased"/>
      <FollowPath path="{path}" controller_id="FollowPath"/>
    </PipelineSequence>
  </BehaviorTree>
</root>
BTEOF

echo "=== Step 5: 启动 GLIM ==="
source /home/iecme/文档/omnifleet_preserved_projects/slam_overlays/glim_cuda_ws/install/setup.bash
source /home/iecme/文档/omnifleet_preserved_projects/ros2humble_ws/install/setup.bash
ros2 launch rrc_slam_bringup glim_cuda.launch.py operation:=mapping map_id:=airy_active &

# Wait for startup
echo "等待 GLIM 启动 (60s)..."
for i in $(seq 1 30); do
  source /opt/ros/humble/setup.bash
  ros2 node list 2>/dev/null | grep -q glim_ros && break
  sleep 2
done

echo "=== Step 6: 激活 Nav2 ==="
source /opt/ros/humble/setup.bash
for n in bt_navigator planner_server controller_server behavior_server smoother_server velocity_smoother waypoint_follower collision_monitor; do
  ros2 lifecycle set /$n activate 2>/dev/null
done
sleep 3

echo "=== Step 7: 设置简单 BT ==="
ros2 param set /bt_navigator default_nav_to_pose_bt_xml /tmp/simple_bt.xml 2>/dev/null

echo "=== 就绪！现在可以发航点 ==="
echo "ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose '{pose: {header: {frame_id: map}, pose: {position: {x: 0.5, y: 0.2}, orientation: {w: 1.0}}}}'"
