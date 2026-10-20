cmake_minimum_required(VERSION 3.8)
project(omnifleet_vision)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(ament_cmake REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(message_filters REQUIRED)
find_package(OpenCV REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(kcf_follower_node
  src/kcf_follower_node.cpp
  src/kcftracker.cpp
  src/fhog.cpp
)

target_include_directories(kcf_follower_node PRIVATE
  include/omnifleet_vision
  ${cv_bridge_INCLUDE_DIRS}
  /opt/ros/humble/include/cv_bridge
  ${OpenCV_INCLUDE_DIRS}
)

ament_target_dependencies(kcf_follower_node
  geometry_msgs
  message_filters
  rclcpp
  sensor_msgs
  std_msgs
)

# Jetson 同时安装了 NVIDIA OpenCV 和 ROS Humble 所依赖的 Ubuntu OpenCV。
# cv_bridge 来自 Ubuntu 4.5 ABI，因此在目标机上显式链接同一组库，避免一个进程
# 同时加载 4.5 与 4.10；其他平台继续使用 find_package 得到的默认库。
if(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64" AND
   EXISTS "/lib/aarch64-linux-gnu/libopencv_core.so.4.5d")
  if(EXISTS "/usr/include/opencv4/opencv2/core.hpp")
    target_include_directories(kcf_follower_node BEFORE PRIVATE
      /usr/include/opencv4
    )
  elseif(EXISTS "/home/iecme/third_party/opencv45/usr/include/opencv4/opencv2/core.hpp")
    target_include_directories(kcf_follower_node BEFORE PRIVATE
      /home/iecme/third_party/opencv45/usr/include/opencv4
    )
  else()
    message(FATAL_ERROR "OpenCV 4.5 headers are required with ROS cv_bridge on aarch64")
  endif()
  set(OMNIFLEET_OPENCV_LIBRARIES
    /lib/aarch64-linux-gnu/libopencv_core.so.4.5d
    /lib/aarch64-linux-gnu/libopencv_imgproc.so.4.5d
    /lib/aarch64-linux-gnu/libopencv_imgcodecs.so.4.5d
    /lib/aarch64-linux-gnu/libopencv_highgui.so.4.5d
    /opt/ros/humble/lib/libcv_bridge.so
  )
  message(STATUS "OmniFleet KCF uses the ROS cv_bridge OpenCV 4.5 ABI")
else()
  ament_target_dependencies(kcf_follower_node cv_bridge)
  set(OMNIFLEET_OPENCV_LIBRARIES ${OpenCV_LIBRARIES})
endif()

target_link_libraries(kcf_follower_node ${OMNIFLEET_OPENCV_LIBRARIES})

install(TARGETS kcf_follower_node
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME}
  PATTERN "__pycache__" EXCLUDE
  PATTERN "*.pyc" EXCLUDE
)

install(FILES README.md NOTICE.md SOURCE_MANIFEST.sha256
  DESTINATION share/${PROJECT_NAME}
)

# Python 节点按功能分组开发，安装时放到同一 lib 目录，便于 ros2 run 查找。
install(PROGRAMS
  scripts/course_gui_overlay_node.py
  scripts/image_display_node.py
  scripts/classical/apriltag_recognition_node.py
  scripts/classical/camera_monitor_node.py
  scripts/classical/color_recognition_node.py
  scripts/classical/depth_measurement_node.py
  scripts/classical/lane_detection_node.py
  scripts/classical/opencv_processor_node.py
  scripts/classical/qr_recognition_node.py
  scripts/classical/synthetic_scene_publisher.py
  scripts/classical/traffic_light_dual_node.py
  scripts/integration/detection_tracker_node.py
  scripts/integration/detection_aggregator_node.py
  scripts/integration/lane_follow_controller_node.py
  scripts/integration/multimodal_risk_node.py
  scripts/integration/safe_behavior_controller_node.py
  scripts/integration/target_depth_fusion_node.py
  scripts/integration/traffic_course_state_node.py
  scripts/integration/traffic_event_node.py
  scripts/integration/target_follow_controller_node.py
  scripts/integration/vision_nav_target_node.py
  scripts/ml/face_detection_node.py
  scripts/ml/inference_status_node.py
  scripts/ml/license_plate_node.py
  scripts/ml/model_training.py
  scripts/ml/onnx_detector_node.py
  scripts/ml/pose_node.py
  scripts/ml/tensorrt_tools.py
  scripts/ml/ultralytics_detector_node.py
  DESTINATION lib/${PROJECT_NAME}
)

# 纯算法模块不作为 ros2 run 入口，只供同目录节点导入。
install(FILES
  scripts/classical/algorithms.py
  scripts/classical/ros_support.py
  scripts/integration/course_controllers_core.py
  scripts/integration/vision_integration_core.py
  scripts/ml/onnx_yolo_core.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY models
  DESTINATION share/${PROJECT_NAME}
  PATTERN "__pycache__" EXCLUDE
  PATTERN "*.pyc" EXCLUDE
)

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_kcf_contract test/test_kcf_contract.py)
  ament_add_pytest_test(test_classical_vision test/test_classical_vision.py)
  ament_add_pytest_test(test_vision_integration test/test_vision_integration.py)
  ament_add_pytest_test(test_ml_vision test/test_ml_vision.py)
  ament_add_pytest_test(test_course_controllers test/test_course_controllers.py)
  ament_add_pytest_test(test_course_gui_overlay test/test_course_gui_overlay.py)
endif()

ament_package()
