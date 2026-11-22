#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "mola::mola_bridge_ros2" for configuration "Release"
set_property(TARGET mola::mola_bridge_ros2 APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mola::mola_bridge_ros2 PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "mola::mola_kernel;mrpt::mrpt_maps;mrpt_libros_bridge::mrpt_libros_bridge"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmola_bridge_ros2.so.3.6.0"
  IMPORTED_SONAME_RELEASE "libmola_bridge_ros2.so.3.6"
  )

list(APPEND _IMPORT_CHECK_TARGETS mola::mola_bridge_ros2 )
list(APPEND _IMPORT_CHECK_FILES_FOR_mola::mola_bridge_ros2 "${_IMPORT_PREFIX}/lib/libmola_bridge_ros2.so.3.6.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
