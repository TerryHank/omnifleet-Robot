# mvs_camera_driver

ROS 2 Humble wrapper for the MVS 5.0.1 Linux SDK. The package embeds the x86_64 and aarch64 SDK tarballs and selects the correct one at CMake configure time.

## Supported targets

- Ubuntu 22.04 with ROS 2 Humble
- x86_64 using `MVS-5.0.1_x86_64_20260512.tar.gz`
- aarch64 using `MVS-5.0.1_aarch64_20260512.tar.gz`

## Build

```bash
mkdir -p ~/ros2_ws/src
tar -xzf mvs_camera_driver_humble_bundle.tar.gz -C ~/ros2_ws/src
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select mvs_camera_driver
source install/setup.bash
```

By default, CMake extracts the bundled SDK into the build directory and installs the selected runtime libraries next to the node. To link an existing `/opt/MVS` installation instead:

```bash
colcon build --packages-select mvs_camera_driver --cmake-args -DMVS_USE_SYSTEM_SDK=ON -DMVS_SDK_ROOT=/opt/MVS
```

## Optional system install

The ROS node bundles the user-space runtime libraries. For USB permissions, GigE filter driver, services, or vendor GUI tools, run the vendor installer from the package:

```bash
cd ~/ros2_ws/src/mvs_camera_driver
./scripts/install_mvs_system.sh
```

## Run

```bash
ros2 launch mvs_camera_driver mvs_camera.launch.py
```

The node publishes:

- `image_raw` as `sensor_msgs/msg/Image`
- `camera_info` as `sensor_msgs/msg/CameraInfo`

## Parameters

- `camera_index`: zero-based index when no serial or user-defined name is set
- `serial_number`: preferred device selector when set
- `user_defined_name`: secondary device selector when set
- `frame_id`: frame id on published image headers
- `pixel_format`: optional MVS PixelFormat string, for example `Mono8` or `RGB8Packed`
- `exposure_time`: set when greater than zero
- `gain`: set when greater than zero
- `trigger_mode`: enables trigger mode when true
- `trigger_source`: optional trigger source string
- `grab_timeout_ms`: image-buffer wait timeout
