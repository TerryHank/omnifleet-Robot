// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from mola_msgs:srv/RelocalizeNearPose.idl
// generated code does not contain a copyright notice
#include "mola_msgs/srv/detail/relocalize_near_pose__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `pose`
#include "geometry_msgs/msg/detail/pose_with_covariance_stamped__functions.h"

bool
mola_msgs__srv__RelocalizeNearPose_Request__init(mola_msgs__srv__RelocalizeNearPose_Request * msg)
{
  if (!msg) {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__PoseWithCovarianceStamped__init(&msg->pose)) {
    mola_msgs__srv__RelocalizeNearPose_Request__fini(msg);
    return false;
  }
  return true;
}

void
mola_msgs__srv__RelocalizeNearPose_Request__fini(mola_msgs__srv__RelocalizeNearPose_Request * msg)
{
  if (!msg) {
    return;
  }
  // pose
  geometry_msgs__msg__PoseWithCovarianceStamped__fini(&msg->pose);
}

bool
mola_msgs__srv__RelocalizeNearPose_Request__are_equal(const mola_msgs__srv__RelocalizeNearPose_Request * lhs, const mola_msgs__srv__RelocalizeNearPose_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__PoseWithCovarianceStamped__are_equal(
      &(lhs->pose), &(rhs->pose)))
  {
    return false;
  }
  return true;
}

bool
mola_msgs__srv__RelocalizeNearPose_Request__copy(
  const mola_msgs__srv__RelocalizeNearPose_Request * input,
  mola_msgs__srv__RelocalizeNearPose_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__PoseWithCovarianceStamped__copy(
      &(input->pose), &(output->pose)))
  {
    return false;
  }
  return true;
}

