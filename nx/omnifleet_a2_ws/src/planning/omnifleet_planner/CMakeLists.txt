cmake_minimum_required(VERSION 3.8)
project(omnifleet_planner)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

ament_python_install_package(omnifleet_planner)

install(DIRECTORY config launch behavior_trees
  DESTINATION share/${PROJECT_NAME})
install(FILES README.md DESTINATION share/${PROJECT_NAME})
install(PROGRAMS
  scripts/nav_steering_adapter
  DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_nav2_contract test/test_nav2_contract.py)
  ament_add_pytest_test(test_ackermann_stack test/test_nav2_ackermann_stack.py)
  ament_add_pytest_test(
    test_global_planner_experiments
    test/test_global_planner_experiments.py)
  ament_add_pytest_test(test_nav_steering_adapter test/test_nav_steering_adapter.py)
endif()

ament_package()
