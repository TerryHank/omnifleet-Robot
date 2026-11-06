# mola_yaml｜OmniFleet 工作区介绍

YAML helper library common to MOLA modules

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/omnifleet_mola/mola_yaml`。
- colcon 类型：`(ros.cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [tests/](tests)：测试。当前项：`CMakeLists.txt`、`d1`、`test-yaml-parser.cpp`、`test1.yaml`、`test2.yaml`、`test_define_base.yaml`、`test_define_chain_middle.yaml`、`test_define_nested.yaml`、`test_import_base.yaml`、`test_import_o2.yaml`、`test_import_top.yaml`、`test_include1.yaml`、`test_include2.yaml`、`test_include3.yaml`。

## 工作区内声明依赖

- [mola_common](../mola_common/README.omnifleet.md)

## 原有资料

- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
