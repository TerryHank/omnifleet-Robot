cmake_minimum_required(VERSION 3.8)
project(omnifleet_localization)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)

ament_python_install_package(omnifleet_localization)

install(DIRECTORY config DESTINATION share/${PROJECT_NAME})
install(DIRECTORY launch/backends/
  DESTINATION share/${PROJECT_NAME}/launch
  FILES_MATCHING PATTERN "*.launch.py")
install(DIRECTORY launch/includes/
  DESTINATION share/${PROJECT_NAME}/launch/includes
  FILES_MATCHING PATTERN "*.launch.py")
install(PROGRAMS
  scripts/cloud_filter
  scripts/depth_dropoff_detector
  scripts/glim_manager
  scripts/glim_map_projector
  scripts/glim_odom_adapter
  scripts/rrc-slamctl
  scripts/terrain_mapper
  scripts/wheel_slip_detector
  DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  find_package(ament_cmake_pytest REQUIRED)


  ament_add_pytest_test(test_state_machine test/test_state_machine.py)
  ament_add_pytest_test(test_process_supervisor test/test_process_supervisor.py)
  ament_add_pytest_test(test_map_registry test/test_map_registry.py)
  ament_add_pytest_test(test_odom_adapter test/test_glim_odom_adapter.py)
  ament_add_pytest_test(test_stop_stack_contract test/test_stop_stack_contract.py)
  ament_add_pytest_test(test_occupancy_grid_saver test/test_occupancy_grid_saver.py)
  ament_add_pytest_test(test_optional_foxglove test/test_optional_foxglove.py)
  ament_add_pytest_test(test_runtime_entity_contract test/test_runtime_entity_contract.py)
  ament_add_pytest_test(test_conservative_projection test/mapping/test_conservative_projection.py)
  ament_add_pytest_test(test_map_projector test/mapping/test_glim_map_projector_source.py)
  ament_add_pytest_test(test_occupancy_evidence test/mapping/test_occupancy_evidence.py)
  ament_add_pytest_test(test_terrain_analysis test/mapping/test_terrain_analysis.py)
endif()

ament_package()
