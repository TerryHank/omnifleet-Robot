<!-- OMNIFLEET_WORKSPACE_DOC_LINK -->
本工作区职责、入口及104约定见 [README.omnifleet.md](README.omnifleet.md)。

# omnifleet_behaviors

机器人行为、Foxglove导航桥、任务服务以及地图保存/停止事务。

## WonderEcho 语音控制

`wonderecho_voice` 默认以 20 Hz 读取 WonderEcho 的 Type-C 串口 `/dev/wonderecho_flash`，波特率为 `115200`。串口协议为 5 字节 `AA 55 类型 ID FB`：类型 `0x03` 是唤醒事件，类型 `0x00` 是离散命令事件。节点仍保留 `transport:=i2c` 兼容模式；本车 Orin NX 40Pin 接口默认总线为 `7`，地址 `0x34`、结果寄存器 `0x64`、播报寄存器 `0x6e`。设备不存在、掉线或权限不足时节点不会退出，而是每 2 秒重连。I2C 模式采用寄存器边沿和同 ID 2 秒冷却，串口模式则直接消费每个完整协议帧。

支持的出厂命令词为：

| ID | 语音 | 行为 |
|---:|---|---|
| 1 | 前进 | `/cmd_vel` 前进 0.40 m/s，持续 1 秒 |
| 2 | 后退 | `/cmd_vel` 后退 0.40 m/s，持续 1 秒 |
| 3 / 4 | 左转 / 右转 | `/cmd_vel` 圆弧转向约 90°，速度 0.40 m/s |
| 9 | 停止 / 停下 | 立即向 `/cmd_vel` 连续发布零速 |
| 0x0D / 0x0E | 加速 / 减速 | 下一动作速度按 0.05 m/s 调节，范围 0.40–0.55 m/s |
| 0x1C | 露一手 | 4.8 秒 S 形圆弧 |
| 0x1D | 走两步 | 前进 0.8 m |
| 0x1E | 摇头 | 停车状态下前轮左右摆动 |
| 0x1F / 0x20 | 向前扑 / 向后扑 | 前进 / 后退 0.6 秒 |
| 0x21 | 战斗模式 | 两组短距离前后突进 |
| 0x23 | 抖一抖 | 三组短距离前后抖动 |
| 0x26 | 转动舵机 | 停车状态下前轮左、右各摆一次 |
| 0x6C | 跳舞 | 左右圆弧与前后移动组合 |
| 0x76 | 原地踏步 | 两组短距离前后踏步 |
| 0x78 | 大摇大摆 | 6 秒连续蛇形运动 |
| 0x7B | 关闭玩法 | 与“停止”相同，随时打断并归零 |
| 0x80 / 0x81 | 执行动作一 / 二 | 向左 / 向右绕行一圈，约 9.82 秒 |
| 0x82 | 执行动作三 | 左一圈加右一圈的八字动作，约 19.63 秒 |
| 0x83 / 0x84 | 执行动作四 / 五 | 向左 / 向右掉头约 180° |

启动文件默认使用 `motion_backend:=twist`，直接发布到 `/cmd_vel`，不依赖定位或 Nav2。直行动作按“距离/速度”换算持续时间；左/右转以 `|angular.z|=0.64 rad/s` 定时执行。组合玩法由多个定时 Twist 分段组成，任何分段都可被“停止”“停下”或“关闭玩法”立即打断。当前已烧录词表没有“自转一圈”，因此使用预留词“执行动作一”（协议 ID `0x80`）触发向左绕圈。节点以 10 Hz 发布速度，动作结束、停止命令、锁定或节点退出时都会发布零速。非零速度下限固定为 0.40 m/s，避免底盘死区。只有 `enable_motion=true` 且 `/cmd_vel` 存在底盘订阅者时才接受运动命令。旧的 Nav2 Behavior 后端仍可显式设置 `motion_backend:=nav2` 使用；圆弧与组合动作只允许直接速度后端。

默认不主动通过 `0x6e` 重复播报，因为出厂固件已经播放命令反馈；需要动作被 Nav2 接受后再播报一次时设置 `speak_on_accept:=true`。

独立启动（只要求底盘驱动已经订阅 `/cmd_vel`）：

```bash
cd /home/iecme/omnifleet_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=42
ros2 launch omnifleet_behaviors wonderecho_voice.launch.py transport:=serial serial_port:=/dev/wonderecho_flash serial_baud:=115200 motion_backend:=twist cmd_vel_topic:=/cmd_vel enable_motion:=false
```

人工确认周围安全后，显式解锁或再次锁定语音运动：

```bash
ros2 service call /omnifleet_t2/voice/enable_motion std_srvs/srv/SetBool "{data: true}"
ros2 service call /omnifleet_t2/voice/enable_motion std_srvs/srv/SetBool "{data: false}"
```

验收话题均为 JSON 格式的 `std_msgs/msg/String`，并采用 transient-local 锁存，晚启动的观察者也能读取最后一次识别和状态：

```bash
ros2 topic echo /omnifleet_t2/voice/recognized
ros2 topic echo /omnifleet_t2/voice/status
```

其他参数可用 `--ros-args -p poll_hz:=20.0 -p reconnect_sec:=2.0` 覆盖。串口模式需可访问 `/dev/wonderecho_flash` 并安装 `python3-serial`。I2C 兼容模式可附加 `transport:=i2c bus:=7 address:=52`，系统需安装 `python3-smbus`（代码也兼容已有的 `smbus2`）。
