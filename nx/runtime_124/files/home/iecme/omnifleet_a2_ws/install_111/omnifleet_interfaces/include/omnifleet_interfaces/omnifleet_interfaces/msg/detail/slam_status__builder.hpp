// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from omnifleet_interfaces:msg/SlamStatus.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__MSG__DETAIL__SLAM_STATUS__BUILDER_HPP_
#define OMNIFLEET_INTERFACES__MSG__DETAIL__SLAM_STATUS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "omnifleet_interfaces/msg/detail/slam_status__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace omnifleet_interfaces
{

namespace msg
{

namespace builder
{

class Init_SlamStatus_message
{
public:
  explicit Init_SlamStatus_message(::omnifleet_interfaces::msg::SlamStatus & msg)
  : msg_(msg)
  {}
  ::omnifleet_interfaces::msg::SlamStatus message(::omnifleet_interfaces::msg::SlamStatus::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_interfaces::msg::SlamStatus msg_;
};

class Init_SlamStatus_transaction_id
{
public:
  explicit Init_SlamStatus_transaction_id(::omnifleet_interfaces::msg::SlamStatus & msg)
  : msg_(msg)
  {}
  Init_SlamStatus_message transaction_id(::omnifleet_interfaces::msg::SlamStatus::_transaction_id_type arg)
  {
    msg_.transaction_id = std::move(arg);
    return Init_SlamStatus_message(msg_);
  }

private:
  ::omnifleet_interfaces::msg::SlamStatus msg_;
};

class Init_SlamStatus_map_id
{
public:
  explicit Init_SlamStatus_map_id(::omnifleet_interfaces::msg::SlamStatus & msg)
  : msg_(msg)
  {}
  Init_SlamStatus_transaction_id map_id(::omnifleet_interfaces::msg::SlamStatus::_map_id_type arg)
  {
    msg_.map_id = std::move(arg);
    return Init_SlamStatus_transaction_id(msg_);
  }

private:
  ::omnifleet_interfaces::msg::SlamStatus msg_;
};

class Init_SlamStatus_operation
{
public:
  explicit Init_SlamStatus_operation(::omnifleet_interfaces::msg::SlamStatus & msg)
  : msg_(msg)
  {}
  Init_SlamStatus_map_id operation(::omnifleet_interfaces::msg::SlamStatus::_operation_type arg)
  {
    msg_.operation = std::move(arg);
    return Init_SlamStatus_map_id(msg_);
  }

private:
  ::omnifleet_interfaces::msg::SlamStatus msg_;
};

class Init_SlamStatus_mode
{
public:
  explicit Init_SlamStatus_mode(::omnifleet_interfaces::msg::SlamStatus & msg)
  : msg_(msg)
  {}
  Init_SlamStatus_operation mode(::omnifleet_interfaces::msg::SlamStatus::_mode_type arg)
  {
    msg_.mode = std::move(arg);
    return Init_SlamStatus_operation(msg_);
  }

private:
  ::omnifleet_interfaces::msg::SlamStatus msg_;
};

class Init_SlamStatus_state
{
public:
  explicit Init_SlamStatus_state(::omnifleet_interfaces::msg::SlamStatus & msg)
  : msg_(msg)
  {}
  Init_SlamStatus_mode state(::omnifleet_interfaces::msg::SlamStatus::_state_type arg)
  {
    msg_.state = std::move(arg);
    return Init_SlamStatus_mode(msg_);
  }

private:
  ::omnifleet_interfaces::msg::SlamStatus msg_;
};

class Init_SlamStatus_stamp
{
public:
  Init_SlamStatus_stamp()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SlamStatus_state stamp(::omnifleet_interfaces::msg::SlamStatus::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return Init_SlamStatus_state(msg_);
  }

private:
  ::omnifleet_interfaces::msg::SlamStatus msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_interfaces::msg::SlamStatus>()
{
  return omnifleet_interfaces::msg::builder::Init_SlamStatus_stamp();
}

}  // namespace omnifleet_interfaces

#endif  // OMNIFLEET_INTERFACES__MSG__DETAIL__SLAM_STATUS__BUILDER_HPP_
