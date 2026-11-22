#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "mola::mola_lidar_odometry" for configuration "Release"
set_property(TARGET mola::mola_lidar_odometry APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mola::mola_lidar_odometry PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "mola::mola_relocalization;TBB::tbb"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmola_lidar_odometry.so.3.6.0"
  IMPORTED_SONAME_RELEASE "libmola_lidar_odometry.so.3.6"
  )

list(APPEND _IMPORT_CHECK_TARGETS mola::mola_lidar_odometry )
list(APPEND _IMPORT_CHECK_FILES_FOR_mola::mola_lidar_odometry "${_IMPORT_PREFIX}/lib/libmola_lidar_odometry.so.3.6.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
