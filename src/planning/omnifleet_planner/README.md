<!-- OMNIFLEET_WORKSPACE_DOC_LINK -->
本工作区职责、入口及104约定见 [README.omnifleet.md](README.omnifleet.md)。

# OmniFleet tracked Nav2 production stack

The production path is intentionally short:

```text
MOLA /map + map->odom
t2_driver /odom + odom->base_link
Nav2 SmacPlanner2D -> DWB -> /cmd_vel -> t2_driver
```

- Footprint: 0.50 m x 0.37 m.
- Collision height in the URDF: 0.33 m.
- Track-center separation: 0.33 m.
- Global planner: official `nav2_smac_planner/SmacPlanner2D`.
- Local controller: official `dwb_core::DWBLocalPlanner`.
- Airy `/rslidar_points` is consumed directly by the official ObstacleLayer.

There is no steering adapter, velocity smoother, collision monitor, twist mux,
or `/cmd_vel_nav_raw` in the production chain.
# Footprint-safe navigation success

`general_goal_checker` uses `omnifleet_planner::FootprintSafeGoalChecker`.
The checker first applies the configured XY and yaw tolerances, then checks the
current padded robot footprint against the latest local costmap. Unknown,
inscribed, and lethal footprint costs cannot report navigation success. A safe
footprint must remain continuous for `safe_hold_time` before success is
returned, allowing delayed LiDAR and costmap updates to arrive.

The global costmap combines the MOLA static map with a live `/rslidar_points`
obstacle layer. Global inflation uses a 1.0 m radius and 2.0 decay factor so
live obstacles affect planning without closing the small mapped area; the local
costmap keeps its more conservative 2.0 m radius and 3.0 decay factor.
