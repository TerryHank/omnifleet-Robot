// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from omnifleet_interfaces:srv/StoreMission.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__SRV__DETAIL__STORE_MISSION__BUILDER_HPP_
#define OMNIFLEET_INTERFACES__SRV__DETAIL__STORE_MISSION__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "omnifleet_interfaces/srv/detail/store_mission__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace omnifleet_interfaces
{

namespace srv
{

namespace builder
{

class Init_StoreMission_Request_loop
{
public:
  explicit Init_StoreMission_Request_loop(::omnifleet_interfaces::srv::StoreMission_Request & msg)
  : msg_(msg)
  {}
  ::omnifleet_interfaces::srv::StoreMission_Request loop(::omnifleet_interfaces::srv::StoreMission_Request::_loop_type arg)
  {
    msg_.loop = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_interfaces::srv::StoreMission_Request msg_;
};

class Init_StoreMission_Request_poses
{
public:
  explicit Init_StoreMission_Request_poses(::omnifleet_interfaces::srv::StoreMission_Request & msg)
  : msg_(msg)
  {}
  Init_StoreMission_Request_loop poses(::omnifleet_interfaces::srv::StoreMission_Request::_poses_type arg)
  {
    msg_.poses = std::move(arg);
    return Init_StoreMission_Request_loop(msg_);
  }

private:
  ::omnifleet_interfaces::srv::StoreMission_Request msg_;
};

class Init_StoreMission_Request_mission_id
{
public:
  Init_StoreMission_Request_mission_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StoreMission_Request_poses mission_id(::omnifleet_interfaces::srv::StoreMission_Request::_mission_id_type arg)
  {
    msg_.mission_id = std::move(arg);
    return Init_StoreMission_Request_poses(msg_);
  }

private:
  ::omnifleet_interfaces::srv::StoreMission_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_interfaces::srv::StoreMission_Request>()
{
  return omnifleet_interfaces::srv::builder::Init_StoreMission_Request_mission_id();
}

}  // namespace omnifleet_interfaces


namespace omnifleet_interfaces
{

namespace srv
{

namespace builder
{

class Init_StoreMission_Response_message
{
public:
  explicit Init_StoreMission_Response_message(::omnifleet_interfaces::srv::StoreMission_Response & msg)
  : msg_(msg)
  {}
  ::omnifleet_interfaces::srv::StoreMission_Response message(::omnifleet_interfaces::srv::StoreMission_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_interfaces::srv::StoreMission_Response msg_;
};

class Init_StoreMission_Response_map_sha256
{
public:
  explicit Init_StoreMission_Response_map_sha256(::omnifleet_interfaces::srv::StoreMission_Response & msg)
  : msg_(msg)
  {}
  Init_StoreMission_Response_message map_sha256(::omnifleet_interfaces::srv::StoreMission_Response::_map_sha256_type arg)
  {
    msg_.map_sha256 = std::move(arg);
    return Init_StoreMission_Response_message(msg_);
  }

private:
  ::omnifleet_interfaces::srv::StoreMission_Response msg_;
};

class Init_StoreMission_Response_map_id
{
public:
  explicit Init_StoreMission_Response_map_id(::omnifleet_interfaces::srv::StoreMission_Response & msg)
  : msg_(msg)
  {}
  Init_StoreMission_Response_map_sha256 map_id(::omnifleet_interfaces::srv::StoreMission_Response::_map_id_type arg)
  {
    msg_.map_id = std::move(arg);
    return Init_StoreMission_Response_map_sha256(msg_);
  }

private:
  ::omnifleet_interfaces::srv::StoreMission_Response msg_;
};

class Init_StoreMission_Response_revision
{
public:
  explicit Init_StoreMission_Response_revision(::omnifleet_interfaces::srv::StoreMission_Response & msg)
  : msg_(msg)
  {}
  Init_StoreMission_Response_map_id revision(::omnifleet_interfaces::srv::StoreMission_Response::_revision_type arg)
  {
    msg_.revision = std::move(arg);
    return Init_StoreMission_Response_map_id(msg_);
  }

private:
  ::omnifleet_interfaces::srv::StoreMission_Response msg_;
};

class Init_StoreMission_Response_accepted
{
public:
  Init_StoreMission_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StoreMission_Response_revision accepted(::omnifleet_interfaces::srv::StoreMission_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_StoreMission_Response_revision(msg_);
  }

private:
  ::omnifleet_interfaces::srv::StoreMission_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_interfaces::srv::StoreMission_Response>()
{
  return omnifleet_interfaces::srv::builder::Init_StoreMission_Response_accepted();
}

}  // namespace omnifleet_interfaces

#endif  // OMNIFLEET_INTERFACES__SRV__DETAIL__STORE_MISSION__BUILDER_HPP_
