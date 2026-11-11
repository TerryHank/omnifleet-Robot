# omnifleet_a2_vision

OmniFleet 视觉课程的可复用 ROS 2 实现包。代码按三层组织：经典视觉、学习型视觉、功能联调；学生通过 `omnifleet_a2_tutorials` 中的 32 个课程 Launch 启动，不需要直接修改源码。

当前实现覆盖：

- 相机监控、OpenCV、颜色、二维码、AprilTag、深度、车道线与 KCF；
- YOLO 通用目标、行人、红绿灯、路标、车辆、姿态、人脸与车牌识别；
- 检测跟踪、目标深度、视觉与激光风险融合、交通事件、安全控制、视觉导航候选；
- 颜色跟随、人和物体跟随、车道巡线、目标导航、多模态避障、边缘部署、交通安全项目；
- 数据集训练、PyTorch CUDA 推理、ONNX 导出和 TensorRT 构建/基准测试。

## Python 运行环境

远端 Jetson 不使用 Conda。统一由 `uv` 管理独立运行环境，并通过 `--system-site-packages` 复用 ROS 2 Humble 的 `rclpy`、`cv_bridge` 等系统包：

```bash
source /home/iecme/omnifleet_a2_vision_runtime/activate_remote_vision.sh
```

运行环境包含适配 JetPack 6 / CUDA 12.6 的 PyTorch、torchvision 与 Ultralytics。模型默认优先使用 PyTorch CUDA；ONNX 文件保留给跨平台验证和 TensorRT 转换。

## KCF 双流实现

参数化 KCF 节点使用以下接口：

- 高频跟踪彩色流：默认 `/tof/color/image_raw`，每帧只做 KCF 更新和结果图发布
- 对齐彩色流：默认 `/tof/rgbd/color/image_raw`
- 对齐深度流：默认 `/tof/aligned_depth_to_color/image_raw`
- 调试图像：`/omnifleet_a2/vision/kcf/image`
- 底盘速度（仅 `enable_motion:=true` 时创建发布者）：`/cmd_vel`
- 深度编码：支持 `16UC1` 和 `32FC1`
- 默认 `enable_motion=false`

对齐彩色流和深度流通过 ApproximateTime 配对，只负责刷新深度和运动候选，不会再次执行 KCF。这样既兼容 RGB-D 同频的 1/1 采集，也兼容高频彩色、低频深度的 30/5 采集。控制由固定频率定时器发布；跟踪或深度超过 `tracking_timeout` / `depth_timeout`、RGB-D 时间戳差超过 `max_pair_delta`、深度无效或目标丢失时，都会立即输出零速。生产相机实测 RGB-D 时间差约为 0.72 秒，因此默认 `max_pair_delta=0.8`；它仍小于课程配置的一秒配对上限。

生产底盘的非零启动阈值是 `0.40 m/s`。本节点以相同的 `minimum_linear_speed=0.40` 和 `max_linear_speed=0.40` 生成线速度，并将距离死区设为 `0.15 m`，避免视觉端声称 `0.15 m/s`、底盘却实际提升到 `0.40 m/s`。这些参数仍需在实车低风险场地标定。

GUI 模式下首次收到高频彩色图像后会按原图像素尺寸打开选框窗口。鼠标拖出目标框并松开即可确认；按键焦点必须在图像窗口，终端回车不参与选框。无 `DISPLAY` 时请通过 Launch 参数提供初始 ROI。

```bash
ros2 launch omnifleet_a2_vision kcf_follower.launch.py \
  use_gui:=false roi_x:=300 roi_y:=200 roi_width:=200 roi_height:=180
```

运动输出不能直接接最终 `/cmd_vel`，必须先通过整车仲裁与碰撞监控。
运动节点只允许标准话题 `/cmd_vel`；默认 `enable_motion:=false` 时不创建速度发布者。视觉运动与 Nav2 必须互斥运行。

## 相机课程模式

远端提供可恢复的相机配置切换工具。进入视觉课程前可切换高帧率彩色模式，结束后恢复生产 RGB-D 服务：

```bash
sudo omnifleet-camera-profile rgb_fast
sudo omnifleet-camera-profile restore
```

课程测试结束必须执行 `restore`，保证原有建图、导航与深度链路不被课程配置长期占用。
