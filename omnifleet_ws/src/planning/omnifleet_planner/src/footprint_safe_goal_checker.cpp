#include "omnifleet_planner/footprint_safe_goal_checker.hpp"
#include "omnifleet_planner/goal_footprint_cost.hpp"
#include "nav2_core/exceptions.hpp"

#include <mutex>
#include <stdexcept>
#include <nlohmann/json.hpp>

#include "nav2_costmap_2d/cost_values.hpp"
#include "nav2_util/node_utils.hpp"
#include "pluginlib/class_list_macros.hpp"
#include "tf2/utils.h"

namespace omnifleet_planner
{

void FootprintSafeGoalChecker::initialize(
  const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent,
  const std::string & plugin_name,
  const std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros)
{
  nav2_controller::SimpleGoalChecker::initialize(parent, plugin_name, costmap_ros);
  auto node = parent.lock();
  if (!node) {
    throw std::runtime_error("FootprintSafeGoalChecker parent node expired");
  }
  costmap_ros_ = costmap_ros;
  clock_ = node->get_clock();
  logger_ = node->get_logger();
  nav2_util::declare_parameter_if_not_declared(
    node, plugin_name + ".safe_hold_time", rclcpp::ParameterValue(0.35));
  node->get_parameter(plugin_name + ".safe_hold_time", safe_hold_time_);
  if (safe_hold_time_ < 0.0) {
    throw std::invalid_argument(plugin_name + ".safe_hold_time must be non-negative");
  }
  nav2_util::declare_parameter_if_not_declared(
    node, plugin_name + ".require_ordered_waypoints", rclcpp::ParameterValue(false));
  node->get_parameter(plugin_name + ".require_ordered_waypoints", require_ordered_waypoints_);
  if (plugin_name_ == "fleet_goal_checker") {
    route_sub_ = node->create_subscription<std_msgs::msg::String>(
      "navigation/fleet/follow_context", rclcpp::QoS(10),
      [this](std_msgs::msg::String::ConstSharedPtr message) {
        bool stopped = false;
        try {
          const auto value = nlohmann::json::parse(message->data);
          const double speed = std::hypot(value.at("speed").get<double>(),value.value("angular_speed",0.));
          stopped = std::isfinite(speed) && std::abs(speed) <= 0.02;
        } catch (const nlohmann::json::exception &) {}
        std::lock_guard<std::mutex> lock(route_mutex_);
        route_complete_ = stopped;
      });
  } else if (require_ordered_waypoints_) {
    route_sub_ = node->create_subscription<std_msgs::msg::String>(
      "omnifleet_t2/waypoints/execution_state", rclcpp::QoS(1),
      [this](std_msgs::msg::String::ConstSharedPtr message) {
        try {
          const auto data = nlohmann::json::parse(message->data);
          const auto stamp = data.at("stamp_ns").get<int64_t>();
          const bool complete = !data.at("run_id").get<std::string>().empty() &&
            data.at("remaining").get<size_t>() == 1 && data.at("state") == "tracking";
          std::lock_guard<std::mutex> lock(route_mutex_);
          if (stamp > route_reset_ns_ && stamp > route_stamp_ns_) {
            route_stamp_ns_ = stamp; route_complete_ = complete;
          }
        } catch (const nlohmann::json::exception &) {
          // Incomplete/failed messages cannot authorize final completion.
          std::lock_guard<std::mutex> lock(route_mutex_);
          route_complete_ = false;
        }
      });
  }
}

void FootprintSafeGoalChecker::reset()
{
  nav2_controller::SimpleGoalChecker::reset();
  safe_timer_started_ = false;
  std::lock_guard<std::mutex> lock(route_mutex_);
  route_reset_ns_ = clock_->now().nanoseconds();
  route_stamp_ns_ = 0; route_complete_ = false;
}

bool FootprintSafeGoalChecker::isGoalReached(
  const geometry_msgs::msg::Pose & query_pose,
  const geometry_msgs::msg::Pose & goal_pose,
  const geometry_msgs::msg::Twist & velocity)
{
  if (plugin_name_ == "fleet_goal_checker") {
    std::lock_guard<std::mutex> lock(route_mutex_);
    // A short moving reference is not a terminal goal, including when the
    // follower momentarily stops inside its position tolerance.
    if (!route_complete_ || std::hypot(velocity.linear.x, velocity.linear.y) > 0.02 || std::abs(velocity.angular.z) > 0.05) {
      safe_timer_started_ = false;
      return false;
    }
  }
  if (require_ordered_waypoints_) {
    std::lock_guard<std::mutex> lock(route_mutex_);
    const auto age = clock_->now().nanoseconds() - route_stamp_ns_;
    if (!route_complete_ || route_stamp_ns_ <= route_reset_ns_ || age < 0 || age > 500000000) {
      safe_timer_started_ = false;
      return false;
    }
  }
  if (!nav2_controller::SimpleGoalChecker::isGoalReached(query_pose, goal_pose, velocity)) {
    safe_timer_started_ = false;
    return false;
  }

  auto * costmap = costmap_ros_->getCostmap();
  double footprint_cost;
  {
    std::lock_guard<nav2_costmap_2d::Costmap2D::mutex_t> lock(*costmap->getMutex());
    footprint_cost = goalFootprintCost(costmap, costmap_ros_->getRobotFootprint(),
      query_pose.position.x,
      query_pose.position.y,
      tf2::getYaw(query_pose.orientation));
  }

  const bool footprint_safe =
    footprint_cost >= 0.0 &&
    footprint_cost < nav2_costmap_2d::LETHAL_OBSTACLE;
  if (!footprint_safe) {
    safe_timer_started_ = false;
    nav2_controller::SimpleGoalChecker::reset();
    // Returning false would keep the controller producing near-goal micro motions.
    throw nav2_core::PlannerException(
      "到点安全检查失败：车身覆盖真实障碍、未知区域或地图外；已停止跟踪，请检查目标位置");
  }

  const auto now = clock_->now();
  if (!safe_timer_started_) {
    safe_since_ = now;
    safe_timer_started_ = true;
  }
  return (now - safe_since_).seconds() >= safe_hold_time_;
}

}  // namespace omnifleet_planner

PLUGINLIB_EXPORT_CLASS(omnifleet_planner::FootprintSafeGoalChecker, nav2_core::GoalChecker)
