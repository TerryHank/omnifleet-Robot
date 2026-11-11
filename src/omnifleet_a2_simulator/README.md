# OmniFleet A2 simulator

The maintained simulation entry point is Gazebo Classic 11 on ROS 2 Humble:

```bash
ros2 launch omnifleet_a2_simulator traffic_sandbox.launch.py gui:=true
```

It uses the production A2 URDF, wheelbase, wheel tracks, wheel radius, steering
joint limits, Hybrid-A* planner, and RPP controller. The simulator adds only:

- Gazebo Classic sensor and `gazebo_ros2_control` plugins;
- the official ROS 2 Ackermann steering controller;
- ROS remaps from `/cmd_vel`, `/odom`, and `/tf` to the controller's standard topics;
- a transient-local static `/map` matching the world collision geometry.

The integrated sandbox contains a road course, intersection, traffic light,
road signs, construction obstacles, barrier, parking area, tunnel, and finish
checker. AutoRace artwork provenance is recorded in `THIRD_PARTY_NOTICE.md`.

Run the executable closed-loop acceptance test after launch:

```bash
ros2 run omnifleet_a2_simulator traffic_closed_loop_test.py --timeout 240
```

The test fails unless NavigateThroughPoses succeeds, `/cmd_vel` contains motion
commands, odometry travels at least 12 m, and the final position error is below
0.35 m.

`gazebo_harmonic_test.launch.py` remains as the earlier sensor-only experiment;
it is not the maintained navigation closed-loop entry point.
