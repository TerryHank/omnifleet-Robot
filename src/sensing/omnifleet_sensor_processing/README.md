<!-- OMNIFLEET_WORKSPACE_DOC_LINK -->
本工作区职责、入口及104约定见 [README.omnifleet.md](README.omnifleet.md)。

# omnifleet_sensor_processing

Camera, point-cloud, deskew and Airy IMU processing.

Extracted from the original OmniFleet packages. Legacy imports and executables remain available.

Original package license declarations are retained: MIT, Apache-2.0. See the relocation manifest for file provenance.

104雷达IMU标定唯一源码入口：config/airy_imu_calibration.yaml；安装到包share/config后由system/omnifleet_bringup加载。输入/rslidar_imu_data，输出/rslidar_imu_data_corrected，零偏/外参/单位换算沿用已标定值。
