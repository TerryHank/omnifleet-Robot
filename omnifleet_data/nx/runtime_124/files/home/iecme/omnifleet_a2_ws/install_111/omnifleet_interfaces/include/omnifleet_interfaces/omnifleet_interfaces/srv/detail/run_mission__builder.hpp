// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from omnifleet_interfaces:srv/RunMission.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__SRV__DETAIL__RUN_MISSION__BUILDER_HPP_
#define OMNIFLEET_INTERFACES__SRV__DETAIL__RUN_MISSION__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "omnifleet_interfaces/srv/detail/run_mission__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace omnifleet_interfaces
{

namespace srv
{

namespace builder
{

class Init_RunMission_Request_policy
{
public:
  explicit Init_RunMission_Request_policy(::omnifleet_interfaces::srv::RunMission_Request & msg)
  : msg_(msg)
  {}
  ::omnifleet_interfaces::srv::RunMission_Request policy(::omnifleet_interfaces::srv::RunMission_Request::_policy_type arg)
  {
    msg_.policy = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_interfaces::srv::RunMission_Request msg_;
};

class Init_RunMission_Request_revision
{
public:
  explicit Init_RunMission_Request_revision(::omnifleet_interfaces::srv::RunMission_Request & msg)
  : msg_(msg)
  {}
  Init_RunMission_Request_policy revision(::omnifleet_interfaces::srv::RunMission_Request::_revision_type arg)
  {
    msg_.revision = std::move(arg);
    return Init_RunMission_Request_policy(msg_);
  }

private:
  ::omnifleet_interfaces::srv::RunMission_Request msg_;
};

class Init_RunMission_Request_mission_id
{
public:
  Init_RunMission_Request_mission_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_RunMission_Request_revision mission_id(::omnifleet_interfaces::srv::RunMission_Request::_mission_id_type arg)
  {
    msg_.mission_id = std::move(arg);
    return Init_RunMission_Request_revision(msg_);
  }

private:
  ::omnifleet_interfaces::srv::RunMission_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_interfaces::srv::RunMission_Request>()
{
  return omnifleet_interfaces::srv::builder::Init_RunMission_Request_mission_id();
}

}  // namespace omnifleet_interfaces


namespace omnifleet_interfaces
{

namespace srv
{

namespace builder
{

class Init_RunMission_Response_message
{
public:
  explicit Init_RunMission_Response_message(::omnifleet_interfaces::srv::RunMission_Response & msg)
  : msg_(msg)
  {}
  ::omnifleet_interfaces::srv::RunMission_Response message(::omnifleet_interfaces::srv::RunMission_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_interfaces::srv::RunMission_Response msg_;
};

class Init_RunMission_Response_transaction_id
{
public:
  explicit Init_RunMission_Response_transaction_id(::omnifleet_interfaces::srv::RunMission_Response & msg)
  : msg_(msg)
  {}
  Init_RunMission_Response_message transaction_id(::omnifleet_interfaces::srv::RunMission_Response::_transaction_id_type arg)
  {
    msg_.transaction_id = std::move(arg);
    return Init_RunMission_Response_message(msg_);
  }

private:
  ::omnifleet_interfaces::srv::RunMission_Response msg_;
};

class Init_RunMission_Response_accepted
{
public:
  Init_RunMission_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_RunMission_Response_transaction_id accepted(::omnifleet_interfaces::srv::RunMission_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_RunMission_Response_transaction_id(msg_);
  }

private:
  ::omnifleet_interfaces::srv::RunMission_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_interfaces::srv::RunMission_Response>()
{
  return omnifleet_interfaces::srv::builder::Init_RunMission_Response_accepted();
}

}  // namespace omnifleet_interfaces

#endif  // OMNIFLEET_INTERFACES__SRV__DETAIL__RUN_MISSION__BUILDER_HPP_
