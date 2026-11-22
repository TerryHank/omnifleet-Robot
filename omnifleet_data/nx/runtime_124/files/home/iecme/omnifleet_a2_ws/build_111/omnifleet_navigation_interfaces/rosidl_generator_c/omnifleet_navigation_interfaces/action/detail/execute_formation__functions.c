// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from omnifleet_navigation_interfaces:action/ExecuteFormation.idl
// generated code does not contain a copyright notice
#include "omnifleet_navigation_interfaces/action/detail/execute_formation__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `task_id`
// Member `command_epoch`
#include "rosidl_runtime_c/string_functions.h"
// Member `waypoints`
#include "omnifleet_navigation_interfaces/msg/detail/navigation_point__functions.h"

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__init(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * msg)
{
  if (!msg) {
    return false;
  }
  // task_id
  if (!rosidl_runtime_c__String__init(&msg->task_id)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__fini(msg);
    return false;
  }
  // command_epoch
  if (!rosidl_runtime_c__String__init(&msg->command_epoch)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__fini(msg);
    return false;
  }
  // revision
  // waypoints
  if (!omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__init(&msg->waypoints, 0)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__fini(msg);
    return false;
  }
  // pass_radius
  msg->pass_radius = 0.25f;
  return true;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * msg)
{
  if (!msg) {
    return;
  }
  // task_id
  rosidl_runtime_c__String__fini(&msg->task_id);
  // command_epoch
  rosidl_runtime_c__String__fini(&msg->command_epoch);
  // revision
  // waypoints
  omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__fini(&msg->waypoints);
  // pass_radius
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // task_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->task_id), &(rhs->task_id)))
  {
    return false;
  }
  // command_epoch
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->command_epoch), &(rhs->command_epoch)))
  {
    return false;
  }
  // revision
  if (lhs->revision != rhs->revision) {
    return false;
  }
  // waypoints
  if (!omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__are_equal(
      &(lhs->waypoints), &(rhs->waypoints)))
  {
    return false;
  }
  // pass_radius
  if (lhs->pass_radius != rhs->pass_radius) {
    return false;
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * output)
{
  if (!input || !output) {
    return false;
  }
  // task_id
  if (!rosidl_runtime_c__String__copy(
      &(input->task_id), &(output->task_id)))
  {
    return false;
  }
  // command_epoch
  if (!rosidl_runtime_c__String__copy(
      &(input->command_epoch), &(output->command_epoch)))
  {
    return false;
  }
  // revision
  output->revision = input->revision;
  // waypoints
  if (!omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__copy(
      &(input->waypoints), &(output->waypoints)))
  {
    return false;
  }
  // pass_radius
  output->pass_radius = input->pass_radius;
  return true;
}

omnifleet_navigation_interfaces__action__ExecuteFormation_Goal *
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * msg = (omnifleet_navigation_interfaces__action__ExecuteFormation_Goal *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal));
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * data = NULL;

  if (size) {
    data = (omnifleet_navigation_interfaces__action__ExecuteFormation_Goal *)allocator.zero_allocate(size, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__fini(&data[i - 1]);
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
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * array)
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
      omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__fini(&array->data[i]);
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

omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * array = (omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * data =
      (omnifleet_navigation_interfaces__action__ExecuteFormation_Goal *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `code`
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__init(omnifleet_navigation_interfaces__action__ExecuteFormation_Result * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // code
  if (!rosidl_runtime_c__String__init(&msg->code)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Result__fini(msg);
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Result__fini(msg);
    return false;
  }
  return true;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_Result * msg)
{
  if (!msg) {
    return;
  }
  // success
  // code
  rosidl_runtime_c__String__fini(&msg->code);
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_Result * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_Result * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // code
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->code), &(rhs->code)))
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
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_Result * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_Result * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  // code
  if (!rosidl_runtime_c__String__copy(
      &(input->code), &(output->code)))
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

omnifleet_navigation_interfaces__action__ExecuteFormation_Result *
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_Result * msg = (omnifleet_navigation_interfaces__action__ExecuteFormation_Result *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Result), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Result));
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_Result__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_Result * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Result__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_Result * data = NULL;

  if (size) {
    data = (omnifleet_navigation_interfaces__action__ExecuteFormation_Result *)allocator.zero_allocate(size, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Result), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_Result__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_navigation_interfaces__action__ExecuteFormation_Result__fini(&data[i - 1]);
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
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * array)
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
      omnifleet_navigation_interfaces__action__ExecuteFormation_Result__fini(&array->data[i]);
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

omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * array = (omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Result__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Result);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_navigation_interfaces__action__ExecuteFormation_Result * data =
      (omnifleet_navigation_interfaces__action__ExecuteFormation_Result *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Result__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_navigation_interfaces__action__ExecuteFormation_Result__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Result__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `task_id`
// Member `phase`
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__init(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * msg)
{
  if (!msg) {
    return false;
  }
  // task_id
  if (!rosidl_runtime_c__String__init(&msg->task_id)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__fini(msg);
    return false;
  }
  // phase
  if (!rosidl_runtime_c__String__init(&msg->phase)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__fini(msg);
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__fini(msg);
    return false;
  }
  // passed_points
  // tf_age_ms
  return true;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * msg)
{
  if (!msg) {
    return;
  }
  // task_id
  rosidl_runtime_c__String__fini(&msg->task_id);
  // phase
  rosidl_runtime_c__String__fini(&msg->phase);
  // message
  rosidl_runtime_c__String__fini(&msg->message);
  // passed_points
  // tf_age_ms
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // task_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->task_id), &(rhs->task_id)))
  {
    return false;
  }
  // phase
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->phase), &(rhs->phase)))
  {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->message), &(rhs->message)))
  {
    return false;
  }
  // passed_points
  if (lhs->passed_points != rhs->passed_points) {
    return false;
  }
  // tf_age_ms
  if (lhs->tf_age_ms != rhs->tf_age_ms) {
    return false;
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * output)
{
  if (!input || !output) {
    return false;
  }
  // task_id
  if (!rosidl_runtime_c__String__copy(
      &(input->task_id), &(output->task_id)))
  {
    return false;
  }
  // phase
  if (!rosidl_runtime_c__String__copy(
      &(input->phase), &(output->phase)))
  {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  // passed_points
  output->passed_points = input->passed_points;
  // tf_age_ms
  output->tf_age_ms = input->tf_age_ms;
  return true;
}

omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback *
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * msg = (omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback));
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * data = NULL;

  if (size) {
    data = (omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback *)allocator.zero_allocate(size, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__fini(&data[i - 1]);
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
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * array)
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
      omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__fini(&array->data[i]);
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

omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * array = (omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * data =
      (omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `goal_id`
#include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `goal`
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__functions.h"

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__init(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * msg)
{
  if (!msg) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__init(&msg->goal_id)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__fini(msg);
    return false;
  }
  // goal
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__init(&msg->goal)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__fini(msg);
    return false;
  }
  return true;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * msg)
{
  if (!msg) {
    return;
  }
  // goal_id
  unique_identifier_msgs__msg__UUID__fini(&msg->goal_id);
  // goal
  omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__fini(&msg->goal);
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->goal_id), &(rhs->goal_id)))
  {
    return false;
  }
  // goal
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__are_equal(
      &(lhs->goal), &(rhs->goal)))
  {
    return false;
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->goal_id), &(output->goal_id)))
  {
    return false;
  }
  // goal
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__copy(
      &(input->goal), &(output->goal)))
  {
    return false;
  }
  return true;
}

omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request *
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * msg = (omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request));
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * data = NULL;

  if (size) {
    data = (omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request *)allocator.zero_allocate(size, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__fini(&data[i - 1]);
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
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * array)
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
      omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__fini(&array->data[i]);
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

omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * array = (omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * data =
      (omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__init(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * msg)
{
  if (!msg) {
    return false;
  }
  // accepted
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__fini(msg);
    return false;
  }
  return true;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * msg)
{
  if (!msg) {
    return;
  }
  // accepted
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // accepted
  if (lhs->accepted != rhs->accepted) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->stamp), &(rhs->stamp)))
  {
    return false;
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // accepted
  output->accepted = input->accepted;
  // stamp
  if (!builtin_interfaces__msg__Time__copy(
      &(input->stamp), &(output->stamp)))
  {
    return false;
  }
  return true;
}

omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response *
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * msg = (omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response));
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * data = NULL;

  if (size) {
    data = (omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response *)allocator.zero_allocate(size, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__fini(&data[i - 1]);
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
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * array)
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
      omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__fini(&array->data[i]);
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

omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * array = (omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * data =
      (omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__functions.h"

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__init(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * msg)
{
  if (!msg) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__init(&msg->goal_id)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__fini(msg);
    return false;
  }
  return true;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * msg)
{
  if (!msg) {
    return;
  }
  // goal_id
  unique_identifier_msgs__msg__UUID__fini(&msg->goal_id);
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->goal_id), &(rhs->goal_id)))
  {
    return false;
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->goal_id), &(output->goal_id)))
  {
    return false;
  }
  return true;
}

omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request *
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * msg = (omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request));
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * data = NULL;

  if (size) {
    data = (omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request *)allocator.zero_allocate(size, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__fini(&data[i - 1]);
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
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * array)
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
      omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__fini(&array->data[i]);
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

omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * array = (omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * data =
      (omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `result`
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__functions.h"

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__init(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * msg)
{
  if (!msg) {
    return false;
  }
  // status
  // result
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Result__init(&msg->result)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__fini(msg);
    return false;
  }
  return true;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * msg)
{
  if (!msg) {
    return;
  }
  // status
  // result
  omnifleet_navigation_interfaces__action__ExecuteFormation_Result__fini(&msg->result);
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // status
  if (lhs->status != rhs->status) {
    return false;
  }
  // result
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Result__are_equal(
      &(lhs->result), &(rhs->result)))
  {
    return false;
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // status
  output->status = input->status;
  // result
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Result__copy(
      &(input->result), &(output->result)))
  {
    return false;
  }
  return true;
}

omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response *
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * msg = (omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response));
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * data = NULL;

  if (size) {
    data = (omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response *)allocator.zero_allocate(size, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__fini(&data[i - 1]);
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
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * array)
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
      omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__fini(&array->data[i]);
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

omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * array = (omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * data =
      (omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `feedback`
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__functions.h"

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__init(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * msg)
{
  if (!msg) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__init(&msg->goal_id)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__fini(msg);
    return false;
  }
  // feedback
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__init(&msg->feedback)) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__fini(msg);
    return false;
  }
  return true;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * msg)
{
  if (!msg) {
    return;
  }
  // goal_id
  unique_identifier_msgs__msg__UUID__fini(&msg->goal_id);
  // feedback
  omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__fini(&msg->feedback);
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->goal_id), &(rhs->goal_id)))
  {
    return false;
  }
  // feedback
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__are_equal(
      &(lhs->feedback), &(rhs->feedback)))
  {
    return false;
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * output)
{
  if (!input || !output) {
    return false;
  }
  // goal_id
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->goal_id), &(output->goal_id)))
  {
    return false;
  }
  // feedback
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__copy(
      &(input->feedback), &(output->feedback)))
  {
    return false;
  }
  return true;
}

omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage *
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * msg = (omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage));
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * data = NULL;

  if (size) {
    data = (omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage *)allocator.zero_allocate(size, sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__fini(&data[i - 1]);
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
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * array)
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
      omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__fini(&array->data[i]);
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

omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * array = (omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * data =
      (omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
