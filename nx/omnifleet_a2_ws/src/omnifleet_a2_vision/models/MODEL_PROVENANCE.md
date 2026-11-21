# 视觉模型来源与转换记录

原始模型来自用户提供的厂商资料：

```text
D:\UserData\TerryHank\Desktop\北理7.20材料_单点导航\视频素材\轮趣科技\
1.WHEELTEC ROS机器人通用资料\6.ROS2系列教程\4.ROS2机器人进阶应用视频教程\
16.Jetracer自动驾驶沙盘\ros2沙盘源码.zip
```

原压缩包 SHA-256：

```text
8CB4D1B796F1A810BEFD7C99D25E4BEBFAF812FB3A8B949923A1463DCC236DE5
```

复用的原始权重：

- `traffic_light.pt`：`red / green / yellow`
- `yolo11n_coco.pt`：COCO 80 类，课程使用行人和车辆子集
- `yolov8s_pose.pt`：单类 `person` 与 17 个 COCO 关键点

ONNX 由本机 Ultralytics `8.4.124` 以 `imgsz=640`、`opset=12`、固定输入形状导出。TensorRT 引擎必须在目标 Jetson 上由 TensorRT 10.3 重新生成，不能复制其他机器生成的 `.engine`。

模型文件本身不添加厂商品牌、水印或绝对路径；课程演示图片和视频应在 OmniFleet 实机重新录制。
