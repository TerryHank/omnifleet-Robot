# 生产 TF 约定

```text
nav_map             二维导航地面坐标，z=0为轮胎接地点
└── map             GLIM原生三维地图坐标，原点位于启动时传感器高度
    └── odom        GLIM
        └── base_link   后轴中心，完整 6DoF
            ├── imu_link
            ├── livox_frame
            ├── hik_camera_link
            │   └── camera_color_optical_frame
            └── steering / wheel links
```

- `navigation_ground_frame`唯一发布静态 `nav_map -> map`；默认Z偏移为
  `0.374553341297 m`（MID-360相对`base_link`高度加轮半径）。
- `glim_ros`唯一发布 `map -> odom` 和 `odom -> base_link`。
- Nav2的BT、Global Costmap、Local Costmap和Behavior Server统一使用`nav_map`。
- `robot_state_publisher`发布全部车体与传感器固定关系。
- 轮速节点发布 `/wheel/odometry`，子帧为 `base_link`，但不发布 TF。
- `glim_odom_adapter`发布标准 `/odom` 消息，但不发布 TF、不滤波、不估计位姿。
- 禁止 `base_footprint`、EKF、`map_odom_corrector` 或其他静态 TF 发布器创建并行父链。

版本化外参以 `config/extrinsics.yaml` 与生产 URDF 为准。MID-360 点云和 IMU
当前都声明为 `livox_frame`；只有驱动真实输出独立 IMU frame 时才可增加对应固定边。
