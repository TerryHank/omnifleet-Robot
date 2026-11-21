# omnifleet_a2_tutorials

面向操作员和初学者的任务入口：

- `mapping_keyboard.launch.py`：键盘建图；
- `waypoint_navigation.launch.py`：GLIM在线定位建图与Nav2单点导航；
- `mapping_save_view_stop.launch.py`：保存建图成果并安全停止；
- `waypoint_save_view_stop.launch.py`：保存导航会话并安全停止。
- `vision_02_07_kcf.launch.py`：KCF 目标跟踪学生入口；默认关闭运动输出，支持 GUI 拖框和无界面 ROI 参数。
- `human_follow_chassis.launch.py`：检测人体、读取深度并驱动底盘保持距离；
- `kcf_follow_chassis.launch.py`：鼠标框选任意目标、读取深度并驱动底盘跟随。

`docs/` 保存工程架构约束和面向远端整车工作流的故障自查资料。

KCF 课程入口：

```bash
cd /home/iecme/omnifleet_a2_ws
source runtime/activate_remote_vision.sh
sudo omnifleet-camera-profile rgb_fast
ros2 launch omnifleet_a2_tutorials vision_02_07_kcf.launch.py
```

默认通过高频 `/tof/color/image_raw` 跟踪目标并发布 `/omnifleet_a2/vision/kcf/image`。GUI 中拖框并松开鼠标即确认，不需要在终端按回车；无图形桌面时可从学生入口传入 `roi_x/roi_y/roi_width/roi_height`。运动默认关闭；显式设置 `enable_motion:=true` 前必须停止Nav2，因为视觉跟随会直接发布 `/cmd_vel`。

需要最高视觉帧率时，先运行 `sudo omnifleet-camera-profile rgb_fast`：相机输入约 29.7～30.1 FPS，KCF 结果约 24～29 FPS，但没有深度。需要距离跟随时改用 `rgbd_course`，实验结束执行 `sudo omnifleet-camera-profile restore`。

默认命令只做视觉跟踪。黄色框稳定包住目标且画面显示有效数值距离后，才能在现场看护下继续车辆跟随验收。

## 独立底盘跟随程序

这两个程序与 GLIM/Nav2 导航程序互斥，启动前必须先停止导航 launch。程序默认只看不动；首次实车启用前先架起驱动轮。

```bash
cd /home/iecme/omnifleet_a2_ws
source runtime/activate_remote_vision.sh

# 人体跟随：自动选择检测到的人，保持约 0.8 m 距离
ros2 launch omnifleet_a2_tutorials human_follow_chassis.launch.py enable_motion:=false

# KCF 跟随：在弹出的画面中拖框，松开鼠标即确认目标
ros2 launch omnifleet_a2_tutorials kcf_follow_chassis.launch.py enable_motion:=false
```

确认图像、目标框和距离稳定，并停止 Nav2 后，把对应命令的 `enable_motion` 改为 `true`。视觉节点会直接发布标准 `/cmd_vel`；默认关闭运动时不创建速度发布者。

## 视觉课程入口

`vision_02_*.launch.py`、`vision_03_*.launch.py`、`vision_04_*.launch.py` 分别对应单项实验、模块联调和阶段项目，共 32 个学生入口。每个入口固定课程功能编号，再转入 `omnifleet_a2_vision/launch/course_function.launch.py` 编排所需节点和模型。

例如：

```bash
cd /home/iecme/omnifleet_a2_ws
source runtime/activate_remote_vision.sh

# 单项实验：红绿灯检测
ros2 launch omnifleet_a2_tutorials vision_02_14_traffic_light.launch.py

# 模块联调：目标检测与跟踪
ros2 launch omnifleet_a2_tutorials vision_03_02_detection_tracking.launch.py

# 阶段项目：红绿灯、行人与路标安全决策
ros2 launch omnifleet_a2_tutorials vision_04_07_traffic_safety.launch.py
```

所有视觉课程默认 `enable_motion:=false`。视觉运动与 Nav2 必须互斥启动，保证 `/cmd_vel` 同一时刻最多只有一个发布节点。

除模型训练和 TensorRT 基准外，30 个实时视觉课程默认打开对应实时窗口，同时继续发布各自调试图话题。经典视觉和 KCF 自行显示，其余 23 个学习型视觉、模块联调和阶段项目使用统一显示节点。按 `q` 或 `Esc` 关闭窗口；无 `DISPLAY` 时自动退回调试图话题。

训练和 TensorRT 入口不会猜测输入路径；未提供数据集、模型或输出路径时会安全退出并打印中文提示。远端 Python 环境统一使用 `uv`。
