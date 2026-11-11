# OmniFleet T2 生产架构约束

## 唯一生产主线

```text
Airy -> MOLA -> map/odom TF + /map
                         |
                         v
                Nav2 SmacPlanner2D + DWB
                         |
                         v
                      /cmd_vel
                         |
                         v
              omnifleet_t2_driver -> STM32
```

- `omnifleet-t2-airy.service` 是 Airy 的唯一持有者。
- MOLA 是 `map -> odom` 的唯一发布者。
- `omnifleet_t2_driver` 是 `/odom`、`odom -> base_link` 和底盘串口的唯一持有者。
- STM32 设备名固定为 `/dev/omnifleet_t2_stm32`。
- T2 话题前缀固定为 `/omnifleet_t2/*`。
- 单点导航使用 `/goal_pose`；多点航点只使用
  `/omnifleet_t2/waypoints/add_pose`，两者不能混用。

## 生产服务边界

常驻：底盘、Airy、robot description、Foxglove bridge、航点 UI、网卡别名、
Jetson 性能配置和可选 Orbbec 相机。导航服务保持 disabled，由操作员手动拉起。

Cartographer 仅作为冷切换测试后端保留，不与 MOLA 同时运行。
第三方驱动包和原始 URDF 文件名可保留其上游名称；运行节点、设备别名、服务名和
T2 自有话题不得使用旧工程名称。

## 尺寸与运动模型

- footprint：长 0.50 m、宽 0.37 m、高 0.33 m；
- 两履带中心距：0.33 m；
- 全局规划：SmacPlanner2D；
- 局部控制：DWB；
- 生产定位建图：MOLA。
