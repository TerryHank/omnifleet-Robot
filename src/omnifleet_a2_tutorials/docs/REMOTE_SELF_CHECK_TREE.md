# 远端阿克曼小车自查树与单变量隔离体系

适用主机：`iecme@192.168.3.112`。适用主链：Airy、GLIM、2D/2.5D
地图、Nav2、STM32 阿克曼底盘。相机是可选支线，不纳入主链通过条件。

## 1. 不可违反的架构合同

```text
Airy PointCloud2 + IMU
        ↓
GLIM（唯一动态位姿源）
├── map → odom → base_link
├── /odom
├── /glim_ros/points_corrected
└── /glim_ros/map
        │
        ├── /rslidar_points → Nav2官方ObstacleLayer → Local Costmap
        └── /map + 可选/omnifleet_a2/terrain/costmap → Global Costmap
                                             ↓
                    Smac Hybrid → MPPI Ackermann
                                             ↓
Nav2 Controller / Behavior → /cmd_vel
                                             ↓
NX串口直传 → STM32：通信看门狗、v/w逆解、舵角与电机闭环
```

强制规则：

1. 不启用 EKF、AMCL、slam_toolbox 或第二套 LIO。
2. GLIM 独占 `map→odom` 和 `odom→base_link`。
3. NX 不做执行层阿克曼逆解；STM32 是运动学唯一所有者。
4. `terrain_mode` 与 `local_obstacle_mode` 相互独立，只能冷切换。
5. MVS 相机缺失不能判定主导航链失败。
6. 不以“节点名或话题名存在”作为通过证据，必须收到实际消息或查询到实际状态。

## 2. 标准环境和只读体检

每次排查先进入同一环境：

```bash
ssh iecme@192.168.3.112
set -a
source /etc/rrc/robot.env
set +a
source /opt/ros/humble/setup.bash
source /home/iecme/omnifleet_a2_ws/install/setup.bash
```

基础硬件体检，不要求 GLIM/Nav2 已启动：

```bash
ros2 run omnifleet_a2_bringup robot_doctor --scope base
```

GLIM、TF 和地图体检：

```bash
ros2 run omnifleet_a2_bringup robot_doctor --scope slam
```

按当前冷启动模式检查完整导航链：

```bash
# 默认生产模式
ros2 run omnifleet_a2_bringup robot_doctor --scope nav \
  --terrain-mode 2d --local-obstacle-mode obstacle

# 例：2.5D + STVL
ros2 run omnifleet_a2_bringup robot_doctor --scope nav \
  --terrain-mode 2_5d --local-obstacle-mode stvl
```

`robot_doctor`是只读工具：不启动/停止服务、不发布速度、不发送目标、不切换
Lifecycle。它按首个失败项给出最小故障单元。

## 3. 总自查树

固定按“执行层到算法层”的顺序检查：

```text
单点导航异常
│
├─ 1. 唯一控制器发布的/cmd_vel能驱动底盘吗？
│    ├─ 否 → STM32串口、驱动、固件、舵机/电机
│    └─ 是
│
├─ 2. Nav2目标期间/cmd_vel有非零输出吗？
│    ├─ 无 → Controller、局部代价地图、TF或路径输入
│    └─ 有但反馈无 → STM32链
│
├─ 3. Controller处于active且收到全局路径吗？
│    ├─ 否 → MPPI、odom、Local Costmap、goal checker
│    └─ 是
│
├─ 4. Local Costmap是否把自车或空地标成障碍？
│    ├─ 是 → 点云预处理、TF、clearing、所选障碍层
│    └─ 否
│
├─ 5. Planner能否产生Smac Hybrid路径？
│    ├─ 否 → 起终点、Global Costmap、转弯半径、REEDS_SHEPP
│    └─ 是
│
├─ 6. /map和Global Costmap有效吗？
│    ├─ 2D失败 → GLIM地图投影、StaticLayer
│    ├─ 仅2.5D失败 → terrain_mapper、/omnifleet_a2/terrain/costmap、TraversabilityLayer
│    └─ 正常
│
├─ 7. map→odom→base_link与/odom连续吗？
│    ├─ 否 → GLIM、时间戳、外参、TF所有权
│    └─ 是
│
└─ 8. Airy点云/IMU是否持续到达？
     ├─ 否 → RoboSense Airy服务、网络、设备、电源
     └─ 是 → 重新检查首个出现异常的上层边界
```

