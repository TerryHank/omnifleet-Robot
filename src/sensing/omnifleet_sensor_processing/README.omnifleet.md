# omnifleet_sensor_processing

相机、点云和 Airy IMU 的预处理。车端 MOLA 的去畸变配置见 [工作区说明](../../../README.workspace.md)。

`airy_imu_adapter_buffered` 订阅 `/rslidar_imu_data`，发布 `/rslidar_imu_data_corrected`。轴映射与零偏参数见 [airy_imu_calibration.yaml](config/airy_imu_calibration.yaml)。

[包声明](package.xml) · [CMakeLists.txt](CMakeLists.txt) · [IMU 源码](src/airy_imu_adapter_buffered.cpp) · [原有包说明](README.md)
