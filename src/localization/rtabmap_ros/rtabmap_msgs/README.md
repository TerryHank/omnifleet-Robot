# rtabmap_msgs｜OmniFleet 工作区介绍

RTAB-Map's msgs package.

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/rtabmap_ros/rtabmap_msgs`。
- colcon 类型：`(ros.ament_cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下未发现同名目录；按源代码/备用组件登记，不能称为已部署运行。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [msg/](msg)：消息定义。当前项：`CameraModel.msg`、`CameraModels.msg`、`EnvSensor.msg`、`GPS.msg`、`GlobalDescriptor.msg`、`Goal.msg`、`Info.msg`、`KeyPoint.msg`、`LandmarkDetection.msg`、`LandmarkDetections.msg`、`Link.msg`、`MapData.msg`、`MapGraph.msg`、`Node.msg`、`OdomInfo.msg`、`Path.msg`、`Point2f.msg`、`Point3f.msg`、`RGBDImage.msg`、`RGBDImages.msg`、`ScanDescriptor.msg`、`SensorData.msg`、`UserData.msg`。
- [srv/](srv)：服务定义。当前项：`AddLink.srv`、`CleanupLocalGrids.srv`、`DetectMoreLoopClosures.srv`、`GetMap.srv`、`GetMap2.srv`、`GetNodeData.srv`、`GetNodesInRadius.srv`、`GetPlan.srv`、`GlobalBundleAdjustment.srv`、`ListLabels.srv`、`LoadDatabase.srv`、`PublishMap.srv`、`RemoveLabel.srv`、`ResetPose.srv`、`SetGoal.srv`、`SetLabel.srv`。

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
