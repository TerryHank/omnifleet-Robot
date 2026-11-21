# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_omnifleet_a2_behaviors_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED omnifleet_a2_behaviors_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(omnifleet_a2_behaviors_FOUND FALSE)
  elseif(NOT omnifleet_a2_behaviors_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(omnifleet_a2_behaviors_FOUND FALSE)
  endif()
  return()
endif()
set(_omnifleet_a2_behaviors_CONFIG_INCLUDED TRUE)

# output package information
if(NOT omnifleet_a2_behaviors_FIND_QUIETLY)
  message(STATUS "Found omnifleet_a2_behaviors: 0.3.0 (${omnifleet_a2_behaviors_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'omnifleet_a2_behaviors' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${omnifleet_a2_behaviors_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(omnifleet_a2_behaviors_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${omnifleet_a2_behaviors_DIR}/${_extra}")
endforeach()
