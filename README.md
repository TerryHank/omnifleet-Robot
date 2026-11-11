# OmniFleet 126

[工作区与运行入口](README.workspace.md) · [源码索引](src/README.md) · [维护约定](AGENTS.md)

## 查状态

```bash
cd /home/iecme/omnifleet_ws
source ./env.bash
systemctl status omnifleet-t2-{chassis,airy,mola,pure-lio-nav2,foxglove}.service omnifleet-local-navigation.service --no-pager
ros2 run omnifleet_bringup robot_doctor --scope nav
```

按需查看日志。

```bash
journalctl -u omnifleet-t2-mola.service -u omnifleet-t2-pure-lio-nav2.service -u omnifleet-local-navigation.service -n 80 --no-pager
```

## 启动

需要恢复车端服务时，按 [维护约定](AGENTS.md) 核对当前任务和运动状态，再启动主链。

```bash
sudo systemctl start omnifleet-t2-{chassis,airy,mola,pure-lio-nav2}.service omnifleet-local-navigation.service
```
