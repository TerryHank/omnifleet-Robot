# 全局代价地图与路径规划对比实验

所有教学实验都从`omnifleet_tutorials`启动。`map_id`是已保存地图ID，必须提供；
其余实验参数不追加时保持生产默认：

```text
planner_mode=hybrid_astar
global_inflation_radius=0.22
global_cost_scaling_factor=8.0
global_costmap_resolution=0.05
```

## 代价地图实验

每次只追加一个参数，地图、起点和目标点保持不变：

```bash
ros2 launch omnifleet_tutorials waypoint_navigation.launch.py map_id:=<地图ID> global_inflation_radius:=0.40
ros2 launch omnifleet_tutorials waypoint_navigation.launch.py map_id:=<地图ID> global_cost_scaling_factor:=2.0
ros2 launch omnifleet_tutorials waypoint_navigation.launch.py map_id:=<地图ID> global_costmap_resolution:=0.10
```

- `global_inflation_radius`：障碍物影响范围，单位m。
- `global_cost_scaling_factor`：膨胀范围内代价下降速度。
- `global_costmap_resolution`：Global Costmap每格对应的实际长度，单位m/格。

## 全局规划实验

```bash
ros2 launch omnifleet_tutorials waypoint_navigation.launch.py map_id:=<地图ID> planner_mode:=dijkstra
ros2 launch omnifleet_tutorials waypoint_navigation.launch.py map_id:=<地图ID> planner_mode:=astar
ros2 launch omnifleet_tutorials waypoint_navigation.launch.py map_id:=<地图ID> planner_mode:=hybrid_astar
```

- `dijkstra`和`astar`使用同一个NavFn插件，仅切换`use_astar`，用于观察二维搜索路径。
- `hybrid_astar`是生产默认，使用Smac Hybrid和Reeds-Shepp，能够表达本车最小转弯半径与倒车段。
- NavFn不提供阿克曼曲率或倒车保证；需要驱动车辆完成前进/倒车导航时使用`hybrid_astar`。
