#include "nav2_core/progress_checker.hpp"
#include "nav2_util/node_utils.hpp"
#include "pluginlib/class_list_macros.hpp"

namespace omnifleet_planner
{
class NoProgressChecker : public nav2_core::ProgressChecker
{
 public:
  void initialize(
    const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent,
    const std::string & plugin_name) override
  {
    const auto node = parent.lock();
    nav2_util::declare_parameter_if_not_declared(
      node, plugin_name + ".required_movement_radius", rclcpp::ParameterValue(0.1));
    nav2_util::declare_parameter_if_not_declared(
      node, plugin_name + ".required_movement_angle", rclcpp::ParameterValue(0.1));
    nav2_util::declare_parameter_if_not_declared(
      node, plugin_name + ".movement_time_allowance", rclcpp::ParameterValue(10.0));
  }

  bool check(geometry_msgs::msg::PoseStamped &) override {return true;}

  void reset() override {}
};
}

PLUGINLIB_EXPORT_CLASS(omnifleet_planner::NoProgressChecker, nav2_core::ProgressChecker)
