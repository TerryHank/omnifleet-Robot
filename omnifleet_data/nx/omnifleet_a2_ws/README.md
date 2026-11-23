# OmniFleet A2 production mainline

This directory preserves deployment files from `/home/iecme/omnifleet_a2_ws`. The public snapshot is published on the `A2` branch. The live paths and service environment for the captured vehicle are documented in the [124 runtime and restore guide](../runtime_124/README.md).

## Layout

- [ROS 2 source](../../../omnifleet_ws/src): project-owned ROS 2 packages, including the semantic waypoint UI.
- `firmware/V3.5.1/`: STM32 source and the verified release image.
- `foxglove/`: semantic-waypoint extension source and reference layouts.

ROS `build/`, `install/`, `log/`, Python caches, runtime logs and backup copies
are generated artifacts. The repository includes selected ARM64 runtime files in [runtime_124](../runtime_124/README.md). Live maps and local backups are stored separately.

Third-party GLIM, RoboSense Airy, MVS and ROS/Nav2 installations remain in their
own upstream workspaces or system prefixes. The source index and runtime guide identify the sensor driver sources and captured install files included here.

## Production navigation contract

- `/omnifleet_a2/nav/waypoint_poses` is the only navigation-goal input. A
  single-point route is a `PoseArray` containing one pose; all routes are
  forwarded unchanged to `NavigateThroughPoses`.
- Nav2 Controller publishes `/cmd_vel` directly to the chassis driver.
- Stopped steering uses only the custom-radian
  `/omnifleet_a2/chassis/steering_angle_cmd` interface; positive means left.
- Linux has no command timeout, zero-lock, speed-floor or steering adapter.
  STM32 owns the communication-loss stop. NX only sends a configurable
  heartbeat and timeout value and publishes the returned watchdog status.
- `map -> odom -> base_link` is the only dynamic localization chain; no extra
  map-plane transform is created.
- `omnifleet_a2_glim_map_projector` is project code, not a GLIM component. It
  performs direct lightweight projection without temporal evidence, neighbor
  confirmation, wall protection, TTL or ray-clipping history.
- Mission storage and replay are intentionally absent; all semantic routes go
  through the single `omnifleet_a2_waypoint_bridge`.
