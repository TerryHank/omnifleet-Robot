// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from mola_msgs:srv/MolaRuntimeParamSet.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_SET__TRAITS_HPP_
#define MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_SET__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "mola_msgs/srv/detail/mola_runtime_param_set__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace mola_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const MolaRuntimeParamSet_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: parameters
  {
    out << "parameters: ";
    rosidl_generator_traits::value_to_yaml(msg.parameters, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MolaRuntimeParamSet_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: parameters
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "parameters: ";
    rosidl_generator_traits::value_to_yaml(msg.parameters, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MolaRuntimeParamSet_Request & msg, bool use_flow_style = false)
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

}  // namespace mola_msgs

namespace rosidl_generator_traits
{

[[deprecated("use mola_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const mola_msgs::srv::MolaRuntimeParamSet_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  mola_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use mola_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const mola_msgs::srv::MolaRuntimeParamSet_Request & msg)
{
  return mola_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<mola_msgs::srv::MolaRuntimeParamSet_Request>()
{
  return "mola_msgs::srv::MolaRuntimeParamSet_Request";
}

template<>
inline const char * name<mola_msgs::srv::MolaRuntimeParamSet_Request>()
{
  return "mola_msgs/srv/MolaRuntimeParamSet_Request";
}

template<>
struct has_fixed_size<mola_msgs::srv::MolaRuntimeParamSet_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<mola_msgs::srv::MolaRuntimeParamSet_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<mola_msgs::srv::MolaRuntimeParamSet_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace mola_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const MolaRuntimeParamSet_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: error_message
  {
    out << "error_message: ";
    rosidl_generator_traits::value_to_yaml(msg.error_message, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MolaRuntimeParamSet_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }

  // member: error_message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "error_message: ";
    rosidl_generator_traits::value_to_yaml(msg.error_message, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MolaRuntimeParamSet_Response & msg, bool use_flow_style = false)
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

}  // namespace mola_msgs

namespace rosidl_generator_traits
{

[[deprecated("use mola_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const mola_msgs::srv::MolaRuntimeParamSet_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  mola_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use mola_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const mola_msgs::srv::MolaRuntimeParamSet_Response & msg)
{
  return mola_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<mola_msgs::srv::MolaRuntimeParamSet_Response>()
{
  return "mola_msgs::srv::MolaRuntimeParamSet_Response";
}

template<>
inline const char * name<mola_msgs::srv::MolaRuntimeParamSet_Response>()
{
  return "mola_msgs/srv/MolaRuntimeParamSet_Response";
}

template<>
struct has_fixed_size<mola_msgs::srv::MolaRuntimeParamSet_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<mola_msgs::srv::MolaRuntimeParamSet_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<mola_msgs::srv::MolaRuntimeParamSet_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<mola_msgs::srv::MolaRuntimeParamSet>()
{
  return "mola_msgs::srv::MolaRuntimeParamSet";
}

template<>
inline const char * name<mola_msgs::srv::MolaRuntimeParamSet>()
{
  return "mola_msgs/srv/MolaRuntimeParamSet";
}

template<>
struct has_fixed_size<mola_msgs::srv::MolaRuntimeParamSet>
  : std::integral_constant<
    bool,
    has_fixed_size<mola_msgs::srv::MolaRuntimeParamSet_Request>::value &&
    has_fixed_size<mola_msgs::srv::MolaRuntimeParamSet_Response>::value
  >
{
};

template<>
struct has_bounded_size<mola_msgs::srv::MolaRuntimeParamSet>
  : std::integral_constant<
    bool,
    has_bounded_size<mola_msgs::srv::MolaRuntimeParamSet_Request>::value &&
    has_bounded_size<mola_msgs::srv::MolaRuntimeParamSet_Response>::value
  >
{
};

template<>
struct is_service<mola_msgs::srv::MolaRuntimeParamSet>
  : std::true_type
{
};

template<>
struct is_service_request<mola_msgs::srv::MolaRuntimeParamSet_Request>
  : std::true_type
{
};

template<>
struct is_service_response<mola_msgs::srv::MolaRuntimeParamSet_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_SET__TRAITS_HPP_
