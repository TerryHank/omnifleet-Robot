#include "omnifleet_planner/cost_aware_smac.hpp"
#include "omnifleet_planner/cost_aware_smoothing.hpp"
#include "omnifleet_planner/exact_goal_endpoint.hpp"
#include "pluginlib/class_list_macros.hpp"
#include "nav2_util/geometry_utils.hpp"

namespace omnifleet_planner {
void CostAwareSmac2D::configure(const rclcpp_lifecycle::LifecycleNode::WeakPtr& parent,std::string name,
    std::shared_ptr<tf2_ros::Buffer> tf,std::shared_ptr<nav2_costmap_2d::Costmap2DROS> map) {
  nav2_smac_planner::SmacPlanner2D::configure(parent,name,tf,map);
  checked_smoother_=std::move(_smoother);
  nav2_smac_planner::SmootherParams bypass;
  bypass.get(parent.lock(),name);bypass.max_its_=0;bypass.holonomic_=true;
  _smoother=std::make_unique<nav2_smac_planner::Smoother>(bypass);
  _smoother->initialize(1e-50);
}
void CostAwareSmac2D::cleanup() {
  checked_smoother_.reset();nav2_smac_planner::SmacPlanner2D::cleanup();
}
nav_msgs::msg::Path CostAwareSmac2D::createPlan(const geometry_msgs::msg::PoseStamped& start,
    const geometry_msgs::msg::PoseStamped& goal) {
  std::lock_guard<std::mutex> serial(plan_mutex_);
  const auto began=std::chrono::steady_clock::now();
  auto raw=nav2_smac_planner::SmacPlanner2D::createPlan(start,goal);
  auto finish=[&](nav_msgs::msg::Path plan) {
    std::unique_lock<nav2_costmap_2d::Costmap2D::mutex_t> lock(*_costmap->getMutex());
    appendExactGoal(plan,goal,*_costmap,_use_final_approach_orientation);return plan;
  };
  if(raw.poses.size()<3)return finish(raw);
  std::lock_guard<std::mutex> parameters(_mutex);
  const double remaining=_max_planning_time-
    std::chrono::duration<double>(std::chrono::steady_clock::now()-began).count();
  if(remaining<=0)return finish(raw);
  std::unique_lock<nav2_costmap_2d::Costmap2D::mutex_t> grid_lock(*_costmap->getMutex());
  auto candidate=raw;checked_smoother_->smooth(candidate,_costmap,remaining);
  if(!smoothingDoesNotRaiseCost(raw,candidate,*_costmap,_search_info.cost_penalty,_allow_unknown)) {
    RCLCPP_DEBUG(_logger,"Rejected smoothing that raised maximum or integrated traversal cost");
    return finish(raw);
  }
  if(_use_final_approach_orientation) {
    const auto& a=candidate.poses[candidate.poses.size()-2].pose.position;
    const auto& b=candidate.poses.back().pose.position;
    candidate.poses.back().pose.orientation=nav2_util::geometry_utils::orientationAroundZAxis(std::atan2(b.y-a.y,b.x-a.x));
  } else candidate.poses.back().pose.orientation=goal.pose.orientation;
  return finish(candidate);
}
}
PLUGINLIB_EXPORT_CLASS(omnifleet_planner::CostAwareSmac2D,nav2_core::GlobalPlanner)
