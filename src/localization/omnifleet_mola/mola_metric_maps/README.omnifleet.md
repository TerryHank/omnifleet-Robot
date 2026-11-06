# mola_metric_maps｜OmniFleet 工作区介绍

Advanced metric map classes, using the generic `mrpt::maps::CMetricMap` interface, for use in other MOLA odometry and SLAM modules.

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/omnifleet_mola/mola_metric_maps`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [tests/](tests)：测试。当前项：`CMakeLists.txt`、`README-sanitizers.md`、`export-covariance.cpp`、`run-sanitizers.sh`、`test-mola_metric_maps_hashedvoxels.cpp`、`test-mola_metric_maps_incrementalpointcloud-stress.cpp`、`test-mola_metric_maps_incrementalpointcloud.cpp`、`test-mola_metric_maps_index3d_hash.cpp`、`test-mola_metric_maps_keyframemap.cpp`、`test-mola_metric_maps_ndt.cpp`、`test-mola_metric_maps_tsdf.cpp`、`test-occgrid.cpp`、`test-options-ini-io.cpp`、`test-serialization.cpp`、`test-sparsevoxelpointcloud.cpp`、`tsan-suppressions.txt`。

## 工作区内声明依赖

- [mola_common](../mola_common/README.omnifleet.md)
- [mola_kernel](../mola_kernel/README.omnifleet.md)
- [mp2p_icp](../mp2p_icp/README.md)

## 原有资料

- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
