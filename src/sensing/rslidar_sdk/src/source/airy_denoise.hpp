#pragma once

#include <cmath>
#include <cstddef>

// Airy packets are column-major: one column contains all laser channels.
// Called inside the existing ROS packing loop, without a separate cloud pass.
template <typename Points>
inline bool airyIsolatedReturn(const Points& points, size_t index, size_t channels)
{
  if (channels < 2 || index < 5 * channels || index + 5 * channels >= points.size())
    return false; // Keep incomplete scan boundaries.
  const auto& p = points[index];
  if (!std::isfinite(p.x) || !std::isfinite(p.y) || !std::isfinite(p.z))
    return false;
  const float range2 = p.x * p.x + p.y * p.y + p.z * p.z;
  // 10 cm near the sensor, increasing with angular sampling distance.
  const float radius2 = 0.01f + 0.0004f * range2;
  const auto close = [&](size_t neighbor) {
    const auto& q = points[neighbor];
    const float dx = p.x - q.x, dy = p.y - q.y, dz = p.z - q.z;
    return dx * dx + dy * dy + dz * dz <= radius2;
  };
  const size_t channel = index % channels;
  if (close(index - channels) || close(index + channels) ||
      (channel > 0 && close(index - 1)) ||
      (channel + 1 < channels && close(index + 1)))
    return false;
  // Airy can leave gaps between successive firings. Recheck only candidates
  // in a fixed 11-column x 5-channel window, never searching the whole cloud.
  for (int column = -5; column <= 5; ++column)
    for (int row = -2; row <= 2; ++row) {
      if ((column == 0 && row == 0) ||
          int(channel) + row < 0 || int(channel) + row >= int(channels))
        continue;
      const size_t neighbor = size_t(ptrdiff_t(index) + column * ptrdiff_t(channels) + row);
      if (close(neighbor)) return false;
    }
  return true;
}
