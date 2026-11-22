#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "mola::mola_input_rosbag2" for configuration "Release"
set_property(TARGET mola::mola_input_rosbag2 APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mola::mola_input_rosbag2 PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "mola::mola_kernel;mrpt::mrpt_obs;mrpt_libros_bridge::mrpt_libros_bridge;tf2::tf2;rclcpp::rclcpp;rosbag2_cpp::rosbag2_cpp;tf2_msgs::tf2_msgs__rosidl_typesupport_cpp;cv_bridge::cv_bridge;gps_msgs::gps_msgs__rosidl_generator_c;gps_msgs::gps_msgs__rosidl_typesupport_fastrtps_c;gps_msgs::gps_msgs__rosidl_typesupport_introspection_c;gps_msgs::gps_msgs__rosidl_typesupport_c;gps_msgs::gps_msgs__rosidl_typesupport_fastrtps_cpp;gps_msgs::gps_msgs__rosidl_typesupport_introspection_cpp;gps_msgs::gps_msgs__rosidl_typesupport_cpp;gps_msgs::gps_msgs__rosidl_generator_py"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmola_input_rosbag2.so.3.6.0"
  IMPORTED_SONAME_RELEASE "libmola_input_rosbag2.so.3.6"
  )

list(APPEND _IMPORT_CHECK_TARGETS mola::mola_input_rosbag2 )
list(APPEND _IMPORT_CHECK_FILES_FOR_mola::mola_input_rosbag2 "${_IMPORT_PREFIX}/lib/libmola_input_rosbag2.so.3.6.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
