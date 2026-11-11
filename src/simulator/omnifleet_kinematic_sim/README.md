# omnifleet_kinematic_sim｜OmniFleet 工作区介绍

与 ROS 话题契约相匹配的无串口车辆运动学仿真。

- 功能域：`simulator`；源码：`/home/iecme/omnifleet_ws/src/simulator/omnifleet_kinematic_sim`。
- colcon 类型：`(ros.ament_python)`。
- 状态（2026-10-14目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [setup.py](setup.py)：Python包安装与console_scripts入口。
- [launch/](launch)：ROS启动入口。现有项：`standalone_sim.launch.py`。
- [test/](test)：测试。现有项：`test_kinematics.py`。

Python可执行入口（读取setup.py，未启动节点）：

- `ackermann_sim_driver = omnifleet_kinematic_sim.ackermann_sim_driver:main`

## 工作区内声明依赖

- [omnifleet_description](../../vehicle/omnifleet_description/README.omnifleet.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
