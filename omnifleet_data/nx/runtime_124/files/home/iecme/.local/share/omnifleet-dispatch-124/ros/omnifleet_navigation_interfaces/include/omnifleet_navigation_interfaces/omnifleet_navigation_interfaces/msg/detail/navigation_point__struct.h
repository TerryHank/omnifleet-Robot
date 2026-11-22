// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from omnifleet_navigation_interfaces:msg/NavigationPoint.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__STRUCT_H_
#define OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'PASS'.
enum
{
  omnifleet_navigation_interfaces__msg__NavigationPoint__PASS = 0
};

/// Constant 'STOP'.
enum
{
  omnifleet_navigation_interfaces__msg__NavigationPoint__STOP = 1
};

// Include directives for member types
// Member 'name'
#include "rosidl_runtime_c/string.h"
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_stamped__struct.h"

/// Struct defined in msg/NavigationPoint in the package omnifleet_navigation_interfaces.
typedef struct omnifleet_navigation_interfaces__msg__NavigationPoint
{
  rosidl_runtime_c__String name;
  geometry_msgs__msg__PoseStamped pose;
  uint8_t kind;
  float dwell_seconds;
} omnifleet_navigation_interfaces__msg__NavigationPoint;

// Struct for a sequence of omnifleet_navigation_interfaces__msg__NavigationPoint.
typedef struct omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence
{
  omnifleet_navigation_interfaces__msg__NavigationPoint * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__STRUCT_H_
