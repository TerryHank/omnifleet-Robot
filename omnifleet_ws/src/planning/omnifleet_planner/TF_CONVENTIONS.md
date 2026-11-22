# 生产 TF 约定

```text
map                 MOLA全局坐标，也是Nav2全局坐标
└── odom            连续里程计坐标
    └── base_link   后轴中心，完整6DoF
        ├── imu_link
        ├── rslidar
        ├── hik_camera_link
        │   └── camera_color_optical_frame
        └── steering / wheel links
```

- `mola_bridge_ros2`唯一发布 `map -> odom`。
- `omnifleet_t2_driver`唯一发布 `odom -> base_link`。
- Airy当前驱动坐标的Z轴指向雷达穹顶，现场点云已验证无需翻滚修正；
  `base_to_airy`暂按现场A/B检查设为`yaw=0`，使雷达X/Y轴与`base_link`同向。
  该变换是完整右手旋转，禁止单独对某个轴取反。
- 不创建额外的地图平面静态变换；地图、全局代价地图和机器人姿态的
  高度一致性必须由右手系外参与标准TF链本身保证。
- Nav2的BT、局部/全局代价地图和Behavior Server全部直接使用`map`。
- `robot_state_publisher`发布全部车体与传感器固定关系。
- 轮速节点发布 `/omnifleet_t2/chassis/wheel_odometry`，子帧为 `base_link`，但不发布 TF。
- `omnifleet_t2_driver`发布标准 `/odom` 消息。
- 禁止 `base_footprint`、EKF、`map_odom_corrector` 或其他静态 TF 发布器创建并行父链。

版本化外参以 `config/extrinsics.yaml` 为准。Airy 点云和校正后的 IMU
都声明为 `rslidar`；只有驱动真实输出独立 IMU frame 时才可增加对应固定边。
