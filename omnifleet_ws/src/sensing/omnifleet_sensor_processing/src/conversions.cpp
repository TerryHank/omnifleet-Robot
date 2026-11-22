#include "omnifleet_localization/conversions.hpp"

#include <cmath>
#include <stdexcept>

namespace omnifleet_localization
{

std::array<double, 3> rotate_vector_xyzw(
  const std::array<double, 3> & vector,
  const std::array<double, 4> & quaternion_xyzw)
{
  auto quaternion = quaternion_xyzw;
  const double norm = std::sqrt(
    quaternion[0] * quaternion[0] + quaternion[1] * quaternion[1] +
    quaternion[2] * quaternion[2] + quaternion[3] * quaternion[3]);
  if (!std::isfinite(norm) || norm < 1.0e-12) {
    throw std::invalid_argument("rotation quaternion must be finite and non-zero");
  }
  for (auto & value : quaternion) {
    value /= norm;
  }
  const auto x = quaternion[0];
  const auto y = quaternion[1];
  const auto z = quaternion[2];
  const auto w = quaternion[3];
  return {
    (1.0 - 2.0 * (y * y + z * z)) * vector[0] +
      2.0 * (x * y - z * w) * vector[1] +
      2.0 * (x * z + y * w) * vector[2],
    2.0 * (x * y + z * w) * vector[0] +
      (1.0 - 2.0 * (x * x + z * z)) * vector[1] +
      2.0 * (y * z - x * w) * vector[2],
    2.0 * (x * z - y * w) * vector[0] +
      2.0 * (y * z + x * w) * vector[1] +
      (1.0 - 2.0 * (x * x + y * y)) * vector[2],
  };
}

}  // namespace omnifleet_localization
