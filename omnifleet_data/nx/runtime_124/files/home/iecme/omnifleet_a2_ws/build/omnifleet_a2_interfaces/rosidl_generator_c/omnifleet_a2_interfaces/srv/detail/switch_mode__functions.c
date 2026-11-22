// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from omnifleet_a2_interfaces:srv/SwitchMode.idl
// generated code does not contain a copyright notice
#include "omnifleet_a2_interfaces/srv/detail/switch_mode__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `mode`
// Member `operation`
// Member `map_id`
#include "rosidl_runtime_c/string_functions.h"

bool
omnifleet_a2_interfaces__srv__SwitchMode_Request__init(omnifleet_a2_interfaces__srv__SwitchMode_Request * msg)
{
  if (!msg) {
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__init(&msg->mode)) {
    omnifleet_a2_interfaces__srv__SwitchMode_Request__fini(msg);
    return false;
  }
  // operation
  if (!rosidl_runtime_c__String__init(&msg->operation)) {
    omnifleet_a2_interfaces__srv__SwitchMode_Request__fini(msg);
    return false;
  }
  // map_id
  if (!rosidl_runtime_c__String__init(&msg->map_id)) {
    omnifleet_a2_interfaces__srv__SwitchMode_Request__fini(msg);
    return false;
  }
  return true;
}

void
omnifleet_a2_interfaces__srv__SwitchMode_Request__fini(omnifleet_a2_interfaces__srv__SwitchMode_Request * msg)
{
  if (!msg) {
    return;
  }
  // mode
  rosidl_runtime_c__String__fini(&msg->mode);
  // operation
  rosidl_runtime_c__String__fini(&msg->operation);
  // map_id
  rosidl_runtime_c__String__fini(&msg->map_id);
}

bool
omnifleet_a2_interfaces__srv__SwitchMode_Request__are_equal(const omnifleet_a2_interfaces__srv__SwitchMode_Request * lhs, const omnifleet_a2_interfaces__srv__SwitchMode_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->mode), &(rhs->mode)))
  {
    return false;
  }
  // operation
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->operation), &(rhs->operation)))
  {
    return false;
  }
  // map_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->map_id), &(rhs->map_id)))
  {
    return false;
  }
  return true;
}

bool
omnifleet_a2_interfaces__srv__SwitchMode_Request__copy(
  const omnifleet_a2_interfaces__srv__SwitchMode_Request * input,
  omnifleet_a2_interfaces__srv__SwitchMode_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__copy(
      &(input->mode), &(output->mode)))
  {
    return false;
  }
  // operation
  if (!rosidl_runtime_c__String__copy(
      &(input->operation), &(output->operation)))
  {
    return false;
  }
  // map_id
  if (!rosidl_runtime_c__String__copy(
      &(input->map_id), &(output->map_id)))
  {
    return false;
  }
  return true;
}

