// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from omnifleet_interfaces:srv/SaveMap.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__SRV__DETAIL__SAVE_MAP__BUILDER_HPP_
#define OMNIFLEET_INTERFACES__SRV__DETAIL__SAVE_MAP__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "omnifleet_interfaces/srv/detail/save_map__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace omnifleet_interfaces
{

namespace srv
{

namespace builder
{

class Init_SaveMap_Request_label
{
public:
  Init_SaveMap_Request_label()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::omnifleet_interfaces::srv::SaveMap_Request label(::omnifleet_interfaces::srv::SaveMap_Request::_label_type arg)
  {
    msg_.label = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_interfaces::srv::SaveMap_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_interfaces::srv::SaveMap_Request>()
{
  return omnifleet_interfaces::srv::builder::Init_SaveMap_Request_label();
}

}  // namespace omnifleet_interfaces


namespace omnifleet_interfaces
{

namespace srv
{

namespace builder
{

class Init_SaveMap_Response_message
{
public:
  explicit Init_SaveMap_Response_message(::omnifleet_interfaces::srv::SaveMap_Response & msg)
  : msg_(msg)
  {}
  ::omnifleet_interfaces::srv::SaveMap_Response message(::omnifleet_interfaces::srv::SaveMap_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_interfaces::srv::SaveMap_Response msg_;
};

class Init_SaveMap_Response_map_id
{
public:
  explicit Init_SaveMap_Response_map_id(::omnifleet_interfaces::srv::SaveMap_Response & msg)
  : msg_(msg)
  {}
  Init_SaveMap_Response_message map_id(::omnifleet_interfaces::srv::SaveMap_Response::_map_id_type arg)
  {
    msg_.map_id = std::move(arg);
    return Init_SaveMap_Response_message(msg_);
  }

private:
  ::omnifleet_interfaces::srv::SaveMap_Response msg_;
};

class Init_SaveMap_Response_success
{
public:
  Init_SaveMap_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SaveMap_Response_map_id success(::omnifleet_interfaces::srv::SaveMap_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_SaveMap_Response_map_id(msg_);
  }

private:
  ::omnifleet_interfaces::srv::SaveMap_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_interfaces::srv::SaveMap_Response>()
{
  return omnifleet_interfaces::srv::builder::Init_SaveMap_Response_success();
}

}  // namespace omnifleet_interfaces

#endif  // OMNIFLEET_INTERFACES__SRV__DETAIL__SAVE_MAP__BUILDER_HPP_
