#include "omnifleet_a2_planner/path_map_policy.hpp"

#include <cmath>
#include <cstdint>
#include <sstream>

namespace omnifleet_a2_planner
{
namespace
{

struct Cell
{
  std::size_t x;
  std::size_t y;
};

bool worldToCell(
  const geometry_msgs::msg::Point & point,
  const nav_msgs::msg::OccupancyGrid & map,
  Cell & cell)
{
  const auto & origin = map.info.origin;
  const auto & q = origin.orientation;
  const double yaw = std::atan2(
    2.0 * (q.w * q.z + q.x * q.y),
    1.0 - 2.0 * (q.y * q.y + q.z * q.z));
  const double dx = point.x - origin.position.x;
  const double dy = point.y - origin.position.y;
  const double local_x = std::cos(yaw) * dx + std::sin(yaw) * dy;
  const double local_y = -std::sin(yaw) * dx + std::cos(yaw) * dy;
  const long mx = static_cast<long>(std::floor(local_x / map.info.resolution));
  const long my = static_cast<long>(std::floor(local_y / map.info.resolution));
  if (mx < 0 || my < 0 ||
    mx >= static_cast<long>(map.info.width) ||
    my >= static_cast<long>(map.info.height))
  {
    return false;
  }
  cell.x = static_cast<std::size_t>(mx);
  cell.y = static_cast<std::size_t>(my);
  return true;
}

std::size_t cellIndex(const Cell & cell, const nav_msgs::msg::OccupancyGrid & map)
{
  return cell.y * static_cast<std::size_t>(map.info.width) + cell.x;
}

}  // namespace

PathMapResult checkPathAgainstMap(
  const nav_msgs::msg::Path & path,
  const nav_msgs::msg::OccupancyGrid & map)
{
  PathMapResult result;
  const std::size_t expected_cells =
    static_cast<std::size_t>(map.info.width) * static_cast<std::size_t>(map.info.height);
  if (map.info.width == 0 || map.info.height == 0 ||
    !std::isfinite(map.info.resolution) || map.info.resolution <= 0.0 ||
    map.data.size() != expected_cells)
  {
    result.detail = "map is unavailable or malformed";
    return result;
  }
  if (path.poses.empty()) {
    result.code = PathMapResultCode::EMPTY_PATH;
    result.detail = "path is empty";
    return result;
  }
  if (path.header.frame_id.empty() || map.header.frame_id.empty() ||
    path.header.frame_id != map.header.frame_id)
  {
    result.code = PathMapResultCode::FRAME_MISMATCH;
    result.detail = "path and map frames do not match";
    return result;
  }

  Cell goal_cell{};
  if (!worldToCell(path.poses.back().pose.position, map, goal_cell)) {
    result.code = PathMapResultCode::OUT_OF_BOUNDS;
    result.pose_index = path.poses.size() - 1;
    result.detail = "goal is outside map bounds";
    return result;
  }
  result.exploration_mode = map.data[cellIndex(goal_cell, map)] < 0;

  for (std::size_t index = 0; index < path.poses.size(); ++index) {
    const auto & pose = path.poses[index];
    if (!pose.header.frame_id.empty() && pose.header.frame_id != map.header.frame_id) {
      result.code = PathMapResultCode::FRAME_MISMATCH;
      result.pose_index = index;
      result.detail = "path pose frame does not match map frame";
      return result;
    }
    Cell cell{};
    if (!worldToCell(pose.pose.position, map, cell)) {
      result.code = PathMapResultCode::OUT_OF_BOUNDS;
      result.pose_index = index;
      std::ostringstream stream;
      stream << "path pose " << index << " is outside map bounds";
      result.detail = stream.str();
      return result;
    }
    const std::int8_t cell_value = map.data[cellIndex(cell, map)];
    if (!result.exploration_mode && cell_value < 0) {
      result.code = PathMapResultCode::UNKNOWN_NOT_ALLOWED;
      result.pose_index = index;
      std::ostringstream stream;
      stream << "known-space goal path enters unknown cell at pose " << index;
      result.detail = stream.str();
      return result;
    }
    if (cell_value >= 99) {
      result.code = PathMapResultCode::LETHAL_CELL;
      result.pose_index = index;
      std::ostringstream stream;
      stream << "path enters a lethal obstacle cell at pose " << index;
      result.detail = stream.str();
      return result;
    }
  }

  result.code = PathMapResultCode::VALID;
  result.detail = result.exploration_mode ?
    "path is inside map bounds; unknown exploration is allowed" :
    "path stays inside known map cells";
  return result;
}

}  // namespace omnifleet_a2_planner
