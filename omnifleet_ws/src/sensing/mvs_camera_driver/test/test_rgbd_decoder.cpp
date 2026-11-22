#include <cmath>
#include <cstdint>

#include <gtest/gtest.h>

#include "PixelType.h"
#include "mvs_camera_driver/rgbd_decoder.hpp"

namespace mvs_camera_driver
{
namespace
{
TEST(RgbdDecoder, ClassifiesSupportedPixelTypes)
{
  EXPECT_EQ(classify_pixel_type(PixelType_Gvsp_RGB8_Packed), ImageKind::ColorRgb8);
  EXPECT_EQ(classify_pixel_type(PixelType_Gvsp_BGR8_Packed), ImageKind::ColorBgr8);
  EXPECT_EQ(classify_pixel_type(PixelType_Gvsp_Mono8), ImageKind::ColorMono8);
  EXPECT_EQ(classify_pixel_type(PixelType_Gvsp_Coord3D_C16), ImageKind::Depth16);
  EXPECT_EQ(classify_pixel_type(PixelType_Gvsp_Mono16), ImageKind::Depth16);
  EXPECT_EQ(classify_pixel_type(PixelType_Gvsp_BayerRG8), ImageKind::Unsupported);
}

TEST(RgbdDecoder, ConvertsDepthToMetersAndRejectsInvalidSamples)
{
  EXPECT_FLOAT_EQ(depth_u16_to_meters(1250U, 0.001F, 0.2F, 3.5F), 1.25F);
  EXPECT_TRUE(std::isnan(depth_u16_to_meters(0U, 0.001F, 0.2F, 3.5F)));
  EXPECT_TRUE(std::isnan(depth_u16_to_meters(100U, 0.001F, 0.2F, 3.5F)));
  EXPECT_TRUE(std::isnan(depth_u16_to_meters(4000U, 0.001F, 0.2F, 3.5F)));
}

TEST(RgbdDecoder, ScalesNominalIntrinsicsToStreamResolution)
{
  const CameraIntrinsics nominal{1000.0, 1000.0, 768.0, 640.0, 1536U, 1280U};
  const auto scaled = scale_intrinsics(nominal, 768U, 640U);

  EXPECT_DOUBLE_EQ(scaled.fx, 500.0);
  EXPECT_DOUBLE_EQ(scaled.fy, 500.0);
  EXPECT_DOUBLE_EQ(scaled.cx, 384.0);
  EXPECT_DOUBLE_EQ(scaled.cy, 320.0);
  EXPECT_EQ(scaled.width, 768U);
  EXPECT_EQ(scaled.height, 640U);
}

TEST(RgbdDecoder, ResizesRgbToDepthGrid)
{
  const std::uint8_t source[] = {
    10U, 11U, 12U, 20U, 21U, 22U, 30U, 31U, 32U, 40U, 41U, 42U,
    50U, 51U, 52U, 60U, 61U, 62U, 70U, 71U, 72U, 80U, 81U, 82U,
  };

  const auto resized = resize_rgb8_nearest(source, 4U, 2U, 2U, 1U, false);

  ASSERT_EQ(resized.size(), 6U);
  EXPECT_EQ(resized[0], 10U);
  EXPECT_EQ(resized[1], 11U);
  EXPECT_EQ(resized[2], 12U);
  EXPECT_EQ(resized[3], 30U);
  EXPECT_EQ(resized[4], 31U);
  EXPECT_EQ(resized[5], 32U);
}

TEST(RgbdDecoder, ProjectsAColorizedDepthPixel)
{
  const CameraIntrinsics intrinsics{2.0, 2.0, 0.0, 0.0, 2U, 1U};
  const std::uint16_t depth[] = {1000U, 2000U};
  const std::uint8_t rgb[] = {10U, 20U, 30U, 40U, 50U, 60U};

  const auto points = project_rgbd(depth, rgb, 2U, 1U, intrinsics, 0.001F, 0.2F, 3.5F);

  ASSERT_EQ(points.size(), 2U);
  EXPECT_FLOAT_EQ(points[0].x, 0.0F);
  EXPECT_FLOAT_EQ(points[0].y, 0.0F);
  EXPECT_FLOAT_EQ(points[0].z, 1.0F);
  EXPECT_EQ(points[0].r, 10U);
  EXPECT_EQ(points[0].g, 20U);
  EXPECT_EQ(points[0].b, 30U);
  EXPECT_FLOAT_EQ(points[1].x, 1.0F);
  EXPECT_FLOAT_EQ(points[1].z, 2.0F);
  EXPECT_EQ(points[1].r, 40U);
}
}  // namespace
}  // namespace mvs_camera_driver
