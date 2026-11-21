// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from omnifleet_interfaces:srv/RunMission.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__SRV__DETAIL__RUN_MISSION__TRAITS_HPP_
#define OMNIFLEET_INTERFACES__SRV__DETAIL__RUN_MISSION__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "omnifleet_interfaces/srv/detail/run_mission__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace omnifleet_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const RunMission_Request & msg,
  std::ostream & out)
{
  out << "{";
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

  // member: policy
  {
    out << "policy: ";
    rosidl_generator_traits::value_to_yaml(msg.policy, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const RunMission_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
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

  // member: policy
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "policy: ";
    rosidl_generator_traits::value_to_yaml(msg.policy, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const RunMission_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace omnifleet_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_interfaces::srv::RunMission_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_interfaces::srv::RunMission_Request & msg)
{
  return omnifleet_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_interfaces::srv::RunMission_Request>()
{
  return "omnifleet_interfaces::srv::RunMission_Request";
}

template<>
inline const char * name<omnifleet_interfaces::srv::RunMission_Request>()
{
  return "omnifleet_interfaces/srv/RunMission_Request";
}

template<>
struct has_fixed_size<omnifleet_interfaces::srv::RunMission_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<omnifleet_interfaces::srv::RunMission_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<omnifleet_interfaces::srv::RunMission_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace omnifleet_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const RunMission_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: accepted
  {
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
    out << ", ";
  }

  // member: transaction_id
  {
    out << "transaction_id: ";
    rosidl_generator_traits::value_to_yaml(msg.transaction_id, out);
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
  const RunMission_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: accepted
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
    out << "\n";
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

inline std::string to_yaml(const RunMission_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace omnifleet_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_interfaces::srv::RunMission_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_interfaces::srv::RunMission_Response & msg)
{
  return omnifleet_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_interfaces::srv::RunMission_Response>()
{
  return "omnifleet_interfaces::srv::RunMission_Response";
}

template<>
inline const char * name<omnifleet_interfaces::srv::RunMission_Response>()
{
  return "omnifleet_interfaces/srv/RunMission_Response";
}

template<>
struct has_fixed_size<omnifleet_interfaces::srv::RunMission_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<omnifleet_interfaces::srv::RunMission_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<omnifleet_interfaces::srv::RunMission_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<omnifleet_interfaces::srv::RunMission>()
{
  return "omnifleet_interfaces::srv::RunMission";
}

template<>
inline const char * name<omnifleet_interfaces::srv::RunMission>()
{
  return "omnifleet_interfaces/srv/RunMission";
}

template<>
struct has_fixed_size<omnifleet_interfaces::srv::RunMission>
  : std::integral_constant<
    bool,
    has_fixed_size<omnifleet_interfaces::srv::RunMission_Request>::value &&
    has_fixed_size<omnifleet_interfaces::srv::RunMission_Response>::value
  >
{
};

template<>
struct has_bounded_size<omnifleet_interfaces::srv::RunMission>
  : std::integral_constant<
    bool,
    has_bounded_size<omnifleet_interfaces::srv::RunMission_Request>::value &&
    has_bounded_size<omnifleet_interfaces::srv::RunMission_Response>::value
  >
{
};

template<>
struct is_service<omnifleet_interfaces::srv::RunMission>
  : std::true_type
{
};

template<>
struct is_service_request<omnifleet_interfaces::srv::RunMission_Request>
  : std::true_type
{
};

template<>
struct is_service_response<omnifleet_interfaces::srv::RunMission_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // OMNIFLEET_INTERFACES__SRV__DETAIL__RUN_MISSION__TRAITS_HPP_
