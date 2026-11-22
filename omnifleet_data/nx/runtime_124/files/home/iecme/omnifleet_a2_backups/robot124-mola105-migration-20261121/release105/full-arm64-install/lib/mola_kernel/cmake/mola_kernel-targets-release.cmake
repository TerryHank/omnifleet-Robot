#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "mola::mola_kernel" for configuration "Release"
set_property(TARGET mola::mola_kernel APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mola::mola_kernel PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmola_kernel.so.3.6.0"
  IMPORTED_SONAME_RELEASE "libmola_kernel.so.3.6"
  )

list(APPEND _IMPORT_CHECK_TARGETS mola::mola_kernel )
list(APPEND _IMPORT_CHECK_FILES_FOR_mola::mola_kernel "${_IMPORT_PREFIX}/lib/libmola_kernel.so.3.6.0" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
