cmake_minimum_required(VERSION 3.8)
project(rrc_chassis_core)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME})
install(PROGRAMS scripts/voltage_display_node.py
  DESTINATION lib/${PROJECT_NAME})
install(FILES README.md
  DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_command_chain test/test_command_chain.py)
endif()

ament_package()
