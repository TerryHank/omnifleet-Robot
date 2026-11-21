# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_mola_sm_loop_closure_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED mola_sm_loop_closure_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(mola_sm_loop_closure_FOUND FALSE)
  elseif(NOT mola_sm_loop_closure_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(mola_sm_loop_closure_FOUND FALSE)
  endif()
  return()
endif()
set(_mola_sm_loop_closure_CONFIG_INCLUDED TRUE)

# output package information
if(NOT mola_sm_loop_closure_FIND_QUIETLY)
  message(STATUS "Found mola_sm_loop_closure: 1.5.0 (${mola_sm_loop_closure_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'mola_sm_loop_closure' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${mola_sm_loop_closure_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(mola_sm_loop_closure_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${mola_sm_loop_closure_DIR}/${_extra}")
endforeach()
