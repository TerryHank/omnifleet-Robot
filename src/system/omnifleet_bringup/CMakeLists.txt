cmake_minimum_required(VERSION 3.8)
project(omnifleet_bringup)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

ament_python_install_package(omnifleet_bringup)
install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})
install(PROGRAMS
  scripts/t2_driver
  scripts/robot_doctor
  scripts/omnifleet-t2-raw-pwm
  scripts/vr_protocol_adapter
  scripts/usb_camera_publisher
  scripts/pointcloud_radius_filter
  scripts/nav2_readiness_gate.py
  scripts/cleanup_unified_application_nodes.py
  DESTINATION lib/${PROJECT_NAME})
install(FILES README.md DESTINATION share/${PROJECT_NAME})
ament_package()

