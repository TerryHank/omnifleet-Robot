cmake_minimum_required(VERSION 3.8)
project(omnifleet_behaviors)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

ament_python_install_package(omnifleet_behaviors)

install(PROGRAMS
  scripts/traffic_light_nav_supervisor
  scripts/wonderecho_voice
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
  PATTERN "__pycache__" EXCLUDE
  PATTERN "*.pyc" EXCLUDE)

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_traffic_light_navigation test/test_traffic_light_navigation.py)
  ament_add_pytest_test(test_wonderecho_voice_logic test/test_wonderecho_voice_logic.py)
endif()

ament_package()
