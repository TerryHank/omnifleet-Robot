#pragma once

#include <array>

namespace omnifleet_localization
{

std::array<double, 3> rotate_vector_xyzw(
  const std::array<double, 3> & vector,
  const std::array<double, 4> & quaternion_xyzw);

}  // namespace omnifleet_localization
