# MID-360 + GLIM + Nav2 阿克曼生产架构

本文是当前生产运行的唯一架构合同。系统不使用 EKF、AMCL、slam_toolbox、
FAST-LIO、DLIO、MOLA 或 RTAB-Map 参与位姿估计；GLIM 1.2.2 是唯一动态位姿源。

## 1. 工程框架

```text
lunshi_chassis_description   URDF、车辆和传感器静态 TF
rrc_sensor_gateway          MID-360 驱动、QoS 和健康检查
rrc_slam_bringup            GLIM CUDA、点云处理、地图投影和整车启动
rrc_glim_bridge             /odom 语义适配、障碍点云、二维地图投影
rrc_bringup                 Nav2 生命周期、行为树和速度安全链
rrc_slam_manager            GLIM 启停、地图登记、健康检查和零速事务
rrc_chassis_core            twist_mux、阿克曼驱动、轮速诊断和 RSP
```

MID-360 驱动由独立 systemd 服务长期持有硬件，GLIM 由事务式管理器按任务启停。
这保留了传感器故障隔离；若以后改成单进程组件化，只允许替换进程边界，话题、
TF 所有权和下述数据合同不得改变。

## 2. 数据流

```text
MID-360
├── /livox/lidar_points_native  PointCloud2 ─┐
└── /livox/imu_raw              Imu ─────────┤
                                               ▼
                                             GLIM
              ┌────────────────────────────────┼──────────────────────────┐
              │                                │                          │
              ▼                                ▼                          ▼
       map -> odom -> base_link       /glim_ros/points_corrected   /glim_ros/map
              │                                │                          │
              ▼                                ▼                          ▼
       /glim_ros/odom                  自车/高度/距离/异常点过滤      低频二维投影
              │                                │                          │
       glim_odom_adapter                       ▼                          ▼
              │                        /lidar/obstacles                   /map
              ▼                                │                          │
            /odom                       Local Costmap              Global Costmap
                                           VoxelLayer               StaticLayer
                                                └──────────┬───────────────┘
                                                           ▼
                                             SmacPlannerHybrid (Reeds-Shepp)
                                                           ▼
                                               MPPI Ackermann Controller
                                                           ▼
 /cmd_vel_nav_raw -> velocity_smoother -> /cmd_vel_nav_smoothed
                                                           ▼
                                             collision_monitor
                                                           ▼
                                               /cmd_vel_nav_safe
                                                           ▼
                       teleop / zero lock -> twist_mux -> /cmd_vel
                                                           ▼
                    STM32 transport -> FUNC_MOTION(Vx, 0, Vz) -> MCU
                                                           ▼
                         STM32 Ackermann_Ctrl -> 舵角/左右轮速度/执行器
```

`glim_odom_adapter`不估计、不滤波、也不发布 TF。它只把 GLIM 原生 IMU 语义的
Odometry 转成 `odom/base_link` 消息语义；动态位姿仍以 GLIM TF 为唯一真值。

## 3. TF 所有权

```text
map
└── odom                         GLIM 全局优化
    └── base_link                GLIM 连续 6DoF 里程计；后轴中心
        ├── imu_link             robot_state_publisher
        ├── livox_frame          robot_state_publisher
        ├── steering/wheel links robot_state_publisher + joint states
        └── hik_camera_link      robot_state_publisher
```

| TF 边 | 唯一发布者 |
|---|---|
| `map -> odom` | `glim_ros` |
| `odom -> base_link` | `glim_ros` |
| `base_link -> sensors` | `robot_state_publisher` |
| 转向/车轮关节 | `robot_state_publisher` 使用的 joint states |

STM32通过 `/vel_raw` 上报实际纵向速度、实际舵角和实际角速度；
`stm32_feedback_adapter`只把其中的实际速度封装成`/wheel/odometry.twist`供打滑检测，
不填充推算位姿。NX不再根据舵角、轴距重新计算或积分轮式里程计。严禁重新引入 `base_node_R2`、
`ackermann_steering_controller`、`ekf_filter_node`、`map_odom_corrector` 或第二个
`odom -> base_link` 发布者。

## 4. STM32运动学所有权

生产驱动固定发送：

```text
Twist.linear.x  -> Vx，m/s转mm/s
Twist.linear.y  -> 忽略
Twist.angular.z -> Vz，rad/s转mrad/s
Vy              -> 固定为0
```

