# OmniFleet Ranger Mini 3.0 四驱四转工作区

系统底包：124 的 2026-11-20 完整镜像，保留 MOLA、相机、模型、地图及烧录修复。
车型代码：可恢复的 104 Ranger 适配和 2026-11-11 单点导航修复，来源见 /usr/local/share/omnifleet-image/ranger3-source.json。

底盘采用 Ranger Mini 3.0 官方 ROS 2 SDK 及对应 V3 协议补丁，CAN 500 kbit/s，自动识别 gs_usb 适配器。
启动入口 omnifleet-t2-chassis.service 的最终覆盖配置 zzzzzz-ranger3.conf，启动 ranger3.launch.py。
控制链路 /navigation/nav_cmd_vel → local_navigation → /navigation/cmd_vel_safe → Ranger SDK。
唯一兼容里程计 /odom 由 CAN 反馈节点发布，SDK 独立输出 /ranger_sdk/odom。

车型轮廓 0.72 × 0.50 m；车体传感器 TF、MOLA 和接收机专用网络沿用 124 系统环境。
普通联网使用 DHCP。车辆编号由调度分配，初始身份按 DHCP 地址尾段生成；EasyTier 也使用自动地址和主机名。
允许横移、斜移和四轮转向，网页使用 Ranger 运动面板。
没有连接实车进行运动或烧录验收，软件验证记录随完整工具包交付。
