#include "omnifleet_planner/hard_cost_filter.hpp"

#include <algorithm>
#include <stdexcept>
#include <nav2_costmap_2d/cost_values.hpp>
#include <nav2_costmap_2d/layered_costmap.hpp>
#include <pluginlib/class_list_macros.hpp>

namespace omnifleet_planner
{
void HardCostFilter::onInitialize()
{
  auto node = node_.lock();
  if (!node) {throw std::runtime_error("Costmap node expired");}
  declareParameter("hard_cost_threshold", rclcpp::ParameterValue(200));
  const auto value = node->get_parameter(name_ + ".hard_cost_threshold").as_int();
  if (value < 1 || value > 252) {
    throw std::invalid_argument("hard_cost_threshold must be an integer in [1, 252]");
  }
  threshold_ = static_cast<int>(value);
  callback_ = node->add_on_set_parameters_callback(
    [this](const auto & values) {return parameters(values);});
  enabled_ = true;
  current_ = true;
}

rcl_interfaces::msg::SetParametersResult HardCostFilter::parameters(
  const std::vector<rclcpp::Parameter> & values)
{
  rcl_interfaces::msg::SetParametersResult result;
  result.successful = true;
  int next = threshold_;
  for (const auto & value : values) {
    if (value.get_name() != name_ + ".hard_cost_threshold") {continue;}
    if (value.get_type() != rclcpp::ParameterType::PARAMETER_INTEGER ||
      value.as_int() < 1 || value.as_int() > 252)
    {
      result.successful = false;
      result.reason = "hard_cost_threshold must be an integer in [1, 252]";
      return result;
    }
    next = static_cast<int>(value.as_int());
  }
  if (threshold_.exchange(next) != next) {refresh_all_ = true;}
  return result;
}

void HardCostFilter::updateBounds(
  double, double, double, double * min_x, double * min_y, double * max_x, double * max_y)
{
  if (!refresh_all_.exchange(false)) {return;}
  const auto * map = layered_costmap_->getCostmap();
  *min_x = std::min(*min_x, map->getOriginX());
  *min_y = std::min(*min_y, map->getOriginY());
  *max_x = std::max(*max_x, map->getOriginX() + map->getSizeInMetersX());
  *max_y = std::max(*max_y, map->getOriginY() + map->getSizeInMetersY());
}

void HardCostFilter::updateCosts(
  nav2_costmap_2d::Costmap2D & map, int min_i, int min_j, int max_i, int max_j)
{
  const int threshold = threshold_;
  min_i = std::max(0, min_i);
  min_j = std::max(0, min_j);
  max_i = std::min(static_cast<int>(map.getSizeInCellsX()), max_i);
  max_j = std::min(static_cast<int>(map.getSizeInCellsY()), max_j);
  auto * data = map.getCharMap();
  for (int y = min_j; y < max_j; ++y) {
    for (int x = min_i; x < max_i; ++x) {
      auto & cost = data[map.getIndex(x, y)];
      if (cost >= threshold && cost < nav2_costmap_2d::LETHAL_OBSTACLE) {
        cost = nav2_costmap_2d::LETHAL_OBSTACLE;
      }
    }
  }
  current_ = true;
}
}  // namespace omnifleet_planner

PLUGINLIB_EXPORT_CLASS(omnifleet_planner::HardCostFilter, nav2_costmap_2d::Layer)
