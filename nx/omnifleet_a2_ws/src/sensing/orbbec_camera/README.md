# orbbec_camera｜OmniFleet 工作区介绍

Orbbec Camera package

- 功能域：`sensing`；源码：`/home/iecme/omnifleet_ws/src/sensing/orbbec_camera`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-10-14目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [launch/](launch)：ROS启动入口。现有项：`astra.launch.py`、`astra2.launch.py`、`astra_adv.launch.py`、`astra_embedded_s.launch.py`、`astra_pro2.launch.py`、`astra_pro_plus.launch.py`、`astra_stereo_u3.launch.py`、`dabai.launch.py`、`dabai_d1.launch.py`、`dabai_dcl.py` 等。
- [config/](config)：业务/算法运行配置。现有项：`.gitkeep`、`OrbbecSDKConfig_v1.0.xml`、`camera_params.yaml`、`depthfilter`。
- [scripts/](scripts)：可执行脚本。现有项：`99-obsensor-libusb.rules`、`echo_extrintisics.sh`、`generate_orbbec_launch.sh`、`group_image.py`、`install_udev_rules.sh`、`list_ob_devices.sh`、`monitor_fd.sh`、`plot_stat.py`、`receive_pc.py`、`save_images.sh` 等。

## 工作区内声明依赖

- [orbbec_camera_msgs](../orbbec_camera_msgs/README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
