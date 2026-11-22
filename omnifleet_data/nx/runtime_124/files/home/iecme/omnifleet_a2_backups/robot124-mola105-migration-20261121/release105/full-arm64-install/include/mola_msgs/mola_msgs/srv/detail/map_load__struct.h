// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from mola_msgs:srv/MapLoad.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__MAP_LOAD__STRUCT_H_
#define MOLA_MSGS__SRV__DETAIL__MAP_LOAD__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'map_path'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/MapLoad in the package mola_msgs.
typedef struct mola_msgs__srv__MapLoad_Request
{
  /// Request.
  /// File relative or absolute path. Do not add any file extension, since maps
  /// may be loaded/saved to several files depending on implementation.
  rosidl_runtime_c__String map_path;
} mola_msgs__srv__MapLoad_Request;

// Struct for a sequence of mola_msgs__srv__MapLoad_Request.
typedef struct mola_msgs__srv__MapLoad_Request__Sequence
{
  mola_msgs__srv__MapLoad_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} mola_msgs__srv__MapLoad_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'error_message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/MapLoad in the package mola_msgs.
typedef struct mola_msgs__srv__MapLoad_Response
{
  bool success;
  /// In case of no success, here is a human-readable error reason.
  rosidl_runtime_c__String error_message;
} mola_msgs__srv__MapLoad_Response;

// Struct for a sequence of mola_msgs__srv__MapLoad_Response.
typedef struct mola_msgs__srv__MapLoad_Response__Sequence
{
  mola_msgs__srv__MapLoad_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} mola_msgs__srv__MapLoad_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MOLA_MSGS__SRV__DETAIL__MAP_LOAD__STRUCT_H_
