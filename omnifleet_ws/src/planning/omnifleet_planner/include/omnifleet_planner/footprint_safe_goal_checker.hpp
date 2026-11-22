#ifndef OMNIFLEET_PLANNER__FOOTPRINT_SAFE_GOAL_CHECKER_HPP_
#define OMNIFLEET_PLANNER__FOOTPRINT_SAFE_GOAL_CHECKER_HPP_

#include <memory>
#include <string>
#include <mutex>
#include "std_msgs/msg/string.hpp"

#include "nav2_controller/plugins/simple_goal_checker.hpp"
#include "nav2_costmap_2d/costmap_2d_ros.hpp"
#include "nav2_costmap_2d/footprint_collision_checker.hpp"
#include "rclcpp/rclcpp.hpp"

namespace omnifleet_planner
{

class FootprintSafeGoalChecker : public nav2_controller::SimpleGoalChecker
{
public:
  bool requiresOrderedWaypoints() const {return require_ordered_waypoints_;}
  void initialize(
    const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent,
    const std::string & plugin_name,
    const std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros) override;

  void reset() override;

  bool isGoalReached(
    const geometry_msgs::msg::Pose & query_pose,
    const geometry_msgs::msg::Pose & goal_pose,
    const geometry_msgs::msg::Twist & velocity) override;

private:
  std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros_;
  rclcpp::Clock::SharedPtr clock_;
  rclcpp::Logger logger_{rclcpp::get_logger("FootprintSafeGoalChecker")};
  rclcpp::Time safe_since_{0, 0, RCL_ROS_TIME};
  double safe_hold_time_{0.35};
  bool safe_timer_started_{false};
  bool require_ordered_waypoints_{false};
  std::mutex route_mutex_;
  int64_t route_reset_ns_{0}, route_stamp_ns_{0};
  bool route_complete_{false};
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr route_sub_;
};

}  // namespace omnifleet_planner

#endif  // OMNIFLEET_PLANNER__FOOTPRINT_SAFE_GOAL_CHECKER_HPP_
