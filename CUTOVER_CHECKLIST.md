# OmniFleet A2 主线切换清单

## 已完成并部署

- [x] 备份旧 ROS 源码、systemd 配置、Foxglove 数据和 STM32 固件源码。
- [x] 建立 Git 主线：`/home/iecme/omnifleet_a2_ws`，分支 `main`。
- [x] 删除 ROS 侧转向适配、指令超时、零速自动打舵、预打舵和锁车逻辑。
- [x] `/cmd_vel` 由 Nav2 controller 直接发布给底盘；自检只报告发布者数量，不锁车。
- [x] 增加 `/omnifleet_a2/chassis/steering_angle_cmd` 自定义弧度舵角接口。
- [x] 把通信失联看门狗移入 STM32；NX 可调心跳和超时，并可监测状态及累计触发次数。
- [x] STM32 已由 ST-Link 烧录并逐字节回读；固件 SHA-256 为 `6af1029877c711b0f5652ee1815a59a1adc0b41080a2eb85b3fb6d483f596f19`。
- [x] 架空验证明确舵角接口、零速不打舵、杀驱动进程停车和串口驱动解绑/重绑后独立停车。
- [x] 单点和多点统一由 `/omnifleet_a2/nav/waypoint_poses` 使用 `NavigateThroughPoses`。
- [x] 删除单点目标后方 1.56 m 进场点逻辑。
- [x] 删除旧任务保存/回放管理器及其消息、服务、存储和测试。
- [x] 删除 `OccupancyEvidence`、邻域确认、多帧历史、墙面保护、TTL 和射线裁剪。
- [x] 删除额外地图平面，统一使用 `map`。
- [x] 把自定义包、节点、话题、状态目录和服务统一到 `omnifleet_a2` 身份。
- [x] `glim_map_projector` 只处理内容变化的 `/glim_ros/map`，不订阅或累计实时点云。
- [x] Airy 障碍点改为 C++ 单帧 XY 栅格降采样，默认 `6.0 m / 0.12 m / 5 Hz`。
- [x] Foxglove 默认布局只保留地图、路径、车模、固定航点和电压；重型数据使用独立配置。
- [x] 已停止并禁用旧底盘、Airy、Foxglove 和航点服务；生产服务统一为 `omnifleet-a2-*`。
- [x] 生产栈从新工作区启动 `slam_navigation`，旧工作区不再作为生产入口。
- [x] `/cmd_vel` 只有 controller server 一个发布者、底盘一个订阅者，图中无中间转向适配节点。
- [x] 地图、全局代价地图、局部代价地图均使用 `map` 平面。
- [x] 已记录 30 分钟 GLIM、TF、障碍过滤器和 Foxglove 负载；消息年龄无持续增长。
- [x] 全仓 11 个包构建通过，383 项测试为 0 error / 0 failure / 0 skipped。

## 仍需车辆落地后执行

- [ ] 直线 0.40 m 航点位移验收。当前车辆架空，只完成了轮端输出、转向、失联停车和导航命令链验证；不能把架空轮转冒充实际地面位移。
