#include "omnifleet_planner/publish_native_progress.hpp"
#include "omnifleet_planner/normalize_path.hpp"
#include <chrono>
#include <cmath>
#include <memory>
#include <thread>
#include "behaviortree_cpp_v3/bt_factory.h"
#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"

namespace omnifleet_planner
{
// One parameter endpoint shared by both navigation trees, also available when idle.
class Policy
{
public:
  rclcpp::Node::SharedPtr node;
  Policy(const rclcpp::Node::SharedPtr & seed)
  {
    node = std::make_shared<rclcpp::Node>("omnifleet_navigation_policy",
      rclcpp::NodeOptions().use_global_arguments(false));
    bool recovery = true, replan = true;
    double interval = 3.0;
    seed->get_parameter_or("automatic_recovery", recovery, recovery);
    seed->get_parameter_or("automatic_replanning", replan, replan);
    seed->get_parameter_or("replanning_interval", interval, interval);
    node->declare_parameter("automatic_recovery", recovery);
    node->declare_parameter("automatic_replanning", replan);
    node->declare_parameter("replanning_interval", interval);
    callback_ = node->add_on_set_parameters_callback([](const auto & parameters) {
      rcl_interfaces::msg::SetParametersResult result;
      result.successful = true;
      for (const auto & p : parameters) {
        if (p.get_name() == "replanning_interval") {
          if (p.get_type() != rclcpp::ParameterType::PARAMETER_DOUBLE ||
            !std::isfinite(p.as_double()) || p.as_double() < 0.2 || p.as_double() > 60.0)
          { result.successful = false; result.reason = "重新规划间隔必须在0.2到60秒之间"; }
        } else if (p.get_name() == "automatic_recovery" || p.get_name() == "automatic_replanning") {
          if (p.get_type() != rclcpp::ParameterType::PARAMETER_BOOL)
          { result.successful = false; result.reason = "开关必须是布尔值"; }
        }
      }
      return result;
    });
    executor_.add_node(node);
    thread_ = std::thread([this]() { executor_.spin(); });
  }
  ~Policy() {executor_.cancel(); if (thread_.joinable()) {thread_.join();}}
private:
  rclcpp::executors::SingleThreadedExecutor executor_;
  std::thread thread_;
  rclcpp::node_interfaces::OnSetParametersCallbackHandle::SharedPtr callback_;
};

std::shared_ptr<Policy> policy(const BT::NodeConfiguration & config)
{
  static auto value = std::make_shared<Policy>(
    config.blackboard->get<rclcpp::Node::SharedPtr>("node"));
  return value;
}

class RecoveryAllowed : public BT::DecoratorNode
{
public:
  RecoveryAllowed(const std::string & name, const BT::NodeConfiguration & config)
  : BT::DecoratorNode(name, config), policy_(policy(config)) {}
  static BT::PortsList providedPorts() {return {};}
  BT::NodeStatus tick() override
  {
    if (!policy_->node->get_parameter("automatic_recovery").as_bool()) {
      resetChild();
      RCLCPP_WARN_THROTTLE(policy_->node->get_logger(), *policy_->node->get_clock(), 2000,
        "自动恢复已关闭：导航无法继续，已停止恢复动作。请检查前方障碍后重新发送目标。");
      return BT::NodeStatus::FAILURE;
    }
    return child_node_->executeTick();
  }
private:
  std::shared_ptr<Policy> policy_;
};

class ReplanningControl : public BT::DecoratorNode
{
public:
  ReplanningControl(const std::string & name, const BT::NodeConfiguration & config)
  : BT::DecoratorNode(name, config), policy_(policy(config)) {}
  static BT::PortsList providedPorts() {
    return {BT::InputPort<geometry_msgs::msg::PoseStamped>("goal"),
      BT::InputPort<std::vector<geometry_msgs::msg::PoseStamped>>("goals"),
      BT::InputPort<std::string>("planner_id"),
      BT::BidirectionalPort<nav_msgs::msg::Path>("path")};
  }
  void halt() override {planned_ = false; BT::DecoratorNode::halt();}
  BT::NodeStatus tick() override
  {
    geometry_msgs::msg::PoseStamped goal;
    std::vector<geometry_msgs::msg::PoseStamped> goals;
    std::string planner;
    getInput("goal", goal); getInput("goals", goals); getInput("planner_id", planner);
    if (goal != goal_ || goals != goals_ || planner != planner_) {
      resetChild(); planned_ = false; goal_ = goal; goals_ = goals; planner_ = planner;
    }
    const auto now = std::chrono::steady_clock::now();
    const bool enabled = policy_->node->get_parameter("automatic_replanning").as_bool();
    const double interval = policy_->node->get_parameter("replanning_interval").as_double();
    // Never interrupt an in-flight initial plan; disabling suppresses subsequent requests.
    if (!planned_ || child_node_->status() == BT::NodeStatus::RUNNING ||
      (enabled && std::chrono::duration<double>(now - last_).count() >= interval)) {
      const auto result = child_node_->executeTick();
      if (result == BT::NodeStatus::SUCCESS) {
        nav_msgs::msg::Path path;
        if (getInput("path", path)) {
          const auto normalized = normalizePathJunctions(path);
          setOutput("path", normalized);
          if (normalized.poses.size() != path.poses.size()) {
            RCLCPP_INFO(policy_->node->get_logger(),
              "Path junction normalization: %zu -> %zu poses",
              path.poses.size(), normalized.poses.size());
          }
        }
        planned_ = true; last_ = now;
      }
      return result;
    }
    return BT::NodeStatus::SUCCESS;
  }
private:
  std::shared_ptr<Policy> policy_;
  bool planned_ = false;
  std::chrono::steady_clock::time_point last_;
  geometry_msgs::msg::PoseStamped goal_;
  std::vector<geometry_msgs::msg::PoseStamped> goals_;
  std::string planner_;
};
}

BT_REGISTER_NODES(factory)
{
  factory.registerNodeType<omnifleet_planner::PublishNativeWaypointProgress>("PublishNativeWaypointProgress");
  factory.registerNodeType<omnifleet_planner::RecoveryAllowed>("RecoveryAllowed");
  factory.registerNodeType<omnifleet_planner::ReplanningControl>("ReplanningControl");
}
