// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from mola_msgs:srv/MolaRuntimeParamSet.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_SET__STRUCT_H_
#define MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_SET__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'parameters'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/MolaRuntimeParamSet in the package mola_msgs.
typedef struct mola_msgs__srv__MolaRuntimeParamSet_Request
{
  /// Request: a multiline string in YAML format with all parameters that need to be changed, in this format:
  /// ---
  /// module1:
  ///   var: value
  /// module2:
  ///   var: value
  /// ...
  /// ---
  rosidl_runtime_c__String parameters;
} mola_msgs__srv__MolaRuntimeParamSet_Request;

// Struct for a sequence of mola_msgs__srv__MolaRuntimeParamSet_Request.
typedef struct mola_msgs__srv__MolaRuntimeParamSet_Request__Sequence
{
  mola_msgs__srv__MolaRuntimeParamSet_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} mola_msgs__srv__MolaRuntimeParamSet_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'error_message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/MolaRuntimeParamSet in the package mola_msgs.
typedef struct mola_msgs__srv__MolaRuntimeParamSet_Response
{
  bool success;
  /// In case of no success, here is a human-readable error reason.
  rosidl_runtime_c__String error_message;
} mola_msgs__srv__MolaRuntimeParamSet_Response;

// Struct for a sequence of mola_msgs__srv__MolaRuntimeParamSet_Response.
typedef struct mola_msgs__srv__MolaRuntimeParamSet_Response__Sequence
{
  mola_msgs__srv__MolaRuntimeParamSet_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} mola_msgs__srv__MolaRuntimeParamSet_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_SET__STRUCT_H_
