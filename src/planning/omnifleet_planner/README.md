# OmniFleet 104 Nav2 navigation

Current entry: `omnifleet-t2-pure-lio-nav2.service` launches `omnifleet_bringup/navigation.launch.py`.
Persistent parameters: [config/nav2_t2.yaml](config/nav2_t2.yaml); launch can override topic/frame parameters. The service supplies `obstacle_topic:=/navigation/deskewed_points` and `odom_topic:=/odom`, so raw YAML defaults alone do not describe the running inputs.

```text
MOLA localization + /map + navigation point cloud
Nav2 -> /navigation/nav_cmd_vel
local_navigation -> /navigation/cmd_vel_safe -> STM32
/cmd_vel -> local_navigation (manual input)
```

The YAML registers multiple planner/controller plugins, including CostAwareSmac2D, ExactGoalSmacLattice, HotDWBLocalPlanner, HotRegulatedPurePursuitController and OrderedMPPI. Task selection and current parameters determine which is used; the stack is not fixed to stock SmacPlanner2D and DWB. The configured footprint is 0.50 m × 0.37 m before padding. Inflation and other editable values must be read from the current configuration rather than copied from historical README values.

The installed Nav2 config resolves to this package's source YAML. Runtime safety arbitration belongs to local_navigation. See [workspace entry](../../../README.workspace.md) and [package inventory](README.omnifleet.md).

# Footprint-safe navigation success

`general_goal_checker` uses `omnifleet_planner::FootprintSafeGoalChecker`.
The checker first applies the configured XY and yaw tolerances, then checks the
current padded robot footprint against the latest local costmap. Unknown,
inscribed, and lethal footprint costs cannot report navigation success. A safe
footprint must remain continuous for `safe_hold_time` before success is
returned, allowing delayed LiDAR and costmap updates to arrive.

