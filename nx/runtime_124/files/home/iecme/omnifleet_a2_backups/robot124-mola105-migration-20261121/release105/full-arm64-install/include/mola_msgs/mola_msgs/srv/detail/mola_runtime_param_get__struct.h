// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from mola_msgs:srv/MolaRuntimeParamGet.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_GET__STRUCT_H_
#define MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_GET__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/MolaRuntimeParamGet in the package mola_msgs.
typedef struct mola_msgs__srv__MolaRuntimeParamGet_Request
{
  uint8_t structure_needs_at_least_one_member;
} mola_msgs__srv__MolaRuntimeParamGet_Request;

// Struct for a sequence of mola_msgs__srv__MolaRuntimeParamGet_Request.
typedef struct mola_msgs__srv__MolaRuntimeParamGet_Request__Sequence
{
  mola_msgs__srv__MolaRuntimeParamGet_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} mola_msgs__srv__MolaRuntimeParamGet_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'parameters'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/MolaRuntimeParamGet in the package mola_msgs.
typedef struct mola_msgs__srv__MolaRuntimeParamGet_Response
{
  rosidl_runtime_c__String parameters;
} mola_msgs__srv__MolaRuntimeParamGet_Response;

// Struct for a sequence of mola_msgs__srv__MolaRuntimeParamGet_Response.
typedef struct mola_msgs__srv__MolaRuntimeParamGet_Response__Sequence
{
  mola_msgs__srv__MolaRuntimeParamGet_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} mola_msgs__srv__MolaRuntimeParamGet_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_GET__STRUCT_H_
