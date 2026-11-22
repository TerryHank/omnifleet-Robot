# mola_academic_datasets｜OmniFleet 工作区介绍

Metapackage with all packages supporting reading academic datasets.

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/omnifleet_mola/mola_academic_datasets`。
- colcon 类型：`(ros.cmake)`。
- 状态（2026-10-14目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。

## 工作区内声明依赖

- [kitti_metrics_eval](../kitti_metrics_eval/README.omnifleet.md)
- [mola_input_euroc_dataset](../mola_input_euroc_dataset/README.omnifleet.md)
- [mola_input_kitti360_dataset](../mola_input_kitti360_dataset/README.omnifleet.md)
- [mola_input_kitti_dataset](../mola_input_kitti_dataset/README.omnifleet.md)
- [mola_input_mulran_dataset](../mola_input_mulran_dataset/README.omnifleet.md)
- [mola_input_paris_luco_dataset](../mola_input_paris_luco_dataset/README.omnifleet.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
