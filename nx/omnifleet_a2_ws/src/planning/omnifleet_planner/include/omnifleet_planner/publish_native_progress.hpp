#pragma once
#include "behaviortree_cpp_v3/bt_factory.h"
#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "nav_msgs/msg/path.hpp"
#include "std_msgs/msg/string.hpp"
#include <nlohmann/json.hpp>

namespace omnifleet_planner {
class PublishNativeWaypointProgress : public BT::SyncActionNode {
public:
  PublishNativeWaypointProgress(const std::string & name,const BT::NodeConfiguration & config)
  : BT::SyncActionNode(name,config),node_(config.blackboard->get<rclcpp::Node::SharedPtr>("node")) {
    publisher_=node_->create_publisher<std_msgs::msg::String>("omnifleet_t2/waypoints/native_progress",1);
    run_=std::to_string(node_->get_clock()->now().nanoseconds());
  }
  static BT::PortsList providedPorts() {
    return {BT::InputPort<std::vector<geometry_msgs::msg::PoseStamped>>("goals"),BT::InputPort<nav_msgs::msg::Path>("path")};
  }
  BT::NodeStatus tick() override {
    std::vector<geometry_msgs::msg::PoseStamped> goals;nav_msgs::msg::Path path;
    if (!getInput("goals",goals) || !getInput("path",path) || goals.empty() || path.poses.empty()) {return BT::NodeStatus::FAILURE;}
    const auto & end=path.poses.back().pose.position;
    nlohmann::json value={{"run_id",run_},{"stamp_ns",node_->get_clock()->now().nanoseconds()},
      {"remaining",goals.size()},{"goal_x",end.x},{"goal_y",end.y}};
    std_msgs::msg::String message;message.data=value.dump();publisher_->publish(message);
    return BT::NodeStatus::SUCCESS;
  }
private:
  rclcpp::Node::SharedPtr node_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  std::string run_;
};
}  // namespace omnifleet_planner
