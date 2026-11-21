// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from omnifleet_a2_interfaces:srv/SwitchMode.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_A2_INTERFACES__SRV__DETAIL__SWITCH_MODE__BUILDER_HPP_
#define OMNIFLEET_A2_INTERFACES__SRV__DETAIL__SWITCH_MODE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "omnifleet_a2_interfaces/srv/detail/switch_mode__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace omnifleet_a2_interfaces
{

namespace srv
{

namespace builder
{

class Init_SwitchMode_Request_map_id
{
public:
  explicit Init_SwitchMode_Request_map_id(::omnifleet_a2_interfaces::srv::SwitchMode_Request & msg)
  : msg_(msg)
  {}
  ::omnifleet_a2_interfaces::srv::SwitchMode_Request map_id(::omnifleet_a2_interfaces::srv::SwitchMode_Request::_map_id_type arg)
  {
    msg_.map_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_a2_interfaces::srv::SwitchMode_Request msg_;
};

class Init_SwitchMode_Request_operation
{
public:
  explicit Init_SwitchMode_Request_operation(::omnifleet_a2_interfaces::srv::SwitchMode_Request & msg)
  : msg_(msg)
  {}
  Init_SwitchMode_Request_map_id operation(::omnifleet_a2_interfaces::srv::SwitchMode_Request::_operation_type arg)
  {
    msg_.operation = std::move(arg);
    return Init_SwitchMode_Request_map_id(msg_);
  }

private:
  ::omnifleet_a2_interfaces::srv::SwitchMode_Request msg_;
};

class Init_SwitchMode_Request_mode
{
public:
  Init_SwitchMode_Request_mode()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SwitchMode_Request_operation mode(::omnifleet_a2_interfaces::srv::SwitchMode_Request::_mode_type arg)
  {
    msg_.mode = std::move(arg);
    return Init_SwitchMode_Request_operation(msg_);
  }

private:
  ::omnifleet_a2_interfaces::srv::SwitchMode_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_a2_interfaces::srv::SwitchMode_Request>()
{
  return omnifleet_a2_interfaces::srv::builder::Init_SwitchMode_Request_mode();
}

}  // namespace omnifleet_a2_interfaces


namespace omnifleet_a2_interfaces
{

namespace srv
{

namespace builder
{

class Init_SwitchMode_Response_message
{
public:
  explicit Init_SwitchMode_Response_message(::omnifleet_a2_interfaces::srv::SwitchMode_Response & msg)
  : msg_(msg)
  {}
  ::omnifleet_a2_interfaces::srv::SwitchMode_Response message(::omnifleet_a2_interfaces::srv::SwitchMode_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_a2_interfaces::srv::SwitchMode_Response msg_;
};

class Init_SwitchMode_Response_transaction_id
{
public:
  explicit Init_SwitchMode_Response_transaction_id(::omnifleet_a2_interfaces::srv::SwitchMode_Response & msg)
  : msg_(msg)
  {}
  Init_SwitchMode_Response_message transaction_id(::omnifleet_a2_interfaces::srv::SwitchMode_Response::_transaction_id_type arg)
  {
    msg_.transaction_id = std::move(arg);
    return Init_SwitchMode_Response_message(msg_);
  }

private:
  ::omnifleet_a2_interfaces::srv::SwitchMode_Response msg_;
};

class Init_SwitchMode_Response_accepted
{
public:
  Init_SwitchMode_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SwitchMode_Response_transaction_id accepted(::omnifleet_a2_interfaces::srv::SwitchMode_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_SwitchMode_Response_transaction_id(msg_);
  }

private:
  ::omnifleet_a2_interfaces::srv::SwitchMode_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_a2_interfaces::srv::SwitchMode_Response>()
{
  return omnifleet_a2_interfaces::srv::builder::Init_SwitchMode_Response_accepted();
}

}  // namespace omnifleet_a2_interfaces

#endif  // OMNIFLEET_A2_INTERFACES__SRV__DETAIL__SWITCH_MODE__BUILDER_HPP_
