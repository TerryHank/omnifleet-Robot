cmake_minimum_required(VERSION 3.8)
project(omnifleet_vr_bridge)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

ament_python_install_package(omnifleet_vr_bridge)

install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})
install(PROGRAMS scripts/vr_bridge DESTINATION lib/${PROJECT_NAME})

ament_package()
