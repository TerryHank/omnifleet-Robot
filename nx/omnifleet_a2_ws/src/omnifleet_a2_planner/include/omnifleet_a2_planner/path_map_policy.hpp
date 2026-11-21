#ifndef OMNIFLEET_A2_PLANNER__PATH_MAP_POLICY_HPP_
#define OMNIFLEET_A2_PLANNER__PATH_MAP_POLICY_HPP_

#include <cstddef>
#include <string>

#include "nav_msgs/msg/occupancy_grid.hpp"
#include "nav_msgs/msg/path.hpp"

namespace omnifleet_a2_planner
{

enum class PathMapResultCode
{
  VALID,
  MAP_UNAVAILABLE,
  EMPTY_PATH,
  FRAME_MISMATCH,
  OUT_OF_BOUNDS,
  UNKNOWN_NOT_ALLOWED,
  LETHAL_CELL,
};

struct PathMapResult
{
  PathMapResultCode code{PathMapResultCode::MAP_UNAVAILABLE};
  std::size_t pose_index{0};
  bool exploration_mode{false};
  std::string detail;

  bool accepted() const {return code == PathMapResultCode::VALID;}
};

PathMapResult checkPathAgainstMap(
  const nav_msgs::msg::Path & path,
  const nav_msgs::msg::OccupancyGrid & map);

}  // namespace omnifleet_a2_planner

#endif  // OMNIFLEET_A2_PLANNER__PATH_MAP_POLICY_HPP_
