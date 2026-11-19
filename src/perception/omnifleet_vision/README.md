<!-- OMNIFLEET_WORKSPACE_DOC_LINK -->
本工作区职责、入口及104约定见 [README.omnifleet.md](README.omnifleet.md)。

# omnifleet_vision

OmniFleet 视觉课程的可复用 ROS 2 实现包。代码按三层组织：经典视觉、学习型视觉、功能联调；学生通过 `omnifleet_tutorials` 中的 32 个课程 Launch 启动，不需要直接修改源码。

当前实现覆盖：

- 相机监控、OpenCV、颜色、二维码、AprilTag、深度、车道线与 KCF；
- YOLO 通用目标、行人、红绿灯、路标、车辆、姿态、人脸与车牌识别；
- 检测跟踪、目标深度、视觉与激光风险融合、交通事件、安全控制、视觉导航候选；
- 颜色跟随、人和物体跟随、车道巡线、目标导航、多模态避障、边缘部署、交通安全项目；
- 数据集训练、PyTorch CUDA 推理、ONNX 导出和 TensorRT 构建/基准测试。

## Python 运行环境

远端 Jetson 不使用 Conda。统一由 `uv` 管理独立运行环境，并通过 `--system-site-packages` 复用 ROS 2 Humble 的 `rclpy`、`cv_bridge` 等系统包：

```bash
source /home/iecme/omnifleet_ws/env.bash
source /home/iecme/omnifleet_ws/.env/vision/bin/activate
```

运行环境包含适配 JetPack 6 / CUDA 12.6 的 PyTorch、torchvision 与 Ultralytics。模型默认优先使用 PyTorch CUDA；ONNX 文件保留给跨平台验证和 TensorRT 转换。

## KCF 双流实现

参数化 KCF 节点使用以下接口：

- 高频跟踪彩色流：默认 `/camera/color/image_raw`，每帧只做 KCF 更新和结果图发布
- 对齐彩色流：默认 `/camera/color/image_raw`
- 对齐深度流：默认 `/camera/depth/image_raw`
- 调试图像：`/omnifleet_vision/kcf/image`
- 运动候选：`/cmd_vel_vision`
- 深度编码：支持 `16UC1` 和 `32FC1`
- 默认 `enable_motion=false`

对齐彩色流和深度流通过 ApproximateTime 配对，只负责刷新深度和运动候选，不会再次执行 KCF。这样既兼容 RGB-D 同频的 1/1 采集，也兼容高频彩色、低频深度的 30/5 采集。控制由固定频率定时器发布；跟踪或深度超过 `tracking_timeout` / `depth_timeout`、RGB-D 时间戳差超过 `max_pair_delta`、深度无效或目标丢失时，都会立即输出零速。生产相机实测 RGB-D 时间差约为 0.72 秒，因此默认 `max_pair_delta=0.8`；它仍小于课程配置的一秒配对上限。

生产底盘的非零启动阈值是 `0.40 m/s`。本节点以相同的 `minimum_linear_speed=0.40` 和 `max_linear_speed=0.40` 生成线速度，并将距离死区设为 `0.15 m`，避免视觉端声称 `0.15 m/s`、底盘却实际提升到 `0.40 m/s`。这些参数仍需在实车低风险场地标定。

GUI 模式下首次收到高频彩色图像后会按原图像素尺寸打开选框窗口。鼠标拖出目标框并松开即可确认；按键焦点必须在图像窗口，终端回车不参与选框。无 `DISPLAY` 时请通过 Launch 参数提供初始 ROI。

```bash
ros2 launch omnifleet_vision kcf_follower.launch.py \
  use_gui:=false roi_x:=300 roi_y:=200 roi_width:=200 roi_height:=180
```

运动输出不能直接接最终 `/cmd_vel`，必须先通过整车仲裁与碰撞监控。
节点只允许运动候选话题 `/cmd_vel_vision`，`/cmd_vel` 和相对话题 `cmd_vel` 均会在启动时被拒绝。

