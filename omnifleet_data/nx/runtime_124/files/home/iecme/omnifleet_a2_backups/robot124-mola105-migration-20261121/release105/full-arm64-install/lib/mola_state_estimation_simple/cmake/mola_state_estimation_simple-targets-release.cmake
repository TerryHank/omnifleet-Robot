#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "mola::mola_state_estimation_simple" for configuration "Release"
set_property(TARGET mola::mola_state_estimation_simple APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mola::mola_state_estimation_simple PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmola_state_estimation_simple.so.3.4.0"
  IMPORTED_SONAME_RELEASE "libmola_state_estimation_simple.so.3.4"
  )

list(APPEND _IMPORT_CHECK_TARGETS mola::mola_state_estimation_simple )
list(APPEND _IMPORT_CHECK_FILES_FOR_mola::mola_state_estimation_simple "${_IMPORT_PREFIX}/lib/libmola_state_estimation_simple.so.3.4.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
