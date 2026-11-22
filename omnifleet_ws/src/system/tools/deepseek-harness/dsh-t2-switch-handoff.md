# T2 切回 DSH：2026-09-07

目标主机：`iecme@192.168.3.113`。

部署链路：微信 iLink → `@xmanrui/dsh-im@4.13.0` → `@deepseek-ai/dsh@0.1.2-rc.1` → 官方 `@deepseek-ai/dsh-mcp-client` → `ros-mcp==3.1.0` → 本机 rosbridge → ROS 2 Humble。

阿里端点和默认 `qwen3.8-max` 沿用既有配置。机器人接口仅启用 ros-mcp；Hermes 网关已停止并禁用自启动，保留其安装、人格、技能和数据。

## 验证结果

- 微信已有登录态已迁入 DSH，dsh-im 状态接口返回 `connected=true`、`health.status=healthy`；工作区 `/home/iecme/omnifleet_t2_ws`。无需重新扫码。
- ros-mcp 标准 MCP 握手发现 31 个工具。
- 实测读到 84 个话题、实时 `/odom`（odom → base_link）以及 `/map`（188×88、分辨率约 0.1 m）。
- DSH headless 经阿里 qwen3.8-max 实际调用 `mcp__ros__get_topics` 与 `mcp__ros__subscribe_once`，读回 `/odom` 时间戳 `1788763114.627217304`。
- 本轮没有测试底盘运动、导航目标或微信图片回传。迁移后尚需用户在微信发送消息验收完整收发。
- FastMCP 4 与 ros-mcp 的旧导入路径不兼容，已按上游锁文件固定 FastMCP 2.13.0，MCP SDK 固定 1.29.1。安装在独立 `/home/iecme/omnifleet_ws/.env/ros_mcp`，未改 Hermes Python 依赖。

## 常驻服务

- `deepseek-harness.service`：DSH 与微信接收，PID 124047（验证时），仅监听 `127.0.0.1:3080`。
- `dsh-rosbridge-t2.service`：为 DSH 提供 ROS 连接，主 PID 123193（验证时），仅监听 `127.0.0.1:9090`。
- MCP 子进程由 DSH 管理。一次性验证客户端已经退出。

在 Windows 启停：

```powershell
ssh iecme@192.168.3.113 "systemctl --user start dsh-rosbridge-t2.service deepseek-harness.service"
ssh iecme@192.168.3.113 "systemctl --user stop deepseek-harness.service dsh-rosbridge-t2.service"
```

服务使用的 ROS 启动脚本：`/home/iecme/.local/bin/dsh-rosbridge-t2`。如需手动前台运行，先停止相应 bridge 服务避免占用同一端口，再执行：

```bash
source /opt/ros/humble/setup.bash
source /home/iecme/omnifleet_ws/install/setup.bash
source /home/iecme/omnifleet_ws/install/setup.bash
source /home/iecme/omnifleet_ws/install/setup.bash
set -a
source /etc/omnifleet_t2/robot.env
set +a
cd /home/iecme/omnifleet_t2_ws
ros2 launch rosbridge_server rosbridge_websocket_launch.xml address:=127.0.0.1 port:=9090 call_services_in_new_thread:=true default_call_service_timeout:=10.0
```

当前服务环境文件的域号为 73、RMW 为 rmw_fastrtps_cpp、FASTDDS_BUILTIN_TRANSPORTS 为 DEFAULT，以现网为准。

## 配置与恢复

- DSH MCP patch：`/home/iecme/.dsh-t2/cordis.patch.yml`。
- 切换前 DSH 配置备份：`/home/iecme/backups/dsh-switch-20260907-143504`（含私有凭据，勿上传）。
- 微信配置：`/home/iecme/.dsh-t2/integrations/dsh-weixin/config.json`，凭据在 DSH 独立凭据文件中，扫码者身份沿用；没有开放给其他用户。
- 保留 Hermes 安装，但恢复它前应先停止 DSH，避免同一微信机器人存在两个收信进程。
- 微信 `/stop` 停止 agent 回合，不等同于机器人硬件急停。

参考：https://github.com/robotmcp/ros-mcp-server/blob/main/docs/install/installation.md
