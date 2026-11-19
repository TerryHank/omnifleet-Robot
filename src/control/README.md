# control 功能域

本机导航任务执行、控制权仲裁、安全速度出口、车队执行和遥控协议。

## 包与组件索引

| 包/组件 | 职责 |
|---|---|
| [omnifleet_behaviors](omnifleet_behaviors/README.omnifleet.md) | 导航行为、地图工作流和语音控制集成。 |
| [omnifleet_dwb_hot](omnifleet_dwb_hot/README.md) | DWB critic 权重在控制周期边界的热更新实现。 |
| [omnifleet_local_navigation](omnifleet_local_navigation/README.md) | 独立单车/多点导航任务执行、LOCAL/FLEET 控制权仲裁及唯一底盘安全速度出口。 |
| [omnifleet_teleop](omnifleet_teleop/README.omnifleet.md) | VR 协议适配及操作者遥控入口。 |
| [omnifleet_vr_bridge](omnifleet_vr_bridge/README.md) | VR 与 ROS 消息/舵机控制的桥接；运行时是否启用驱动应查实际参数。 |
