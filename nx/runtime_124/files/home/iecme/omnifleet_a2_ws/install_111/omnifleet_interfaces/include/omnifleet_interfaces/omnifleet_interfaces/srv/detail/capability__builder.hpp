// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from omnifleet_interfaces:srv/Capability.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__SRV__DETAIL__CAPABILITY__BUILDER_HPP_
#define OMNIFLEET_INTERFACES__SRV__DETAIL__CAPABILITY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "omnifleet_interfaces/srv/detail/capability__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace omnifleet_interfaces
{

namespace srv
{

namespace builder
{

class Init_Capability_Request_capability
{
public:
  Init_Capability_Request_capability()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::omnifleet_interfaces::srv::Capability_Request capability(::omnifleet_interfaces::srv::Capability_Request::_capability_type arg)
  {
    msg_.capability = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_interfaces::srv::Capability_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_interfaces::srv::Capability_Request>()
{
  return omnifleet_interfaces::srv::builder::Init_Capability_Request_capability();
}

}  // namespace omnifleet_interfaces


namespace omnifleet_interfaces
{

namespace srv
{

namespace builder
{

class Init_Capability_Response_message
{
public:
  explicit Init_Capability_Response_message(::omnifleet_interfaces::srv::Capability_Response & msg)
  : msg_(msg)
  {}
  ::omnifleet_interfaces::srv::Capability_Response message(::omnifleet_interfaces::srv::Capability_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_interfaces::srv::Capability_Response msg_;
};

class Init_Capability_Response_transaction_id
{
public:
  explicit Init_Capability_Response_transaction_id(::omnifleet_interfaces::srv::Capability_Response & msg)
  : msg_(msg)
  {}
  Init_Capability_Response_message transaction_id(::omnifleet_interfaces::srv::Capability_Response::_transaction_id_type arg)
  {
    msg_.transaction_id = std::move(arg);
    return Init_Capability_Response_message(msg_);
  }

private:
  ::omnifleet_interfaces::srv::Capability_Response msg_;
};

class Init_Capability_Response_accepted
{
public:
  explicit Init_Capability_Response_accepted(::omnifleet_interfaces::srv::Capability_Response & msg)
  : msg_(msg)
  {}
  Init_Capability_Response_transaction_id accepted(::omnifleet_interfaces::srv::Capability_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_Capability_Response_transaction_id(msg_);
  }

private:
  ::omnifleet_interfaces::srv::Capability_Response msg_;
};

class Init_Capability_Response_available
{
public:
  Init_Capability_Response_available()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Capability_Response_accepted available(::omnifleet_interfaces::srv::Capability_Response::_available_type arg)
  {
    msg_.available = std::move(arg);
    return Init_Capability_Response_accepted(msg_);
  }

private:
  ::omnifleet_interfaces::srv::Capability_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_interfaces::srv::Capability_Response>()
{
  return omnifleet_interfaces::srv::builder::Init_Capability_Response_available();
}

}  // namespace omnifleet_interfaces

#endif  // OMNIFLEET_INTERFACES__SRV__DETAIL__CAPABILITY__BUILDER_HPP_
