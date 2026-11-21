#include "omnifleet_mola_grid/grid_core.hpp"
#include <gtest/gtest.h>
#include <algorithm>
#include <stdexcept>

TEST(ExternalGrid, MolaSliceRetainsOccupiedFreeAndUnknown)
{
  auto voxels = std::make_shared<mrpt::maps::CVoxelMap>(0.1);
  mrpt::maps::CSimplePointsMap points;
  points.insertPoint(2, 0, 0.5);
  points.insertPoint(0, 2, 0.5);
  for (int i = 0; i < 12; ++i) voxels->insertPointCloudAsRays(points, {0, 0, 0.5});
  std_msgs::msg::Header header;
  header.frame_id = "camera_init";
  auto map = omnifleet_mola_grid::slice(voxels, 0.4, 0.6, header, 10000);
  EXPECT_EQ(map.header.frame_id, "camera_init");
  EXPECT_DOUBLE_EQ(map.info.origin.orientation.w, 1.0);
  EXPECT_EQ(map.data.size(), map.info.width * map.info.height);
  EXPECT_NE(std::find(map.data.begin(), map.data.end(), -1), map.data.end());
  EXPECT_TRUE(std::any_of(map.data.begin(), map.data.end(), [](int v){return v >= 0 && v < 20;}));
  EXPECT_TRUE(std::any_of(map.data.begin(), map.data.end(), [](int v){return v > 80;}));
}

TEST(ExternalGrid, RejectsInvalidHeightAndOversizedGrid)
{
  auto voxels = std::make_shared<mrpt::maps::CVoxelMap>(0.1);
  voxels->updateVoxel(0, 0, 0.5, true);
  voxels->updateVoxel(5, 5, 0.5, true);
  std_msgs::msg::Header header;
  EXPECT_THROW(omnifleet_mola_grid::slice(voxels, 1, 0, header, 10000), std::invalid_argument);
  EXPECT_THROW(omnifleet_mola_grid::slice(voxels, 0, 1, header, 4), std::length_error);
}

TEST(ExternalGrid, ExcludesVoxelsAboveTheObstacleSlice)
{
  auto voxels = std::make_shared<mrpt::maps::CVoxelMap>(0.1);
  voxels->updateVoxel(2, 2, 2, true);
  std_msgs::msg::Header header;
  auto map = omnifleet_mola_grid::slice(voxels, 0, 1, header, 10000);
  EXPECT_TRUE(std::all_of(map.data.begin(), map.data.end(), [](int v){return v == -1;}));
}
