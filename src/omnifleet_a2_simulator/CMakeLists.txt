cmake_minimum_required(VERSION 3.8)
project(omnifleet_a2_simulator)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config launch models worlds DESTINATION share/${PROJECT_NAME})
install(PROGRAMS
  scripts/traffic_closed_loop_test.py
  scripts/traffic_map_publisher.py
  DESTINATION lib/${PROJECT_NAME}
)
install(FILES THIRD_PARTY_NOTICE.md README.md DESTINATION share/${PROJECT_NAME})

ament_package()
