cmake_minimum_required(VERSION 3.8)
project(omnifleet_a2_bringup)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

ament_python_install_package(omnifleet_a2_bringup)

install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})
install(PROGRAMS
  scripts/ackermann_driver
  scripts/omnifleet-a2-resolve-chassis-port
  scripts/run_direct_serial_radius_test
  scripts/robot_doctor
  scripts/vehicle_status
  scripts/vehicle_boot_selfcheck
  scripts/vehicle_task_log
  DESTINATION lib/${PROJECT_NAME})
install(FILES README.md DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_command_chain test/test_command_chain.py)
  ament_add_pytest_test(test_kinematics_ownership test/test_kinematics_ownership.py)
  ament_add_pytest_test(test_r2_sensor_contract test/test_r2_sensor_contract.py)
  ament_add_pytest_test(test_robot_doctor test/test_robot_doctor.py)
  ament_add_pytest_test(test_vehicle_task_log test/test_vehicle_task_log.py)
  ament_add_pytest_test(test_boot_selfcheck test/test_boot_selfcheck.py)
endif()

ament_package()
