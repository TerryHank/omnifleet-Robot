# omnifleet_description — Xacro + RViz2 + Gazebo Harmonic

This package keeps the user's latest Ackermann chassis structure and converts the main model to Xacro.

## Main files

- `urdf/lunshi_ackermann.urdf.xacro` — main robot model.
- `urdf/gazebo_sensors.gazebo.xacro` — Gazebo Harmonic sensor simulation parameters.
- `rviz/lunshi_ackermann.rviz` — RViz2 configuration.
- `worlds/lunshi_sensor_test.sdf` — small Gazebo sensor test world.
- `launch/display_xacro.launch.py` — RViz2 test.
- `launch/gazebo_harmonic_test.launch.py` — Gazebo Harmonic + ROS bridge test.
- `config/sensor_specs.yaml` — sensor spec values used in the Xacro.
- `config/ros_gz_bridge.yaml` — ROS <-> Gazebo topic bridge.

## Joint interfaces preserved

- `front_left_steering_joint`: position command/state
- `front_right_steering_joint`: position command/state
- `rear_left_wheel_joint`: velocity command/state
- `rear_right_wheel_joint`: velocity command/state
- `front_left_wheel_joint`: passive/state-only
- `front_right_wheel_joint`: passive/state-only

## Build

```bash
cd ~/ackermann_mid360_glim_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## RViz2

```bash
ros2 launch omnifleet_description display_xacro.launch.py
```

## Gazebo Harmonic test

```bash
ros2 launch omnifleet_simulator gazebo_harmonic_test.launch.py
```

Then check:

```bash
ros2 topic list | grep -E "scan|camera"
ros2 topic echo /scan --once
ros2 run rqt_image_view rqt_image_view
```

## Notes

- The S3 and MV-DT01SDU CAD sensor meshes are preserved at original STL scale; no `<scale>` is applied.
- Complex CAD/STL is used for `visual`; collisions stay simplified to avoid Gazebo performance issues.
- Sensor optical/performance parameters are in `gazebo_sensors.gazebo.xacro`, not mixed with mechanical link geometry.
