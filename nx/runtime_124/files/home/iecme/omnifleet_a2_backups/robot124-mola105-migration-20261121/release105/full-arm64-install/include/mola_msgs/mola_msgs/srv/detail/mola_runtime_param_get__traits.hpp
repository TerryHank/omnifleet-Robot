// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from mola_msgs:srv/MolaRuntimeParamGet.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_GET__TRAITS_HPP_
#define MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_GET__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "mola_msgs/srv/detail/mola_runtime_param_get__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace mola_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const MolaRuntimeParamGet_Request & msg,
  std::ostream & out)
{
  (void)msg;
  out << "null";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const MolaRuntimeParamGet_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  (void)msg;
  (void)indentation;
  out << "null\n";
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const MolaRuntimeParamGet_Request & msg, bool use_flow_style = false)
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
  const mola_msgs::srv::MolaRuntimeParamGet_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  mola_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use mola_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const mola_msgs::srv::MolaRuntimeParamGet_Request & msg)
{
  return mola_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<mola_msgs::srv::MolaRuntimeParamGet_Request>()
{
  return "mola_msgs::srv::MolaRuntimeParamGet_Request";
}

template<>
inline const char * name<mola_msgs::srv::MolaRuntimeParamGet_Request>()
{
  return "mola_msgs/srv/MolaRuntimeParamGet_Request";
}

template<>
struct has_fixed_size<mola_msgs::srv::MolaRuntimeParamGet_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<mola_msgs::srv::MolaRuntimeParamGet_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<mola_msgs::srv::MolaRuntimeParamGet_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace mola_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const MolaRuntimeParamGet_Response & msg,
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
  const MolaRuntimeParamGet_Response & msg,
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

inline std::string to_yaml(const MolaRuntimeParamGet_Response & msg, bool use_flow_style = false)
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
  const mola_msgs::srv::MolaRuntimeParamGet_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  mola_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use mola_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const mola_msgs::srv::MolaRuntimeParamGet_Response & msg)
{
  return mola_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<mola_msgs::srv::MolaRuntimeParamGet_Response>()
{
  return "mola_msgs::srv::MolaRuntimeParamGet_Response";
}

template<>
inline const char * name<mola_msgs::srv::MolaRuntimeParamGet_Response>()
{
  return "mola_msgs/srv/MolaRuntimeParamGet_Response";
}

template<>
struct has_fixed_size<mola_msgs::srv::MolaRuntimeParamGet_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<mola_msgs::srv::MolaRuntimeParamGet_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<mola_msgs::srv::MolaRuntimeParamGet_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<mola_msgs::srv::MolaRuntimeParamGet>()
{
  return "mola_msgs::srv::MolaRuntimeParamGet";
}

template<>
inline const char * name<mola_msgs::srv::MolaRuntimeParamGet>()
{
  return "mola_msgs/srv/MolaRuntimeParamGet";
}

template<>
struct has_fixed_size<mola_msgs::srv::MolaRuntimeParamGet>
  : std::integral_constant<
    bool,
    has_fixed_size<mola_msgs::srv::MolaRuntimeParamGet_Request>::value &&
    has_fixed_size<mola_msgs::srv::MolaRuntimeParamGet_Response>::value
  >
{
};

template<>
struct has_bounded_size<mola_msgs::srv::MolaRuntimeParamGet>
  : std::integral_constant<
    bool,
    has_bounded_size<mola_msgs::srv::MolaRuntimeParamGet_Request>::value &&
    has_bounded_size<mola_msgs::srv::MolaRuntimeParamGet_Response>::value
  >
{
};

template<>
struct is_service<mola_msgs::srv::MolaRuntimeParamGet>
  : std::true_type
{
};

template<>
struct is_service_request<mola_msgs::srv::MolaRuntimeParamGet_Request>
  : std::true_type
{
};

template<>
struct is_service_response<mola_msgs::srv::MolaRuntimeParamGet_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_GET__TRAITS_HPP_
