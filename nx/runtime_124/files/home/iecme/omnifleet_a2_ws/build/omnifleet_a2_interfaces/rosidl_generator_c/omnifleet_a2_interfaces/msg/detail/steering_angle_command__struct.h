// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from omnifleet_a2_interfaces:msg/SteeringAngleCommand.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_A2_INTERFACES__MSG__DETAIL__STEERING_ANGLE_COMMAND__STRUCT_H_
#define OMNIFLEET_A2_INTERFACES__MSG__DETAIL__STEERING_ANGLE_COMMAND__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/SteeringAngleCommand in the package omnifleet_a2_interfaces.
/**
  * Front-wheel steering target in radians. Positive means left turn.
 */
typedef struct omnifleet_a2_interfaces__msg__SteeringAngleCommand
{
  float steering_angle_rad;
} omnifleet_a2_interfaces__msg__SteeringAngleCommand;

// Struct for a sequence of omnifleet_a2_interfaces__msg__SteeringAngleCommand.
typedef struct omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence
{
  omnifleet_a2_interfaces__msg__SteeringAngleCommand * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // OMNIFLEET_A2_INTERFACES__MSG__DETAIL__STEERING_ANGLE_COMMAND__STRUCT_H_
