# omnifleet_fleet｜目录说明

旧兼容运行入口、作用域 remap、env/start/run 脚本。许多旧文件是指向新功能包的软链接，不另建一套实现。

- [relocalization/](relocalization)
- [zenoh-patched-v2/](zenoh-patched-v2)

上级域说明：[README.md](../README.md)。执行入口以实际服务和配置为准。

## 车端身份广播

在车端进入本目录，执行 `sudo python3 install_beacon.py`。安装器将同目录的 `fleet_beacon.py` 安装到 `/usr/local/lib/omnifleet-discovery/`，并按本地导航服务的用户和组启用 `omnifleet-discovery-beacon.service`。广播身份来自本车的 `/etc/omnifleet_t2/robot.env` 和运行中的本地导航进程，无需填写调度主机 IP。

中央端的接收和部署说明见 [广播自动发现与接入](https://github.com/TerryHank/omnifleet-Robot/blob/dispatch/src/system/omnifleet_rmf_adapter/BROADCAST_DISCOVERY.md)。
