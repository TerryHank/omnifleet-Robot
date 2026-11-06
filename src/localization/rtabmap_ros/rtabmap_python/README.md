# rtabmap_python｜OmniFleet 工作区介绍

RTAB-Map's python package.

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/rtabmap_ros/rtabmap_python`。
- colcon 类型：`(ros.ament_python)`。
- 状态（2026-11-06目录核对）：当前 install 下未发现同名目录；按源代码/备用组件登记，不能称为已部署运行。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [setup.py](setup.py)：Python包安装与console_scripts入口。
- [test/](test)：测试。当前项：`test_copyright.py`、`test_flake8.py`、`test_pep257.py`。

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
