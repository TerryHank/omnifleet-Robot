#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "mola::mola_launcher" for configuration "Release"
set_property(TARGET mola::mola_launcher APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mola::mola_launcher PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmola_launcher.so.3.6.0"
  IMPORTED_SONAME_RELEASE "libmola_launcher.so.3.6"
  )

list(APPEND _IMPORT_CHECK_TARGETS mola::mola_launcher )
list(APPEND _IMPORT_CHECK_FILES_FOR_mola::mola_launcher "${_IMPORT_PREFIX}/lib/libmola_launcher.so.3.6.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
