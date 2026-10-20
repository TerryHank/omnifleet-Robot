#pragma once
#include "nav2_smac_planner/smac_planner_2d.hpp"

namespace omnifleet_planner {
class CostAwareSmac2D : public nav2_smac_planner::SmacPlanner2D {
 public:
  void configure(const rclcpp_lifecycle::LifecycleNode::WeakPtr& parent,std::string name,
    std::shared_ptr<tf2_ros::Buffer> tf,std::shared_ptr<nav2_costmap_2d::Costmap2DROS> map) override;
  void cleanup() override;
  nav_msgs::msg::Path createPlan(const geometry_msgs::msg::PoseStamped& start,
    const geometry_msgs::msg::PoseStamped& goal) override;
 private:
  std::unique_ptr<nav2_smac_planner::Smoother> checked_smoother_;
  std::mutex plan_mutex_;
};
}
