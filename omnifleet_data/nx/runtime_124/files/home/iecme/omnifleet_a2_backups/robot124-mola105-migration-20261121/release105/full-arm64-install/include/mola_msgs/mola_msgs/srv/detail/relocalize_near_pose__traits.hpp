// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from mola_msgs:srv/RelocalizeNearPose.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__RELOCALIZE_NEAR_POSE__TRAITS_HPP_
#define MOLA_MSGS__SRV__DETAIL__RELOCALIZE_NEAR_POSE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "mola_msgs/srv/detail/relocalize_near_pose__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_with_covariance_stamped__traits.hpp"

namespace mola_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const RelocalizeNearPose_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: pose
  {
    out << "pose: ";
    to_flow_style_yaml(msg.pose, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const RelocalizeNearPose_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pose:\n";
    to_block_style_yaml(msg.pose, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const RelocalizeNearPose_Request & msg, bool use_flow_style = false)
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
  const mola_msgs::srv::RelocalizeNearPose_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  mola_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use mola_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const mola_msgs::srv::RelocalizeNearPose_Request & msg)
{
  return mola_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<mola_msgs::srv::RelocalizeNearPose_Request>()
{
  return "mola_msgs::srv::RelocalizeNearPose_Request";
}

template<>
inline const char * name<mola_msgs::srv::RelocalizeNearPose_Request>()
{
  return "mola_msgs/srv/RelocalizeNearPose_Request";
}

template<>
struct has_fixed_size<mola_msgs::srv::RelocalizeNearPose_Request>
  : std::integral_constant<bool, has_fixed_size<geometry_msgs::msg::PoseWithCovarianceStamped>::value> {};

template<>
struct has_bounded_size<mola_msgs::srv::RelocalizeNearPose_Request>
  : std::integral_constant<bool, has_bounded_size<geometry_msgs::msg::PoseWithCovarianceStamped>::value> {};

template<>
struct is_message<mola_msgs::srv::RelocalizeNearPose_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace mola_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const RelocalizeNearPose_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: accepted
  {
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const RelocalizeNearPose_Response & msg,
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
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const RelocalizeNearPose_Response & msg, bool use_flow_style = false)
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
  const mola_msgs::srv::RelocalizeNearPose_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  mola_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use mola_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const mola_msgs::srv::RelocalizeNearPose_Response & msg)
{
  return mola_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<mola_msgs::srv::RelocalizeNearPose_Response>()
{
  return "mola_msgs::srv::RelocalizeNearPose_Response";
}

template<>
inline const char * name<mola_msgs::srv::RelocalizeNearPose_Response>()
{
  return "mola_msgs/srv/RelocalizeNearPose_Response";
}

template<>
struct has_fixed_size<mola_msgs::srv::RelocalizeNearPose_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<mola_msgs::srv::RelocalizeNearPose_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<mola_msgs::srv::RelocalizeNearPose_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<mola_msgs::srv::RelocalizeNearPose>()
{
  return "mola_msgs::srv::RelocalizeNearPose";
}

template<>
inline const char * name<mola_msgs::srv::RelocalizeNearPose>()
{
  return "mola_msgs/srv/RelocalizeNearPose";
}

template<>
struct has_fixed_size<mola_msgs::srv::RelocalizeNearPose>
  : std::integral_constant<
    bool,
    has_fixed_size<mola_msgs::srv::RelocalizeNearPose_Request>::value &&
    has_fixed_size<mola_msgs::srv::RelocalizeNearPose_Response>::value
  >
{
};

template<>
struct has_bounded_size<mola_msgs::srv::RelocalizeNearPose>
  : std::integral_constant<
    bool,
    has_bounded_size<mola_msgs::srv::RelocalizeNearPose_Request>::value &&
    has_bounded_size<mola_msgs::srv::RelocalizeNearPose_Response>::value
  >
{
};

template<>
struct is_service<mola_msgs::srv::RelocalizeNearPose>
  : std::true_type
{
};

template<>
struct is_service_request<mola_msgs::srv::RelocalizeNearPose_Request>
  : std::true_type
{
};

template<>
struct is_service_response<mola_msgs::srv::RelocalizeNearPose_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // MOLA_MSGS__SRV__DETAIL__RELOCALIZE_NEAR_POSE__TRAITS_HPP_
