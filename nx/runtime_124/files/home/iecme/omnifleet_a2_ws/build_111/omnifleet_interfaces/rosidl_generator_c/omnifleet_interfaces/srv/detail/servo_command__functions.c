// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from omnifleet_interfaces:srv/ServoCommand.idl
// generated code does not contain a copyright notice
#include "omnifleet_interfaces/srv/detail/servo_command__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

bool
omnifleet_interfaces__srv__ServoCommand_Request__init(omnifleet_interfaces__srv__ServoCommand_Request * msg)
{
  if (!msg) {
    return false;
  }
  // operation
  // id
  // arg0
  // arg1
  // arg2
  return true;
}

void
omnifleet_interfaces__srv__ServoCommand_Request__fini(omnifleet_interfaces__srv__ServoCommand_Request * msg)
{
  if (!msg) {
    return;
  }
  // operation
  // id
  // arg0
  // arg1
  // arg2
}

bool
omnifleet_interfaces__srv__ServoCommand_Request__are_equal(const omnifleet_interfaces__srv__ServoCommand_Request * lhs, const omnifleet_interfaces__srv__ServoCommand_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // operation
  if (lhs->operation != rhs->operation) {
    return false;
  }
  // id
  if (lhs->id != rhs->id) {
    return false;
  }
  // arg0
  if (lhs->arg0 != rhs->arg0) {
    return false;
  }
  // arg1
  if (lhs->arg1 != rhs->arg1) {
    return false;
  }
  // arg2
  if (lhs->arg2 != rhs->arg2) {
    return false;
  }
  return true;
}

bool
omnifleet_interfaces__srv__ServoCommand_Request__copy(
  const omnifleet_interfaces__srv__ServoCommand_Request * input,
  omnifleet_interfaces__srv__ServoCommand_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // operation
  output->operation = input->operation;
  // id
  output->id = input->id;
  // arg0
  output->arg0 = input->arg0;
  // arg1
  output->arg1 = input->arg1;
  // arg2
  output->arg2 = input->arg2;
  return true;
}

