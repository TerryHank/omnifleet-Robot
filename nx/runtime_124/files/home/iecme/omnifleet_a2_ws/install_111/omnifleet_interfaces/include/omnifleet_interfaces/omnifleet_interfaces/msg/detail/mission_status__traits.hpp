// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from omnifleet_interfaces:msg/MissionStatus.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__MSG__DETAIL__MISSION_STATUS__TRAITS_HPP_
#define OMNIFLEET_INTERFACES__MSG__DETAIL__MISSION_STATUS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "omnifleet_interfaces/msg/detail/mission_status__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace omnifleet_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const MissionStatus & msg,
  std::ostream & out)
{
  out << "{";
  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
    out << ", ";
  }

  // member: transaction_id
  {
    out << "transaction_id: ";
    rosidl_generator_traits::value_to_yaml(msg.transaction_id, out);
    out << ", ";
  }

  // member: state
  {
    out << "state: ";
    rosidl_generator_traits::value_to_yaml(msg.state, out);
    out << ", ";
  }

  // member: mission_id
  {
    out << "mission_id: ";
    rosidl_generator_traits::value_to_yaml(msg.mission_id, out);
    out << ", ";
  }

  // member: revision
  {
    out << "revision: ";
    rosidl_generator_traits::value_to_yaml(msg.revision, out);
    out << ", ";
  }

  // member: current_index
  {
    out << "current_index: ";
    rosidl_generator_traits::value_to_yaml(msg.current_index, out);
    out << ", ";
  }

  // member: total
  {
    out << "total: ";
    rosidl_generator_traits::value_to_yaml(msg.total, out);
    out << ", ";
  }

  // member: map_id
  {
    out << "map_id: ";
    rosidl_generator_traits::value_to_yaml(msg.map_id, out);
    out << ", ";
  }

  // member: message
  {
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MissionStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: stamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stamp:\n";
    to_block_style_yaml(msg.stamp, out, indentation + 2);
  }

  // member: transaction_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "transaction_id: ";
    rosidl_generator_traits::value_to_yaml(msg.transaction_id, out);
    out << "\n";
  }

  // member: state
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "state: ";
    rosidl_generator_traits::value_to_yaml(msg.state, out);
    out << "\n";
  }

  // member: mission_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mission_id: ";
    rosidl_generator_traits::value_to_yaml(msg.mission_id, out);
    out << "\n";
  }

  // member: revision
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "revision: ";
    rosidl_generator_traits::value_to_yaml(msg.revision, out);
    out << "\n";
  }

  // member: current_index
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "current_index: ";
    rosidl_generator_traits::value_to_yaml(msg.current_index, out);
    out << "\n";
  }

  // member: total
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "total: ";
    rosidl_generator_traits::value_to_yaml(msg.total, out);
    out << "\n";
  }

  // member: map_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "map_id: ";
    rosidl_generator_traits::value_to_yaml(msg.map_id, out);
    out << "\n";
  }

  // member: message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MissionStatus & msg, bool use_flow_style = false)
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

}  // namespace omnifleet_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_interfaces::msg::MissionStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_interfaces::msg::MissionStatus & msg)
{
  return omnifleet_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_interfaces::msg::MissionStatus>()
{
  return "omnifleet_interfaces::msg::MissionStatus";
}

template<>
inline const char * name<omnifleet_interfaces::msg::MissionStatus>()
{
  return "omnifleet_interfaces/msg/MissionStatus";
}

template<>
struct has_fixed_size<omnifleet_interfaces::msg::MissionStatus>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<omnifleet_interfaces::msg::MissionStatus>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<omnifleet_interfaces::msg::MissionStatus>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // OMNIFLEET_INTERFACES__MSG__DETAIL__MISSION_STATUS__TRAITS_HPP_
