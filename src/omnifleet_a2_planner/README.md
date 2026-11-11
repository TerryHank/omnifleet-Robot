# 全局代价地图与路径规划对比实验

所有教学实验都从`omnifleet_a2_tutorials`启动。`map_id`是已保存地图ID，必须提供；
其余实验参数不追加时保持生产默认：

```text
planner_mode=hybrid_astar
global_inflation_radius=0.22
global_cost_scaling_factor=8.0
global_costmap_resolution=0.05
```

## 局部控制器冷切换

平时使用的`omnifleet_a2_bringup/robot.launch.py`直接接受`controller_mode`外参。
默认`rpp`保持不变；要在边建图边导航模式切到MPPI：

```bash
ros2 launch omnifleet_a2_bringup robot.launch.py operation:=slam_navigation mapping_profile:=lidar controller_mode:=mppi
```

- `rpp`：已验证的生产默认，控制频率10 Hz。
- `mppi`：Ackermann模型、允许按Hybrid-A*路径倒车，控制频率20 Hz；关闭轨迹可视化并将采样批量限制为500，以保留GLIM建图余量。
- 两种模式都直接发布标准`/cmd_vel`；转向方向与执行器限制只由STM32负责。

## 代价地图实验

每次只追加一个参数，地图、起点和目标点保持不变：

```bash
ros2 launch omnifleet_a2_tutorials waypoint_navigation.launch.py map_id:=<地图ID> global_inflation_radius:=0.40
ros2 launch omnifleet_a2_tutorials waypoint_navigation.launch.py map_id:=<地图ID> global_cost_scaling_factor:=2.0
ros2 launch omnifleet_a2_tutorials waypoint_navigation.launch.py map_id:=<地图ID> global_costmap_resolution:=0.10
```

- `global_inflation_radius`：障碍物影响范围，单位m。
- `global_cost_scaling_factor`：膨胀范围内代价下降速度。
- `global_costmap_resolution`：Global Costmap每格对应的实际长度，单位m/格。

## 全局规划实验

```bash
ros2 launch omnifleet_a2_tutorials waypoint_navigation.launch.py map_id:=<地图ID> planner_mode:=dijkstra
ros2 launch omnifleet_a2_tutorials waypoint_navigation.launch.py map_id:=<地图ID> planner_mode:=astar
ros2 launch omnifleet_a2_tutorials waypoint_navigation.launch.py map_id:=<地图ID> planner_mode:=hybrid_astar
```

- `dijkstra`和`astar`使用同一个NavFn插件，仅切换`use_astar`，用于观察二维搜索路径。
- `hybrid_astar`是实车默认，使用Smac Hybrid和Reeds-Shepp，表达本车最小转弯半径，并在必要时生成倒车段。
- NavFn不提供阿克曼曲率保证；需要驱动车辆完成受约束前进导航时使用`hybrid_astar`。
