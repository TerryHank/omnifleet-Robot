// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from omnifleet_a2_interfaces:msg/SteeringAngleCommand.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_A2_INTERFACES__MSG__DETAIL__STEERING_ANGLE_COMMAND__BUILDER_HPP_
#define OMNIFLEET_A2_INTERFACES__MSG__DETAIL__STEERING_ANGLE_COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "omnifleet_a2_interfaces/msg/detail/steering_angle_command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace omnifleet_a2_interfaces
{

namespace msg
{

namespace builder
{

class Init_SteeringAngleCommand_steering_angle_rad
{
public:
  Init_SteeringAngleCommand_steering_angle_rad()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::omnifleet_a2_interfaces::msg::SteeringAngleCommand steering_angle_rad(::omnifleet_a2_interfaces::msg::SteeringAngleCommand::_steering_angle_rad_type arg)
  {
    msg_.steering_angle_rad = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_a2_interfaces::msg::SteeringAngleCommand msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_a2_interfaces::msg::SteeringAngleCommand>()
{
  return omnifleet_a2_interfaces::msg::builder::Init_SteeringAngleCommand_steering_angle_rad();
}

}  // namespace omnifleet_a2_interfaces

#endif  // OMNIFLEET_A2_INTERFACES__MSG__DETAIL__STEERING_ANGLE_COMMAND__BUILDER_HPP_