## 4. 每层的检查、替代与最小结论

### 4.1 底盘执行层

先运行：

```bash
systemctl is-active omnifleet-a2-chassis.service
readlink -f /dev/myserial
ros2 topic info /cmd_vel -v
ros2 topic echo /omnifleet_a2/chassis/velocity_raw --once
journalctl -u omnifleet-a2-chassis.service -n 80 --no-pager
```

正常判据：

- `/dev/myserial`解析到真实`ttyUSB*`；
- `/cmd_vel`发布者只允许当前启动的Nav2 Controller/Behavior，订阅者包含底盘驱动；
- `/omnifleet_a2/chassis/velocity_raw`持续返回速度、实际舵角和角速度；
- 日志中 TX 为 `FUNC_MOTION Vx=... Vy=0 Vz=... kinematics_owner=stm32`；
- RX校验/接收错误不持续增加。

已知正常替代物：架空车、人在现场并准备急停时，直接向`/cmd_vel`发测试命令；
停发后由STM32通信看门狗制动：

```bash
timeout 2 ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.08}, angular: {z: 0.15}}"
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

替换后能执行：Nav2以上不是本层故障。替换后仍不能执行：最小故障单元位于
`底盘驱动 → 串口 → STM32 → 执行器`。修复后必须用
同一条低速命令回装复测，并确认最后反馈回零。

### 4.2 Nav2到底盘直连链

在同一个目标执行期间分别观察：

```bash
ros2 topic echo /cmd_vel
ros2 topic info /cmd_vel -v
ros2 topic echo /omnifleet_a2/chassis/velocity_raw
```

定位规则：

| 最后一个有非零值的话题 | 最小故障单元 |
|---|---|
| `/cmd_vel`没有非零值 | Controller、局部代价地图、TF或路径输入 |
| `/cmd_vel` | STM32驱动/固件/执行器 |

先确认`/cmd_vel`没有意外的第三方发布者，再沿唯一的直连边界排查。

### 4.3 Controller与里程计

```bash
ros2 lifecycle get /controller_server
ros2 topic echo /plan --once
ros2 topic echo /odom --once
ros2 topic echo /local_costmap/costmap --once \
  --qos-durability transient_local
ros2 param get /controller_server FollowPath.motion_model
```

正常判据：Controller为`active`，有全局路径、连续`/odom`和非空Local Costmap，
MPPI使用Ackermann运动模型。

已知正常替代物：保持地图、定位和目标不变，只将目标换成车头前方、满足最小转弯
半径的近距离自由点。如果近目标能输出速度而原目标不能，检查路径曲率、倒车段和
goal checker；如果都不能，继续检查Local Costmap和MPPI。

### 4.4 Local Costmap与实时点云

```bash
ros2 topic echo /glim_ros/points_corrected --field width --once
ros2 topic echo /rslidar_points --field width --once
ros2 param get /local_costmap/local_costmap plugins
ros2 topic echo /local_costmap/costmap --once \
  --qos-durability transient_local
```

模式合同：

```text
obstacle → [obstacle_layer, inflation_layer]
voxel    → [voxel_layer, inflation_layer]
stvl     → [stvl_layer, inflation_layer]
```

单变量替换：固定`terrain_mode`、目标、车辆位置和环境，只冷切换
`local_obstacle_mode`。若仅一个模式失败，故障位于该插件、其QoS/clearing配置或依赖；
若三个模式都失败，先检查`/rslidar_points`、点云frame、时间戳和Nav2障碍层配置。

### 4.5 Planner、全局地图与2.5D地形

```bash
ros2 lifecycle get /planner_server
ros2 topic echo /map --field info --once --qos-durability transient_local
ros2 topic echo /global_costmap/costmap --once \
  --qos-durability transient_local
