# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target mola_msgs::mola_msgs
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${mola_msgs_TARGETS}.
if(mola_msgs_TARGETS AND NOT TARGET mola_msgs::mola_msgs)
  add_library(mola_msgs::mola_msgs INTERFACE IMPORTED)
  set_target_properties(mola_msgs::mola_msgs PROPERTIES
    INTERFACE_LINK_LIBRARIES "${mola_msgs_TARGETS}")
endif()
