#pragma once

#include <cstdint>
#include <vector>

#include "PixelType.h"

namespace mvs_camera_driver
{
enum class ImageKind
{
  ColorRgb8,
  ColorBgr8,
  ColorMono8,
  Depth16,
  Unsupported,
};

struct CameraIntrinsics
{
  double fx;
  double fy;
  double cx;
  double cy;
  std::uint32_t width;
  std::uint32_t height;
};

struct PointXyzRgb
{
  float x;
  float y;
  float z;
  std::uint8_t b;
  std::uint8_t g;
  std::uint8_t r;
  std::uint8_t reserved;
};

ImageKind classify_pixel_type(MvGvspPixelType pixel_type);

float depth_u16_to_meters(
  std::uint16_t raw_depth,
  float depth_scale,
  float minimum_depth,
  float maximum_depth);

CameraIntrinsics scale_intrinsics(
  const CameraIntrinsics & nominal,
  std::uint32_t width,
  std::uint32_t height);

std::vector<std::uint8_t> resize_rgb8_nearest(
  const std::uint8_t * source,
  std::uint32_t source_width,
  std::uint32_t source_height,
  std::uint32_t target_width,
  std::uint32_t target_height,
  bool allow_jetson_acceleration = true,
  bool * used_jetson_acceleration = nullptr);

std::vector<PointXyzRgb> project_rgbd(
  const std::uint16_t * depth,
  const std::uint8_t * rgb,
  std::uint32_t width,
  std::uint32_t height,
  const CameraIntrinsics & intrinsics,
  float depth_scale,
  float minimum_depth,
  float maximum_depth);
}  // namespace mvs_camera_driver
