// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from omnifleet_a2_interfaces:msg/SlamStatus.idl
// generated code does not contain a copyright notice
#include "omnifleet_a2_interfaces/msg/detail/slam_status__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"
// Member `state`
// Member `mode`
// Member `operation`
// Member `map_id`
// Member `transaction_id`
// Member `message`
#include "rosidl_runtime_c/string_functions.h"

bool
omnifleet_a2_interfaces__msg__SlamStatus__init(omnifleet_a2_interfaces__msg__SlamStatus * msg)
{
  if (!msg) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    omnifleet_a2_interfaces__msg__SlamStatus__fini(msg);
    return false;
  }
  // state
  if (!rosidl_runtime_c__String__init(&msg->state)) {
    omnifleet_a2_interfaces__msg__SlamStatus__fini(msg);
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__init(&msg->mode)) {
    omnifleet_a2_interfaces__msg__SlamStatus__fini(msg);
    return false;
  }
  // operation
  if (!rosidl_runtime_c__String__init(&msg->operation)) {
    omnifleet_a2_interfaces__msg__SlamStatus__fini(msg);
    return false;
  }
  // map_id
  if (!rosidl_runtime_c__String__init(&msg->map_id)) {
    omnifleet_a2_interfaces__msg__SlamStatus__fini(msg);
    return false;
  }
  // transaction_id
  if (!rosidl_runtime_c__String__init(&msg->transaction_id)) {
    omnifleet_a2_interfaces__msg__SlamStatus__fini(msg);
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    omnifleet_a2_interfaces__msg__SlamStatus__fini(msg);
    return false;
  }
  return true;
}

void
omnifleet_a2_interfaces__msg__SlamStatus__fini(omnifleet_a2_interfaces__msg__SlamStatus * msg)
{
  if (!msg) {
    return;
  }
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
  // state
  rosidl_runtime_c__String__fini(&msg->state);
  // mode
  rosidl_runtime_c__String__fini(&msg->mode);
  // operation
  rosidl_runtime_c__String__fini(&msg->operation);
  // map_id
  rosidl_runtime_c__String__fini(&msg->map_id);
  // transaction_id
  rosidl_runtime_c__String__fini(&msg->transaction_id);
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
omnifleet_a2_interfaces__msg__SlamStatus__are_equal(const omnifleet_a2_interfaces__msg__SlamStatus * lhs, const omnifleet_a2_interfaces__msg__SlamStatus * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->stamp), &(rhs->stamp)))
  {
    return false;
  }
  // state
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->state), &(rhs->state)))
  {
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
omnifleet_a2_interfaces__msg__SlamStatus__copy(
  const omnifleet_a2_interfaces__msg__SlamStatus * input,
  omnifleet_a2_interfaces__msg__SlamStatus * output)
{
  if (!input || !output) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__copy(
      &(input->stamp), &(output->stamp)))
  {
    return false;
  }
  // state
  if (!rosidl_runtime_c__String__copy(
      &(input->state), &(output->state)))
  {
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

omnifleet_a2_interfaces__msg__SlamStatus *
omnifleet_a2_interfaces__msg__SlamStatus__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_a2_interfaces__msg__SlamStatus * msg = (omnifleet_a2_interfaces__msg__SlamStatus *)allocator.allocate(sizeof(omnifleet_a2_interfaces__msg__SlamStatus), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_a2_interfaces__msg__SlamStatus));
  bool success = omnifleet_a2_interfaces__msg__SlamStatus__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_a2_interfaces__msg__SlamStatus__destroy(omnifleet_a2_interfaces__msg__SlamStatus * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_a2_interfaces__msg__SlamStatus__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_a2_interfaces__msg__SlamStatus__Sequence__init(omnifleet_a2_interfaces__msg__SlamStatus__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_a2_interfaces__msg__SlamStatus * data = NULL;

  if (size) {
    data = (omnifleet_a2_interfaces__msg__SlamStatus *)allocator.zero_allocate(size, sizeof(omnifleet_a2_interfaces__msg__SlamStatus), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_a2_interfaces__msg__SlamStatus__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_a2_interfaces__msg__SlamStatus__fini(&data[i - 1]);
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
omnifleet_a2_interfaces__msg__SlamStatus__Sequence__fini(omnifleet_a2_interfaces__msg__SlamStatus__Sequence * array)
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
      omnifleet_a2_interfaces__msg__SlamStatus__fini(&array->data[i]);
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

omnifleet_a2_interfaces__msg__SlamStatus__Sequence *
omnifleet_a2_interfaces__msg__SlamStatus__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_a2_interfaces__msg__SlamStatus__Sequence * array = (omnifleet_a2_interfaces__msg__SlamStatus__Sequence *)allocator.allocate(sizeof(omnifleet_a2_interfaces__msg__SlamStatus__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_a2_interfaces__msg__SlamStatus__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_a2_interfaces__msg__SlamStatus__Sequence__destroy(omnifleet_a2_interfaces__msg__SlamStatus__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_a2_interfaces__msg__SlamStatus__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_a2_interfaces__msg__SlamStatus__Sequence__are_equal(const omnifleet_a2_interfaces__msg__SlamStatus__Sequence * lhs, const omnifleet_a2_interfaces__msg__SlamStatus__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_a2_interfaces__msg__SlamStatus__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_a2_interfaces__msg__SlamStatus__Sequence__copy(
  const omnifleet_a2_interfaces__msg__SlamStatus__Sequence * input,
  omnifleet_a2_interfaces__msg__SlamStatus__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_a2_interfaces__msg__SlamStatus);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_a2_interfaces__msg__SlamStatus * data =
      (omnifleet_a2_interfaces__msg__SlamStatus *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_a2_interfaces__msg__SlamStatus__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_a2_interfaces__msg__SlamStatus__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_a2_interfaces__msg__SlamStatus__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
