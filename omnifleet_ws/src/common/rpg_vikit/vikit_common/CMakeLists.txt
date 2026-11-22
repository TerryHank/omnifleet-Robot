cmake_minimum_required(VERSION 3.10)
project(vikit_common)
# Match the OpenCV ABI used by ROS Humble cv_bridge and RTAB-Map.
if(EXISTS "/usr/lib/${CMAKE_LIBRARY_ARCHITECTURE}/cmake/opencv4/OpenCVConfig.cmake")
  set(OpenCV_DIR "/usr/lib/${CMAKE_LIBRARY_ARCHITECTURE}/cmake/opencv4"
      CACHE PATH "ROS system OpenCV" FORCE)
endif()

find_package(ament_cmake REQUIRED)
find_package(OpenCV REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(Sophus REQUIRED)
find_package(fmt REQUIRED)
add_library(vikit_common SHARED
  src/atan_camera.cpp src/omni_camera.cpp src/math_utils.cpp src/vision.cpp
  src/performance_monitor.cpp src/robust_cost.cpp src/user_input_thread.cpp
  src/pinhole_camera.cpp src/equidistant_camera.cpp src/polynomial_camera.cpp
  src/homography.cpp src/img_align.cpp)
target_compile_features(vikit_common PUBLIC cxx_std_17)
target_include_directories(vikit_common PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include> ${OpenCV_INCLUDE_DIRS} ${Sophus_INCLUDE_DIRS})
target_link_libraries(vikit_common PUBLIC Eigen3::Eigen ${OpenCV_LIBS} Sophus::Sophus fmt::fmt)
install(TARGETS vikit_common EXPORT export_vikit_common LIBRARY DESTINATION lib)
install(DIRECTORY include/ DESTINATION include)
ament_export_include_directories(include)
ament_export_targets(export_vikit_common HAS_LIBRARY_TARGET)
ament_export_libraries(vikit_common)
ament_export_dependencies(Eigen3 OpenCV Sophus fmt)
ament_package()
