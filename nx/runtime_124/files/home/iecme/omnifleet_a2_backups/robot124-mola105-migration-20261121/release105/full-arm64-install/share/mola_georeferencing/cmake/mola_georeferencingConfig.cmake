# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_mola_georeferencing_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED mola_georeferencing_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(mola_georeferencing_FOUND FALSE)
  elseif(NOT mola_georeferencing_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(mola_georeferencing_FOUND FALSE)
  endif()
  return()
endif()
set(_mola_georeferencing_CONFIG_INCLUDED TRUE)

# output package information
if(NOT mola_georeferencing_FIND_QUIETLY)
  message(STATUS "Found mola_georeferencing: 3.4.0 (${mola_georeferencing_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'mola_georeferencing' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${mola_georeferencing_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(mola_georeferencing_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${mola_georeferencing_DIR}/${_extra}")
endforeach()
