#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "mola::mola_metric_maps" for configuration "Release"
set_property(TARGET mola::mola_metric_maps APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mola::mola_metric_maps PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELEASE "TBB::tbb"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmola_metric_maps.so.3.6.0"
  IMPORTED_SONAME_RELEASE "libmola_metric_maps.so.3.6"
  )

list(APPEND _IMPORT_CHECK_TARGETS mola::mola_metric_maps )
list(APPEND _IMPORT_CHECK_FILES_FOR_mola::mola_metric_maps "${_IMPORT_PREFIX}/lib/libmola_metric_maps.so.3.6.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
