# Foxglove DSH 诊断助手

2026-09-07，部署于 iecme@192.168.3.113。

## 使用

Foxglove 中的“DSH 诊断助手”：一个问题输入框、一个回答框。输入问题后按 Enter 或点击“诊断”，新回答替换旧回答。回答中的“定位”按钮只滚动并聚焦参数，不改数值、不切换算法。

诊断依据为提问时的数据快照：Foxglove 话题列表、ROS 话题新鲜度、地图尺寸/分辨率/栅格统计与粗略地图、位姿/TF、速度、路径、导航状态、最近错误、永久参数及能读到的运行参数。静态地图旧时间戳不直接判为故障，未取得的数据明确标为缺失。

复用既有 DSH 的模型和私有凭据配置，通过官方 headless profile 处理每个问题。本入口使用专用 overlay 禁用工具与 MCP，不执行 shell、修改文件、设置 ROS 参数或发运动命令。DSH 自己的网页/微信设置不变。不是直接绕过 DSH 调模型接口。

面板不显示聊天历史；DSH 底层仍按既有配置保存独立 headless session，这是 DSH 自身的会话机制。界面只呈现当前回答。

## 链路与入口

`DshDiagnosticPanel.js → /omnifleet_t2/diagnostics/question → diagnostic_node.py → DSH headless → /omnifleet_t2/diagnostics/answer → 回答框`

安装目录：`/home/iecme/omnifleet_ws/src/visualization/omnifleet_t2_ws/foxglove/dsh_diagnostic_panel/`。

- `dsh_runner.py`：调用 DSH、限时、过滤参数定位 ID；凭据留在原 DSH HOME。
- `make_dsh_overlay.py`：生成该入口独用的诊断策略，未改全局 DSH 配置。
- `verify_dsh_profile.py`：核对最终合成配置中的工具/MCP 提供者均禁用。
- `deploy_diagnostic_panel.py`：维护派生客户端的内置注册及 bridge 提问白名单，备份后写入。
- `diagnostic_node.py`：只读采集与请求串行处理。

## 验证

- DSH 真正接收测试问题并返回结构化中文答案。
- ROS 提问/回答完整往返通过。
- 实际 Foxglove 点击提问后，回答框展示 DSH 对当前运行数据的诊断。
- 实测识别 GridBased / FollowPath；可读到地图、局部/全局代价地图、运行参数及 TF。初始发现尚未完成时会报告缺失，不冒充已读到。
- 实际“定位”按钮能聚焦 `nav2-input-planner_cost_multiplier`，输入值保持不变。
- 最终 profile 验证：17 个工具/MCP 提供者均被禁用。
- 模拟测试覆盖单问单答、旧响应忽略、错误恢复、定位不改值、卸载清理；地图摘要正确区分未知、自由、中间代价与占据，不发送完整数组。
- 本次未通过诊断助手设置任何参数、发送导航目标或速度。模型判断仍需结合证据核对，不能把示例或统计占比当成确定故障。

## 启停

诊断服务按用户要求保留常驻：

```bash
sudo systemctl start omnifleet-t2-dsh-diagnostics.service
sudo systemctl status omnifleet-t2-dsh-diagnostics.service --no-pager
sudo systemctl stop omnifleet-t2-dsh-diagnostics.service
```

仅在要手动前台调试时，先停上述诊断服务避免重复实例，再运行：

```bash
cd /home/iecme/omnifleet_ws/src/visualization/omnifleet_t2_ws/foxglove/dsh_diagnostic_panel
source /home/iecme/omnifleet_ws/src/system/omnifleet_fleet/env.bash
python3 diagnostic_node.py
```

正常 Foxglove 启动：`/home/iecme/.local/bin/start-foxglove-single.sh`。

## 回退

修改前 bundle、bridge 配置和布局备份在 `/home/iecme/robot_backups/dsh_diagnostic_panel/`。停止并禁用本次新增诊断服务；核对后恢复需要的 bundle/白名单/布局，再正常启动 Foxglove。若之后已有其他 UI 修改，不要直接用旧整份 bundle 覆盖新功能。
