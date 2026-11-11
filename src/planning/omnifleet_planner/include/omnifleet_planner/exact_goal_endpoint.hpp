#pragma once
#include <cmath>
#include "nav_msgs/msg/path.hpp"
#include "nav2_costmap_2d/costmap_2d.hpp"
#include "nav2_costmap_2d/cost_values.hpp"
#include "nav2_util/geometry_utils.hpp"

namespace omnifleet_planner {
inline bool appendExactGoal(nav_msgs::msg::Path & path,
  const geometry_msgs::msg::PoseStamped & goal,nav2_costmap_2d::Costmap2D & map,bool approach_orientation,bool allow_unknown=false) {
  if(path.poses.empty()||goal.header.frame_id!=path.header.frame_id)return false;
  const auto end=path.poses.back().pose.position;
  unsigned int ex,ey,gx,gy;
  if(!map.worldToMap(end.x,end.y,ex,ey)||!map.worldToMap(goal.pose.position.x,goal.pose.position.y,gx,gy)||
    ex!=gx||ey!=gy||(map.getCost(gx,gy)>=nav2_costmap_2d::LETHAL_OBSTACLE &&
      !(allow_unknown && map.getCost(gx,gy)==nav2_costmap_2d::NO_INFORMATION)))return false;
  // Replacing the last cell centre avoids a tiny return segment/cusp when the
  // exact target lies before it. Retain the original tail if the shortcut is blocked.
  bool replace=path.poses.size()>1;
  const auto from=replace?path.poses[path.poses.size()-2].pose.position:end;
  const int steps=std::max(1,static_cast<int>(std::ceil(std::hypot(goal.pose.position.x-from.x,
    goal.pose.position.y-from.y)/(map.getResolution()*.25))));
  for(int k=0;replace && k<=steps;++k) {
    unsigned int mx,my;const double u=static_cast<double>(k)/steps;
    if(!map.worldToMap(from.x+u*(goal.pose.position.x-from.x),from.y+u*(goal.pose.position.y-from.y),mx,my)||
       (map.getCost(mx,my)>=nav2_costmap_2d::INSCRIBED_INFLATED_OBSTACLE &&
        !(allow_unknown && map.getCost(mx,my)==nav2_costmap_2d::NO_INFORMATION)))replace=false;
  }
  auto exact=goal;exact.header=path.header;
  const auto tangent=replace?from:end;
  if(approach_orientation) {
    if(std::hypot(exact.pose.position.x-tangent.x,exact.pose.position.y-tangent.y)>1e-6)
      exact.pose.orientation=nav2_util::geometry_utils::orientationAroundZAxis(std::atan2(exact.pose.position.y-tangent.y,exact.pose.position.x-tangent.x));
    else exact.pose.orientation=path.poses.back().pose.orientation;
  }
  if(replace)path.poses.back()=exact;
  else if(std::hypot(exact.pose.position.x-end.x,exact.pose.position.y-end.y)>1e-6)path.poses.push_back(exact);
  else path.poses.back()=exact;
  return true;
}
}
