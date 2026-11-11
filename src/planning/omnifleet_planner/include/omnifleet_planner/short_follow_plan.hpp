#pragma once
#include <cmath>
#include <memory>
#include "ompl/base/ScopedState.h"
#include "ompl/base/spaces/ReedsSheppStateSpace.h"
#include "ompl/base/spaces/DubinsStateSpace.h"
#include "omnifleet_planner/goal_footprint_cost.hpp"
#include "nav_msgs/msg/path.hpp"
#include "nav2_util/geometry_utils.hpp"
#include "tf2/utils.h"
namespace omnifleet_planner {
inline nav_msgs::msg::Path shortKinematicPlan(
  nav2_costmap_2d::Costmap2D * map,const nav2_costmap_2d::Footprint & footprint,
  const geometry_msgs::msg::PoseStamped & start,const geometry_msgs::msg::PoseStamped & goal,
  double radius,double extent,bool reversing,bool unknown)
{
  nav_msgs::msg::Path path;path.header=goal.header;
  if(start.header.frame_id!=goal.header.frame_id || extent<=0. || radius<=0. ||
    std::hypot(goal.pose.position.x-start.pose.position.x,goal.pose.position.y-start.pose.position.y)>extent)return path;
  namespace ob=ompl::base;
  std::shared_ptr<ob::SE2StateSpace> space;
  if(reversing)space=std::make_shared<ob::ReedsSheppStateSpace>(radius);
  else space=std::make_shared<ob::DubinsStateSpace>(radius);
  ob::ScopedState<ob::SE2StateSpace> a(space),b(space),p(space);
  a->setXY(start.pose.position.x,start.pose.position.y);a->setYaw(tf2::getYaw(start.pose.orientation));
  b->setXY(goal.pose.position.x,goal.pose.position.y);b->setYaw(tf2::getYaw(goal.pose.orientation));
  const double length=space->distance(a.get(),b.get());
  if(!std::isfinite(length)||length>extent)return path;
  const int steps=std::max(1,static_cast<int>(std::ceil(length/(map->getResolution()*.25))));
  for(int i=0;i<=steps;++i) {
    space->interpolate(a.get(),b.get(),static_cast<double>(i)/steps,p.get());
    const double cost=goalFootprintCost(map,footprint,p->getX(),p->getY(),p->getYaw(),unknown);
    if(cost<0.||cost>=nav2_costmap_2d::LETHAL_OBSTACLE){path.poses.clear();return path;}
    auto value=goal;value.pose.position.x=p->getX();value.pose.position.y=p->getY();
    value.pose.orientation=nav2_util::geometry_utils::orientationAroundZAxis(p->getYaw());path.poses.push_back(value);
  }
  path.poses.front()=start;path.poses.back()=goal;return path;
}
}
