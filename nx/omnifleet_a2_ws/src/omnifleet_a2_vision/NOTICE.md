# Third-party source notice

This package retains the KCF/HOG implementation byte-for-byte from the user-provided archive below:

```text
D:\UserData\TerryHank\Desktop\北理7.20材料_单点导航\视频素材\轮趣科技\
1.WHEELTEC ROS机器人通用资料\7.ROS源码\ROS2源码\Humble源码\
X5_wheeltec_ros2_src_20260612.zip
```

Archive member root: `src/wheeltec_robot_kcf`.

`SOURCE_MANIFEST.sha256` records the archive hash and the eight retained file hashes. All eight files matched the archive exactly on 2026-08-21.

The retained files have mixed upstream notices. In particular, `tracker.h` states research-use and redistribution restrictions, while `kcftracker.h` and FHOG-derived files contain permissive notices. Every original notice remains unchanged in its source file; this package does not replace those notices with a blanket BSD declaration.

The OmniFleet ROS2 node, Launch files, configuration and tests are a new MIT-licensed adapter. The adapter parameterizes the camera interfaces and prevents direct publication to the final vehicle `/cmd_vel`.
