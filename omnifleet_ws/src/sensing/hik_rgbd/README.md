# hik_rgbd：MV-DT01SNU ROS2 SDK

这是 OmniFleet 基于已验证 MVS 底层驱动提供的 ROS2 接口封装。包名、启动文件和两个可执行入口参考海康官方 `hik_rgbd` 示例；不替换或伪装成厂商的 `libMv3dRgbd.so`。采集、出厂标定和 RGB-D 配准仍由 `omnifleet_hikrobot_rgbd` 实现，只运行一个相机采集进程。

## 话题接口

RGB 与配准深度为原生 RGB 网格 1536×1280；原始深度为传感器原生 640×480，不插值增加深度细节。图像和 CameraInfo 使用 SensorDataQoS（Best Effort、Volatile），同一硬件帧共用时间戳。

| 话题 | ROS 消息类型 | 数据类型 / encoding | frame_id |
|---|---|---|---|
| `/rgb/image_raw` | `sensor_msgs/msg/Image` | uint8×3 / `bgr8` | `camera_color_optical_frame` |
| `/rgb/camera_info` | `sensor_msgs/msg/CameraInfo` | RGB 内参 | `camera_color_optical_frame` |
| `/depth/image_raw` | `sensor_msgs/msg/Image` | uint16 / `16UC1`，单位毫米 | `camera_depth_optical_frame` |
| `/depth/camera_info` | `sensor_msgs/msg/CameraInfo` | 原始深度内参 | `camera_depth_optical_frame` |
| `/aligned_depth_to_color/image_raw` | `sensor_msgs/msg/Image` | uint16 / `16UC1`，单位毫米 | `camera_color_optical_frame` |
| `/aligned_depth_to_color/camera_info` | `sensor_msgs/msg/CameraInfo` | 与 RGB 相同的内参 | `camera_color_optical_frame` |
| `/depth/image_color` | `sensor_msgs/msg/Image` | uint8×3 / `bgr8`，仅显示 | `camera_depth_optical_frame` |

数值 1000 表示 1 米。原始深度的 0、65535 为无效值，配准后无效/遮挡/视场外区域为 0。伪彩图使用 JET 显示 0–1.5 米，超范围颜色饱和，无效点为黑色；不能从伪彩图读取测距值。

与上游旧示例的明确差异：上游 `/depth/image_raw` 是 `bgr8` 伪彩图；按用户选择，此封装的同名话题提供 `16UC1` 真实深度，伪彩图改到 `/depth/image_color`。MV-DT01SNU 是 ToF 相机，没有 EB435i 的左右双目 IR 图，不发布虚构的 `/lir/image_raw` 或 `/rir/image_raw`。

现有接口继续发布：`/camera/color/{image_raw,camera_info}`、`/camera/depth/{image_raw,camera_info}`、`/camera/aligned_depth_to_color/{image_raw,camera_info}`。这些接口与上述对应话题的像素、编码、内参和时间戳相同。课程继续读取现有 `/camera/...` 接口。

RGB 检测框测距使用 RGB 配准深度及其 CameraInfo。原始深度处于深度相机坐标系；光学坐标 X 向右、Y 向下、Z 向前，三维反投影为 `Z=depth_mm/1000`、`X=(u-cx)*Z/fx`、`Y=(v-cy)*Z/fy`。

## 启动与使用

104 常驻服务 `omnifleet-t2-rgbd-camera.service` 启动此 SDK，正常使用直接订阅话题即可。

```bash
source /home/iecme/omnifleet_ws/env.bash
ros2 topic info /rgb/image_raw
ros2 topic echo /depth/image_raw --once --no-arr --qos-reliability best_effort

# 使用常驻采集，在桌面打开本包 RViz 布局
ros2 launch hik_rgbd hik_rgbd_launch.py start_camera:=false use_rviz:=true
```

需要独立启动时先停止相机服务，避免两个进程同时打开同一 USB 相机：

```bash
sudo systemctl stop omnifleet-t2-rgbd-camera.service
ros2 launch hik_rgbd hik_rgbd_launch.py
# 或 ros2 run hik_rgbd image_pipeline_all_in_one
# 或 ros2 run hik_rgbd camera_node
```

独立程序退出后可用 `sudo systemctl start omnifleet-t2-rgbd-camera.service` 恢复常驻采集。两种可执行入口从驱动包同一个 `config/mv_dt01snu.yaml` 读取配置，没有第二份业务参数。ROS `--ros-args` 可正常传入参数覆盖和话题重映射。

配置与标定说明见相邻的 [omnifleet_hikrobot_rgbd](../omnifleet_hikrobot_rgbd/README.md)。上游参考：[Hikrobot/Mv3dRgbdSDK_ROS2](https://gitee.com/Hikrobot/Mv3dRgbdSDK_ROS2)，参考提交 `2af6f856a1e50347fa7df2694fdc951771325518`。
# Gray depth and 3D visualization

`ros2 run hik_rgbd rgbd_visualization` derives visualization streams from the existing
synchronized images and CameraInfo. On 104 it runs in
`omnifleet-t2-rgbd-visualization.service` without opening a second camera handle.

| Topic | Type / meaning |
| --- | --- |
| `/camera/depth/image_gray` | Image, mono8, near bright / far dark, 0–8m display scale |
| `/camera/depth/image_gray_filtered` | Image, mono8, spatial outlier rejection |
| `/camera/depth/points` | PointCloud2, XYZ metres, depth optical frame |
| `/camera/aligned_depth_to_color/points` | PointCloud2, XYZ metres + RGB uint32, color optical frame |
| `/camera/rgbd/visualization_status` | String JSON, source validity, retained fraction, point count |

Clouds run at the available input rate with pixel stride 2. A 5x5 median consistency check rejects
isolated jumps above max(30mm, 2% of Z), retaining original Z for accepted points.
RGB is matched by the exact source header timestamp. No source depth topic is changed.
For registered clouds, filtering runs on the dense native depth grid before factory
projection into RGB coordinates. Only samples equal to the original registered depth
are kept. This avoids rejecting valid points around holes in the sparse 1536×1280 grid.
The camera is rated for 0.2–1.5m; rendered farther samples have not been accepted for
metric accuracy. Raw metric topics remain 16UC1 millimetres.

The camera configuration now includes `depth_exposure_time_us: 1000.0`; this is
independent of RGB exposure. Startup readback is saved under the 104 camera validation
directory in `foxglove_3d/device_features.json`. Before changing deployment files,
the old sources and parameters were saved in `foxglove_3d/before/`.

Display transport uses full-resolution JPEG images and an optional lossless
WebSocket endpoint `ws://192.168.3.104:8766`, forwarding to the unchanged bridge
on port 8765. The service is `omnifleet-t2-vision-display-bridge.service`; its
isolated Python environment uses `requirements-display.txt`. PointCloud2 payloads
are unchanged, verified by matching same-frame SHA-256 hashes. The current SDK
bridge's `use_compression` flag alone did not negotiate compression.

Large Image/CompressedImage/PointCloud2 payloads use native `array.array('B')`
buffers. No Python per-byte validation loops or global assertion disabling are
used. Gray/cloud encoding is performed on demand; RGB cloud inputs are subscribed
only while a viewer requests the RGB cloud.

