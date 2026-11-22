#include "omnifleet_dwb_hot/hot_dwb.hpp"
#include <cmath>
#include <iomanip>
#include <sstream>
#include "dwb_core/illegal_trajectory_tracker.hpp"
#include "pluginlib/class_list_macros.hpp"
namespace omnifleet_dwb_hot {
void HotDWBLocalPlanner::updateGoalRotationWindow(
  const geometry_msgs::msg::PoseStamped & pose, nav2_core::GoalChecker * goal_checker) {
  defer_goal_rotation_ = false;
  if (!goal_checker || global_plan_.poses.empty() ||
    global_plan_.header.frame_id != pose.header.frame_id) {return;}
  geometry_msgs::msg::Pose tolerance;
  geometry_msgs::msg::Twist velocity_tolerance;
  if (!goal_checker->getTolerances(tolerance, velocity_tolerance) ||
    !std::isfinite(tolerance.position.x) || tolerance.position.x < 0.0) {return;}
  const auto & goal = global_plan_.poses.back();
  defer_goal_rotation_ = std::hypot(goal.x - pose.pose.position.x,
    goal.y - pose.pose.position.y) > tolerance.position.x;
}
geometry_msgs::msg::TwistStamped HotDWBLocalPlanner::computeVelocityCommands(
  const geometry_msgs::msg::PoseStamped & pose, const geometry_msgs::msg::Twist & velocity,
  nav2_core::GoalChecker * goal_checker) {
  updateGoalRotationWindow(pose, goal_checker);
  return dwb_core::DWBLocalPlanner::computeVelocityCommands(pose, velocity, goal_checker);
}
void HotDWBLocalPlanner::syncCriticScales() {
  auto node = node_.lock();
  if (!node) {throw std::runtime_error("DWB parameter node expired");}
  // Set cached critic values only on the controller thread, before scoring.
  for (const auto & critic : critics_) {
    const auto key = dwb_plugin_name_ + "." + critic->getName() + ".scale";
    const double value = node->get_parameter(key).as_double();
    if (!std::isfinite(value) || value < 0.0) {
      throw std::runtime_error("Invalid DWB critic scale: " + key);
    }
    // Do not enter rotate-only scoring before the selected goal checker accepts XY.
    // Keep the saved critic weights and tolerances unchanged.
    critic->setScale(critic->getName() == "RotateToGoal" && defer_goal_rotation_ ? 0.0 : value);
    if (critic->getName() == "RotateToGoal") {
      std::vector<double> settings;
      for (const auto & leaf : {"xy_goal_tolerance", "trans_stopped_velocity", "RotateToGoal.slowing_factor", "RotateToGoal.lookahead_time"}) {
        settings.push_back(node->get_parameter(dwb_plugin_name_ + "." + leaf).as_double());
      }
      if (rotation_settings_.empty() || settings != rotation_settings_) {
        critic->onInit(); // Reload cached fields on the controller thread, only after an edit.
      }
      rotation_settings_ = settings;
    }
  }
}
nav_2d_msgs::msg::Twist2DStamped HotDWBLocalPlanner::computeVelocityCommands(
  const nav_2d_msgs::msg::Pose2DStamped & pose,
  const nav_2d_msgs::msg::Twist2D & velocity,
  std::shared_ptr<dwb_msgs::msg::LocalPlanEvaluation> & results) {
  syncCriticScales();
  try {
    return dwb_core::DWBLocalPlanner::computeVelocityCommands(pose, velocity, results);
  } catch (const dwb_core::NoLegalTrajectoriesException & error) {
    auto node = node_.lock();
    if (node) {
      std::ostringstream details;
      details << "DWB 轨迹拒绝详情：" << error.what();
      for (const auto & failure : error.tracker_.getPercentages()) {
        details << " [" << failure.first.first << ": " << failure.first.second
                << ", " << std::fixed << std::setprecision(1)
                << failure.second * 100.0 << "%]";
      }
      RCLCPP_WARN_THROTTLE(node->get_logger(), *node->get_clock(), 2000,
        "%s", details.str().c_str());
    }
    throw;
  }
}
}
PLUGINLIB_EXPORT_CLASS(omnifleet_dwb_hot::HotDWBLocalPlanner, nav2_core::Controller)
