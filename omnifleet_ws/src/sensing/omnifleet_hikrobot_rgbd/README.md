# omnifleet_hikrobot_rgbd

104 号车 `MV-DT01SNU` ROS 2 驱动，发布：

- `/camera/color/image_raw`：原生最高 1536×1280 `bgr8`
- `/camera/depth/image_raw`：640×480 `16UC1`，毫米深度
- `/camera/aligned_depth_to_color/image_raw`：1536×1280 `16UC1`，配准到 RGB 的毫米深度；网格空洞保留，不增加原生深度细节
- 对应的 `/camera/*/camera_info`

同时提供 [hik_rgbd ROS2 SDK 接口](../hik_rgbd/README.md)：`/rgb/image_raw`、`/depth/image_raw`、`/aligned_depth_to_color/image_raw` 及对应 CameraInfo，像素、内参和时间戳与现有接口一致。`/depth/image_raw` 为用户选择的 `16UC1` 毫米深度，显示用 `bgr8` 伪彩图单独发布到 `/depth/image_color`。完整接口表、官方风格启动入口及单采集进程用法见 SDK 包 README。

厂商 V 社区 Linux `Mv3dRgbdSDK V1.2.0` 已安装在 `/opt/Mv3dRgbdSDK_1.2.0`。它能枚举相机，但会在打开当前固件 `V2.4.6` 时因旧版 `ChunkSelector` 设置失败，不能用于生产取流。当前节点使用 104 已安装并实测可取流的 Hikrobot U3V/MVS 4.8.0.3 接口；服务入口为 `omnifleet-t2-rgbd-camera.service`。

相机以 DepthMode 同时采集主深度图和 RGBImage chunk，同一个硬件帧的三路 ROS 图像共用时间戳。15 秒接收实测 RGB/原始深度约 26 Hz，配准深度约 24 Hz；这不是满载所有算法时的帧率保证。
上述帧率为历史 640×480 输出测量；当前配置取消 RGB 降采样，使用 1536×1280 和对应工厂内参，帧率与带宽需按当前实际负载测量。

RGB 永久启动配置为 `config/mv_dt01snu.yaml` 中的 `color_exposure_mode: DynamicMode`，对应设备 `ColorExposureModeSelector=1`。每次启动均启用自动曝光/增益，不再写入固定的 RGB 曝光与增益；`color_exposure_time_us`、`color_gain` 仅在 `SingleMode` 手动模式生效。深度也独立采用相机原生 `DynamicMode`，自动曝光上限500μs；手动回退值500μs。永久性由开机服务加载源码配置实现，不依赖设备掉电保留用户集。
此前固定深度曝光1000μs限制了15FPS，并非满分辨率的硬件上限。现在原生1536×1280 RGB＋640×480深度已实测约30FPS；500μs手动曝光或自动上限500μs均可实现。图像负载采用原生字节数组，仅向已有订阅者发布；RGB另提供同分辨率JPEG显示话题，算法原图和毫米深度保留。

原始深度使用 `camera_depth_optical_frame` 和深度内参；配准深度使用 `camera_color_optical_frame`，内参与 RGB 一致。配准按本机导出的 `RGBDSensorCali.mfa` 内外参执行 `cv2.rgbd.registerDepth`，外参平移由毫米换为米；不填充无效区域。设备读回 `DepthRectifyEnable=true`、`DepthType=Correct_Type`、`LSLProfileCoordZUnit=1.0`；DepthMode 的彩色图由设备矫正，因此 CameraInfo 畸变为零。案例必须使用配准深度进行 RGB 检测框测距，不能仅缩放原始深度索引。

标定文件：`/home/iecme/omnifleet_data/camera_validation/mv_dt01snu_20261020/RGBDSensorCali.mfa`，序列号 `DB0993529`。`/camera/rgbd/status` 提供硬件帧号和深度单位。当前 SDK 1.2 的兼容问题未解决；此节点实际使用 MVS U3V 取流与 OpenCV 配准，不能当作原生 Mv3dRgbdSDK 验收通过。

```bash
source /home/iecme/omnifleet_ws/env.bash
systemctl status omnifleet-t2-rgbd-camera.service --no-pager
# 常驻服务已运行时，不重复启动另一个相机节点。
# 单独运行需先停止相机服务，再执行：
# ros2 launch omnifleet_hikrobot_rgbd rgbd_camera.launch.py
```


## 2026-10-22 RGB像素按需查询原始深度

公开函数：`omnifleet_hikrobot_rgbd.depth_query.rgb_pixel_to_depth`。

```python
from omnifleet_hikrobot_rgbd.depth_query import rgb_pixel_to_depth

sample = rgb_pixel_to_depth(depth_mm, (u, v), K_depth, K_rgb, T_depth_to_rgb)
z_rgb_m = None if sample is None else sample['depth_m']
```

