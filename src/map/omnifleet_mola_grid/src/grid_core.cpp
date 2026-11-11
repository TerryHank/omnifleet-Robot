#include "omnifleet_mola_grid/grid_core.hpp"
#include <mp2p_icp_filters/FilterVoxelSlice.h>
#include <mrpt/maps/COccupancyGridMap2D.h>
#include <mrpt/ros2bridge/map.h>
#include <cmath>
#include <stdexcept>

namespace omnifleet_mola_grid
{
nav_msgs::msg::OccupancyGrid slice(
  const mrpt::maps::CVoxelMap::Ptr& voxels, double z_min, double z_max,
  const std_msgs::msg::Header& header, size_t max_cells)
{
  if (!std::isfinite(z_min) || !std::isfinite(z_max) || z_min > z_max || voxels->isEmpty())
    throw std::invalid_argument("empty voxel map or invalid slice heights");
  const auto bounds = voxels->boundingBox();
  const double resolution = voxels->grid().resolution;
  const double width = std::ceil((bounds.max.x - bounds.min.x) / resolution) + 4;
  const double height = std::ceil((bounds.max.y - bounds.min.y) / resolution) + 4;
  if (!std::isfinite(width * height) || width * height > max_cells)
    throw std::length_error("grid exceeds max_grid_cells");
  mp2p_icp::metric_map_t map;
  map.layers["voxels"] = voxels;
  mp2p_icp_filters::FilterVoxelSlice filter;
  filter.params.input_layer = "voxels";
  filter.params.output_layer = "grid";
  filter.params.slice_z_min = z_min;
  filter.params.slice_z_max = z_max;
  filter.filter(map);
  auto grid = std::dynamic_pointer_cast<mrpt::maps::COccupancyGridMap2D>(map.layers.at("grid"));
  nav_msgs::msg::OccupancyGrid message;
  mrpt::ros2bridge::toROS(*grid, message, header);
  return message;
}
}
