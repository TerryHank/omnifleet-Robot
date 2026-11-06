# omnifleet_behaviors｜OmniFleet 工作区介绍

导航行为、地图工作流和语音控制集成。

- 功能域：`control`；源码：`/home/iecme/omnifleet_ws/src/control/omnifleet_behaviors`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [launch/](launch)：ROS启动入口。当前项：`wonderecho_voice.launch.py`。
- [scripts/](scripts)：可执行脚本。当前项：`traffic_light_nav_supervisor`、`wonderecho_voice`。
- [test/](test)：测试。当前项：`test_traffic_light_navigation.py`、`test_wonderecho_voice_logic.py`。

## 工作区内声明依赖

- [omnifleet_interfaces](../../common/omnifleet_interfaces/README.omnifleet.md)

## 原有资料

- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
