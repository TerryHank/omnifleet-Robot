// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from omnifleet_a2_interfaces:srv/SaveMap.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_A2_INTERFACES__SRV__DETAIL__SAVE_MAP__STRUCT_H_
#define OMNIFLEET_A2_INTERFACES__SRV__DETAIL__SAVE_MAP__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'label'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/SaveMap in the package omnifleet_a2_interfaces.
typedef struct omnifleet_a2_interfaces__srv__SaveMap_Request
{
  rosidl_runtime_c__String label;
} omnifleet_a2_interfaces__srv__SaveMap_Request;

// Struct for a sequence of omnifleet_a2_interfaces__srv__SaveMap_Request.
typedef struct omnifleet_a2_interfaces__srv__SaveMap_Request__Sequence
{
  omnifleet_a2_interfaces__srv__SaveMap_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_a2_interfaces__srv__SaveMap_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'map_id'
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/SaveMap in the package omnifleet_a2_interfaces.
typedef struct omnifleet_a2_interfaces__srv__SaveMap_Response
{
  bool success;
  rosidl_runtime_c__String map_id;
  rosidl_runtime_c__String message;
} omnifleet_a2_interfaces__srv__SaveMap_Response;

// Struct for a sequence of omnifleet_a2_interfaces__srv__SaveMap_Response.
typedef struct omnifleet_a2_interfaces__srv__SaveMap_Response__Sequence
{
  omnifleet_a2_interfaces__srv__SaveMap_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_a2_interfaces__srv__SaveMap_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // OMNIFLEET_A2_INTERFACES__SRV__DETAIL__SAVE_MAP__STRUCT_H_
