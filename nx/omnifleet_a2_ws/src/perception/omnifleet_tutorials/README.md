# omnifleet_tutorials

面向操作员和初学者的任务入口：

- `mapping_keyboard.launch.py`：键盘建图；
- `waypoint_navigation.launch.py`：GLIM在线定位建图与Nav2单点导航；
- `mapping_save_view_stop.launch.py`：保存建图成果并安全停止；
- `waypoint_save_view_stop.launch.py`：保存导航会话并安全停止。
- `vision_02_07_kcf.launch.py`：KCF 目标跟踪学生入口；默认关闭运动输出，支持 GUI 拖框和无界面 ROI 参数。

`docs/` 保存工程架构约束和面向远端整车工作流的故障自查资料。

KCF 课程入口：

```bash
cd /home/iecme/ackermann_mid360_glim_ws
source runtime/activate_remote_vision.sh
ros2 launch omnifleet_tutorials vision_02_07_kcf.launch.py
```

默认通过高频 `/tof/color/image_raw` 跟踪目标并发布 `/omnifleet_vision/kcf/image`。GUI 中拖框并松开鼠标即确认，不需要在终端按回车；无图形桌面时可从学生入口传入 `roi_x/roi_y/roi_width/roi_height`。只有在 `/cmd_vel_vision` 已接入整车安全仲裁后，才允许设置 `enable_motion:=true`。

默认命令只做视觉跟踪。黄色框稳定包住目标且画面显示有效数值距离后，才能在现场看护下继续车辆跟随验收。

## 视觉课程入口

`vision_02_*.launch.py`、`vision_03_*.launch.py`、`vision_04_*.launch.py` 分别对应单项实验、模块联调和阶段项目，共 32 个学生入口。每个入口固定课程功能编号，再转入 `omnifleet_vision/launch/course_function.launch.py` 编排所需节点和模型。

例如：

```bash
# 单项实验：红绿灯检测
ros2 launch omnifleet_tutorials vision_02_14_traffic_light.launch.py

# 模块联调：目标检测与跟踪
ros2 launch omnifleet_tutorials vision_03_02_detection_tracking.launch.py

# 阶段项目：红绿灯、行人与路标安全决策
ros2 launch omnifleet_tutorials vision_04_07_traffic_safety.launch.py
```

所有会产生运动候选的入口默认 `enable_motion:=false`，且只能发布 `/cmd_vel_vision`。实车运动前必须确认该话题已经接入 `twist_mux -> collision_monitor -> /cmd_vel` 安全链，并由现场人员看护。

训练和 TensorRT 入口不会猜测输入路径；未提供数据集、模型或输出路径时会安全退出并打印中文提示。远端 Python 环境统一使用 `uv`。
