// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from omnifleet_interfaces:msg/MissionStatus.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__MSG__DETAIL__MISSION_STATUS__BUILDER_HPP_
#define OMNIFLEET_INTERFACES__MSG__DETAIL__MISSION_STATUS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "omnifleet_interfaces/msg/detail/mission_status__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace omnifleet_interfaces
{

namespace msg
{

namespace builder
{

class Init_MissionStatus_message
{
public:
  explicit Init_MissionStatus_message(::omnifleet_interfaces::msg::MissionStatus & msg)
  : msg_(msg)
  {}
  ::omnifleet_interfaces::msg::MissionStatus message(::omnifleet_interfaces::msg::MissionStatus::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_interfaces::msg::MissionStatus msg_;
};

class Init_MissionStatus_map_id
{
public:
  explicit Init_MissionStatus_map_id(::omnifleet_interfaces::msg::MissionStatus & msg)
  : msg_(msg)
  {}
  Init_MissionStatus_message map_id(::omnifleet_interfaces::msg::MissionStatus::_map_id_type arg)
  {
    msg_.map_id = std::move(arg);
    return Init_MissionStatus_message(msg_);
  }

private:
  ::omnifleet_interfaces::msg::MissionStatus msg_;
};

class Init_MissionStatus_total
{
public:
  explicit Init_MissionStatus_total(::omnifleet_interfaces::msg::MissionStatus & msg)
  : msg_(msg)
  {}
  Init_MissionStatus_map_id total(::omnifleet_interfaces::msg::MissionStatus::_total_type arg)
  {
    msg_.total = std::move(arg);
    return Init_MissionStatus_map_id(msg_);
  }

private:
  ::omnifleet_interfaces::msg::MissionStatus msg_;
};

class Init_MissionStatus_current_index
{
public:
  explicit Init_MissionStatus_current_index(::omnifleet_interfaces::msg::MissionStatus & msg)
  : msg_(msg)
  {}
  Init_MissionStatus_total current_index(::omnifleet_interfaces::msg::MissionStatus::_current_index_type arg)
  {
    msg_.current_index = std::move(arg);
    return Init_MissionStatus_total(msg_);
  }

private:
  ::omnifleet_interfaces::msg::MissionStatus msg_;
};

class Init_MissionStatus_revision
{
public:
  explicit Init_MissionStatus_revision(::omnifleet_interfaces::msg::MissionStatus & msg)
  : msg_(msg)
  {}
  Init_MissionStatus_current_index revision(::omnifleet_interfaces::msg::MissionStatus::_revision_type arg)
  {
    msg_.revision = std::move(arg);
    return Init_MissionStatus_current_index(msg_);
  }

private:
  ::omnifleet_interfaces::msg::MissionStatus msg_;
};

class Init_MissionStatus_mission_id
{
public:
  explicit Init_MissionStatus_mission_id(::omnifleet_interfaces::msg::MissionStatus & msg)
  : msg_(msg)
  {}
  Init_MissionStatus_revision mission_id(::omnifleet_interfaces::msg::MissionStatus::_mission_id_type arg)
  {
    msg_.mission_id = std::move(arg);
    return Init_MissionStatus_revision(msg_);
  }

private:
  ::omnifleet_interfaces::msg::MissionStatus msg_;
};

class Init_MissionStatus_state
{
public:
  explicit Init_MissionStatus_state(::omnifleet_interfaces::msg::MissionStatus & msg)
  : msg_(msg)
  {}
  Init_MissionStatus_mission_id state(::omnifleet_interfaces::msg::MissionStatus::_state_type arg)
  {
    msg_.state = std::move(arg);
    return Init_MissionStatus_mission_id(msg_);
  }

private:
  ::omnifleet_interfaces::msg::MissionStatus msg_;
};

class Init_MissionStatus_transaction_id
{
public:
  explicit Init_MissionStatus_transaction_id(::omnifleet_interfaces::msg::MissionStatus & msg)
  : msg_(msg)
  {}
  Init_MissionStatus_state transaction_id(::omnifleet_interfaces::msg::MissionStatus::_transaction_id_type arg)
  {
    msg_.transaction_id = std::move(arg);
    return Init_MissionStatus_state(msg_);
  }

private:
  ::omnifleet_interfaces::msg::MissionStatus msg_;
};

class Init_MissionStatus_stamp
{
public:
  Init_MissionStatus_stamp()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MissionStatus_transaction_id stamp(::omnifleet_interfaces::msg::MissionStatus::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return Init_MissionStatus_transaction_id(msg_);
  }

private:
  ::omnifleet_interfaces::msg::MissionStatus msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_interfaces::msg::MissionStatus>()
{
  return omnifleet_interfaces::msg::builder::Init_MissionStatus_stamp();
}

}  // namespace omnifleet_interfaces

#endif  // OMNIFLEET_INTERFACES__MSG__DETAIL__MISSION_STATUS__BUILDER_HPP_
