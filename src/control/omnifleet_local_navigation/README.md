# omnifleet_local_navigation｜OmniFleet 工作区介绍

独立单车/多点导航任务执行、LOCAL/FLEET 控制权仲裁及唯一底盘安全速度出口。

- 功能域：`control`；源码：`/home/iecme/omnifleet_ws/src/control/omnifleet_local_navigation`。
- colcon 类型：`(ros.ament_python)`。
- 状态（2026-10-14目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [setup.py](setup.py)：Python包安装与console_scripts入口。
- [test/](test)：测试。现有项：`__pycache__`、`test_fleet_lease.py`、`test_task_policy_fleet_updates.py`。

Python可执行入口（读取setup.py，未启动节点）：

- `local_navigation=omnifleet_local_navigation.runtime:main`

## 工作区内声明依赖

- [omnifleet_navigation_interfaces](../../common/omnifleet_navigation_interfaces/README.md)

## 104 当前约定

速度链：Nav2 → `/navigation/nav_cmd_vel` → local_navigation → `/navigation/cmd_vel_safe` → 底盘。手动输入为 `/cmd_vel`。配置中的命名空间与ROS_DOMAIN_ID分别核对。

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
