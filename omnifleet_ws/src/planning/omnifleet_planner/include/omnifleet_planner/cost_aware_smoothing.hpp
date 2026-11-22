#pragma once
#include <algorithm>
#include <cmath>
#include "nav2_costmap_2d/costmap_2d.hpp"
#include "nav_msgs/msg/path.hpp"

namespace omnifleet_planner {
struct PathCost {
  double weighted_length{0};
  unsigned maximum{0};
  bool valid{true};
};
inline PathCost pathCost(const nav_msgs::msg::Path& path,
    const nav2_costmap_2d::Costmap2D& grid,double weight,bool allow_unknown) {
  PathCost result;
  for(size_t i=1;i<path.poses.size();++i) {
    const auto& a=path.poses[i-1].pose.position;const auto& b=path.poses[i].pose.position;
    const double length=std::hypot(b.x-a.x,b.y-a.y);
    const int samples=std::max(1,int(std::ceil(length/(grid.getResolution()*.25))));
    for(int j=0;j<samples;++j) {
      const double t=(j+.5)/samples;unsigned x,y;
      if(!grid.worldToMap(a.x+(b.x-a.x)*t,a.y+(b.y-a.y)*t,x,y)) {result.valid=false;return result;}
      const unsigned cost=grid.getCost(x,y);
      if(cost==nav2_costmap_2d::LETHAL_OBSTACLE ||
          (cost==nav2_costmap_2d::NO_INFORMATION&&!allow_unknown)) {result.valid=false;return result;}
      result.maximum=std::max(result.maximum,cost);
      result.weighted_length+=length/samples*(1.+weight*cost/252.);
    }
  }
  return result;
}
inline bool smoothingDoesNotRaiseCost(const nav_msgs::msg::Path& raw,const nav_msgs::msg::Path& candidate,
    const nav2_costmap_2d::Costmap2D& grid,double weight,bool allow_unknown) {
  if(raw.poses.size()!=candidate.poses.size()||candidate.poses.empty())return false;
  const auto a=pathCost(raw,grid,weight,allow_unknown),b=pathCost(candidate,grid,weight,allow_unknown);
  return a.valid&&b.valid&&b.maximum<=a.maximum&&b.weighted_length<=a.weighted_length+1e-6;
}
}
