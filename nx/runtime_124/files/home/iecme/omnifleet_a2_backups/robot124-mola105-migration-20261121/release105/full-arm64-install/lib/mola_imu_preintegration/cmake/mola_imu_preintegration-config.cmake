include(CMakeFindDependencyMacro)

# Hints to help CMake finding my dependencies (and theirs own), as well as
# other future calls to search for other mola modules from our parent scope:
# 1: MOLA_DIR cmake var:
if (NOT "${MOLA_DIR}" STREQUAL "")
  list(APPEND CMAKE_PREFIX_PATH "${MOLA_DIR}")
  # If the user defines MOLA_DIR, that path overrides whatever CMake on its own
  # found (this file):
  get_filename_component(this_dir "${CMAKE_CURRENT_LIST_DIR}" ABSOLUTE)
  get_filename_component(user_mola_dir "${MOLA_DIR}" ABSOLUTE)
  if ((EXISTS "${MOLA_DIR}/mola_imu_preintegration-config.cmake") AND (NOT "${this_dir}" STREQUAL "${user_mola_dir}"))
    message("mola_imu_preintegration_DIR was: ${mola_imu_preintegration_DIR}")
    set(mola_imu_preintegration_DIR "${MOLA_DIR}" CACHE PATH "Path to mola_imu_preintegration" FORCE)
    include(${MOLA_DIR}/mola_imu_preintegration-config.cmake)
    return()
  endif()
endif()
# 2) The current (and parent) path:
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_LIST_DIR}")
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_CURRENT_LIST_DIR}/../")
list(REMOVE_DUPLICATES CMAKE_PREFIX_PATH)

# Search for dependencies first:
set(_deps "mola_common")
foreach(_dep ${_deps}) # NO quotes for the list to be a CMake list!
  find_dependency(${_dep})
  if(${_dep}_FOUND)
    mark_as_advanced(${_dep}_DIR)
  endif()
endforeach()


# Include targets for this library:
include(${CMAKE_CURRENT_LIST_DIR}/mola_imu_preintegration-targets.cmake)
