// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from mola_msgs:srv/MapLoad.idl
// generated code does not contain a copyright notice
#include "mola_msgs/srv/detail/map_load__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `map_path`
#include "rosidl_runtime_c/string_functions.h"

bool
mola_msgs__srv__MapLoad_Request__init(mola_msgs__srv__MapLoad_Request * msg)
{
  if (!msg) {
    return false;
  }
  // map_path
  if (!rosidl_runtime_c__String__init(&msg->map_path)) {
    mola_msgs__srv__MapLoad_Request__fini(msg);
    return false;
  }
  return true;
}

void
mola_msgs__srv__MapLoad_Request__fini(mola_msgs__srv__MapLoad_Request * msg)
{
  if (!msg) {
    return;
  }
  // map_path
  rosidl_runtime_c__String__fini(&msg->map_path);
}

bool
mola_msgs__srv__MapLoad_Request__are_equal(const mola_msgs__srv__MapLoad_Request * lhs, const mola_msgs__srv__MapLoad_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // map_path
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->map_path), &(rhs->map_path)))
  {
    return false;
  }
  return true;
}

bool
mola_msgs__srv__MapLoad_Request__copy(
  const mola_msgs__srv__MapLoad_Request * input,
  mola_msgs__srv__MapLoad_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // map_path
  if (!rosidl_runtime_c__String__copy(
      &(input->map_path), &(output->map_path)))
  {
    return false;
  }
  return true;
}

mola_msgs__srv__MapLoad_Request *
mola_msgs__srv__MapLoad_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  mola_msgs__srv__MapLoad_Request * msg = (mola_msgs__srv__MapLoad_Request *)allocator.allocate(sizeof(mola_msgs__srv__MapLoad_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(mola_msgs__srv__MapLoad_Request));
  bool success = mola_msgs__srv__MapLoad_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
mola_msgs__srv__MapLoad_Request__destroy(mola_msgs__srv__MapLoad_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    mola_msgs__srv__MapLoad_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
mola_msgs__srv__MapLoad_Request__Sequence__init(mola_msgs__srv__MapLoad_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  mola_msgs__srv__MapLoad_Request * data = NULL;

  if (size) {
    data = (mola_msgs__srv__MapLoad_Request *)allocator.zero_allocate(size, sizeof(mola_msgs__srv__MapLoad_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = mola_msgs__srv__MapLoad_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        mola_msgs__srv__MapLoad_Request__fini(&data[i - 1]);
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
mola_msgs__srv__MapLoad_Request__Sequence__fini(mola_msgs__srv__MapLoad_Request__Sequence * array)
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
      mola_msgs__srv__MapLoad_Request__fini(&array->data[i]);
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

mola_msgs__srv__MapLoad_Request__Sequence *
mola_msgs__srv__MapLoad_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  mola_msgs__srv__MapLoad_Request__Sequence * array = (mola_msgs__srv__MapLoad_Request__Sequence *)allocator.allocate(sizeof(mola_msgs__srv__MapLoad_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = mola_msgs__srv__MapLoad_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
mola_msgs__srv__MapLoad_Request__Sequence__destroy(mola_msgs__srv__MapLoad_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    mola_msgs__srv__MapLoad_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
mola_msgs__srv__MapLoad_Request__Sequence__are_equal(const mola_msgs__srv__MapLoad_Request__Sequence * lhs, const mola_msgs__srv__MapLoad_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!mola_msgs__srv__MapLoad_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
mola_msgs__srv__MapLoad_Request__Sequence__copy(
  const mola_msgs__srv__MapLoad_Request__Sequence * input,
  mola_msgs__srv__MapLoad_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(mola_msgs__srv__MapLoad_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    mola_msgs__srv__MapLoad_Request * data =
      (mola_msgs__srv__MapLoad_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!mola_msgs__srv__MapLoad_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          mola_msgs__srv__MapLoad_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!mola_msgs__srv__MapLoad_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `error_message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

bool
mola_msgs__srv__MapLoad_Response__init(mola_msgs__srv__MapLoad_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // error_message
  if (!rosidl_runtime_c__String__init(&msg->error_message)) {
    mola_msgs__srv__MapLoad_Response__fini(msg);
    return false;
  }
  return true;
}

void
mola_msgs__srv__MapLoad_Response__fini(mola_msgs__srv__MapLoad_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
  // error_message
  rosidl_runtime_c__String__fini(&msg->error_message);
}

bool
mola_msgs__srv__MapLoad_Response__are_equal(const mola_msgs__srv__MapLoad_Response * lhs, const mola_msgs__srv__MapLoad_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // error_message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->error_message), &(rhs->error_message)))
  {
    return false;
  }
  return true;
}

bool
mola_msgs__srv__MapLoad_Response__copy(
  const mola_msgs__srv__MapLoad_Response * input,
  mola_msgs__srv__MapLoad_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  // error_message
  if (!rosidl_runtime_c__String__copy(
      &(input->error_message), &(output->error_message)))
  {
    return false;
  }
  return true;
}

mola_msgs__srv__MapLoad_Response *
mola_msgs__srv__MapLoad_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  mola_msgs__srv__MapLoad_Response * msg = (mola_msgs__srv__MapLoad_Response *)allocator.allocate(sizeof(mola_msgs__srv__MapLoad_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(mola_msgs__srv__MapLoad_Response));
  bool success = mola_msgs__srv__MapLoad_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
mola_msgs__srv__MapLoad_Response__destroy(mola_msgs__srv__MapLoad_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    mola_msgs__srv__MapLoad_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
mola_msgs__srv__MapLoad_Response__Sequence__init(mola_msgs__srv__MapLoad_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  mola_msgs__srv__MapLoad_Response * data = NULL;

  if (size) {
    data = (mola_msgs__srv__MapLoad_Response *)allocator.zero_allocate(size, sizeof(mola_msgs__srv__MapLoad_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = mola_msgs__srv__MapLoad_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        mola_msgs__srv__MapLoad_Response__fini(&data[i - 1]);
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
mola_msgs__srv__MapLoad_Response__Sequence__fini(mola_msgs__srv__MapLoad_Response__Sequence * array)
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
      mola_msgs__srv__MapLoad_Response__fini(&array->data[i]);
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

mola_msgs__srv__MapLoad_Response__Sequence *
mola_msgs__srv__MapLoad_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  mola_msgs__srv__MapLoad_Response__Sequence * array = (mola_msgs__srv__MapLoad_Response__Sequence *)allocator.allocate(sizeof(mola_msgs__srv__MapLoad_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = mola_msgs__srv__MapLoad_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
mola_msgs__srv__MapLoad_Response__Sequence__destroy(mola_msgs__srv__MapLoad_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    mola_msgs__srv__MapLoad_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
mola_msgs__srv__MapLoad_Response__Sequence__are_equal(const mola_msgs__srv__MapLoad_Response__Sequence * lhs, const mola_msgs__srv__MapLoad_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!mola_msgs__srv__MapLoad_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
mola_msgs__srv__MapLoad_Response__Sequence__copy(
  const mola_msgs__srv__MapLoad_Response__Sequence * input,
  mola_msgs__srv__MapLoad_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(mola_msgs__srv__MapLoad_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    mola_msgs__srv__MapLoad_Response * data =
      (mola_msgs__srv__MapLoad_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!mola_msgs__srv__MapLoad_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          mola_msgs__srv__MapLoad_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!mola_msgs__srv__MapLoad_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
