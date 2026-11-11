#pragma once
#include "dwb_core/dwb_local_planner.hpp"
namespace omnifleet_dwb_hot {
class HotDWBLocalPlanner : public dwb_core::DWBLocalPlanner {
public:
  using dwb_core::DWBLocalPlanner::computeVelocityCommands;
  nav_2d_msgs::msg::Twist2DStamped computeVelocityCommands(
    const nav_2d_msgs::msg::Pose2DStamped & pose,
    const nav_2d_msgs::msg::Twist2D & velocity,
    std::shared_ptr<dwb_msgs::msg::LocalPlanEvaluation> & results) override;
protected:
  void syncCriticScales();
  std::vector<double> rotation_settings_;
};
}

