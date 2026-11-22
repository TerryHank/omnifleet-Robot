// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from omnifleet_interfaces:srv/ServoCommand.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__SRV__DETAIL__SERVO_COMMAND__STRUCT_H_
#define OMNIFLEET_INTERFACES__SRV__DETAIL__SERVO_COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/ServoCommand in the package omnifleet_interfaces.
typedef struct omnifleet_interfaces__srv__ServoCommand_Request
{
  uint8_t operation;
  uint8_t id;
  int32_t arg0;
  int32_t arg1;
  int32_t arg2;
} omnifleet_interfaces__srv__ServoCommand_Request;

// Struct for a sequence of omnifleet_interfaces__srv__ServoCommand_Request.
typedef struct omnifleet_interfaces__srv__ServoCommand_Request__Sequence
{
  omnifleet_interfaces__srv__ServoCommand_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_interfaces__srv__ServoCommand_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/ServoCommand in the package omnifleet_interfaces.
typedef struct omnifleet_interfaces__srv__ServoCommand_Response
{
  bool success;
  int32_t value0;
  int32_t value1;
  int32_t value2;
  rosidl_runtime_c__String message;
} omnifleet_interfaces__srv__ServoCommand_Response;

// Struct for a sequence of omnifleet_interfaces__srv__ServoCommand_Response.
typedef struct omnifleet_interfaces__srv__ServoCommand_Response__Sequence
{
  omnifleet_interfaces__srv__ServoCommand_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_interfaces__srv__ServoCommand_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // OMNIFLEET_INTERFACES__SRV__DETAIL__SERVO_COMMAND__STRUCT_H_
