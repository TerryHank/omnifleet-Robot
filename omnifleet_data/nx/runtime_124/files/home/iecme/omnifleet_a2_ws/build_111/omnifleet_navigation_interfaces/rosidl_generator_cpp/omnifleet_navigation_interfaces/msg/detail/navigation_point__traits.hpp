// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from omnifleet_navigation_interfaces:msg/NavigationPoint.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__TRAITS_HPP_
#define OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "omnifleet_navigation_interfaces/msg/detail/navigation_point__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_stamped__traits.hpp"

namespace omnifleet_navigation_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const NavigationPoint & msg,
  std::ostream & out)
{
  out << "{";
  // member: name
  {
    out << "name: ";
    rosidl_generator_traits::value_to_yaml(msg.name, out);
    out << ", ";
  }

  // member: pose
  {
    out << "pose: ";
    to_flow_style_yaml(msg.pose, out);
    out << ", ";
  }

  // member: kind
  {
    out << "kind: ";
    rosidl_generator_traits::value_to_yaml(msg.kind, out);
    out << ", ";
  }

  // member: dwell_seconds
  {
    out << "dwell_seconds: ";
    rosidl_generator_traits::value_to_yaml(msg.dwell_seconds, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const NavigationPoint & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "name: ";
    rosidl_generator_traits::value_to_yaml(msg.name, out);
    out << "\n";
  }

  // member: pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pose:\n";
    to_block_style_yaml(msg.pose, out, indentation + 2);
  }

  // member: kind
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "kind: ";
    rosidl_generator_traits::value_to_yaml(msg.kind, out);
    out << "\n";
  }

  // member: dwell_seconds
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "dwell_seconds: ";
    rosidl_generator_traits::value_to_yaml(msg.dwell_seconds, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const NavigationPoint & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_navigation_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_navigation_interfaces::msg::NavigationPoint & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_navigation_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_navigation_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_navigation_interfaces::msg::NavigationPoint & msg)
{
  return omnifleet_navigation_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_navigation_interfaces::msg::NavigationPoint>()
{
  return "omnifleet_navigation_interfaces::msg::NavigationPoint";
}

template<>
inline const char * name<omnifleet_navigation_interfaces::msg::NavigationPoint>()
{
  return "omnifleet_navigation_interfaces/msg/NavigationPoint";
}

template<>
struct has_fixed_size<omnifleet_navigation_interfaces::msg::NavigationPoint>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<omnifleet_navigation_interfaces::msg::NavigationPoint>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<omnifleet_navigation_interfaces::msg::NavigationPoint>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__TRAITS_HPP_
