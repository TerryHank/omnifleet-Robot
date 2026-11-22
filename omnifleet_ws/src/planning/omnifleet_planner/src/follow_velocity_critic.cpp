#include "omnifleet_planner/follow_velocity_critic.hpp"
#include "pluginlib/class_list_macros.hpp"
#include <nlohmann/json.hpp>
#include <algorithm>
#include <cmath>

namespace mppi::critics
{
void FollowVelocityCritic::initialize()
{
  auto get=parameters_handler_->getParamGetter(name_);
  get(weight_,"cost_weight",30.f);
  auto node=parent_.lock();
  group_=node->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive,false);
  rclcpp::SubscriptionOptions options;options.callback_group=group_;
  context_=node->create_subscription<std_msgs::msg::String>("navigation/fleet/follow_context",rclcpp::QoS(1),
    [this](std_msgs::msg::String::ConstSharedPtr message) {
      try {
        const auto value=nlohmann::json::parse(message->data);
        const float speed=value.at("tracking_speed").get<float>();
        if(!std::isfinite(speed))return;
        const float angular=value.value("tracking_angular",0.f);
        if(!std::isfinite(angular))return;
        active_=value.at("active").get<bool>();reference_=speed;
        angular_reference_=angular;formation_=value.value("formation",false);
        received_=std::chrono::steady_clock::now();
      }catch(const nlohmann::json::exception &){}
    },options);
  executor_.add_callback_group(group_,node->get_node_base_interface());
}

void FollowVelocityCritic::score(CriticData & data)
{
  if(!enabled_)return;
  executor_.spin_some();
  // Match the existing follow-target lifetime, using a clock immune to time corrections.
  if(!active_ || std::chrono::steady_clock::now()-received_>std::chrono::milliseconds(800))return;
  const size_t steps=std::min<size_t>(6,data.state.vx.shape(1));
  if(!steps)return;
  for(size_t i=0;i<data.state.vx.shape(0);++i) {
    float error=0.f;
    for(size_t j=0;j<steps;++j) {
      error+=std::abs(data.state.vx(i,j)-reference_);
      if(formation_)error+=.3f*std::abs(data.state.wz(i,j)-angular_reference_);
    }
    data.costs(i)+=weight_*error/steps;
  }
}
}

PLUGINLIB_EXPORT_CLASS(mppi::critics::FollowVelocityCritic,mppi::critics::CriticFunction)
