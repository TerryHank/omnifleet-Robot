# 当前机器人调度入口（2026-10-18）

本机 Windows 入口：**http://localhost:8080**。原 3000 端口仍在 WSL 中监听，但当前 Windows 的 2989～3088 保留端口范围包含 3000，不能依赖该端口的 localhost 回送。Dashboard 和 API 均只绑定回环地址。

原生 RMF Web 内已接入：车辆前缀与拖拽排序、实时前车跟随、各车单点/多点及拖点编辑、全队列执行与清除、遥控与全部停止、共享/同伴/代价图层、TF/URDF/点云、相机/话题/曲线、永久参数、诊断与参数定位、地图保存/加载/重置、录包和车端导航栈配置。

机器人操作使用 `/omnifleet/operator` 路由。写入口只转交已有中央控制合同，并保留令牌、来源与身份版本检查。车端导航与永久参数保存仍使用原有服务。其他原生 RMF 资源写接口保留原来的只读限制。跟随仍是项目 Adapter 的扩展；接入 Web 不代表完成原生 RMF 多车交通实车验收。

静态前端当前路径为 `install/rmf_web_dashboard/operator-20261018`，`zh-CN` 指向该版本。此前构建位于 `install/rmf_web_dashboard/zh-CN.before-operator-20261018`。新增 MOLA 服务接口来自现用车端的 `mola_msgs`，安装在标准 workspace `build/install` 中，没有在本机启动 MOLA。

本次验收不驱动车辆。浏览器闭环使用独立 HTTP 端口与内存执行端，并调用真实 Missions/OperatorControls 代码。真实设备只核验地图、TF、雷达、IMU、相机、参数读取及只读诊断。地图切换、重置、导航重启和车辆运动没有在实车执行。

启动：

```bash
cd /home/zhangwnag/workspaces/omnifleet_ws
source env.bash
systemctl --user start omnifleet-rmf.target omnifleet-rmf-web.target
```

仅停止网页（保留原中央调度与车辆服务）：

```bash
systemctl --user stop omnifleet-rmf-web.target
```

修改及验收证据位于 Windows `D:/Workspace/stm32_agent_delivery_20260920/OPENRMF_FRONTEND_20261018`，以及 WSL `data/rmf_web/operator-*.log`。

---

以下为此前 2026-10-14 的历史部署记录，其“当前功能边界”描述的是当时的只读部署。

# RMF Web 原生部署记录

部署日期：2026-10-14（Asia/Shanghai）。目标：本机 `Ubuntu-22.04` WSL；未使用或安装 Docker。

## 访问

