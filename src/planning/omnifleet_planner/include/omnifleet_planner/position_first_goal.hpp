#pragma once
#include <cmath>
#include "angles/angles.h"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "nav2_util/geometry_utils.hpp"
#include "nav_msgs/msg/path.hpp"
#include "tf2/utils.h"

namespace omnifleet_planner
{
inline geometry_msgs::msg::PoseStamped positionFirstApproach(
  const geometry_msgs::msg::PoseStamped & start,
  const geometry_msgs::msg::PoseStamped & requested)
{
  auto approach = requested;
  const double dx = requested.pose.position.x - start.pose.position.x;
  const double dy = requested.pose.position.y - start.pose.position.y;
  if (std::hypot(dx, dy) <= 1e-6) {return approach;}
  const double bearing = std::atan2(dy, dx);
  const double start_yaw = tf2::getYaw(start.pose.orientation);
  const double forward = std::abs(angles::shortest_angular_distance(start_yaw, bearing));
  const double reverse_yaw = angles::normalize_angle(bearing + M_PI);
  const double reverse = std::abs(angles::shortest_angular_distance(start_yaw, reverse_yaw));
  approach.pose.orientation = nav2_util::geometry_utils::orientationAroundZAxis(
    forward <= reverse ? bearing : reverse_yaw);
  return approach;
}

class PositionFirstState
{
public:
  geometry_msgs::msg::PoseStamped approach(
    const geometry_msgs::msg::PoseStamped & start,
    const geometry_msgs::msg::PoseStamped & requested)
  {
    if (!set_ || changed(requested)) {
      requested_ = requested;
      approach_yaw_ = tf2::getYaw(positionFirstApproach(start, requested).pose.orientation);
      set_ = true;
    }
    auto value = requested;
    value.pose.orientation = nav2_util::geometry_utils::orientationAroundZAxis(approach_yaw_);
    return value;
  }
private:
  bool changed(const geometry_msgs::msg::PoseStamped & value) const
  {
    return value.header.frame_id != requested_.header.frame_id ||
      std::hypot(value.pose.position.x - requested_.pose.position.x,
        value.pose.position.y - requested_.pose.position.y) > 1e-6 ||
      std::abs(angles::shortest_angular_distance(
        tf2::getYaw(value.pose.orientation), tf2::getYaw(requested_.pose.orientation))) > 1e-6;
  }
  bool set_{false};
  double approach_yaw_{0.0};
  geometry_msgs::msg::PoseStamped requested_;
};

inline bool appendRequestedTerminalOrientation(
  nav_msgs::msg::Path & path,
  const geometry_msgs::msg::PoseStamped & requested)
{
  if (path.poses.empty() || path.header.frame_id != requested.header.frame_id) {return false;}
  const auto & end = path.poses.back().pose;
  if (std::hypot(end.position.x - requested.pose.position.x,
      end.position.y - requested.pose.position.y) > 1e-6) {return false;}
  auto final = requested;
  final.header = path.header;
  if (std::abs(angles::shortest_angular_distance(
      tf2::getYaw(end.orientation), tf2::getYaw(final.pose.orientation))) > 1e-6)
  {
    path.poses.push_back(final);
  } else {
    path.poses.back() = final;
  }
  return true;
}

template<typename Safe>
inline bool collapseInitialRotation(
  nav_msgs::msg::Path & path,
  const geometry_msgs::msg::PoseStamped & start,
  double linear_step,
  Safe safe)
{
  if (path.poses.size() < 3 || path.header.frame_id != start.header.frame_id) {return false;}
  const auto origin = path.poses.front().pose.position;
  size_t moving = 1;
  while (moving < path.poses.size() &&
    std::hypot(path.poses[moving].pose.position.x - origin.x,
      path.poses[moving].pose.position.y - origin.y) <= 1e-6)
  {
    ++moving;
  }
  if (moving <= 1 || moving >= path.poses.size()) {return false;}
  const auto & next = path.poses[moving].pose;
  const double sx = start.pose.position.x, sy = start.pose.position.y;
  const double syaw = tf2::getYaw(start.pose.orientation);
  const double dx = next.position.x - sx, dy = next.position.y - sy;
  const double dyaw = angles::shortest_angular_distance(syaw, tf2::getYaw(next.orientation));
  const int steps = std::max(1, std::max(
    static_cast<int>(std::ceil(std::hypot(dx, dy) / std::max(1e-3, linear_step))),
    static_cast<int>(std::ceil(std::abs(dyaw) / 0.05))));
  for (int i = 0; i <= steps; ++i) {
    const double u = static_cast<double>(i) / steps;
    if (!safe(sx + u * dx, sy + u * dy, syaw + u * dyaw)) {return false;}
  }
  auto first = start;
  first.header = path.header;
  path.poses.erase(path.poses.begin(), path.poses.begin() + moving);
  path.poses.insert(path.poses.begin(), first);
  return true;
}
}  // namespace omnifleet_planner
