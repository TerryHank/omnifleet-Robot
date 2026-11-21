#pragma once

#include <cstdint>
#include <vector>

#include "mvs_camera_driver/rgbd_decoder.hpp"

namespace mvs_camera_driver
{
bool cuda_rgbd_available();
void shutdown_cuda_rgbd();

bool project_rgbd_decimated_cuda(
  const std::uint16_t * depth,
  const std::uint8_t * rgb,
  std::uint32_t width,
  std::uint32_t height,
  std::uint32_t step,
  const CameraIntrinsics & intrinsics,
  float depth_scale,
  float minimum_depth,
  float maximum_depth,
  bool spatial_filter_enabled,
  std::uint32_t minimum_consistent_neighbors,
  float neighbor_depth_tolerance,
  float neighbor_depth_tolerance_ratio,
  std::vector<PointXyzRgb> & points);

bool vpi_vic_available();
void shutdown_vpi_vic();

bool resize_rgb8_vpi_vic(
  const std::uint8_t * source,
  std::uint32_t source_width,
  std::uint32_t source_height,
  std::uint32_t target_width,
  std::uint32_t target_height,
  std::vector<std::uint8_t> & target);
}  // namespace mvs_camera_driver
