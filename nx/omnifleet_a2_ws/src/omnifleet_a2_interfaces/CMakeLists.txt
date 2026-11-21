cmake_minimum_required(VERSION 3.8)
project(omnifleet_a2_interfaces)

find_package(ament_cmake REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/SlamStatus.msg"
  "msg/SteeringAngleCommand.msg"
  "srv/SaveMap.srv"
  "srv/SwitchMode.srv"
  DEPENDENCIES builtin_interfaces)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
