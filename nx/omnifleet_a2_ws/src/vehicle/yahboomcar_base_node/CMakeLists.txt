cmake_minimum_required(VERSION 3.5)
project(yahboomcar_base_node)

# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.

find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rclcpp  REQUIRED)
if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_r2_odometry_contract test/test_r2_odometry_contract.py)
  ament_add_pytest_test(test_r2_only_contract test/test_r2_only_contract.py)
endif()

add_executable(base_node_R2 src/base_node_R2.cpp)
ament_target_dependencies(base_node_R2 rclcpp tf2 tf2_ros nav_msgs geometry_msgs)
install(TARGETS
  base_node_R2
	DESTINATION lib/${PROJECT_NAME}
)
ament_package()
