cmake_minimum_required(VERSION 3.8)
project(omnifleet_tutorials)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch docs config DESTINATION share/${PROJECT_NAME}
  PATTERN "__pycache__" EXCLUDE
  PATTERN "*.pyc" EXCLUDE
)
install(FILES README.md DESTINATION share/${PROJECT_NAME})
install(PROGRAMS scripts/vision_demo_manager.py DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_vision_course_launches test/test_vision_course_launches.py)
endif()

ament_package()
