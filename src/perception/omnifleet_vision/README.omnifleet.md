# omnifleet_vision｜OmniFleet 工作区介绍

视觉模型与推理集成；模型权重放 omnifleet_data/ml_models。

- 功能域：`perception`；源码：`/home/iecme/omnifleet_ws/src/perception/omnifleet_vision`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [launch/](launch)：ROS启动入口。当前项：`course_function.launch.py`、`kcf_follower.launch.py`、`marker_follow.launch.py`。
- [config/](config)：业务/算法运行配置。当前项：`apriltag_36h11_210mm.yaml`、`kcf_follower.yaml`、`mvs_rgb_fast.yaml`、`mvs_rgbd_course.yaml`。
- [scripts/](scripts)：可执行脚本。当前项：`classical`、`course_gui_overlay_node.py`、`image_display_node.py`、`integration`、`kcf_follower_python_node.py`、`ml`。
- [test/](test)：测试。当前项：`test_classical_vision.py`、`test_course_controllers.py`、`test_course_gui_overlay.py`、`test_depth_arrival.py`、`test_depth_reuse.py`、`test_foreground_observation.py`、`test_gesture_person_follow.py`、`test_kcf_contract.py`、`test_ml_vision.py`、`test_nanotrack.py`、`test_nanotrack_scale.py`、`test_roi_box_geometry.py`、`test_roi_template_guard.py`、`test_standoff_strategy.py`、`test_vision_integration.py`。

## 原有资料

- [README.md](README.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
