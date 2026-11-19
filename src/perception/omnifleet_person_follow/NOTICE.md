# Third-party sources

Follow state/loss prediction is a selective Python adaptation of D-Robotics
`tros_person_following`, commit `202e8c8a04dc41e3d3771daa131b852cc24f7c0d`:
https://github.com/D-Robotics/tros_person_following
Copyright (c) 2024 D-Robotics. Apache License 2.0.

Retained concepts: IDLE/TRACKING/LOST, recent-velocity prediction, last-known
and history observation points, directional scans, spatial/moving-target relock,
and a robot-to-person trailing goal.
PAUSED, explicit gesture ID ownership, masks/depth, and the Humble public Nav2
adapter are OmniFleet changes. This is not the unchanged upstream BPU node.
User-authorized new-ID relock uses measured motion and phased spatial proximity;
it is not appearance-based identity recognition. Directional scans are finite
Nav2 orientation goals through the local owner, not upstream direct cmd_vel.
The complete upstream checkout/license remains at
`/home/iecme/omnifleet_data/reference_sources/tros_person_following`.

YOLO26n-seg and ByteTrack/Kalman are supplied by the installed Ultralytics
8.4.124 package (AGPL-3.0 / available upstream enterprise license):
https://github.com/ultralytics/ultralytics

The MediaPipe palm/21-keypoint hand ONNX models and inference implementations
are loaded from the existing OpenCV Zoo checkout, with its original notices:
https://github.com/opencv/opencv_zoo
The adapter runs their CUDA FP16 path and reuses previous hand ROIs. It does not
claim to run the Google MediaPipe Tasks GPU runtime.
The cropped-warp geometry in hand_preprocess.py adapts the Apache-2.0
OpenCV Zoo MediaPipe hand preprocessing, preserving its coordinate transforms.

Nav2 Humble GoalUpdater and NavigateToPose retain their upstream interfaces.
This adapter sends to the existing local navigation owner; it never publishes
vehicle velocity or invokes the private navigation backend directly.


The Gemini Body Tracking face input uses OpenCV Zoo YuNet
`face_detection_yunet_2023mar.onnx` (MIT, Copyright 2020 Shiqi Yu).
Source: https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet
The full model licence is retained beside the installed model as
`face_detection_yunet_LICENSE`.
