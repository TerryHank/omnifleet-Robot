// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from omnifleet_interfaces:srv/StoreMission.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__SRV__DETAIL__STORE_MISSION__STRUCT_H_
#define OMNIFLEET_INTERFACES__SRV__DETAIL__STORE_MISSION__STRUCT_H_

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
#include "rosidl_runtime_c/string.h"
// Member 'poses'
#include "geometry_msgs/msg/detail/pose__struct.h"

/// Struct defined in srv/StoreMission in the package omnifleet_interfaces.
typedef struct omnifleet_interfaces__srv__StoreMission_Request
{
  rosidl_runtime_c__String mission_id;
  geometry_msgs__msg__Pose__Sequence poses;
  bool loop;
} omnifleet_interfaces__srv__StoreMission_Request;

// Struct for a sequence of omnifleet_interfaces__srv__StoreMission_Request.
typedef struct omnifleet_interfaces__srv__StoreMission_Request__Sequence
{
  omnifleet_interfaces__srv__StoreMission_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_interfaces__srv__StoreMission_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'map_id'
// Member 'map_sha256'
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/StoreMission in the package omnifleet_interfaces.
typedef struct omnifleet_interfaces__srv__StoreMission_Response
{
  bool accepted;
  uint64_t revision;
  rosidl_runtime_c__String map_id;
  rosidl_runtime_c__String map_sha256;
  rosidl_runtime_c__String message;
} omnifleet_interfaces__srv__StoreMission_Response;

// Struct for a sequence of omnifleet_interfaces__srv__StoreMission_Response.
typedef struct omnifleet_interfaces__srv__StoreMission_Response__Sequence
{
  omnifleet_interfaces__srv__StoreMission_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_interfaces__srv__StoreMission_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // OMNIFLEET_INTERFACES__SRV__DETAIL__STORE_MISSION__STRUCT_H_
