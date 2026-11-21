<!-- OMNIFLEET_WORKSPACE_DOC_LINK -->
本工作区职责、入口及104约定见 [README.omnifleet.md](README.omnifleet.md)。

# OmniFleet map TF generator

Organized under `src/map/` following Autoware Universe's map-domain package layout.
Autoware's corresponding package generates a map viewer frame; this package preserves
OmniFleet's existing map/fleet transforms rather than copying that visualization algorithm.

- `transforms.py`: planar angle/pose normalization, composition and inverse.
- `map_tf.py`: constructs map-related TransformStamped messages.
- `grid_codec.py`: lossless shared-grid encoding, decoding and QOS.

Existing MSC nodes continue to own the publishers and all validity conditions. This package
starts no node and creates no broadcaster. It adds no competing TF publisher.
MOLA's vehicle localization output, sensor extrinsics, fleet safety and transport stay in their
existing domains. `omnifleet_msc.geometry` and `omnifleet_msc.shared_map` keep compatibility imports.

Existing frames and topics are retained, including reference map -> fleet_map,
fleet_map -> robot map, fleet_map -> fleet_pose and the existing optional map -> odom bridge.

生产导航栅格入口：ros2 run omnifleet_map_tf_generator mola_realtime_nav_grid.py，由system/omnifleet_bringup启动，直接使用本包mola_realtime_nav_grid.main，不再经过实验包转发。

当前栅格清空接口：`/mola_realtime_nav_grid/clear`（std_srvs/Trigger）。清空当前内存栅格与待处理点云并立即发布空栅格；保持MOLA定位原点、参数、TF和磁盘已保存地图。新的雷达数据随后重新填充栅格。Windows视觉面板的“清空当前地图”同时请求暂停当前人体跟随，并调用Nav2全局/局部ClearEntireCostmap。
