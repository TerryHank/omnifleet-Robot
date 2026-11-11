#pragma once

#include <sensor_msgs/msg/point_cloud2.hpp>
#include <array>
#include <cstdint>

namespace mola
{
// Inspect only the header/layout; do not traverse or convert the point buffer.
inline const char* pointCloudInputError(
    const sensor_msgs::msg::PointCloud2& cloud, double now, double max_age_ms,
    double& last_accepted_stamp)
{
  if (cloud.header.stamp.sec < 0 || cloud.header.stamp.nanosec >= 1000000000U)
    return "invalid_timestamp";
  const double stamp = cloud.header.stamp.sec + cloud.header.stamp.nanosec * 1e-9;
  if ((now - stamp) * 1000.0 > max_age_ms) return "late";
  if (stamp <= last_accepted_stamp) return "duplicate_or_out_of_order";
  if (!cloud.width || !cloud.height || !cloud.point_step) return "empty_or_invalid_layout";
  if (static_cast<std::uint64_t>(cloud.width) * cloud.point_step > cloud.row_step ||
      static_cast<std::uint64_t>(cloud.row_step) * cloud.height > cloud.data.size())
    return "truncated_or_invalid_layout";

  constexpr std::array<unsigned, 9> field_sizes = {0, 1, 1, 2, 2, 4, 4, 4, 8};
  unsigned xyz = 0;
  for (const auto& field : cloud.fields)
  {
    if (field.datatype >= field_sizes.size() || !field_sizes[field.datatype] || !field.count ||
        field.offset + static_cast<std::uint64_t>(field.count) * field_sizes[field.datatype] >
            cloud.point_step)
      return "invalid_field_layout";
    if (field.name == "x") xyz |= 1;
    if (field.name == "y") xyz |= 2;
    if (field.name == "z") xyz |= 4;
  }
  if (xyz != 7) return "missing_xyz";
  last_accepted_stamp = stamp;
  return nullptr;
}
}  // namespace mola
