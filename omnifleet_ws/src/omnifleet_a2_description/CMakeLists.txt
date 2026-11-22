cmake_minimum_required(VERSION 3.8)
project(omnifleet_a2_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf meshes metadata config launch rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
