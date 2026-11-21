// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from omnifleet_a2_interfaces:msg/SlamStatus.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_A2_INTERFACES__MSG__DETAIL__SLAM_STATUS__STRUCT_H_
#define OMNIFLEET_A2_INTERFACES__MSG__DETAIL__SLAM_STATUS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"
// Member 'state'
// Member 'mode'
// Member 'operation'
// Member 'map_id'
// Member 'transaction_id'
// Member 'message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/SlamStatus in the package omnifleet_a2_interfaces.
typedef struct omnifleet_a2_interfaces__msg__SlamStatus
{
  builtin_interfaces__msg__Time stamp;
  rosidl_runtime_c__String state;
  rosidl_runtime_c__String mode;
  rosidl_runtime_c__String operation;
  rosidl_runtime_c__String map_id;
  rosidl_runtime_c__String transaction_id;
  rosidl_runtime_c__String message;
} omnifleet_a2_interfaces__msg__SlamStatus;

// Struct for a sequence of omnifleet_a2_interfaces__msg__SlamStatus.
typedef struct omnifleet_a2_interfaces__msg__SlamStatus__Sequence
{
  omnifleet_a2_interfaces__msg__SlamStatus * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_a2_interfaces__msg__SlamStatus__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // OMNIFLEET_A2_INTERFACES__MSG__DETAIL__SLAM_STATUS__STRUCT_H_