omnifleet_interfaces__srv__ServoCommand_Request *
omnifleet_interfaces__srv__ServoCommand_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__srv__ServoCommand_Request * msg = (omnifleet_interfaces__srv__ServoCommand_Request *)allocator.allocate(sizeof(omnifleet_interfaces__srv__ServoCommand_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_interfaces__srv__ServoCommand_Request));
  bool success = omnifleet_interfaces__srv__ServoCommand_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_interfaces__srv__ServoCommand_Request__destroy(omnifleet_interfaces__srv__ServoCommand_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_interfaces__srv__ServoCommand_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_interfaces__srv__ServoCommand_Request__Sequence__init(omnifleet_interfaces__srv__ServoCommand_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__srv__ServoCommand_Request * data = NULL;

  if (size) {
    data = (omnifleet_interfaces__srv__ServoCommand_Request *)allocator.zero_allocate(size, sizeof(omnifleet_interfaces__srv__ServoCommand_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_interfaces__srv__ServoCommand_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_interfaces__srv__ServoCommand_Request__fini(&data[i - 1]);
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
omnifleet_interfaces__srv__ServoCommand_Request__Sequence__fini(omnifleet_interfaces__srv__ServoCommand_Request__Sequence * array)
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
      omnifleet_interfaces__srv__ServoCommand_Request__fini(&array->data[i]);
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

omnifleet_interfaces__srv__ServoCommand_Request__Sequence *
omnifleet_interfaces__srv__ServoCommand_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__srv__ServoCommand_Request__Sequence * array = (omnifleet_interfaces__srv__ServoCommand_Request__Sequence *)allocator.allocate(sizeof(omnifleet_interfaces__srv__ServoCommand_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_interfaces__srv__ServoCommand_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_interfaces__srv__ServoCommand_Request__Sequence__destroy(omnifleet_interfaces__srv__ServoCommand_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_interfaces__srv__ServoCommand_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_interfaces__srv__ServoCommand_Request__Sequence__are_equal(const omnifleet_interfaces__srv__ServoCommand_Request__Sequence * lhs, const omnifleet_interfaces__srv__ServoCommand_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_interfaces__srv__ServoCommand_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_interfaces__srv__ServoCommand_Request__Sequence__copy(
  const omnifleet_interfaces__srv__ServoCommand_Request__Sequence * input,
  omnifleet_interfaces__srv__ServoCommand_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_interfaces__srv__ServoCommand_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_interfaces__srv__ServoCommand_Request * data =
      (omnifleet_interfaces__srv__ServoCommand_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_interfaces__srv__ServoCommand_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_interfaces__srv__ServoCommand_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_interfaces__srv__ServoCommand_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `message`
#include "rosidl_runtime_c/string_functions.h"

bool
omnifleet_interfaces__srv__ServoCommand_Response__init(omnifleet_interfaces__srv__ServoCommand_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // value0
  // value1
  // value2
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    omnifleet_interfaces__srv__ServoCommand_Response__fini(msg);
    return false;
  }
  return true;
}

void
omnifleet_interfaces__srv__ServoCommand_Response__fini(omnifleet_interfaces__srv__ServoCommand_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
  // value0
  // value1
  // value2
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
omnifleet_interfaces__srv__ServoCommand_Response__are_equal(const omnifleet_interfaces__srv__ServoCommand_Response * lhs, const omnifleet_interfaces__srv__ServoCommand_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // value0
  if (lhs->value0 != rhs->value0) {
    return false;
  }
  // value1
  if (lhs->value1 != rhs->value1) {
    return false;
  }
  // value2
  if (lhs->value2 != rhs->value2) {
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
omnifleet_interfaces__srv__ServoCommand_Response__copy(
  const omnifleet_interfaces__srv__ServoCommand_Response * input,
  omnifleet_interfaces__srv__ServoCommand_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  // value0
  output->value0 = input->value0;
  // value1
  output->value1 = input->value1;
  // value2
  output->value2 = input->value2;
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  return true;
}

omnifleet_interfaces__srv__ServoCommand_Response *
omnifleet_interfaces__srv__ServoCommand_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__srv__ServoCommand_Response * msg = (omnifleet_interfaces__srv__ServoCommand_Response *)allocator.allocate(sizeof(omnifleet_interfaces__srv__ServoCommand_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(omnifleet_interfaces__srv__ServoCommand_Response));
  bool success = omnifleet_interfaces__srv__ServoCommand_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
omnifleet_interfaces__srv__ServoCommand_Response__destroy(omnifleet_interfaces__srv__ServoCommand_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    omnifleet_interfaces__srv__ServoCommand_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
omnifleet_interfaces__srv__ServoCommand_Response__Sequence__init(omnifleet_interfaces__srv__ServoCommand_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__srv__ServoCommand_Response * data = NULL;

  if (size) {
    data = (omnifleet_interfaces__srv__ServoCommand_Response *)allocator.zero_allocate(size, sizeof(omnifleet_interfaces__srv__ServoCommand_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = omnifleet_interfaces__srv__ServoCommand_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        omnifleet_interfaces__srv__ServoCommand_Response__fini(&data[i - 1]);
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
omnifleet_interfaces__srv__ServoCommand_Response__Sequence__fini(omnifleet_interfaces__srv__ServoCommand_Response__Sequence * array)
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
      omnifleet_interfaces__srv__ServoCommand_Response__fini(&array->data[i]);
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

omnifleet_interfaces__srv__ServoCommand_Response__Sequence *
omnifleet_interfaces__srv__ServoCommand_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  omnifleet_interfaces__srv__ServoCommand_Response__Sequence * array = (omnifleet_interfaces__srv__ServoCommand_Response__Sequence *)allocator.allocate(sizeof(omnifleet_interfaces__srv__ServoCommand_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = omnifleet_interfaces__srv__ServoCommand_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
omnifleet_interfaces__srv__ServoCommand_Response__Sequence__destroy(omnifleet_interfaces__srv__ServoCommand_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    omnifleet_interfaces__srv__ServoCommand_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
omnifleet_interfaces__srv__ServoCommand_Response__Sequence__are_equal(const omnifleet_interfaces__srv__ServoCommand_Response__Sequence * lhs, const omnifleet_interfaces__srv__ServoCommand_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!omnifleet_interfaces__srv__ServoCommand_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
omnifleet_interfaces__srv__ServoCommand_Response__Sequence__copy(
  const omnifleet_interfaces__srv__ServoCommand_Response__Sequence * input,
  omnifleet_interfaces__srv__ServoCommand_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(omnifleet_interfaces__srv__ServoCommand_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    omnifleet_interfaces__srv__ServoCommand_Response * data =
      (omnifleet_interfaces__srv__ServoCommand_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!omnifleet_interfaces__srv__ServoCommand_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          omnifleet_interfaces__srv__ServoCommand_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!omnifleet_interfaces__srv__ServoCommand_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
