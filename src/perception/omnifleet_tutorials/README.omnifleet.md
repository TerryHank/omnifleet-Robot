# omnifleet_tutorials｜OmniFleet 工作区介绍

面向操作者的建图、导航和视觉示例，入口位于 perception。

- 功能域：`perception`；源码：`/home/iecme/omnifleet_ws/src/perception/omnifleet_tutorials`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [launch/](launch)：ROS启动入口。当前项：`robot_kcf.launch.py`、`vision_02_01_camera_monitor.launch.py`、`vision_02_03_opencv.launch.py`、`vision_02_04_color.launch.py`、`vision_02_05_qr.launch.py`、`vision_02_06_apriltag.launch.py`、`vision_02_07_kcf.launch.py`、`vision_02_08_human_perception.launch.py`、`vision_02_09_yolo.launch.py`、`vision_02_10_depth.launch.py`、`vision_02_11_model_training.launch.py`、`vision_02_12_tensorrt.launch.py`、`vision_02_13_pedestrian.launch.py`、`vision_02_14_traffic_light.launch.py`、`vision_02_16_vehicle.launch.py`、`vision_02_17_license_plate.launch.py`、`vision_03_01_camera_topics.launch.py`、`vision_03_02_detection_tracking.launch.py`、`vision_03_03_target_depth.launch.py`、`vision_03_04_vision_lidar.launch.py`、`vision_03_05_traffic_events.launch.py`、`vision_03_06_chassis_control.launch.py`、`vision_03_07_lane_integration.launch.py`、`vision_03_08_vision_nav.launch.py`、`vision_03_09_edge_deployment.launch.py`、`vision_04_01_color_follow.launch.py`、`vision_04_02_human_object_follow.launch.py`、`vision_04_03_lane_project.launch.py`、`vision_04_04_object_navigation.launch.py`、`vision_04_05_multimodal_avoidance.launch.py`、`vision_04_06_edge_detection.launch.py`、`vision_04_07_traffic_safety.launch.py`、`vision_04_08_gesture_person_follow.launch.py`、`vision_04_09_body_tracking.launch.py`。
- [test/](test)：测试。当前项：`test_vision_course_launches.py`。

## 工作区内声明依赖

- [omnifleet_behaviors](../../control/omnifleet_behaviors/README.omnifleet.md)
- [omnifleet_bringup](../../system/omnifleet_bringup/README.omnifleet.md)
- [omnifleet_vision](../omnifleet_vision/README.omnifleet.md)

## 原有资料

- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
