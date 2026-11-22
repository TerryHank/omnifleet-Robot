#pragma once
#include <mrpt/maps/CVoxelMap.h>
#include <mrpt/maps/CSimplePointsMap.h>
#include <nav_msgs/msg/occupancy_grid.hpp>

namespace omnifleet_mola_grid
{
nav_msgs::msg::OccupancyGrid slice(
  const mrpt::maps::CVoxelMap::Ptr& voxels, double z_min, double z_max,
  const std_msgs::msg::Header& header, size_t max_cells);
}
