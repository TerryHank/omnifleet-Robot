cmake_minimum_required(VERSION 3.8)
project(omnifleet_bringup)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

ament_python_install_package(omnifleet_bringup)

install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})
install(PROGRAMS
  scripts/ackermann_driver
  scripts/keyboard_teleop
  scripts/robot_doctor
  scripts/vr_protocol_adapter
  scripts/stm32_feedback_adapter
  scripts/teleop_command_repeater
  scripts/voltage_display_node.py
  DESTINATION lib/${PROJECT_NAME})
install(FILES README.md DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_command_chain test/test_command_chain.py)
  ament_add_pytest_test(test_kinematics_ownership test/test_kinematics_ownership.py)
  ament_add_pytest_test(test_feedback_adapter test/test_feedback_adapter.py)
  ament_add_pytest_test(test_r2_sensor_contract test/test_r2_sensor_contract.py)
  ament_add_pytest_test(test_robot_doctor test/test_robot_doctor.py)
  ament_add_pytest_test(test_manual_stack_shutdown test/test_manual_stack_shutdown.py)
endif()

ament_package()
