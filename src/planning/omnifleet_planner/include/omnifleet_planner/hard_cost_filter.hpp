#pragma once

#include <atomic>
#include <nav2_costmap_2d/layer.hpp>
#include <rcl_interfaces/msg/set_parameters_result.hpp>

namespace omnifleet_planner
{
// Run as a costmap filter, after inflation, so promoted cells never seed
// inflation again on the next update.
class HardCostFilter : public nav2_costmap_2d::Layer
{
public:
  void onInitialize() override;
  void updateBounds(double, double, double, double *, double *, double *, double *) override;
  void updateCosts(nav2_costmap_2d::Costmap2D &, int, int, int, int) override;
  void reset() override {refresh_all_ = true; current_ = true;}
  bool isClearable() override {return false;}

private:
  rcl_interfaces::msg::SetParametersResult parameters(
    const std::vector<rclcpp::Parameter> & values);
  std::atomic<int> threshold_{200};
  std::atomic<bool> refresh_all_{true};
  rclcpp::node_interfaces::OnSetParametersCallbackHandle::SharedPtr callback_;
};
}  // namespace omnifleet_planner
