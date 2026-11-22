<!-- OMNIFLEET_WORKSPACE_DOC_LINK -->
本工作区职责、入口及104约定见 [README.omnifleet.md](README.omnifleet.md)。

# FAST-LIVO2 registered cloud to navigation grid

Uses the existing MOLA/MP2P `txt2mm`, `mm-filter`, `FilterVoxelSlice` and `mm2grid` implementations. The small PCL helper only converts ASCII/binary/compressed PCD to XYZ; it does not implement a projection algorithm.

```bash
source /home/iecme/omnifleet_ws/env.bash
ros2 run omnifleet_cloud_grid_export cloud_to_grid /path/registered_map.pcd /path/new_map --resolution 0.05 --z-min 0.1 --z-max 1.5
```

Slice bounds are mandatory and are measured in the input cloud's world/map frame. The command preserves that coordinate system. Example values require calibration against the actual floor/robot; they are not a production calibration.

A merged PCD has no individual scan viewpoints. Free-space ray tracing is disabled rather than inventing a sensor pose. Occupied and unknown cells can be exported, but this is not proof of a traversable navigation map. Use recorded scan/pose observations to obtain supported free-space evidence.

The resulting PNG/YAML is accepted by native `nav2_map_server`. Publishing it to the active `/map` requires choosing this backend and its map/TF ownership instead of the current MOLA publisher. This package neither switches services nor starts a map server automatically.
