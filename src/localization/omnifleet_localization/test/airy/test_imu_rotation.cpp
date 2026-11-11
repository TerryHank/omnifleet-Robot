#include <array>

#include <gtest/gtest.h>

#include "omnifleet_localization/conversions.hpp"

TEST(AiryImuRotation, RotatesFactoryAxesIntoTheLidarFrame)
{
  const std::array<double, 4> factory_rotation{
    -0.7068467736244202, 0.7073657512664795,
    -0.0005705897347070277, 0.000999057781882584};
  const auto output = omnifleet_localization::rotate_vector_xyzw(
    {0.0072021484375, 0.0150146484375, -1.005859375}, factory_rotation);

  EXPECT_NEAR(output[0], -0.0172529341, 1.0e-9);
  EXPECT_NEAR(output[1], -0.0077997911, 1.0e-9);
  EXPECT_NEAR(output[2], 1.0058190157, 1.0e-9);
}
