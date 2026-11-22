#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "mola::mola_sm_loop_closure" for configuration "Release"
set_property(TARGET mola::mola_sm_loop_closure APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mola::mola_sm_loop_closure PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "TBB::tbb"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmola_sm_loop_closure.so.1.5.0"
  IMPORTED_SONAME_RELEASE "libmola_sm_loop_closure.so.1.5"
  )

list(APPEND _IMPORT_CHECK_TARGETS mola::mola_sm_loop_closure )
list(APPEND _IMPORT_CHECK_FILES_FOR_mola::mola_sm_loop_closure "${_IMPORT_PREFIX}/lib/libmola_sm_loop_closure.so.1.5.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