omnifleet_a2_interfaces__srv__SwitchMode_Request *
omnifleet_a2_interfaces__srv__SwitchMode_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_a2_interfaces__srv__SwitchMode_Request * msg = (omnifleet_a2_interfaces__srv__SwitchMode_Request *)allocator.allocate(sizeof(omnifleet_a2_interfaces__srv__SwitchMode_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_a2_interfaces__srv__SwitchMode_Request));
  bool success = omnifleet_a2_interfaces__srv__SwitchMode_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_a2_interfaces__srv__SwitchMode_Request__destroy(omnifleet_a2_interfaces__srv__SwitchMode_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_a2_interfaces__srv__SwitchMode_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence__init(omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_a2_interfaces__srv__SwitchMode_Request * data = NULL;

  if (size) {
    data = (omnifleet_a2_interfaces__srv__SwitchMode_Request *)allocator.zero_allocate(size, sizeof(omnifleet_a2_interfaces__srv__SwitchMode_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_a2_interfaces__srv__SwitchMode_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_a2_interfaces__srv__SwitchMode_Request__fini(&data[i - 1]);
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
omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence__fini(omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence * array)
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
      omnifleet_a2_interfaces__srv__SwitchMode_Request__fini(&array->data[i]);
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

omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence *
omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence * array = (omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence *)allocator.allocate(sizeof(omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence__destroy(omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence__are_equal(const omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence * lhs, const omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_a2_interfaces__srv__SwitchMode_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence__copy(
  const omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence * input,
  omnifleet_a2_interfaces__srv__SwitchMode_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_a2_interfaces__srv__SwitchMode_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_a2_interfaces__srv__SwitchMode_Request * data =
      (omnifleet_a2_interfaces__srv__SwitchMode_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_a2_interfaces__srv__SwitchMode_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_a2_interfaces__srv__SwitchMode_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_a2_interfaces__srv__SwitchMode_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `transaction_id`
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

bool
omnifleet_a2_interfaces__srv__SwitchMode_Response__init(omnifleet_a2_interfaces__srv__SwitchMode_Response * msg)
{
  if (!msg) {
    return false;
  }
  // accepted
  // transaction_id
  if (!rosidl_runtime_c__String__init(&msg->transaction_id)) {
    omnifleet_a2_interfaces__srv__SwitchMode_Response__fini(msg);
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    omnifleet_a2_interfaces__srv__SwitchMode_Response__fini(msg);
    return false;
  }
  return true;
}

void
omnifleet_a2_interfaces__srv__SwitchMode_Response__fini(omnifleet_a2_interfaces__srv__SwitchMode_Response * msg)
{
  if (!msg) {
    return;
  }
  // accepted
  // transaction_id
  rosidl_runtime_c__String__fini(&msg->transaction_id);
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
omnifleet_a2_interfaces__srv__SwitchMode_Response__are_equal(const omnifleet_a2_interfaces__srv__SwitchMode_Response * lhs, const omnifleet_a2_interfaces__srv__SwitchMode_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // accepted
  if (lhs->accepted != rhs->accepted) {
    return false;
  }
  // transaction_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->transaction_id), &(rhs->transaction_id)))
  {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->message), &(rhs->message)))
  {
    return false;
  }
  return true;
}

bool
omnifleet_a2_interfaces__srv__SwitchMode_Response__copy(
  const omnifleet_a2_interfaces__srv__SwitchMode_Response * input,
  omnifleet_a2_interfaces__srv__SwitchMode_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // accepted
  output->accepted = input->accepted;
  // transaction_id
  if (!rosidl_runtime_c__String__copy(
      &(input->transaction_id), &(output->transaction_id)))
  {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  return true;
}

omnifleet_a2_interfaces__srv__SwitchMode_Response *
omnifleet_a2_interfaces__srv__SwitchMode_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_a2_interfaces__srv__SwitchMode_Response * msg = (omnifleet_a2_interfaces__srv__SwitchMode_Response *)allocator.allocate(sizeof(omnifleet_a2_interfaces__srv__SwitchMode_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_a2_interfaces__srv__SwitchMode_Response));
  bool success = omnifleet_a2_interfaces__srv__SwitchMode_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_a2_interfaces__srv__SwitchMode_Response__destroy(omnifleet_a2_interfaces__srv__SwitchMode_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_a2_interfaces__srv__SwitchMode_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence__init(omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_a2_interfaces__srv__SwitchMode_Response * data = NULL;

  if (size) {
    data = (omnifleet_a2_interfaces__srv__SwitchMode_Response *)allocator.zero_allocate(size, sizeof(omnifleet_a2_interfaces__srv__SwitchMode_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_a2_interfaces__srv__SwitchMode_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_a2_interfaces__srv__SwitchMode_Response__fini(&data[i - 1]);
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
omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence__fini(omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence * array)
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
      omnifleet_a2_interfaces__srv__SwitchMode_Response__fini(&array->data[i]);
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

omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence *
omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence * array = (omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence *)allocator.allocate(sizeof(omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence__destroy(omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence__are_equal(const omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence * lhs, const omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_a2_interfaces__srv__SwitchMode_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence__copy(
  const omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence * input,
  omnifleet_a2_interfaces__srv__SwitchMode_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_a2_interfaces__srv__SwitchMode_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_a2_interfaces__srv__SwitchMode_Response * data =
      (omnifleet_a2_interfaces__srv__SwitchMode_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_a2_interfaces__srv__SwitchMode_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_a2_interfaces__srv__SwitchMode_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_a2_interfaces__srv__SwitchMode_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
