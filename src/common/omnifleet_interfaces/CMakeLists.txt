cmake_minimum_required(VERSION 3.8)
project(omnifleet_interfaces)

find_package(ament_cmake REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/SlamStatus.msg"
  "msg/MissionStatus.msg"
  "srv/Capability.srv"
  "srv/LoadMission.srv"
  "srv/RunMission.srv"
  "srv/SaveMap.srv"
  "srv/StoreMission.srv"
  "srv/SwitchMode.srv"
  "srv/ServoCommand.srv"
  DEPENDENCIES builtin_interfaces geometry_msgs)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