## 相机课程模式

远端提供可恢复的相机配置切换工具。进入视觉课程前可切换高帧率彩色模式，结束后恢复生产 RGB-D 服务：

```bash
sudo omnifleet-camera-profile rgb_fast
sudo omnifleet-camera-profile restore
```

课程测试结束必须执行 `restore`，保证原有建图、导航与深度链路不被课程配置长期占用。


## 04.08 单模型手势人体跟随

104 上的 `gesture_person_follow_node.py` 使用一个 RTMW-m COCO-WholeBody ONNX 模型。
每帧仅一次 ONNX Runtime `session.run`，输出133个关键点，其中双手各21点；
不加载 MediaPipe 的人体检测、姿态、手掌检测、手部关键点四个独立网络。
使用104既有 ONNX Runtime GPU 1.20.0，CUDAExecutionProvider 执行主体计算；
少量 Slice/Concat 算子由CPU执行，本次未强制转换TensorRT或FP16。

模型路径：`/home/iecme/omnifleet_data/ml_models/omnifleet_vision/vendor/rtmw/end2end.onnx`。
ROS参数 `model_path` 可指定此文件。输入直接仿射到192x256后再归一化，避免全分辨率浮点处理。
模型来源、下载URL及SHA256保存在同目录 `model-source.json`。

RTMW是单人区域姿态模型；本适配以整幅图作为该区域，不另调用人体检测器。
适合画面中以一个人为主，不能视作可靠的多人检测/选择或人员身份锁定方案。
模型本身会输出身体点；跟随控制只使用这些点计算出的框中心和配准深度，不使用骨骼运动学。
握拳、张掌、1/2/3继续由21个手部关键点判断，原有话题、状态机、深度单位和运动配置保持。

`/vision/gesture_follow/status` 新增 `model_name`、`model_count`、`inference_calls`、
`execution_provider`、`preprocess_ms`、`forward_ms`、`postprocess_ms`；
`inference_ms`沿用整段识别处理耗时，`cuda_target=null`表示不再使用OpenCV DNN目标编号。

2026-10-21现场采样445帧：每帧一个模型、一次调用，CUDA，深度有效接收，运动输出关闭。
五种手势均有输出；208帧unknown（约47%），不能据此声称稳定准确或完成实车运动验收。
均值：预处理6.84ms、forward接口42.67ms、后处理2.02ms、识别处理60.28ms；
状态约7.43Hz、显示约6.47Hz。此为当时场景及导航并发负载下的结果，不保证固定帧率。


## Foreground tracking on104 (2026-10-23)

02.07 selected-object tracking defaults to NanoTrack V2 / OpenCV4.10 CUDA FP16.
The KCF case option uses OpenCV KCF CPU with the same foreground input. The
standalone original C++ KCF implementation remains available in its existing
launch. C++ controller/display public topics and2m hot distance are preserved.
Color uses the existing HSV mask; generic objects use depth continuity. NanoTrack
initialization/update consume foreground-conditioned pixels, not a debug-only
overlay. Raw detector boxes maintain association IDs; foreground refines visual
observations. Expired model instances can be reused with a new template/ID.
The selected follow target gets high-frequency native range; other object
candidates can reuse short-lived mask estimates with original depth timestamps.
RGB reception is separate from inference/drawing, with only the latest frame held.
Native depth outputs reuse the tracker's component instead of a second box median.
Unavailable foreground/range is reported explicitly; existing RGB tracking can
continue as fallback. No confidence/motion gates or SAM model were added.

## Depth arrival and HD display (2026-10-23)

RGB is buffered for delayed native-depth arrival and only the newest covered frame is processed. Depth wakes the worker; the existing200ms matching and500ms controller freshness limits stay unchanged. Foreground forwarding avoids a duplicate native-depth subscription. KCF/NanoTrack directly publishes full-resolution JPEG at the existing compressed topic; the raw image topic remains on demand. This removes the extra raw HD relay. See depth_match_20261023 validation for measured causes and live acceptance limits.
