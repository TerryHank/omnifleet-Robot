// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from omnifleet_a2_interfaces:msg/SteeringAngleCommand.idl
// generated code does not contain a copyright notice
#include "omnifleet_a2_interfaces/msg/detail/steering_angle_command__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
omnifleet_a2_interfaces__msg__SteeringAngleCommand__init(omnifleet_a2_interfaces__msg__SteeringAngleCommand * msg)
{
  if (!msg) {
    return false;
  }
  // steering_angle_rad
  return true;
}

void
omnifleet_a2_interfaces__msg__SteeringAngleCommand__fini(omnifleet_a2_interfaces__msg__SteeringAngleCommand * msg)
{
  if (!msg) {
    return;
  }
  // steering_angle_rad
}

bool
omnifleet_a2_interfaces__msg__SteeringAngleCommand__are_equal(const omnifleet_a2_interfaces__msg__SteeringAngleCommand * lhs, const omnifleet_a2_interfaces__msg__SteeringAngleCommand * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // steering_angle_rad
  if (lhs->steering_angle_rad != rhs->steering_angle_rad) {
    return false;
  }
  return true;
}

bool
omnifleet_a2_interfaces__msg__SteeringAngleCommand__copy(
  const omnifleet_a2_interfaces__msg__SteeringAngleCommand * input,
  omnifleet_a2_interfaces__msg__SteeringAngleCommand * output)
{
  if (!input || !output) {
    return false;
  }
  // steering_angle_rad
  output->steering_angle_rad = input->steering_angle_rad;
  return true;
}

omnifleet_a2_interfaces__msg__SteeringAngleCommand *
omnifleet_a2_interfaces__msg__SteeringAngleCommand__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_a2_interfaces__msg__SteeringAngleCommand * msg = (omnifleet_a2_interfaces__msg__SteeringAngleCommand *)allocator.allocate(sizeof(omnifleet_a2_interfaces__msg__SteeringAngleCommand), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_a2_interfaces__msg__SteeringAngleCommand));
  bool success = omnifleet_a2_interfaces__msg__SteeringAngleCommand__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_a2_interfaces__msg__SteeringAngleCommand__destroy(omnifleet_a2_interfaces__msg__SteeringAngleCommand * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_a2_interfaces__msg__SteeringAngleCommand__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence__init(omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_a2_interfaces__msg__SteeringAngleCommand * data = NULL;

  if (size) {
    data = (omnifleet_a2_interfaces__msg__SteeringAngleCommand *)allocator.zero_allocate(size, sizeof(omnifleet_a2_interfaces__msg__SteeringAngleCommand), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_a2_interfaces__msg__SteeringAngleCommand__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_a2_interfaces__msg__SteeringAngleCommand__fini(&data[i - 1]);
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
omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence__fini(omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence * array)
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
      omnifleet_a2_interfaces__msg__SteeringAngleCommand__fini(&array->data[i]);
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

omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence *
omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence * array = (omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence *)allocator.allocate(sizeof(omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence__destroy(omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence__are_equal(const omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence * lhs, const omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_a2_interfaces__msg__SteeringAngleCommand__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence__copy(
  const omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence * input,
  omnifleet_a2_interfaces__msg__SteeringAngleCommand__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_a2_interfaces__msg__SteeringAngleCommand);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_a2_interfaces__msg__SteeringAngleCommand * data =
      (omnifleet_a2_interfaces__msg__SteeringAngleCommand *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_a2_interfaces__msg__SteeringAngleCommand__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_a2_interfaces__msg__SteeringAngleCommand__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_a2_interfaces__msg__SteeringAngleCommand__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
