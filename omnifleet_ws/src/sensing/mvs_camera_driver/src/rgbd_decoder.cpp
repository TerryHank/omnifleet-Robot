#include "mvs_camera_driver/rgbd_decoder.hpp"

#ifdef MVS_HAS_JETSON_ACCELERATION
#include "mvs_camera_driver/rgbd_acceleration.hpp"
#endif

#include <cmath>
#include <limits>
#include <stdexcept>

namespace mvs_camera_driver
{
ImageKind classify_pixel_type(MvGvspPixelType pixel_type)
{
  switch (pixel_type) {
    case PixelType_Gvsp_RGB8_Packed:
      return ImageKind::ColorRgb8;
    case PixelType_Gvsp_BGR8_Packed:
      return ImageKind::ColorBgr8;
    case PixelType_Gvsp_Mono8:
      return ImageKind::ColorMono8;
    case PixelType_Gvsp_Coord3D_C16:
    case PixelType_Gvsp_Mono16:
      return ImageKind::Depth16;
    default:
      return ImageKind::Unsupported;
  }
}

float depth_u16_to_meters(
  std::uint16_t raw_depth,
  float depth_scale,
  float minimum_depth,
  float maximum_depth)
{
  const float invalid = std::numeric_limits<float>::quiet_NaN();
  if (raw_depth == 0U || depth_scale <= 0.0F) {
    return invalid;
  }

  const float depth = static_cast<float>(raw_depth) * depth_scale;
  if (depth < minimum_depth || depth > maximum_depth) {
    return invalid;
  }
  return depth;
}

CameraIntrinsics scale_intrinsics(
  const CameraIntrinsics & nominal,
  std::uint32_t width,
  std::uint32_t height)
{
  if (nominal.width == 0U || nominal.height == 0U || width == 0U || height == 0U) {
    throw std::invalid_argument("camera dimensions must be nonzero");
  }

  const double scale_x = static_cast<double>(width) / static_cast<double>(nominal.width);
  const double scale_y = static_cast<double>(height) / static_cast<double>(nominal.height);
  return CameraIntrinsics{
    nominal.fx * scale_x,
    nominal.fy * scale_y,
    nominal.cx * scale_x,
    nominal.cy * scale_y,
    width,
    height,
  };
}

std::vector<std::uint8_t> resize_rgb8_nearest(
  const std::uint8_t * source,
  std::uint32_t source_width,
  std::uint32_t source_height,
  std::uint32_t target_width,
  std::uint32_t target_height,
  bool allow_jetson_acceleration,
  bool * used_jetson_acceleration)
{
  if (used_jetson_acceleration != nullptr) {
    *used_jetson_acceleration = false;
  }
  if (source == nullptr) {
    throw std::invalid_argument("RGB source buffer must not be null");
  }
  if (source_width == 0U || source_height == 0U || target_width == 0U || target_height == 0U) {
    throw std::invalid_argument("RGB image dimensions must be nonzero");
  }

#ifdef MVS_HAS_JETSON_ACCELERATION
  std::vector<std::uint8_t> accelerated_target;
  if (allow_jetson_acceleration && resize_rgb8_vpi_vic(
      source, source_width, source_height, target_width, target_height, accelerated_target))
  {
    if (used_jetson_acceleration != nullptr) {
      *used_jetson_acceleration = true;
    }
    return accelerated_target;
  }
#endif

  std::vector<std::uint8_t> target(
    static_cast<std::size_t>(target_width) * target_height * 3U);
  for (std::uint32_t y = 0; y < target_height; ++y) {
    const std::uint32_t source_y = static_cast<std::uint32_t>(
      static_cast<std::uint64_t>(y) * source_height / target_height);
    for (std::uint32_t x = 0; x < target_width; ++x) {
      const std::uint32_t source_x = static_cast<std::uint32_t>(
        static_cast<std::uint64_t>(x) * source_width / target_width);
      const std::size_t source_index =
        (static_cast<std::size_t>(source_y) * source_width + source_x) * 3U;
      const std::size_t target_index =
        (static_cast<std::size_t>(y) * target_width + x) * 3U;
      target[target_index] = source[source_index];
      target[target_index + 1U] = source[source_index + 1U];
      target[target_index + 2U] = source[source_index + 2U];
    }
  }
  return target;
}

std::vector<PointXyzRgb> project_rgbd(
  const std::uint16_t * depth,
  const std::uint8_t * rgb,
  std::uint32_t width,
  std::uint32_t height,
  const CameraIntrinsics & intrinsics,
  float depth_scale,
  float minimum_depth,
  float maximum_depth)
{
  if (depth == nullptr || rgb == nullptr) {
    throw std::invalid_argument("RGB-D buffers must not be null");
  }
  if (intrinsics.fx <= 0.0 || intrinsics.fy <= 0.0) {
    throw std::invalid_argument("camera focal lengths must be positive");
  }

  const std::size_t pixel_count = static_cast<std::size_t>(width) * height;
  std::vector<PointXyzRgb> points(pixel_count);
  const float invalid = std::numeric_limits<float>::quiet_NaN();

  for (std::uint32_t v = 0; v < height; ++v) {
    for (std::uint32_t u = 0; u < width; ++u) {
      const std::size_t index = static_cast<std::size_t>(v) * width + u;
      const float z = depth_u16_to_meters(
        depth[index], depth_scale, minimum_depth, maximum_depth);
      auto & point = points[index];
      point.r = rgb[index * 3U];
      point.g = rgb[index * 3U + 1U];
      point.b = rgb[index * 3U + 2U];
      point.z = z;

      if (std::isfinite(z)) {
        point.x = static_cast<float>((static_cast<double>(u) - intrinsics.cx) * z / intrinsics.fx);
        point.y = static_cast<float>((static_cast<double>(v) - intrinsics.cy) * z / intrinsics.fy);
      } else {
        point.x = invalid;
        point.y = invalid;
      }
    }
  }

  return points;
}
}  // namespace mvs_camera_driver
