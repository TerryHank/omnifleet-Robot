#include <memory>
#include <mutex>
#include <string>

#include "behaviortree_cpp_v3/bt_factory.h"
#include "behaviortree_cpp_v3/condition_node.h"
#include "nav_msgs/msg/occupancy_grid.hpp"
#include "nav_msgs/msg/path.hpp"
#include "rclcpp/rclcpp.hpp"

#include "omnifleet_a2_planner/path_map_policy.hpp"

namespace omnifleet_a2_planner
{

class IsPathWithinMapCondition : public BT::ConditionNode
{
public:
  IsPathWithinMapCondition(
    const std::string & condition_name,
    const BT::NodeConfiguration & configuration)
  : BT::ConditionNode(condition_name, configuration)
  {
    node_ = config().blackboard->get<rclcpp::Node::SharedPtr>("node");
    std::string map_topic = "/global_costmap/costmap";
    getInput("map_topic", map_topic);
    map_subscription_ = node_->create_subscription<nav_msgs::msg::OccupancyGrid>(
      map_topic,
      rclcpp::QoS(1).reliable().transient_local(),
      [this](nav_msgs::msg::OccupancyGrid::SharedPtr message) {
        std::lock_guard<std::mutex> lock(map_mutex_);
        map_ = std::move(message);
      });
  }

  static BT::PortsList providedPorts()
  {
    return {
      BT::InputPort<nav_msgs::msg::Path>("path", "Path to check"),
      BT::InputPort<std::string>(
        "map_topic", "/global_costmap/costmap", "Occupancy grid used as the map boundary")
    };
  }

  BT::NodeStatus tick() override
  {
    nav_msgs::msg::Path path;
    if (!getInput("path", path)) {
      RCLCPP_WARN(node_->get_logger(), "路径边界检查拒绝：行为树没有提供路径");
      return BT::NodeStatus::FAILURE;
    }

    nav_msgs::msg::OccupancyGrid::SharedPtr map;
    {
      std::lock_guard<std::mutex> lock(map_mutex_);
      map = map_;
    }
    if (!map) {
      RCLCPP_WARN_THROTTLE(
        node_->get_logger(), *node_->get_clock(), 2000,
        "路径边界检查拒绝：尚未收到全局代价图");
      return BT::NodeStatus::FAILURE;
    }

    const PathMapResult result = checkPathAgainstMap(path, *map);
    if (!result.accepted()) {
      RCLCPP_WARN(
        node_->get_logger(),
        "路径边界检查拒绝：%s；位置序号=%zu",
        result.detail.c_str(), result.pose_index);
      return BT::NodeStatus::FAILURE;
    }
    return BT::NodeStatus::SUCCESS;
  }

private:
  rclcpp::Node::SharedPtr node_;
  rclcpp::Subscription<nav_msgs::msg::OccupancyGrid>::SharedPtr map_subscription_;
  nav_msgs::msg::OccupancyGrid::SharedPtr map_;
  std::mutex map_mutex_;
};

}  // namespace omnifleet_a2_planner

BT_REGISTER_NODES(factory)
{
  factory.registerNodeType<omnifleet_a2_planner::IsPathWithinMapCondition>("IsPathWithinMap");
}
