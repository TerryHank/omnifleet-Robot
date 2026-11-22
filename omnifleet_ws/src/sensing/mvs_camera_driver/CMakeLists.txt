cmake_minimum_required(VERSION 3.8)
project(mvs_camera_driver)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(
    $<$<COMPILE_LANGUAGE:CXX>:-Wall>
    $<$<COMPILE_LANGUAGE:CXX>:-Wextra>
    $<$<COMPILE_LANGUAGE:CXX>:-Wpedantic>
  )
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

option(MVS_USE_SYSTEM_SDK "Use an already installed SDK from MVS_SDK_ROOT or /opt/MVS" OFF)
option(MVS_INSTALL_VENDOR_ARCHIVES "Install bundled MVS SDK archives into the package share directory" ON)
option(MVS_ENABLE_JETSON_ACCELERATION "Use CUDA and VPI/VIC for RGB-D processing on Jetson" ON)
set(MVS_SDK_ROOT "" CACHE PATH "Root of an installed MVS SDK, for example /opt/MVS")
set(MVS_SDK_LIB_DIR "" CACHE PATH "MVS SDK library directory override")

find_package(ament_cmake REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(image_transport REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)

function(mvs_detect_sdk_arch out_arch out_relative_lib_dir out_archive out_outer_dir)
  string(TOLOWER "${CMAKE_SYSTEM_PROCESSOR}" mvs_processor)
  if(mvs_processor MATCHES "^(x86_64|amd64)$")
    set(mvs_arch "x86_64")
    set(mvs_relative_lib_dir "lib/64")
    set(mvs_archive "${CMAKE_CURRENT_SOURCE_DIR}/vendor/MVS-5.0.1_x86_64_20260512.tar.gz")
    set(mvs_outer_dir "MVS-5.0.1_x86_64_20260512")
  elseif(mvs_processor MATCHES "^(aarch64|arm64)$")
    set(mvs_arch "aarch64")
    set(mvs_relative_lib_dir "lib/aarch64")
    set(mvs_archive "${CMAKE_CURRENT_SOURCE_DIR}/vendor/MVS-5.0.1_aarch64_20260512.tar.gz")
    set(mvs_outer_dir "MVS-5.0.1_aarch64_20260512")
  else()
    message(FATAL_ERROR "Unsupported CPU architecture for bundled MVS SDK: ${CMAKE_SYSTEM_PROCESSOR}")
  endif()

  set(${out_arch} "${mvs_arch}" PARENT_SCOPE)
  set(${out_relative_lib_dir} "${mvs_relative_lib_dir}" PARENT_SCOPE)
  set(${out_archive} "${mvs_archive}" PARENT_SCOPE)
  set(${out_outer_dir} "${mvs_outer_dir}" PARENT_SCOPE)
endfunction()

mvs_detect_sdk_arch(MVS_ARCH MVS_RELATIVE_LIB_DIR MVS_ARCHIVE MVS_OUTER_DIR_NAME)

if(MVS_USE_SYSTEM_SDK)
  if(NOT MVS_SDK_ROOT)
    set(MVS_SDK_ROOT "/opt/MVS")
  endif()
else()
  if(NOT EXISTS "${MVS_ARCHIVE}")
    message(FATAL_ERROR "Bundled MVS archive not found: ${MVS_ARCHIVE}")
  endif()

  set(MVS_EXTRACT_BASE "${CMAKE_CURRENT_BINARY_DIR}/mvs_sdk/${MVS_ARCH}")
  set(MVS_OUTER_EXTRACT_DIR "${MVS_EXTRACT_BASE}/outer")
  set(MVS_SDK_ROOT "${MVS_EXTRACT_BASE}/MVS")
  set(MVS_EXTRACT_STAMP "${MVS_SDK_ROOT}/.mvs_extracted")

  if(NOT EXISTS "${MVS_EXTRACT_STAMP}")
    file(REMOVE_RECURSE "${MVS_EXTRACT_BASE}")
    file(MAKE_DIRECTORY "${MVS_OUTER_EXTRACT_DIR}" "${MVS_SDK_ROOT}")

    execute_process(
      COMMAND "${CMAKE_COMMAND}" -E tar xzf "${MVS_ARCHIVE}"
      WORKING_DIRECTORY "${MVS_OUTER_EXTRACT_DIR}"
      RESULT_VARIABLE MVS_OUTER_RESULT
    )
    if(NOT MVS_OUTER_RESULT EQUAL 0)
      message(FATAL_ERROR "Failed to extract outer MVS archive: ${MVS_ARCHIVE}")
    endif()

    set(MVS_INNER_ARCHIVE "${MVS_OUTER_EXTRACT_DIR}/${MVS_OUTER_DIR_NAME}/MVS.tar.gz")
    if(NOT EXISTS "${MVS_INNER_ARCHIVE}")
      message(FATAL_ERROR "Inner MVS.tar.gz not found after extracting: ${MVS_ARCHIVE}")
    endif()

    execute_process(
      COMMAND "${CMAKE_COMMAND}" -E tar xzf "${MVS_INNER_ARCHIVE}"
      WORKING_DIRECTORY "${MVS_SDK_ROOT}"
      RESULT_VARIABLE MVS_INNER_RESULT
    )
    if(NOT MVS_INNER_RESULT EQUAL 0)
      message(FATAL_ERROR "Failed to extract inner MVS.tar.gz from: ${MVS_ARCHIVE}")
    endif()

    file(WRITE "${MVS_EXTRACT_STAMP}" "Extracted ${MVS_OUTER_DIR_NAME}\n")
  endif()
endif()

set(MVS_SDK_INCLUDE_DIR "${MVS_SDK_ROOT}/include")
if(NOT MVS_SDK_LIB_DIR)
  set(MVS_SDK_LIB_DIR "${MVS_SDK_ROOT}/${MVS_RELATIVE_LIB_DIR}")
endif()

if(NOT EXISTS "${MVS_SDK_INCLUDE_DIR}/MvCameraControl.h")
  message(FATAL_ERROR "MVS SDK header not found: ${MVS_SDK_INCLUDE_DIR}/MvCameraControl.h")
endif()

if(NOT EXISTS "${MVS_SDK_LIB_DIR}/libMvCameraControl.so")
  message(FATAL_ERROR "MVS SDK library not found: ${MVS_SDK_LIB_DIR}/libMvCameraControl.so")
endif()

add_library(MVS::CameraControl SHARED IMPORTED)
set_target_properties(MVS::CameraControl PROPERTIES
  IMPORTED_LOCATION "${MVS_SDK_LIB_DIR}/libMvCameraControl.so"
  INTERFACE_INCLUDE_DIRECTORIES "${MVS_SDK_INCLUDE_DIR}"
)

add_library(mvs_rgbd_decoder
  src/rgbd_decoder.cpp
)
target_include_directories(mvs_rgbd_decoder PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
  "${MVS_SDK_INCLUDE_DIR}"
)

if(MVS_ENABLE_JETSON_ACCELERATION AND MVS_ARCH STREQUAL "aarch64")
  include(CheckLanguage)
  if(EXISTS "/usr/local/cuda/bin/nvcc")
    set(
      CMAKE_CUDA_COMPILER "/usr/local/cuda/bin/nvcc" CACHE FILEPATH
      "JetPack CUDA compiler" FORCE
    )
  endif()
  check_language(CUDA)
  if(CMAKE_CUDA_COMPILER)
    enable_language(CUDA)
    find_package(CUDAToolkit REQUIRED)
    find_package(OpenCV REQUIRED COMPONENTS core)
    find_path(VPI_INCLUDE_DIR
      NAMES vpi/VPI.h
      PATHS /opt/nvidia/vpi3/include
      REQUIRED
    )
    find_library(VPI_LIBRARY
      NAMES nvvpi
      PATHS /opt/nvidia/vpi3/lib/aarch64-linux-gnu /usr/lib/aarch64-linux-gnu
      REQUIRED
    )

    target_sources(mvs_rgbd_decoder PRIVATE
      src/rgbd_cuda.cu
      src/rgbd_vpi.cpp
    )
    target_include_directories(mvs_rgbd_decoder PRIVATE
      "${VPI_INCLUDE_DIR}"
      ${OpenCV_INCLUDE_DIRS}
    )
    target_link_libraries(mvs_rgbd_decoder PUBLIC
      CUDA::cudart
      "${VPI_LIBRARY}"
      ${OpenCV_LIBS}
    )
    target_compile_definitions(mvs_rgbd_decoder PUBLIC MVS_HAS_JETSON_ACCELERATION=1)
    set_target_properties(mvs_rgbd_decoder PROPERTIES
      CUDA_STANDARD 17
      CUDA_STANDARD_REQUIRED ON
      CUDA_ARCHITECTURES 87
      POSITION_INDEPENDENT_CODE ON
    )
    message(STATUS "MVS Jetson acceleration enabled: CUDA RGB-D projection and VPI/VIC resize")
  else()
    message(WARNING "CUDA compiler not found; building MVS driver with CPU fallback")
  endif()
endif()

add_executable(mvs_camera_node
  src/mvs_camera_node.cpp
)

target_include_directories(mvs_camera_node PRIVATE
  include
  "${MVS_SDK_INCLUDE_DIR}"
)

ament_target_dependencies(mvs_camera_node
  ament_index_cpp
  image_transport
  rclcpp
  sensor_msgs
  std_msgs
)

target_link_libraries(mvs_camera_node
  MVS::CameraControl
  mvs_rgbd_decoder
  pthread
)

target_compile_definitions(mvs_camera_node PRIVATE
  MVS_CAMERA_DRIVER_PACKAGE_NAME="${PROJECT_NAME}"
)

set_target_properties(mvs_camera_node PROPERTIES
  BUILD_RPATH "${MVS_SDK_LIB_DIR};${MVS_SDK_LIB_DIR}/ThirdParty"
  INSTALL_RPATH "$ORIGIN/../../share/${PROJECT_NAME}/mvs;$ORIGIN/../../share/${PROJECT_NAME}/mvs/ThirdParty"
)

install(TARGETS mvs_camera_node
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY "${MVS_SDK_LIB_DIR}/"
  DESTINATION share/${PROJECT_NAME}/mvs
  USE_SOURCE_PERMISSIONS
)

install(DIRECTORY config launch
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY scripts
  DESTINATION share/${PROJECT_NAME}
  USE_SOURCE_PERMISSIONS
)

if(MVS_INSTALL_VENDOR_ARCHIVES)
  install(DIRECTORY vendor
    DESTINATION share/${PROJECT_NAME}
  )
endif()

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_gtest(test_rgbd_decoder
    test/test_rgbd_decoder.cpp
  )
  target_include_directories(test_rgbd_decoder PRIVATE
    include
    "${MVS_SDK_INCLUDE_DIR}"
  )
  target_link_libraries(test_rgbd_decoder
    mvs_rgbd_decoder
  )
  ament_add_pytest_test(test_rgbd_config
    test/test_rgbd_config.py
  )
endif()

ament_package()
