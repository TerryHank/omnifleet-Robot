# 广播自动发现与接入

2026-10-18，Asia/Shanghai。

车辆运行 fleet_beacon.py，从实际运行的本地导航进程读取 ROS Domain 和中间件，并按当前网卡广播地址，每秒发送身份包到 UDP 7446。广播包括稳定 robot_id、机器身份、启动身份、Domain 和 Zenoh 端口，不填写调度主机 IP。

Windows 的本机接收器转发到 NAT WSL 的 UDP 7448。WSL 地址由 hostname -I 自动解析，不存储车辆地址。转发包需要本机随机令牌；令牌文件不进入仓库、聊天或本报告。

WSL 的 omnifleet-rmf-discovery.service 按广播来源地址生成 data/run/discovery/ 中的临时 Zenoh 会话文件，启动每车独立的 ROS 客户端。没有静态车辆 IP 回退。广播超过 6 秒未刷新会撤下对应连接并删除临时地址文件，状态仍受原有新鲜度判定约束；收到新广播后重新连接。多网卡广播不会生成重复车辆；不同机器占用同一身份、不同车辆使用同一 ROS 域、车辆占用中央 Domain 42 时拒绝接入。

central.assignments 保存中央 ID、前缀与顺序。原有 car1/car2 分配、motion_enabled 和已保存航点保留。未知 robot_id 自动加入分配列表，默认 motion_enabled=false；接入不代表地图配准、执行许可或实车运动验收通过。现有地图自动配准仍是双车流程；本次未实现三辆以上车辆的自动地图配准。

## 常驻入口

- Windows：%LOCALAPPDATA%/OmniFleet/discovery/windows_discovery_relay.py；HKCU Run 的 OmniFleetDiscovery 在登录时启动；普通 Fox 调度入口也确保接收器已运行。
- WSL：omnifleet-rmf.target 自动带起 omnifleet-rmf-discovery.service；旧 robot104/robot113 固定连接服务不再由 target 拉起。
- 车端：omnifleet-discovery-beacon.service，只广播身份，不发送导航或速度。
- 原 Web 104 观察器等待新鲜广播后才建立连接，广播消失或地址变化后重新发现。

## WSL 手动启动与查询

```bash
cd /home/zhangwnag/workspaces/omnifleet_ws
source env.bash
systemctl --user start omnifleet-rmf.target
systemctl --user status omnifleet-rmf-discovery.service --no-pager
cat data/discovery.json
journalctl --user -u omnifleet-rmf-discovery.service -n 30 --no-pager
```

data/discovery.json 和临时会话中出现的是实际发现的运行时地址，不是源配置中的固定地址。不要手工填回 config/framework.json 的 host 或静态 endpoint。

## 新车一次性部署

新车广播程序和安装步骤位于 [单车分支的车端接入目录](https://github.com/TerryHank/omnifleet-Robot/tree/main/src/system/omnifleet_fleet)。在车上执行安装。广播程序读取本车 `/etc/omnifleet_t2/robot.env` 及运行中的本地导航服务，中央调度继续通过广播发现车辆。

## 当前验收

- 包构建通过；282 项测试通过。
- 113：实际广播经 Windows 转入 NAT WSL，调度 online=true、navigation_ready=true；WSL 接入管理器重启后自动重新发现。
- 隔离 UDP 集成：错误令牌拒绝，广播超时停止惰性测试客户端，更换来源地址后自动重新加入，源配置未改动。测试进程均已退出。
- 没有下发目标、遥控速度或启动实车任务；113 车端 Nav2 PID 307518 未变。
- 104：用户开机后已补部署广播服务，实际自动发现并恢复为 car2；与 113 连续 8 次采样均在线、导航就绪，未重启导航进程。两车当前仍需完成地图会话校验，未执行实车任务。
- 自动审批拒绝了临时停止车端广播的实车断线测试，未给出具体原因；没有执行该动作。生产断线场景没有计为实测通过。


## 通用移植入口（2026-10-18 23:44 更新）

在单车分支的 `src/system/omnifleet_fleet/` 目录运行 `sudo python3 install_beacon.py`。程序安装到 `/usr/local/lib/omnifleet-discovery/`，按本车导航服务的用户和组运行。身份和 ROS 域来自本车配置，安装命令无需 IP 参数。

本车身份和 ROS 域必须唯一，广播需在可互通局域网络内。克隆 machine-id 但不同 boot-id 的同时在线冲突也会拒绝。已用统一安装器更新 104、113，两车实际接入通过；不同用户名/域等移植场景通过隔离测试，最终共 286 项测试通过。未执行运动，未改车端导航参数或身份。
