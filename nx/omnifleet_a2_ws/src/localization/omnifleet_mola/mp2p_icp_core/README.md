# mp2p_icp_core｜OmniFleet 工作区介绍

C++ libraries for multi primitive-to-primitive (MP2P) ICP algorithms and point cloud processing pipelines, plus headless CLI applications. No GUI/display dependencies; see mp2p_icp_viz for the GUI apps.

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/omnifleet_mola/mp2p_icp_core`。
- colcon 类型：`(ros.cmake)`。
- 状态（2026-10-14目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [scripts/](scripts)：可执行脚本。现有项：`formatter.sh`、`kitti-batch-convert.py`、`kitti-run-seq.py`、`viewSimilarityImages.m`。
- [tests/](tests)：测试。现有项：`CMakeLists.txt`、`test-georef-yaml.cpp`、`test-mp2p_FilterAbsoluteTimestamp.cpp`、`test-mp2p_FilterByExpression.cpp`、`test-mp2p_FilterByIntensity.cpp`、`test-mp2p_FilterByRange.cpp`、`test-mp2p_FilterByRing.cpp`、`test-mp2p_FilterClear.cpp`、`test-mp2p_FilterCurvature.cpp`、`test-mp2p_FilterDecimate.cpp` 等。

## 工作区内声明依赖

- [mola_common](../mola_common/README.omnifleet.md)
- [mola_imu_preintegration](../mola_imu_preintegration/README.omnifleet.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
