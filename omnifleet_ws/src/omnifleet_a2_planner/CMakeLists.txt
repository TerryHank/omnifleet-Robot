cmake_minimum_required(VERSION 3.8)
project(omnifleet_a2_planner)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(behaviortree_cpp_v3 REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(rclcpp REQUIRED)

ament_python_install_package(omnifleet_a2_planner)

add_library(path_map_policy SHARED
  src/path_map_policy.cpp)
target_include_directories(path_map_policy PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)
ament_target_dependencies(path_map_policy nav_msgs)

add_library(omnifleet_is_path_within_map_condition_bt_node SHARED
  src/is_path_within_map_condition.cpp)
target_compile_definitions(
  omnifleet_is_path_within_map_condition_bt_node PRIVATE BT_PLUGIN_EXPORT)
target_include_directories(omnifleet_is_path_within_map_condition_bt_node PRIVATE
  include)
target_link_libraries(
  omnifleet_is_path_within_map_condition_bt_node path_map_policy)
ament_target_dependencies(
  omnifleet_is_path_within_map_condition_bt_node
  behaviortree_cpp_v3 nav_msgs rclcpp)

install(DIRECTORY config launch behavior_trees
  DESTINATION share/${PROJECT_NAME})
install(FILES README.md DESTINATION share/${PROJECT_NAME})
install(TARGETS
  path_map_policy
  omnifleet_is_path_within_map_condition_bt_node
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin)
install(DIRECTORY include/
  DESTINATION include)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_nav2_contract test/test_nav2_contract.py)
  ament_add_pytest_test(test_ackermann_stack test/test_nav2_ackermann_stack.py)
  ament_add_pytest_test(
    test_global_planner_experiments
    test/test_global_planner_experiments.py)
  ament_add_gtest(test_path_map_policy test/test_path_map_policy.cpp)
  target_link_libraries(test_path_map_policy path_map_policy)
  ament_target_dependencies(test_path_map_policy nav_msgs)
endif()

ament_export_include_directories(include)
ament_export_libraries(path_map_policy)
ament_export_dependencies(nav_msgs)

ament_package()
