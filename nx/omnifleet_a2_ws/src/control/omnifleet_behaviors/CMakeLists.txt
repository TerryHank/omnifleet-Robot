cmake_minimum_required(VERSION 3.8)
project(omnifleet_behaviors)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

ament_python_install_package(omnifleet_behaviors)

install(PROGRAMS
  scripts/foxglove_nav_bridge
  scripts/map_save_view_stop
  scripts/mission_manager
  DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_goal_transactions test/test_goal_transactions.py)
  ament_add_pytest_test(test_manual_stop_detector test/test_manual_stop_detector.py)
  ament_add_pytest_test(test_mission_transactions test/test_mission_transactions.py)
  ament_add_pytest_test(test_storage test/test_storage.py)
  ament_add_pytest_test(test_shutdown_contract test/test_shutdown_contract.py)
endif()

ament_package()
