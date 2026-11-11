# omnifleet_sensor_processing｜OmniFleet 工作区介绍

相机、点云与 Airy IMU 处理实现；含可选去畸变代码，但104当前主链已旁路运动去畸变。

- 功能域：`sensing`；源码：`/home/iecme/omnifleet_ws/src/sensing/omnifleet_sensor_processing`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-10-14目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [scripts/](scripts)：可执行脚本。现有项：`fresh_pointcloud_filter.py`、`lidar_velocity.py`、`pointcloud_radius_filter`、`sensor_clock_guard.py`、`usb_camera_publisher`。

## 104 当前约定

包内可选去畸变实现仍存在，但104当前运行的MOLA主链绕过运动补偿；说明代码能力不等于当前启用。

## 原有资料

- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。

## Airy IMU 当前接口

`airy_imu_adapter_buffered`接收驱动滤波输出`/rslidar_imu_data`，输出`/rslidar_imu_data_corrected`，frame=`rslidar`，不加车辆前缀。2026-10-14三轴gyro零偏已用104本机60秒静止数据重标定。协方差与数值执行同一轴旋转，加速度协方差按比例平方换算。底盘`/imu/data_raw`不是此节点输入。
