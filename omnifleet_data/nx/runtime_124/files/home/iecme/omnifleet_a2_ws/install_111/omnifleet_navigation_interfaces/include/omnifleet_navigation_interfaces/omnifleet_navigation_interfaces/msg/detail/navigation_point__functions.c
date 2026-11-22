// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from omnifleet_navigation_interfaces:msg/NavigationPoint.idl
// generated code does not contain a copyright notice
#include "omnifleet_navigation_interfaces/msg/detail/navigation_point__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `name`
#include "rosidl_runtime_c/string_functions.h"
// Member `pose`
#include "geometry_msgs/msg/detail/pose_stamped__functions.h"

bool
omnifleet_navigation_interfaces__msg__NavigationPoint__init(omnifleet_navigation_interfaces__msg__NavigationPoint * msg)
{
  if (!msg) {
    return false;
  }
  // name
  if (!rosidl_runtime_c__String__init(&msg->name)) {
    omnifleet_navigation_interfaces__msg__NavigationPoint__fini(msg);
    return false;
  }
  // pose
  if (!geometry_msgs__msg__PoseStamped__init(&msg->pose)) {
    omnifleet_navigation_interfaces__msg__NavigationPoint__fini(msg);
    return false;
  }
  // kind
  // dwell_seconds
  return true;
}

void
omnifleet_navigation_interfaces__msg__NavigationPoint__fini(omnifleet_navigation_interfaces__msg__NavigationPoint * msg)
{
  if (!msg) {
    return;
  }
  // name
  rosidl_runtime_c__String__fini(&msg->name);
  // pose
  geometry_msgs__msg__PoseStamped__fini(&msg->pose);
  // kind
  // dwell_seconds
}

bool
omnifleet_navigation_interfaces__msg__NavigationPoint__are_equal(const omnifleet_navigation_interfaces__msg__NavigationPoint * lhs, const omnifleet_navigation_interfaces__msg__NavigationPoint * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // name
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->name), &(rhs->name)))
  {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__PoseStamped__are_equal(
      &(lhs->pose), &(rhs->pose)))
  {
    return false;
  }
  // kind
  if (lhs->kind != rhs->kind) {
    return false;
  }
  // dwell_seconds
  if (lhs->dwell_seconds != rhs->dwell_seconds) {
    return false;
  }
  return true;
}

bool
omnifleet_navigation_interfaces__msg__NavigationPoint__copy(
  const omnifleet_navigation_interfaces__msg__NavigationPoint * input,
  omnifleet_navigation_interfaces__msg__NavigationPoint * output)
{
  if (!input || !output) {
    return false;
  }
  // name
  if (!rosidl_runtime_c__String__copy(
      &(input->name), &(output->name)))
  {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__PoseStamped__copy(
      &(input->pose), &(output->pose)))
  {
    return false;
  }
  // kind
  output->kind = input->kind;
  // dwell_seconds
  output->dwell_seconds = input->dwell_seconds;
  return true;
}

omnifleet_navigation_interfaces__msg__NavigationPoint *
omnifleet_navigation_interfaces__msg__NavigationPoint__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__msg__NavigationPoint * msg = (omnifleet_navigation_interfaces__msg__NavigationPoint *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__msg__NavigationPoint), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_navigation_interfaces__msg__NavigationPoint));
  bool success = omnifleet_navigation_interfaces__msg__NavigationPoint__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_navigation_interfaces__msg__NavigationPoint__destroy(omnifleet_navigation_interfaces__msg__NavigationPoint * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_navigation_interfaces__msg__NavigationPoint__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__init(omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__msg__NavigationPoint * data = NULL;

  if (size) {
    data = (omnifleet_navigation_interfaces__msg__NavigationPoint *)allocator.zero_allocate(size, sizeof(omnifleet_navigation_interfaces__msg__NavigationPoint), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_navigation_interfaces__msg__NavigationPoint__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_navigation_interfaces__msg__NavigationPoint__fini(&data[i - 1]);
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
omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__fini(omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * array)
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
      omnifleet_navigation_interfaces__msg__NavigationPoint__fini(&array->data[i]);
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

omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence *
omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * array = (omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence *)allocator.allocate(sizeof(omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__destroy(omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__are_equal(const omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * lhs, const omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_navigation_interfaces__msg__NavigationPoint__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__copy(
  const omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * input,
  omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_navigation_interfaces__msg__NavigationPoint);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_navigation_interfaces__msg__NavigationPoint * data =
      (omnifleet_navigation_interfaces__msg__NavigationPoint *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_navigation_interfaces__msg__NavigationPoint__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_navigation_interfaces__msg__NavigationPoint__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_navigation_interfaces__msg__NavigationPoint__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
