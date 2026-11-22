// Copyright (c) 2022 Samsung Research America, @artofnothingness Alexey Budyakov
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "nav2_mppi_controller/critics/goal_angle_critic.hpp"
#include <nlohmann/json.hpp>

namespace mppi::critics
{

void GoalAngleCritic::initialize()
{
  auto node=parent_.lock();
  formation_group_=node->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive,false);
  rclcpp::SubscriptionOptions options;options.callback_group=formation_group_;
  formation_context_=node->create_subscription<std_msgs::msg::String>("navigation/fleet/follow_context",rclcpp::QoS(1),
    [this](std_msgs::msg::String::ConstSharedPtr m) {
      try {formation_=nlohmann::json::parse(m->data).value("joint_formation",false);
        formation_received_=std::chrono::steady_clock::now();}
      catch(const nlohmann::json::exception &) {formation_=false;}
    },options);
  formation_executor_.add_callback_group(formation_group_,node->get_node_base_interface());
  auto getParam = parameters_handler_->getParamGetter(name_);

  getParam(power_, "cost_power", 1);
  getParam(weight_, "cost_weight", 3.0);

  getParam(threshold_to_consider_, "threshold_to_consider", 0.5);

  RCLCPP_INFO(
    logger_,
    "GoalAngleCritic instantiated with %d power, %f weight, and %f "
    "angular threshold.",
    power_, weight_, threshold_to_consider_);
}

void GoalAngleCritic::score(CriticData & data)
{
  formation_executor_.spin_some();
  const bool formation=formation_ && std::chrono::steady_clock::now()-formation_received_<std::chrono::milliseconds(800);
  if (!enabled_ || (!formation && !utils::withinPositionGoalTolerance(
      threshold_to_consider_, data.state.pose.pose, data.path)))
  {
    return;
  }

  const auto goal_idx = data.path.x.shape(0) - 1;
  const float goal_yaw = data.path.yaws(goal_idx);

  data.costs += xt::pow(
    xt::mean(xt::abs(utils::shortest_angular_distance(data.trajectories.yaws, goal_yaw)), {1}) *
    weight_, power_);
}

}  // namespace mppi::critics

#include <pluginlib/class_list_macros.hpp>

PLUGINLIB_EXPORT_CLASS(
  mppi::critics::GoalAngleCritic,
  mppi::critics::CriticFunction)
