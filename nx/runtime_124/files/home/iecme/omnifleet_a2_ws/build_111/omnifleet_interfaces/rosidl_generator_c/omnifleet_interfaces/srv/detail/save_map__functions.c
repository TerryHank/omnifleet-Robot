// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from omnifleet_interfaces:srv/SaveMap.idl
// generated code does not contain a copyright notice
#include "omnifleet_interfaces/srv/detail/save_map__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `label`
#include "rosidl_runtime_c/string_functions.h"

bool
omnifleet_interfaces__srv__SaveMap_Request__init(omnifleet_interfaces__srv__SaveMap_Request * msg)
{
  if (!msg) {
    return false;
  }
  // label
  if (!rosidl_runtime_c__String__init(&msg->label)) {
    omnifleet_interfaces__srv__SaveMap_Request__fini(msg);
    return false;
  }
  return true;
}

void
omnifleet_interfaces__srv__SaveMap_Request__fini(omnifleet_interfaces__srv__SaveMap_Request * msg)
{
  if (!msg) {
    return;
  }
  // label
  rosidl_runtime_c__String__fini(&msg->label);
}

bool
omnifleet_interfaces__srv__SaveMap_Request__are_equal(const omnifleet_interfaces__srv__SaveMap_Request * lhs, const omnifleet_interfaces__srv__SaveMap_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // label
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->label), &(rhs->label)))
  {
    return false;
  }
  return true;
}

bool
omnifleet_interfaces__srv__SaveMap_Request__copy(
  const omnifleet_interfaces__srv__SaveMap_Request * input,
  omnifleet_interfaces__srv__SaveMap_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // label
  if (!rosidl_runtime_c__String__copy(
      &(input->label), &(output->label)))
  {
    return false;
  }
  return true;
}