depth_mm为原始640×480的16UC1毫米深度；K_depth/K_rgb是对应分辨率的3×3内参，
T_depth_to_rgb为工厂4×4外参，平移单位米。RGB点必须使用当前原图像素坐标。
返回RGB光学坐标系中的Z（depth_m）及XYZ（rgb_xyz_m）、实际原始深度像素（depth_uv）、
其毫米值（raw_depth_mm）与重投影误差；不是把RGB坐标按分辨率直接缩放。
没有匹配的有效测量时返回None，不补洞或伪造深度。

函数只查RGB射线在原始深度中的小范围极线区域，不创建整幅配准图或点云。
默认最大重投影误差3个RGB像素；边界/遮挡处应检查返回误差，不能把近邻采样当成亚像素标定精度。
全帧配准接口保留兼容，但驱动仅在图像实际被订阅时执行，不被本函数触发。

104现场查询示例：仅检查660/307200个深度像素，平均约0.365ms，查询结果能还原到实际原始像素，
RGB重投影误差为0。该结果证明坐标/单位实现，不等于完成外部标准距离精度标定。

## 深度曝光热修改与相机原生处理

永久配置：`depth_exposure_mode: DynamicMode`、`depth_auto_exposure_max_us: 500`、
`depth_gap_fill_class: Normal`、`depth_range_filter_class: Normal`。
原生补洞与范围平滑均已通过设备设置/读回及30FPS原生取流验证。
`image_raw`现在表示设备输出，包含这些固件处理；补洞结果不是独立的真实测量。
主机端查询函数不额外补洞，原始毫米单位、标定与话题类型保持兼容。

Foxglove控制话题 `/camera/rgbd/control`，类型 `std_msgs/msg/String`，JSON示例：

```json
{"id":"request-1","depth_exposure_mode":"DynamicMode","depth_auto_exposure_max_us":500,"persist":true}
```

手动改用 `depth_exposure_mode: SingleMode` 和 `depth_exposure_time_us: 500`。
设备允许范围读回为3–1400μs；自动模式中的数值是上限，不是当前瞬时曝光。
固件自动模式不开放标准ExposureTime读回，所以状态中该瞬时值为null，不伪造为固定500。

`/camera/rgbd/status`返回模式、上限/固定值、帧率、RGB自动曝光及原生滤波开关，
`last_control`包含请求ID、成功/失败原因与永久保存状态。
切换曝光模式或修改自动曝光上限时，采集线程在帧边界暂停取流、写设备、更新可用最高帧率、恢复取流；
不重启ROS节点。手动固定曝光在帧边界直接写入。失败时尝试恢复旧参数。
勾选永久保存仅改包内源码配置中的曝光模式及对应值；其他参数保留。

Foxglove同时提供滑块与数字输入：滑块松开应用，数字输入按Enter或点击应用。
灰度深度采用0–1500mm近亮远暗映射，PNG无损传输；设备无效像素保持黑色。
灰度显示是8位映射，算法/测距继续使用16UC1毫米数据。

## 人物Mask稀疏采样

`rgb_mask_to_depth(depth_mm, mask, bbox, (rgb_width,rgb_height), K_depth, K_rgb, T_depth_to_rgb)`
在人物框对应的原始深度ROI采样16×16网格，最多256个实际原始像素。
采样点按工厂标定投影回RGB，过滤到人物Mask内，再以深度MAD剔除离群值，返回中位XYZ。
Mask使用YOLO方形letterbox输出坐标，bbox使用原始RGB像素坐标；返回XYZ单位米、RGB光学坐标系。
返回还包含 `sampled_count`、`mask_valid_count`、`inlier_count`、`depth_mad_m`。
原始无效深度不插值，不创建整幅配准图或点云。单点查询函数保留兼容。

## 104本机帧对传输

`/camera/rgbd/local_frame`（std_msgs/String）用于同机识别进程：消息给出私有`/dev/shm/omnifleet_rgbd_104_<pid>.frame`路径、序号和光学坐标系。
`local_frames.LocalFrameReader.read`返回同一硬件帧的BGR数组、16UC1毫米深度、采集时间戳和硬件帧号。
生产端在同一文件锁内提交头部和两幅图，读端复制到自己的数组；识别只处理最新帧。
这不是远程Windows图像接口，公开ROS图像、CameraInfo及曝光控制话题保持原接口。
启动相机服务后按需创建共享文件，正常退出删除；设备重启时订阅者根据新文件路径重新连接。
现场对两对相同时间戳的公开ROS图像与共享数组执行`np.array_equal`，RGB和原始16UC1深度均完全一致。
