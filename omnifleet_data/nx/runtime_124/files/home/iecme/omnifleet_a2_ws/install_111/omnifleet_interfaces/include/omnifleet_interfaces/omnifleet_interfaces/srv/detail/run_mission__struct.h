// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from omnifleet_interfaces:srv/RunMission.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__SRV__DETAIL__RUN_MISSION__STRUCT_H_
#define OMNIFLEET_INTERFACES__SRV__DETAIL__RUN_MISSION__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'mission_id'
// Member 'policy'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/RunMission in the package omnifleet_interfaces.
typedef struct omnifleet_interfaces__srv__RunMission_Request
{
  rosidl_runtime_c__String mission_id;
  uint64_t revision;
  rosidl_runtime_c__String policy;
} omnifleet_interfaces__srv__RunMission_Request;

// Struct for a sequence of omnifleet_interfaces__srv__RunMission_Request.
typedef struct omnifleet_interfaces__srv__RunMission_Request__Sequence
{
  omnifleet_interfaces__srv__RunMission_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_interfaces__srv__RunMission_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'transaction_id'
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/RunMission in the package omnifleet_interfaces.
typedef struct omnifleet_interfaces__srv__RunMission_Response
{
  bool accepted;
  rosidl_runtime_c__String transaction_id;
  rosidl_runtime_c__String message;
} omnifleet_interfaces__srv__RunMission_Response;

// Struct for a sequence of omnifleet_interfaces__srv__RunMission_Response.
typedef struct omnifleet_interfaces__srv__RunMission_Response__Sequence
{
  omnifleet_interfaces__srv__RunMission_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_interfaces__srv__RunMission_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // OMNIFLEET_INTERFACES__SRV__DETAIL__RUN_MISSION__STRUCT_H_
