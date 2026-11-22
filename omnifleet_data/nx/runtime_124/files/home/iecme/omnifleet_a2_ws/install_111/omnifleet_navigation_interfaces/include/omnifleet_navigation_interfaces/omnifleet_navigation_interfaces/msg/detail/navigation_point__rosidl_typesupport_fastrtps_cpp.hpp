// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__rosidl_typesupport_fastrtps_cpp.hpp.em
// with input from omnifleet_navigation_interfaces:msg/NavigationPoint.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
#define OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_

#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "omnifleet_navigation_interfaces/msg/rosidl_typesupport_fastrtps_cpp__visibility_control.h"
#include "omnifleet_navigation_interfaces/msg/detail/navigation_point__struct.hpp"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

#include "fastcdr/Cdr.h"

namespace omnifleet_navigation_interfaces
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_omnifleet_navigation_interfaces
cdr_serialize(
  const omnifleet_navigation_interfaces::msg::NavigationPoint & ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_omnifleet_navigation_interfaces
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  omnifleet_navigation_interfaces::msg::NavigationPoint & ros_message);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_omnifleet_navigation_interfaces
get_serialized_size(
  const omnifleet_navigation_interfaces::msg::NavigationPoint & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_omnifleet_navigation_interfaces
max_serialized_size_NavigationPoint(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace omnifleet_navigation_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_omnifleet_navigation_interfaces
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, omnifleet_navigation_interfaces, msg, NavigationPoint)();

#ifdef __cplusplus
}
#endif

#endif  // OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