STM32是唯一执行层运动学所有者，统一完成`v,w -> steering`、舵角限幅、左右轮
速度目标以及电机/舵机闭环。NX只保留命令仲裁、安全限速、超时停车、单位换算、
串口封装和状态展示。Smac与MPPI仍在NX上使用Ackermann模型进行路径可行性预测，
但不得输出单轮速度或舵机目标。

执行层以`base_link`所在的后轴中心为车体速度参考点，采用标准自行车模型与后轴
左右轮速度分配。令纵向速度为`v`、ROS左转为正的角速度为`w`、轴距为`L`、
后驱轮距为`W_r`，则：

```text
曲率：          k = w / v
等效前轮舵角：  delta = atan(L * k) = atan(L * w / v)
左后轮速度：    v_left  = v * (1 - W_r * k / 2) = v - w * W_r / 2
右后轮速度：    v_right = v * (1 + W_r * k / 2) = v + w * W_r / 2
```

舵角被限幅或转向速率限制后，左右轮目标必须用实际执行舵角重新计算：
`k_actual = tan(delta_actual) / L`。`v=0`时必须停车，不允许用左右轮反转模拟原地旋转。
当前实测几何参数为：

```text
L   = 0.362295943 m    轴距
W_r = 0.245400019 m    后驱轮距，参与左右驱动轮差速
W_f = 0.264956799 m    前转向轮距，仅用于前轮几何/URDF
D   = 0.117056526 m    平均轮径
r   = 0.058528263 m    平均轮半径
C   = 0.36774 m        STM32编码器速度换算使用的有效轮周长
```

本车为单舵机机械转向机构，STM32输出等效舵角，机械连杆负责两个前轮的内外轮角度
关系；不得把`W_f`误用于后驱轮速度分配。固件中的M1/M2与物理左后/右后轮映射、
编码器正负号必须通过架空低速试验验收，不能依靠变量名推断。固件中仍存在
“轮径106 mm”的旧注释，但实际常量`AKM_CIRCLE_MM=367.74`与上述实测轮径一致；
不得根据该旧注释回改有效轮周长。

## 5. Nav2 合同

- Global Costmap：`StaticLayer + InflationLayer`，输入 `/map`。
- Local Costmap：`VoxelLayer + InflationLayer`，输入 MID-360、RGB-D 和跌落点云。
- Planner：`SmacPlannerHybrid + REEDS_SHEPP`。
- Smoother：`ConstrainedSmoother`，允许倒车。
- Controller：`MPPI + AckermannMotionModel`。
- 三处最小转弯半径统一为 `0.63 m`；实车复测后只能同步修改。
- `base_link` 位于后轴中心；footprint 为
  `[[-0.06,-0.16],[-0.06,0.16],[0.42,0.16],[0.42,-0.16]]`，另加 0.02 m padding。
- 行为树不包含 Spin；恢复动作使用清图、倒车、等待和重新规划。
- 速度必须依次经过 smoother、collision monitor 和 chassis twist mux。

## 6. 地图边界

在线建图和同一 GLIM 会话内导航已闭环。`/glim_ros/map` 是三维 PointCloud2，
`glim_map_projector`以低频/增量证据生成 Nav2 的 OccupancyGrid。GLIM dump 是三维
源地图，二维 `/map` 是导航派生物，两者不可互相替代。

`localization` 使用本工程扩展的 GLIM prior-map 模块和显式初始位姿；这不是上游
GLIM 1.2.2 的通用 localization-only 能力。地图清单必须校验传感器配置和外参哈希。

## 7. 验收

```bash
export ROS_DOMAIN_ID=42
source /opt/ros/humble/setup.bash
source ~/ros2humble_ws/install/setup.bash
source ~/stm32_driver_ws/install/setup.bash
source ~/slam_overlays/glim_cuda_ws/setup_glim_cuda.bash

ros2 node list
ros2 topic info /odom -v
ros2 topic info /cmd_vel -v
ros2 run tf2_ros tf2_echo map odom
ros2 run tf2_ros tf2_echo odom base_link
```

验收条件：`glim_ros`是两条动态 TF 的唯一发布者；`/odom`由
`glim_odom_adapter`唯一发布；`/cmd_vel`由 `rrc_command_mux`唯一发布；节点图中
不存在 `ekf_filter_node`、`map_odom_corrector`、AMCL 或其他 LIO/SLAM 后端。
