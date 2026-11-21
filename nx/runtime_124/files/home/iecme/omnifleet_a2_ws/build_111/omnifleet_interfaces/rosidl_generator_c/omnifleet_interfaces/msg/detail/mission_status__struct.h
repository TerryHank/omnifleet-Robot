// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from omnifleet_interfaces:msg/MissionStatus.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__MSG__DETAIL__MISSION_STATUS__STRUCT_H_
#define OMNIFLEET_INTERFACES__MSG__DETAIL__MISSION_STATUS__STRUCT_H_

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
// Member 'transaction_id'
// Member 'state'
// Member 'mission_id'
// Member 'map_id'
// Member 'message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/MissionStatus in the package omnifleet_interfaces.
typedef struct omnifleet_interfaces__msg__MissionStatus
{
  builtin_interfaces__msg__Time stamp;
  rosidl_runtime_c__String transaction_id;
  rosidl_runtime_c__String state;
  rosidl_runtime_c__String mission_id;
  uint64_t revision;
  uint32_t current_index;
  uint32_t total;
  rosidl_runtime_c__String map_id;
  rosidl_runtime_c__String message;
} omnifleet_interfaces__msg__MissionStatus;

// Struct for a sequence of omnifleet_interfaces__msg__MissionStatus.
typedef struct omnifleet_interfaces__msg__MissionStatus__Sequence
{
  omnifleet_interfaces__msg__MissionStatus * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_interfaces__msg__MissionStatus__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // OMNIFLEET_INTERFACES__MSG__DETAIL__MISSION_STATUS__STRUCT_H_
