// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__rosidl_typesupport_fastrtps_cpp.hpp.em
// with input from omnifleet_a2_interfaces:msg/SlamStatus.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_A2_INTERFACES__MSG__DETAIL__SLAM_STATUS__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
#define OMNIFLEET_A2_INTERFACES__MSG__DETAIL__SLAM_STATUS__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_

#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "omnifleet_a2_interfaces/msg/rosidl_typesupport_fastrtps_cpp__visibility_control.h"
#include "omnifleet_a2_interfaces/msg/detail/slam_status__struct.hpp"

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

namespace omnifleet_a2_interfaces
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_omnifleet_a2_interfaces
cdr_serialize(
  const omnifleet_a2_interfaces::msg::SlamStatus & ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_omnifleet_a2_interfaces
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  omnifleet_a2_interfaces::msg::SlamStatus & ros_message);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_omnifleet_a2_interfaces
get_serialized_size(
  const omnifleet_a2_interfaces::msg::SlamStatus & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_omnifleet_a2_interfaces
max_serialized_size_SlamStatus(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace omnifleet_a2_interfaces

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_omnifleet_a2_interfaces
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, omnifleet_a2_interfaces, msg, SlamStatus)();

#ifdef __cplusplus
}
#endif

#endif  // OMNIFLEET_A2_INTERFACES__MSG__DETAIL__SLAM_STATUS__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
