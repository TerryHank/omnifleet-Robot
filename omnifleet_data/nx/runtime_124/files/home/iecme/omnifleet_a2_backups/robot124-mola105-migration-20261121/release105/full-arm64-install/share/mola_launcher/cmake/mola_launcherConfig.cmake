# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_mola_launcher_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED mola_launcher_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(mola_launcher_FOUND FALSE)
  elseif(NOT mola_launcher_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(mola_launcher_FOUND FALSE)
  endif()
  return()
endif()
set(_mola_launcher_CONFIG_INCLUDED TRUE)

# output package information
if(NOT mola_launcher_FIND_QUIETLY)
  message(STATUS "Found mola_launcher: 3.6.0 (${mola_launcher_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'mola_launcher' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${mola_launcher_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(mola_launcher_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${mola_launcher_DIR}/${_extra}")
endforeach()
