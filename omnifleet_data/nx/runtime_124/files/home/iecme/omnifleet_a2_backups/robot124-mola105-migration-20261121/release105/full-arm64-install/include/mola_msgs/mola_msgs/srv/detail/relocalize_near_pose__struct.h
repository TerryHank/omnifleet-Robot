// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from mola_msgs:srv/RelocalizeNearPose.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__RELOCALIZE_NEAR_POSE__STRUCT_H_
#define MOLA_MSGS__SRV__DETAIL__RELOCALIZE_NEAR_POSE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_with_covariance_stamped__struct.h"

/// Struct defined in srv/RelocalizeNearPose in the package mola_msgs.
typedef struct mola_msgs__srv__RelocalizeNearPose_Request
{
  /// Request
  geometry_msgs__msg__PoseWithCovarianceStamped pose;
} mola_msgs__srv__RelocalizeNearPose_Request;

// Struct for a sequence of mola_msgs__srv__RelocalizeNearPose_Request.
typedef struct mola_msgs__srv__RelocalizeNearPose_Request__Sequence
{
  mola_msgs__srv__RelocalizeNearPose_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} mola_msgs__srv__RelocalizeNearPose_Request__Sequence;


// Constants defined in the message

/// Struct defined in srv/RelocalizeNearPose in the package mola_msgs.
typedef struct mola_msgs__srv__RelocalizeNearPose_Response
{
  bool accepted;
} mola_msgs__srv__RelocalizeNearPose_Response;

// Struct for a sequence of mola_msgs__srv__RelocalizeNearPose_Response.
typedef struct mola_msgs__srv__RelocalizeNearPose_Response__Sequence
{
  mola_msgs__srv__RelocalizeNearPose_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} mola_msgs__srv__RelocalizeNearPose_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MOLA_MSGS__SRV__DETAIL__RELOCALIZE_NEAR_POSE__STRUCT_H_
