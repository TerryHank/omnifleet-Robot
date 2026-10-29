# 104 与中央 RMF 状态实时接入

2026-10-14（Asia/Shanghai）。入口：[系统概览](http://localhost:3000/robots)，顶部新增“104 与中央调度实时状态”面板。

## 实际接入链路

```text
104 当前 ROS 话题（Domain 104，原生 Zenoh）
  /navigation/status
  /navigation/local_status
  /lidar_odometry/pose
  /voltage
      ↓ 仅订阅
WSL 专用只读采集器 omnifleet_web_read_only_robot104
      ↓ 本机 Unix datagram socket
RMF Web API（Domain 42）
      ↓ 每秒 SSE 推送
中文 Web 实时状态面板
```

中央状态接入 `/omnifleet/rmf/connection_status`、`/dispatch_states`、`/rmf_traffic/participants`、`/rmf_traffic/registered_queries`。另每两秒只读查询 `/get_dispatches` 和交通调度节点的 `get_parameters`，用实际响应确认活性，避免把话题存在或进程运行误判为通信正常。

104 与中央域始终处于独立 ROS 进程。Web 专用采集器没有创建车辆命令发布者、动作客户端或车辆控制服务客户端；不依赖 MSC。传入状态中的旧 agent/coordinator 兼容字段不进入新的 Web API 视图。

运行期间原框架客户端入口被更新为控制客户端，并出现 `rclpy.Node.handle` 属性冲突。因此 Web 最终使用独立只读采集服务，没有覆盖或修改当前控制客户端。

## 页面显示

104 的在线/过期状态、采集来源、导航阶段和任务号、控制模式、本地覆盖、急停、导航后端就绪、TF 年龄、原始位姿、坐标系、电压、各类消息计数和数据年龄。

中央域号、状态桥消息计数、调度核心和分发器活性、分发中/结束记录、交通参与者、注册查询数和分发话题接收计数。注册状态读取中央最新上报，页面任务下发仍为只读禁用。

位姿显示车辆原始坐标，没有转换或发布成中央 RMF 地图位置。当前地图配准验证配置仍为 false。只收到电压，因此电量百分比明确显示“未知”，不推算百分比。分发结束不代表任务执行完成。

原版 RMF 车队/任务视图仍保留在原位置及任务选项卡，其数据继续由标准 RMF Web 接口提供；顶部实时监测面板使用本次新增的观察接口。

## 验收结果

- 生产构建和 TypeScript 检查通过，`git diff --check` 通过。
- 5 项离线测试通过：车辆数据过期、中央桥过期、调度 RPC 过期、独立采集不受框架客户端数据过期影响、兼容字段过滤及不虚构任务。
- SSE 连续帧验证通过：桥消息、调度响应、104 导航和位姿消息计数持续增长；校验了采集来源与原始坐标系、电压及中央注册状态。
- Web API 已实际订阅中央状态桥和分发状态话题。
- 暂停专用只读采集器后，API 的 104 在线状态变为 false，页面显示“状态过期／未连接”；中央调度的只读查询继续正常。恢复后页面无需刷新重新在线。
- Web API 重启后 SSE 自动重连，独立采集器继续工作。
- 任务下发接口仍返回 403；本轮没有提交机器人任务或车辆控制请求。

证据文件：`live-stream-acceptance.json`、`dedicated-outage.json`、`dedicated-expired.txt`、`final-page.txt`、`recovered.png`，以及部署源码快照与检查脚本。

截图 `online-before.*`、`expired.*`、最初的 `recovered.*` 记录了首轮桥接方案的在线/过期/恢复过程；`dedicated-*` 与 `final-*` 记录最终独立采集方案。

## 运行与接口

- 快照：[http://localhost:8000/omnifleet/status](http://localhost:8000/omnifleet/status)
- SSE：`http://localhost:8000/omnifleet/status/stream`
- 新服务：`omnifleet-rmf-web-robot104.service`，已加入原来的 `omnifleet-rmf-web.target`。
- 源码：`/home/zhangwnag/workspaces/omnifleet_ws/src/visualization/omnifleet_rmf_web/`；前端组件位于官方源码中的 `packages/dashboard/src/components/live-status-app.tsx`。
- 状态 IPC：`/home/zhangwnag/workspaces/omnifleet_ws/data/rmf_web/run/robot104.sock`。

```bash
systemctl --user status omnifleet-rmf-web-api.service omnifleet-rmf-web-robot104.service
journalctl --user -u omnifleet-rmf-web-api.service -u omnifleet-rmf-web-robot104.service -f
systemctl --user restart omnifleet-rmf-web.target
```

回滚副本在 `/home/zhangwnag/workspaces/omnifleet_ws/data/rmf_web/backup_before_live_status/`，保存了原 API 包装器、启动脚本、target、前端注册表/布局与原中文构建。回滚前端时可用该目录的 `dashboard` 内容恢复当前服务目录；只取消采集可停止 `omnifleet-rmf-web-robot104.service`。恢复 target 与 API/启动脚本快照后再重启原 Web 服务组，即可移除本次接入。原有车辆、中央框架源码和数据库没有回滚或覆盖。