omnifleet_interfaces__srv__SaveMap_Request *
omnifleet_interfaces__srv__SaveMap_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__srv__SaveMap_Request * msg = (omnifleet_interfaces__srv__SaveMap_Request *)allocator.allocate(sizeof(omnifleet_interfaces__srv__SaveMap_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_interfaces__srv__SaveMap_Request));
  bool success = omnifleet_interfaces__srv__SaveMap_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_interfaces__srv__SaveMap_Request__destroy(omnifleet_interfaces__srv__SaveMap_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_interfaces__srv__SaveMap_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_interfaces__srv__SaveMap_Request__Sequence__init(omnifleet_interfaces__srv__SaveMap_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__srv__SaveMap_Request * data = NULL;

  if (size) {
    data = (omnifleet_interfaces__srv__SaveMap_Request *)allocator.zero_allocate(size, sizeof(omnifleet_interfaces__srv__SaveMap_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_interfaces__srv__SaveMap_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_interfaces__srv__SaveMap_Request__fini(&data[i - 1]);
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
omnifleet_interfaces__srv__SaveMap_Request__Sequence__fini(omnifleet_interfaces__srv__SaveMap_Request__Sequence * array)
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
      omnifleet_interfaces__srv__SaveMap_Request__fini(&array->data[i]);
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

omnifleet_interfaces__srv__SaveMap_Request__Sequence *
omnifleet_interfaces__srv__SaveMap_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__srv__SaveMap_Request__Sequence * array = (omnifleet_interfaces__srv__SaveMap_Request__Sequence *)allocator.allocate(sizeof(omnifleet_interfaces__srv__SaveMap_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_interfaces__srv__SaveMap_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_interfaces__srv__SaveMap_Request__Sequence__destroy(omnifleet_interfaces__srv__SaveMap_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_interfaces__srv__SaveMap_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_interfaces__srv__SaveMap_Request__Sequence__are_equal(const omnifleet_interfaces__srv__SaveMap_Request__Sequence * lhs, const omnifleet_interfaces__srv__SaveMap_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_interfaces__srv__SaveMap_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_interfaces__srv__SaveMap_Request__Sequence__copy(
  const omnifleet_interfaces__srv__SaveMap_Request__Sequence * input,
  omnifleet_interfaces__srv__SaveMap_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_interfaces__srv__SaveMap_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_interfaces__srv__SaveMap_Request * data =
      (omnifleet_interfaces__srv__SaveMap_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_interfaces__srv__SaveMap_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_interfaces__srv__SaveMap_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_interfaces__srv__SaveMap_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `map_id`
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

bool
omnifleet_interfaces__srv__SaveMap_Response__init(omnifleet_interfaces__srv__SaveMap_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // map_id
  if (!rosidl_runtime_c__String__init(&msg->map_id)) {
    omnifleet_interfaces__srv__SaveMap_Response__fini(msg);
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    omnifleet_interfaces__srv__SaveMap_Response__fini(msg);
    return false;
  }
  return true;
}

void
omnifleet_interfaces__srv__SaveMap_Response__fini(omnifleet_interfaces__srv__SaveMap_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
  // map_id
  rosidl_runtime_c__String__fini(&msg->map_id);
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
omnifleet_interfaces__srv__SaveMap_Response__are_equal(const omnifleet_interfaces__srv__SaveMap_Response * lhs, const omnifleet_interfaces__srv__SaveMap_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // map_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->map_id), &(rhs->map_id)))
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
omnifleet_interfaces__srv__SaveMap_Response__copy(
  const omnifleet_interfaces__srv__SaveMap_Response * input,
  omnifleet_interfaces__srv__SaveMap_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  // map_id
  if (!rosidl_runtime_c__String__copy(
      &(input->map_id), &(output->map_id)))
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

omnifleet_interfaces__srv__SaveMap_Response *
omnifleet_interfaces__srv__SaveMap_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__srv__SaveMap_Response * msg = (omnifleet_interfaces__srv__SaveMap_Response *)allocator.allocate(sizeof(omnifleet_interfaces__srv__SaveMap_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_interfaces__srv__SaveMap_Response));
  bool success = omnifleet_interfaces__srv__SaveMap_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_interfaces__srv__SaveMap_Response__destroy(omnifleet_interfaces__srv__SaveMap_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_interfaces__srv__SaveMap_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_interfaces__srv__SaveMap_Response__Sequence__init(omnifleet_interfaces__srv__SaveMap_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__srv__SaveMap_Response * data = NULL;

  if (size) {
    data = (omnifleet_interfaces__srv__SaveMap_Response *)allocator.zero_allocate(size, sizeof(omnifleet_interfaces__srv__SaveMap_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_interfaces__srv__SaveMap_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_interfaces__srv__SaveMap_Response__fini(&data[i - 1]);
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
omnifleet_interfaces__srv__SaveMap_Response__Sequence__fini(omnifleet_interfaces__srv__SaveMap_Response__Sequence * array)
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
      omnifleet_interfaces__srv__SaveMap_Response__fini(&array->data[i]);
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

omnifleet_interfaces__srv__SaveMap_Response__Sequence *
omnifleet_interfaces__srv__SaveMap_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__srv__SaveMap_Response__Sequence * array = (omnifleet_interfaces__srv__SaveMap_Response__Sequence *)allocator.allocate(sizeof(omnifleet_interfaces__srv__SaveMap_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_interfaces__srv__SaveMap_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_interfaces__srv__SaveMap_Response__Sequence__destroy(omnifleet_interfaces__srv__SaveMap_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_interfaces__srv__SaveMap_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_interfaces__srv__SaveMap_Response__Sequence__are_equal(const omnifleet_interfaces__srv__SaveMap_Response__Sequence * lhs, const omnifleet_interfaces__srv__SaveMap_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_interfaces__srv__SaveMap_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_interfaces__srv__SaveMap_Response__Sequence__copy(
  const omnifleet_interfaces__srv__SaveMap_Response__Sequence * input,
  omnifleet_interfaces__srv__SaveMap_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_interfaces__srv__SaveMap_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_interfaces__srv__SaveMap_Response * data =
      (omnifleet_interfaces__srv__SaveMap_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_interfaces__srv__SaveMap_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_interfaces__srv__SaveMap_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_interfaces__srv__SaveMap_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
