<!-- OMNIFLEET_WORKSPACE_DOC_LINK -->
本工作区职责、入口及104约定见 [README.omnifleet.md](README.omnifleet.md)。

# omnifleet_tutorials

本包保留 104 履带车仍可运行的视觉课程入口。原先四个建图/航点教程依赖一个
不存在的旧 SLAM 包，现已从生产工作区删除；建图与导航统一使用
`omnifleet_bringup` 的当前入口。

## 建图导航入口

加载 `/home/iecme/omnifleet_ws/env.bash`，使用当前MOLA和Nav2服务。见 [104启动说明](../../system/omnifleet_bringup/README.md)。旧hardware_drivers_ws与omnifleet_t2_ws嵌套工作区路径已不存在。

## 视觉课程

`vision_02_*.launch.py`、`vision_03_*.launch.py`、`vision_04_*.launch.py`
分别对应单项实验、模块联调和阶段项目。所有会产生运动候选的入口默认
`enable_motion:=false`。

```bash
ros2 launch omnifleet_tutorials vision_02_07_kcf.launch.py
ros2 launch omnifleet_tutorials vision_02_14_traffic_light.launch.py
ros2 launch omnifleet_tutorials vision_03_02_detection_tracking.launch.py
```

KCF 可选串口参数的默认值已经统一为 `/dev/omnifleet_t2_stm32`。视觉课程不是
T2 生产导航主线，只有现场看护并明确启用时才允许产生运动命令。