- Dashboard：[http://localhost:3000](http://localhost:3000)
- API 文档：[http://localhost:8000/docs](http://localhost:8000/docs)
- 轨迹 WebSocket：`ws://localhost:8006`

采用官方 [rmf-web Humble 分支](https://github.com/open-rmf/rmf-web/tree/humble)的生产静态构建，适配本机 Ubuntu 22.04 / ROS 2 Humble。上游提交：`54c9630abdce1eede0d319dc87f3a740ca1faed4`。首次部署采用原版，随后按要求汉化；当前服务中文版本，详见 `../rmf-web-zh-CN/README.md`。

## 当前功能边界

Dashboard 页面、API、Socket.IO 状态订阅与轨迹 WebSocket 已验证；服务重启后重新验证通过。官方系统概览和任务页可正常浏览，当前 `/fleets` 与 `/tasks` 均为 `[]`，没有虚构车辆、地图或任务数据。

中央域为 **42**，使用已有 `rmw_zenoh_cpp` 和 WSL 本地 Router。API 使用实际时间，`use_sim_time=false`，不采用官方演示脚本的模拟时间配置。

现有中央框架只导出连接状态，尚未通过 Fleet Adapter 注册 RMF 车队或向 Web API 推送 fleet/task 状态。Robot 104 的连接状态存在于 `data/connection_status.json`，不等于它已出现在 RMF Web；Robot 113 尚未接入。RMF 导航图、建筑地图、车辆到 RMF 地图的坐标转换及实车任务执行均未验收。

根据现有 WSL 工程 `AGENTS.md` 的只读要求，部署增加独立 API 启动包装器：阻止 HTTP POST/PUT/PATCH/DELETE 等写入；保留 GET/HEAD/OPTIONS 和 Socket.IO polling。Socket.IO 的上游事件仅用于订阅/取消订阅。任务下发、取消及设备控制请求验证返回 **403**。没有修改车辆服务或开启运动。

认证仍采用上游演示 stub；Dashboard/API 绑定本机回环地址。没有配置公网或局域网发布、HTTPS 或正式身份提供商。轨迹服务器使用上游默认监听方式，端口为 8006；本次未建立 Windows 端口代理或添加入站防火墙规则。

## WSL 文件位置

| 内容 | 绝对路径 |
| --- | --- |
| 官方源码 | `/home/zhangwnag/workspaces/omnifleet_ws/src/visualization/rmf-web` |
| 本地部署配置 | `/home/zhangwnag/workspaces/omnifleet_ws/src/visualization/omnifleet_rmf_web` |
| Node / pnpm / serve / Python venv | `/home/zhangwnag/workspaces/omnifleet_ws/install/rmf_web_runtime` |
| SQLite 与地图资源缓存 | `/home/zhangwnag/workspaces/omnifleet_ws/data/rmf_web` |
| 用户服务 | `/home/zhangwnag/.config/systemd/user/omnifleet-rmf-web*` |

Node：20.20.2；pnpm：9.15.9；serve：14.2.6；Python：3.10.12。前端依赖使用上游锁文件安装；Python 依赖位于独立 venv，并读取已有 ROS 系统包。新增 apt 包为 `python3.10-venv`、`python3-pip-whl`、`python3-setuptools-whl`、`ros-humble-rmf-visualization-schedule`、`ros-humble-rmf-visualization-msgs`。

测得源码、前端依赖与构建目录约 1.1 GiB，隔离运行时约 278 MiB；另有 npm/pnpm/pip 缓存。上游构建有 CSS 弃用、浏览器数据库过旧与包体积提示，构建成功。

## 启停与日志

在 WSL 中执行：

```bash
systemctl --user status omnifleet-rmf-web.target \
  omnifleet-rmf-web-api.service \
  omnifleet-rmf-web-dashboard.service \
  omnifleet-rmf-web-trajectory.service

systemctl --user restart omnifleet-rmf-web.target
systemctl --user stop omnifleet-rmf-web.target
systemctl --user start omnifleet-rmf-web.target

journalctl --user -u omnifleet-rmf-web-api.service \
  -u omnifleet-rmf-web-dashboard.service \
  -u omnifleet-rmf-web-trajectory.service -f
```

`omnifleet-rmf-web.target` 已启用，用户 lingering 已存在并确认开启，WSL 启动后由用户 systemd 自动运行。未验证整台 Windows 重启；本轮验证的是 Web 服务组重启。Windows 没有运行 WSL 时服务无法运行，可手动执行 `wsl -d Ubuntu-22.04 -- true` 启动 WSL。

停止并取消自启动，可执行：

```bash
systemctl --user disable --now omnifleet-rmf-web.target
```

此操作保留源码、配置、SQLite 和原有中央服务。

## 验证证据

- `acceptance-before-restart.json` 与 `acceptance-after-restart.json`：HTTP 页面/API、真实时间、Socket.IO 协议订阅、轨迹时间响应、控制请求拦截、持久化管理员记录。
- `service-state.txt`：重启后的服务 PID、状态与启用状态。
- `python-packages.txt`：venv 内安装包版本。
- 同级 `../rmf-dashboard.png`：浏览器实际系统概览截图。

Windows 对 `/`、`/robots`、`/tasks` 和 API 文档的 HTTP 访问均成功。浏览器检查了系统概览与任务页，捕获到的 error 日志为空。

## 后续实际车队接入

需要先完成真实 RMF 建筑地图/导航图与车辆坐标配准，再按照官方契约提供 fleet 状态、任务状态与适配器到 API 的内部连接。前端部署本身不补齐车端控制租约、分段路径执行、取消确认或断连停车。

本记录只确认原生 Web 部署通过；不作为 Robot 104/113 实车调度或多车交通协调验收。
