# 104 实时导航地图接入

2026-10-14。入口：[地图首页](http://localhost:3000/)。

原来的空白原因：中央域 42 的 `/map` 是 RMF `BuildingMap`，没有发布者，`/building_map` 返回 404。上一轮接入仅包含状态，没有为这个官方地图视图提供地图数据。

本次接入车辆域 104 的真实 `/map`：`nav_msgs/msg/OccupancyGrid`，发布者 `mola_realtime_nav_grid`。当前为 500×500、0.1 米/格，原点约 (-25,-25)，坐标系为 `map`。

专用只读采集器订阅可靠、Transient Local 地图消息，生成灰度 PNG，经原本的本机 Unix socket 传递图像与几何信息。API 提供 `/omnifleet/robots/robot_104/map.png`。SSE 只推送几何信息、消息计数与图像版本，图像按版本加载。首页在未收到 RMF 建筑地图时显示此车辆导航地图；之后收到 RMF 建筑地图仍可使用原来的官方渲染逻辑。

初始视图聚焦已观测区域，提供放大、缩小、适合地图。白色为空闲、黑色为占据、灰色为未知。红色箭头叠加 104 位姿与朝向，坐标投影包含地图原点平移/旋转以及图像纵轴翻转；仅在位姿和地图 frame 相同时叠加，过期位姿使用灰色标记。

验证：构建/TypeScript 与 `git diff --check` 通过；占据值灰度映射、纵轴翻转、已知区域边界、旋转原点投影检查通过；图像接口实际返回 PNG；页面确认 104 地图、坐标和朝向标记显示且消息计数更新，放大按钮实际生效。

此图是车辆实时导航栅格，不等于 RMF 建筑地图或已经完成中央地图配准。未增加目标下发或修改车辆导航服务。

回滚副本：`/home/zhangwnag/workspaces/omnifleet_ws/data/rmf_web/backup_before_map/`。源码快照位于本目录 `source/`；当前浏览器截图：`map104-web.png`。