mola_msgs__srv__RelocalizeNearPose_Request *
mola_msgs__srv__RelocalizeNearPose_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  mola_msgs__srv__RelocalizeNearPose_Request * msg = (mola_msgs__srv__RelocalizeNearPose_Request *)allocator.allocate(sizeof(mola_msgs__srv__RelocalizeNearPose_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(mola_msgs__srv__RelocalizeNearPose_Request));
  bool success = mola_msgs__srv__RelocalizeNearPose_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
mola_msgs__srv__RelocalizeNearPose_Request__destroy(mola_msgs__srv__RelocalizeNearPose_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    mola_msgs__srv__RelocalizeNearPose_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
mola_msgs__srv__RelocalizeNearPose_Request__Sequence__init(mola_msgs__srv__RelocalizeNearPose_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  mola_msgs__srv__RelocalizeNearPose_Request * data = NULL;

  if (size) {
    data = (mola_msgs__srv__RelocalizeNearPose_Request *)allocator.zero_allocate(size, sizeof(mola_msgs__srv__RelocalizeNearPose_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = mola_msgs__srv__RelocalizeNearPose_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        mola_msgs__srv__RelocalizeNearPose_Request__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
mola_msgs__srv__RelocalizeNearPose_Request__Sequence__fini(mola_msgs__srv__RelocalizeNearPose_Request__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      mola_msgs__srv__RelocalizeNearPose_Request__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

mola_msgs__srv__RelocalizeNearPose_Request__Sequence *
mola_msgs__srv__RelocalizeNearPose_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  mola_msgs__srv__RelocalizeNearPose_Request__Sequence * array = (mola_msgs__srv__RelocalizeNearPose_Request__Sequence *)allocator.allocate(sizeof(mola_msgs__srv__RelocalizeNearPose_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = mola_msgs__srv__RelocalizeNearPose_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
mola_msgs__srv__RelocalizeNearPose_Request__Sequence__destroy(mola_msgs__srv__RelocalizeNearPose_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    mola_msgs__srv__RelocalizeNearPose_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
mola_msgs__srv__RelocalizeNearPose_Request__Sequence__are_equal(const mola_msgs__srv__RelocalizeNearPose_Request__Sequence * lhs, const mola_msgs__srv__RelocalizeNearPose_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!mola_msgs__srv__RelocalizeNearPose_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
mola_msgs__srv__RelocalizeNearPose_Request__Sequence__copy(
  const mola_msgs__srv__RelocalizeNearPose_Request__Sequence * input,
  mola_msgs__srv__RelocalizeNearPose_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(mola_msgs__srv__RelocalizeNearPose_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    mola_msgs__srv__RelocalizeNearPose_Request * data =
      (mola_msgs__srv__RelocalizeNearPose_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!mola_msgs__srv__RelocalizeNearPose_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          mola_msgs__srv__RelocalizeNearPose_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!mola_msgs__srv__RelocalizeNearPose_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


bool
mola_msgs__srv__RelocalizeNearPose_Response__init(mola_msgs__srv__RelocalizeNearPose_Response * msg)
{
  if (!msg) {
    return false;
  }
  // accepted
  return true;
}

void
mola_msgs__srv__RelocalizeNearPose_Response__fini(mola_msgs__srv__RelocalizeNearPose_Response * msg)
{
  if (!msg) {
    return;
  }
  // accepted
}

bool
mola_msgs__srv__RelocalizeNearPose_Response__are_equal(const mola_msgs__srv__RelocalizeNearPose_Response * lhs, const mola_msgs__srv__RelocalizeNearPose_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // accepted
  if (lhs->accepted != rhs->accepted) {
    return false;
  }
  return true;
}

bool
mola_msgs__srv__RelocalizeNearPose_Response__copy(
  const mola_msgs__srv__RelocalizeNearPose_Response * input,
  mola_msgs__srv__RelocalizeNearPose_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // accepted
  output->accepted = input->accepted;
  return true;
}

mola_msgs__srv__RelocalizeNearPose_Response *
mola_msgs__srv__RelocalizeNearPose_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  mola_msgs__srv__RelocalizeNearPose_Response * msg = (mola_msgs__srv__RelocalizeNearPose_Response *)allocator.allocate(sizeof(mola_msgs__srv__RelocalizeNearPose_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(mola_msgs__srv__RelocalizeNearPose_Response));
  bool success = mola_msgs__srv__RelocalizeNearPose_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
mola_msgs__srv__RelocalizeNearPose_Response__destroy(mola_msgs__srv__RelocalizeNearPose_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    mola_msgs__srv__RelocalizeNearPose_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
mola_msgs__srv__RelocalizeNearPose_Response__Sequence__init(mola_msgs__srv__RelocalizeNearPose_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  mola_msgs__srv__RelocalizeNearPose_Response * data = NULL;

  if (size) {
    data = (mola_msgs__srv__RelocalizeNearPose_Response *)allocator.zero_allocate(size, sizeof(mola_msgs__srv__RelocalizeNearPose_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = mola_msgs__srv__RelocalizeNearPose_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        mola_msgs__srv__RelocalizeNearPose_Response__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
mola_msgs__srv__RelocalizeNearPose_Response__Sequence__fini(mola_msgs__srv__RelocalizeNearPose_Response__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      mola_msgs__srv__RelocalizeNearPose_Response__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

mola_msgs__srv__RelocalizeNearPose_Response__Sequence *
mola_msgs__srv__RelocalizeNearPose_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  mola_msgs__srv__RelocalizeNearPose_Response__Sequence * array = (mola_msgs__srv__RelocalizeNearPose_Response__Sequence *)allocator.allocate(sizeof(mola_msgs__srv__RelocalizeNearPose_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = mola_msgs__srv__RelocalizeNearPose_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
mola_msgs__srv__RelocalizeNearPose_Response__Sequence__destroy(mola_msgs__srv__RelocalizeNearPose_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    mola_msgs__srv__RelocalizeNearPose_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
mola_msgs__srv__RelocalizeNearPose_Response__Sequence__are_equal(const mola_msgs__srv__RelocalizeNearPose_Response__Sequence * lhs, const mola_msgs__srv__RelocalizeNearPose_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!mola_msgs__srv__RelocalizeNearPose_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
mola_msgs__srv__RelocalizeNearPose_Response__Sequence__copy(
  const mola_msgs__srv__RelocalizeNearPose_Response__Sequence * input,
  mola_msgs__srv__RelocalizeNearPose_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(mola_msgs__srv__RelocalizeNearPose_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    mola_msgs__srv__RelocalizeNearPose_Response * data =
      (mola_msgs__srv__RelocalizeNearPose_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!mola_msgs__srv__RelocalizeNearPose_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          mola_msgs__srv__RelocalizeNearPose_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!mola_msgs__srv__RelocalizeNearPose_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
