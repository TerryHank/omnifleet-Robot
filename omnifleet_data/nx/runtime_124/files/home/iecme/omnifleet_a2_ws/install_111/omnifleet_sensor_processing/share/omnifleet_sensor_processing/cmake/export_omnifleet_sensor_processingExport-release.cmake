#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "omnifleet_sensor_processing::omnifleet_sensor_conversions" for configuration "Release"
set_property(TARGET omnifleet_sensor_processing::omnifleet_sensor_conversions APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(omnifleet_sensor_processing::omnifleet_sensor_conversions PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libomnifleet_sensor_conversions.a"
  )

list(APPEND _IMPORT_CHECK_TARGETS omnifleet_sensor_processing::omnifleet_sensor_conversions )
list(APPEND _IMPORT_CHECK_FILES_FOR_omnifleet_sensor_processing::omnifleet_sensor_conversions "${_IMPORT_PREFIX}/lib/libomnifleet_sensor_conversions.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
