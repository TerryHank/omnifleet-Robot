# Lunshi Ackermann chassis URDF with S3 lidar and MV-DT01SDU camera

This package is based on the newly uploaded `lunshi_chassis_description_sw_mesh(2).zip`, not the older generated URDF.

Main URDF:

```text
urdf/lunshi_chassis_ackermann_s3_camera.urdf
```

Requested joint/control abstraction:

```text
front_left_steering_joint      position command/state
front_right_steering_joint     position command/state
rear_left_wheel_joint          velocity command/state
rear_right_wheel_joint         velocity command/state
front_left_wheel_joint         passive/state-only
front_right_wheel_joint        passive/state-only
```

Sensor meshes are generated from the user-provided STEP models and are referenced with original size unchanged.
No `<scale>` attribute is used in the visual mesh tags.

Sensor mesh bounding boxes after STEP-to-STL conversion:

```text
RPLIDAR S3 STL bbox: 0.116373 x 0.055600 x 0.041300 m
MV-DT01SDU STL bbox: 0.031205 x 0.089964 x 0.026006 m
```

Sensor placement relative to `base_link`:

```text
rplidar_s3_joint: xyz="0.020 0 0.114" rpy="0 0 0"
laser_frame_joint: xyz="0 0 0.035" rpy="0 0 0"
hik_camera_joint: xyz="0.240 0 0.125" rpy="0 0.13962634016 0"
```

Chassis geometry measured from the uploaded URDF metadata:

```text
wheelbase: 0.362295943 m
front/steering track width: 0.264956799 m
rear/traction track width: 0.245400019 m
wheel radius: 0.058528263 m
```

Display:

```bash
ros2 launch omnifleet_a2_description display_ackermann_s3_camera.launch.py
```


## 2026-06-22 correction

Removed the temporary front steering-axis sphere visual/collision markers. The `front_left_steering_link` and `front_right_steering_link` remain as kinematic links only; the visible front wheels are still mounted under them through their rolling joints.