ros2 param get /planner_server GridBased.plugin
ros2 param get /planner_server GridBased.motion_model_for_search
ros2 param get /planner_server GridBased.minimum_turning_radius
```

2.5D模式额外检查：

```bash
ros2 topic echo /omnifleet_a2/terrain/grid_map --field layers --once
ros2 topic echo /omnifleet_a2/terrain/costmap --field info --once \
  --qos-durability transient_local
ros2 param get /global_costmap/global_costmap plugins
```

全局模式合同：

```text
2d    → StaticLayer + InflationLayer
2_5d  → StaticLayer + TraversabilityLayer + InflationLayer
```

单变量替换：固定局部层、目标、车辆位置和环境，只在`2d`与`2_5d`间冷切换。
如果2D可规划、2.5D不可规划，最小故障单元是
`terrain_mapper → /omnifleet_a2/terrain/costmap → traversability_layer`；不要修改GLIM、MPPI或STM32。

### 4.6 GLIM、TF与Airy

```bash
ros2 topic echo /rslidar_points --field width --once
ros2 topic echo /rslidar_imu_data_corrected --field linear_acceleration --once
ros2 topic echo /odom --once
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo /glim_ros/map --field width --once \
  --qos-durability transient_local
```

已知正常替代物：使用经本车验收的Airy rosbag替换实时点云和IMU，仅验证GLIM；
使用已验收的静态二维地图替换在线投影，仅验证Planner。替换后恢复则锁定被替换链，
不恢复则继续向上层接口检查。

禁止通过启动AMCL、slam_toolbox、EKF或其他LIO来“临时补TF”，这会破坏唯一位姿源
合同并掩盖真实故障。

## 5. 六种冷切换回归矩阵

每轮只修改括号中的一个变量，使用同一位置、同一目标和同一环境：

| `terrain_mode` | `local_obstacle_mode` | 应加载的全局/局部层 |
|---|---|---|
| `2d` | `obstacle` | Static + Obstacle |
| `2d` | `voxel` | Static + Voxel |
| `2d` | `stvl` | Static + STVL |
| `2_5d` | `obstacle` | Static + Traversability + Obstacle |
| `2_5d` | `voxel` | Static + Traversability + Voxel |
| `2_5d` | `stvl` | Static + Traversability + STVL |

标准冷切换不是运行中改插件名，而是停止当前统一Launch，重新启动目标组合，等待
`robot_doctor --scope nav`通过后再发布同一目标。测试后回装原组合并再次通过，才能
证明结论不是偶然恢复。

## 6. 启动、检查与清理

统一手动启动命令：

```bash
cd /home/iecme/omnifleet_a2_ws
set -a
source /etc/rrc/robot.env
set +a
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch omnifleet_a2_tutorials waypoint_navigation.launch.py \
  map_id:=<已保存地图ID> \
  terrain_mode:=2d \
  local_obstacle_mode:=obstacle \
  start_chassis:=false start_airy:=false use_camera:=false
```

GLIM/Nav2由上述前台Launch持有，用`Ctrl-C`整组关闭。基础硬件服务继续由systemd
持有，不要因算法测试停止它们。结束后确认没有遗留算法进程：

```bash
pgrep -af "glim_ros|controller_server|planner_server|bt_navigator|terrain_mapper"
ros2 node list
```

## 7. 故障记录模板

每次只填写一项变量变化：

```text
时间/提交：
现象：
期望：
terrain_mode / local_obstacle_mode：
当前输入：
当前输出：
唯一改变的变量：
已知正常替代物：
替换后的结果：
回装后的结果：
首个失败边界：
最小故障单元：
证据命令与日志路径：
```

只有“替换恢复 + 回装复现”同时成立，才能把问题归因到被替换模块。
