#pragma once

#include "nav2_mppi_controller/critic_function.hpp"
#include "std_msgs/msg/string.hpp"
#include "rclcpp/executors/single_threaded_executor.hpp"
#include <chrono>

namespace mppi::critics
{
// A soft speed reference for live following; CostCritic retains collision ownership.
class FollowVelocityCritic : public CriticFunction
{
public:
  void initialize() override;
  void score(CriticData & data) override;
private:
  float weight_{30.f}, reference_{0.f}, angular_reference_{0.f};
  bool active_{false}, formation_{false};
  std::chrono::steady_clock::time_point received_{};
  rclcpp::CallbackGroup::SharedPtr group_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr context_;
  rclcpp::executors::SingleThreadedExecutor executor_;
};
}
