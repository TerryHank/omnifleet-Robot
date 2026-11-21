#pragma once
#include <cmath>
#include "nav_msgs/msg/path.hpp"
#include "nav2_costmap_2d/costmap_2d.hpp"
#include "nav2_costmap_2d/cost_values.hpp"
#include "nav2_util/geometry_utils.hpp"

namespace omnifleet_planner {
inline bool appendExactGoal(nav_msgs::msg::Path & path,
  const geometry_msgs::msg::PoseStamped & goal,nav2_costmap_2d::Costmap2D & map,bool approach_orientation) {
  if(path.poses.empty()||goal.header.frame_id!=path.header.frame_id)return false;
  const auto & end=path.poses.back().pose.position;
  unsigned int ex,ey,gx,gy;
  if(!map.worldToMap(end.x,end.y,ex,ey)||!map.worldToMap(goal.pose.position.x,goal.pose.position.y,gx,gy)||
    ex!=gx||ey!=gy||map.getCost(gx,gy)>=nav2_costmap_2d::LETHAL_OBSTACLE)return false;
  auto exact=goal;exact.header=path.header;
  if(approach_orientation) {
    if(std::hypot(exact.pose.position.x-end.x,exact.pose.position.y-end.y)>1e-6)
      exact.pose.orientation=nav2_util::geometry_utils::orientationAroundZAxis(std::atan2(exact.pose.position.y-end.y,exact.pose.position.x-end.x));
    else exact.pose.orientation=path.poses.back().pose.orientation;
  }
  if(std::hypot(exact.pose.position.x-end.x,exact.pose.position.y-end.y)>1e-6)path.poses.push_back(exact);
  else path.poses.back()=exact;
  return true;
}
}
