// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from mola_msgs:srv/RelocalizeFromStateEstimator.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__RELOCALIZE_FROM_STATE_ESTIMATOR__STRUCT_H_
#define MOLA_MSGS__SRV__DETAIL__RELOCALIZE_FROM_STATE_ESTIMATOR__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in srv/RelocalizeFromStateEstimator in the package mola_msgs.
typedef struct mola_msgs__srv__RelocalizeFromStateEstimator_Request
{
  uint8_t structure_needs_at_least_one_member;
} mola_msgs__srv__RelocalizeFromStateEstimator_Request;

// Struct for a sequence of mola_msgs__srv__RelocalizeFromStateEstimator_Request.
typedef struct mola_msgs__srv__RelocalizeFromStateEstimator_Request__Sequence
{
  mola_msgs__srv__RelocalizeFromStateEstimator_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} mola_msgs__srv__RelocalizeFromStateEstimator_Request__Sequence;


// Constants defined in the message

/// Struct defined in srv/RelocalizeFromStateEstimator in the package mola_msgs.
typedef struct mola_msgs__srv__RelocalizeFromStateEstimator_Response
{
  bool accepted;
} mola_msgs__srv__RelocalizeFromStateEstimator_Response;

// Struct for a sequence of mola_msgs__srv__RelocalizeFromStateEstimator_Response.
typedef struct mola_msgs__srv__RelocalizeFromStateEstimator_Response__Sequence
{
  mola_msgs__srv__RelocalizeFromStateEstimator_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} mola_msgs__srv__RelocalizeFromStateEstimator_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // MOLA_MSGS__SRV__DETAIL__RELOCALIZE_FROM_STATE_ESTIMATOR__STRUCT_H_
