// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from omnifleet_interfaces:msg/MissionStatus.idl
// generated code does not contain a copyright notice
#include "omnifleet_interfaces/msg/detail/mission_status__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"
// Member `transaction_id`
// Member `state`
// Member `mission_id`
// Member `map_id`
// Member `message`
#include "rosidl_runtime_c/string_functions.h"

bool
omnifleet_interfaces__msg__MissionStatus__init(omnifleet_interfaces__msg__MissionStatus * msg)
{
  if (!msg) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    omnifleet_interfaces__msg__MissionStatus__fini(msg);
    return false;
  }
  // transaction_id
  if (!rosidl_runtime_c__String__init(&msg->transaction_id)) {
    omnifleet_interfaces__msg__MissionStatus__fini(msg);
    return false;
  }
  // state
  if (!rosidl_runtime_c__String__init(&msg->state)) {
    omnifleet_interfaces__msg__MissionStatus__fini(msg);
    return false;
  }
  // mission_id
  if (!rosidl_runtime_c__String__init(&msg->mission_id)) {
    omnifleet_interfaces__msg__MissionStatus__fini(msg);
    return false;
  }
  // revision
  // current_index
  // total
  // map_id
  if (!rosidl_runtime_c__String__init(&msg->map_id)) {
    omnifleet_interfaces__msg__MissionStatus__fini(msg);
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    omnifleet_interfaces__msg__MissionStatus__fini(msg);
    return false;
  }
  return true;
}

void
omnifleet_interfaces__msg__MissionStatus__fini(omnifleet_interfaces__msg__MissionStatus * msg)
{
  if (!msg) {
    return;
  }
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
  // transaction_id
  rosidl_runtime_c__String__fini(&msg->transaction_id);
  // state
  rosidl_runtime_c__String__fini(&msg->state);
  // mission_id
  rosidl_runtime_c__String__fini(&msg->mission_id);
  // revision
  // current_index
  // total
  // map_id
  rosidl_runtime_c__String__fini(&msg->map_id);
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
omnifleet_interfaces__msg__MissionStatus__are_equal(const omnifleet_interfaces__msg__MissionStatus * lhs, const omnifleet_interfaces__msg__MissionStatus * rhs)
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
  // transaction_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->transaction_id), &(rhs->transaction_id)))
  {
    return false;
  }
  // state
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->state), &(rhs->state)))
  {
    return false;
  }
  // mission_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->mission_id), &(rhs->mission_id)))
  {
    return false;
  }
  // revision
  if (lhs->revision != rhs->revision) {
    return false;
  }
  // current_index
  if (lhs->current_index != rhs->current_index) {
    return false;
  }
  // total
  if (lhs->total != rhs->total) {
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
omnifleet_interfaces__msg__MissionStatus__copy(
  const omnifleet_interfaces__msg__MissionStatus * input,
  omnifleet_interfaces__msg__MissionStatus * output)
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
  // transaction_id
  if (!rosidl_runtime_c__String__copy(
      &(input->transaction_id), &(output->transaction_id)))
  {
    return false;
  }
  // state
  if (!rosidl_runtime_c__String__copy(
      &(input->state), &(output->state)))
  {
    return false;
  }
  // mission_id
  if (!rosidl_runtime_c__String__copy(
      &(input->mission_id), &(output->mission_id)))
  {
    return false;
  }
  // revision
  output->revision = input->revision;
  // current_index
  output->current_index = input->current_index;
  // total
  output->total = input->total;
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

omnifleet_interfaces__msg__MissionStatus *
omnifleet_interfaces__msg__MissionStatus__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__msg__MissionStatus * msg = (omnifleet_interfaces__msg__MissionStatus *)allocator.allocate(sizeof(omnifleet_interfaces__msg__MissionStatus), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_interfaces__msg__MissionStatus));
  bool success = omnifleet_interfaces__msg__MissionStatus__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_interfaces__msg__MissionStatus__destroy(omnifleet_interfaces__msg__MissionStatus * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_interfaces__msg__MissionStatus__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_interfaces__msg__MissionStatus__Sequence__init(omnifleet_interfaces__msg__MissionStatus__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__msg__MissionStatus * data = NULL;

  if (size) {
    data = (omnifleet_interfaces__msg__MissionStatus *)allocator.zero_allocate(size, sizeof(omnifleet_interfaces__msg__MissionStatus), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_interfaces__msg__MissionStatus__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_interfaces__msg__MissionStatus__fini(&data[i - 1]);
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
omnifleet_interfaces__msg__MissionStatus__Sequence__fini(omnifleet_interfaces__msg__MissionStatus__Sequence * array)
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
      omnifleet_interfaces__msg__MissionStatus__fini(&array->data[i]);
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

omnifleet_interfaces__msg__MissionStatus__Sequence *
omnifleet_interfaces__msg__MissionStatus__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__msg__MissionStatus__Sequence * array = (omnifleet_interfaces__msg__MissionStatus__Sequence *)allocator.allocate(sizeof(omnifleet_interfaces__msg__MissionStatus__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_interfaces__msg__MissionStatus__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_interfaces__msg__MissionStatus__Sequence__destroy(omnifleet_interfaces__msg__MissionStatus__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_interfaces__msg__MissionStatus__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_interfaces__msg__MissionStatus__Sequence__are_equal(const omnifleet_interfaces__msg__MissionStatus__Sequence * lhs, const omnifleet_interfaces__msg__MissionStatus__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_interfaces__msg__MissionStatus__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_interfaces__msg__MissionStatus__Sequence__copy(
  const omnifleet_interfaces__msg__MissionStatus__Sequence * input,
  omnifleet_interfaces__msg__MissionStatus__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_interfaces__msg__MissionStatus);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_interfaces__msg__MissionStatus * data =
      (omnifleet_interfaces__msg__MissionStatus *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_interfaces__msg__MissionStatus__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_interfaces__msg__MissionStatus__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_interfaces__msg__MissionStatus__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
