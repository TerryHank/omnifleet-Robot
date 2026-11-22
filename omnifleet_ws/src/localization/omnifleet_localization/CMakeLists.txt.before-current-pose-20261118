cmake_minimum_required(VERSION 3.8)
project(omnifleet_localization)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)

ament_python_install_package(omnifleet_localization)

find_package(omnifleet_sensor_processing REQUIRED)
install(PROGRAMS scripts/airy_imu_adapter_node DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY include/ DESTINATION include)
install(DIRECTORY config DESTINATION share/${PROJECT_NAME})
install(DIRECTORY launch/backends/
  DESTINATION share/${PROJECT_NAME}/launch
  FILES_MATCHING PATTERN "*.launch.py")
install(DIRECTORY launch/includes/
  DESTINATION share/${PROJECT_NAME}/launch/includes
  FILES_MATCHING PATTERN "*.launch.py")
install(FILES
  launch/airy_gateway.launch.py
  DESTINATION share/${PROJECT_NAME}/launch)
install(PROGRAMS
  scripts/depth_dropoff_detector
  scripts/cartographer_odom_adapter
  scripts/terrain_mapper
  scripts/wheel_slip_detector
  DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  find_package(ament_cmake_pytest REQUIRED)

  ament_add_gtest(test_airy_imu_rotation test/airy/test_imu_rotation.cpp)
  target_link_libraries(test_airy_imu_rotation omnifleet_sensor_processing::omnifleet_sensor_conversions)
  ament_target_dependencies(test_airy_imu_rotation sensor_msgs)
  ament_add_pytest_test(test_airy_launch test/airy/test_launch_config.py)
  ament_add_pytest_test(test_mode_configs test/test_mode_configs.py)
  ament_add_pytest_test(test_cartographer_3d_contract test/test_cartographer_3d_contract.py)
  ament_add_pytest_test(test_mola_backend_contract test/test_mola_backend_contract.py)
  ament_add_pytest_test(test_terrain_analysis test/mapping/test_terrain_analysis.py)
endif()

ament_export_include_directories(include)
ament_export_dependencies(omnifleet_sensor_processing)
ament_export_dependencies(sensor_msgs)
ament_package(CONFIG_EXTRAS cmake/compatibility.cmake)
