// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from omnifleet_a2_interfaces:msg/SteeringAngleCommand.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_A2_INTERFACES__MSG__DETAIL__STEERING_ANGLE_COMMAND__TRAITS_HPP_
#define OMNIFLEET_A2_INTERFACES__MSG__DETAIL__STEERING_ANGLE_COMMAND__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "omnifleet_a2_interfaces/msg/detail/steering_angle_command__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace omnifleet_a2_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const SteeringAngleCommand & msg,
  std::ostream & out)
{
  out << "{";
  // member: steering_angle_rad
  {
    out << "steering_angle_rad: ";
    rosidl_generator_traits::value_to_yaml(msg.steering_angle_rad, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SteeringAngleCommand & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: steering_angle_rad
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "steering_angle_rad: ";
    rosidl_generator_traits::value_to_yaml(msg.steering_angle_rad, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SteeringAngleCommand & msg, bool use_flow_style = false)
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

}  // namespace omnifleet_a2_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_a2_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_a2_interfaces::msg::SteeringAngleCommand & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_a2_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_a2_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_a2_interfaces::msg::SteeringAngleCommand & msg)
{
  return omnifleet_a2_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_a2_interfaces::msg::SteeringAngleCommand>()
{
  return "omnifleet_a2_interfaces::msg::SteeringAngleCommand";
}

template<>
inline const char * name<omnifleet_a2_interfaces::msg::SteeringAngleCommand>()
{
  return "omnifleet_a2_interfaces/msg/SteeringAngleCommand";
}

template<>
struct has_fixed_size<omnifleet_a2_interfaces::msg::SteeringAngleCommand>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<omnifleet_a2_interfaces::msg::SteeringAngleCommand>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<omnifleet_a2_interfaces::msg::SteeringAngleCommand>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // OMNIFLEET_A2_INTERFACES__MSG__DETAIL__STEERING_ANGLE_COMMAND__TRAITS_HPP_
