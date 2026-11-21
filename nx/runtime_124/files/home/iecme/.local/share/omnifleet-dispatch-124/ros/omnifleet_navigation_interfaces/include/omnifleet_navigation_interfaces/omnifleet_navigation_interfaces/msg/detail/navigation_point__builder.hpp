// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from omnifleet_navigation_interfaces:msg/NavigationPoint.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__BUILDER_HPP_
#define OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "omnifleet_navigation_interfaces/msg/detail/navigation_point__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace omnifleet_navigation_interfaces
{

namespace msg
{

namespace builder
{

class Init_NavigationPoint_dwell_seconds
{
public:
  explicit Init_NavigationPoint_dwell_seconds(::omnifleet_navigation_interfaces::msg::NavigationPoint & msg)
  : msg_(msg)
  {}
  ::omnifleet_navigation_interfaces::msg::NavigationPoint dwell_seconds(::omnifleet_navigation_interfaces::msg::NavigationPoint::_dwell_seconds_type arg)
  {
    msg_.dwell_seconds = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::msg::NavigationPoint msg_;
};

class Init_NavigationPoint_kind
{
public:
  explicit Init_NavigationPoint_kind(::omnifleet_navigation_interfaces::msg::NavigationPoint & msg)
  : msg_(msg)
  {}
  Init_NavigationPoint_dwell_seconds kind(::omnifleet_navigation_interfaces::msg::NavigationPoint::_kind_type arg)
  {
    msg_.kind = std::move(arg);
    return Init_NavigationPoint_dwell_seconds(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::msg::NavigationPoint msg_;
};

class Init_NavigationPoint_pose
{
public:
  explicit Init_NavigationPoint_pose(::omnifleet_navigation_interfaces::msg::NavigationPoint & msg)
  : msg_(msg)
  {}
  Init_NavigationPoint_kind pose(::omnifleet_navigation_interfaces::msg::NavigationPoint::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return Init_NavigationPoint_kind(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::msg::NavigationPoint msg_;
};

class Init_NavigationPoint_name
{
public:
  Init_NavigationPoint_name()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_NavigationPoint_pose name(::omnifleet_navigation_interfaces::msg::NavigationPoint::_name_type arg)
  {
    msg_.name = std::move(arg);
    return Init_NavigationPoint_pose(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::msg::NavigationPoint msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_navigation_interfaces::msg::NavigationPoint>()
{
  return omnifleet_navigation_interfaces::msg::builder::Init_NavigationPoint_name();
}

}  // namespace omnifleet_navigation_interfaces

#endif  // OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__BUILDER_HPP_
