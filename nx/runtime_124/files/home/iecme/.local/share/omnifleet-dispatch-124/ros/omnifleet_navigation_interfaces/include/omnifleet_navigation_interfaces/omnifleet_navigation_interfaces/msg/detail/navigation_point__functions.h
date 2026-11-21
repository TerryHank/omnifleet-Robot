// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from omnifleet_navigation_interfaces:msg/NavigationPoint.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__FUNCTIONS_H_
#define OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "omnifleet_navigation_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "omnifleet_navigation_interfaces/msg/detail/navigation_point__struct.h"

/// Initialize msg/NavigationPoint message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * omnifleet_navigation_interfaces__msg__NavigationPoint
 * )) before or use
 * omnifleet_navigation_interfaces__msg__NavigationPoint__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__msg__NavigationPoint__init(omnifleet_navigation_interfaces__msg__NavigationPoint * msg);

/// Finalize msg/NavigationPoint message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__msg__NavigationPoint__fini(omnifleet_navigation_interfaces__msg__NavigationPoint * msg);

/// Create msg/NavigationPoint message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * omnifleet_navigation_interfaces__msg__NavigationPoint__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__msg__NavigationPoint *
omnifleet_navigation_interfaces__msg__NavigationPoint__create();

/// Destroy msg/NavigationPoint message.
/**
 * It calls
 * omnifleet_navigation_interfaces__msg__NavigationPoint__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__msg__NavigationPoint__destroy(omnifleet_navigation_interfaces__msg__NavigationPoint * msg);

/// Check for msg/NavigationPoint message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__msg__NavigationPoint__are_equal(const omnifleet_navigation_interfaces__msg__NavigationPoint * lhs, const omnifleet_navigation_interfaces__msg__NavigationPoint * rhs);

/// Copy a msg/NavigationPoint message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__msg__NavigationPoint__copy(
  const omnifleet_navigation_interfaces__msg__NavigationPoint * input,
  omnifleet_navigation_interfaces__msg__NavigationPoint * output);

/// Initialize array of msg/NavigationPoint messages.
/**
 * It allocates the memory for the number of elements and calls
 * omnifleet_navigation_interfaces__msg__NavigationPoint__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__init(omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * array, size_t size);

/// Finalize array of msg/NavigationPoint messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__msg__NavigationPoint__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__fini(omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * array);

/// Create array of msg/NavigationPoint messages.
/**
 * It allocates the memory for the array and calls
 * omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence *
omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__create(size_t size);

/// Destroy array of msg/NavigationPoint messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__destroy(omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * array);

/// Check for msg/NavigationPoint message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__are_equal(const omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * lhs, const omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * rhs);

/// Copy an array of msg/NavigationPoint messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__copy(
  const omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * input,
  omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // OMNIFLEET_NAVIGATION_INTERFACES__MSG__DETAIL__NAVIGATION_POINT__FUNCTIONS_H_
