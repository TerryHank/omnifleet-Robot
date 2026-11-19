# map 功能域

点云到栅格/体素地图、地图坐标变换与地图导出。

## 包与组件索引

| 包/组件 | 职责 |
|---|---|
| [omnifleet_cloud_grid_export](omnifleet_cloud_grid_export/README.omnifleet.md) | 将外部已配准点云转换为 MOLA/MP2P 体素及栅格地图。 |
| [omnifleet_map_tf_generator](omnifleet_map_tf_generator/README.omnifleet.md) | 地图坐标变换、TF 构造与共享地图栅格编解码。 |
| [omnifleet_mola_grid](omnifleet_mola_grid/README.md) | MP2P 体素切片及 MRPT/ROS 地图桥接，供外部已配准点云使用。 |
