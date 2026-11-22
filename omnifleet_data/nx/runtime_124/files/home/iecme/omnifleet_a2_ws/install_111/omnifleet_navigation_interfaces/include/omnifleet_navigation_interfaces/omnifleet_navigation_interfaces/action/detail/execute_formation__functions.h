// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from omnifleet_navigation_interfaces:action/ExecuteFormation.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_FORMATION__FUNCTIONS_H_
#define OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_FORMATION__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "omnifleet_navigation_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "omnifleet_navigation_interfaces/action/detail/execute_formation__struct.h"

/// Initialize action/ExecuteFormation message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Goal
 * )) before or use
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__init(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * msg);

/// Finalize action/ExecuteFormation message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * msg);

/// Create action/ExecuteFormation message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal *
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__create();

/// Destroy action/ExecuteFormation message.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * msg);

/// Check for action/ExecuteFormation message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * rhs);

/// Copy a action/ExecuteFormation message.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_Goal * output);

/// Initialize array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the number of elements and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * array, size_t size);

/// Finalize array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * array);

/// Create array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the array and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__create(size_t size);

/// Destroy array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * array);

/// Check for action/ExecuteFormation message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * rhs);

/// Copy an array of action/ExecuteFormation messages.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__Sequence * output);

/// Initialize action/ExecuteFormation message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Result
 * )) before or use
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Result__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__init(omnifleet_navigation_interfaces__action__ExecuteFormation_Result * msg);

/// Finalize action/ExecuteFormation message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_Result * msg);

/// Create action/ExecuteFormation message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Result__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_Result *
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__create();

/// Destroy action/ExecuteFormation message.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Result__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_Result * msg);

/// Check for action/ExecuteFormation message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_Result * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_Result * rhs);

/// Copy a action/ExecuteFormation message.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_Result * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_Result * output);

/// Initialize array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the number of elements and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Result__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * array, size_t size);

/// Finalize array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Result__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * array);

/// Create array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the array and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__create(size_t size);

/// Destroy array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * array);

/// Check for action/ExecuteFormation message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * rhs);

/// Copy an array of action/ExecuteFormation messages.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_Result__Sequence * output);

/// Initialize action/ExecuteFormation message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback
 * )) before or use
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__init(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * msg);

/// Finalize action/ExecuteFormation message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * msg);

/// Create action/ExecuteFormation message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback *
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__create();

/// Destroy action/ExecuteFormation message.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * msg);

/// Check for action/ExecuteFormation message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * rhs);

/// Copy a action/ExecuteFormation message.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback * output);

/// Initialize array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the number of elements and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * array, size_t size);

/// Finalize array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * array);

/// Create array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the array and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__create(size_t size);

/// Destroy array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * array);

/// Check for action/ExecuteFormation message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * rhs);

/// Copy an array of action/ExecuteFormation messages.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__Sequence * output);

/// Initialize action/ExecuteFormation message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request
 * )) before or use
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__init(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * msg);

/// Finalize action/ExecuteFormation message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * msg);

/// Create action/ExecuteFormation message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request *
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__create();

/// Destroy action/ExecuteFormation message.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * msg);

/// Check for action/ExecuteFormation message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * rhs);

/// Copy a action/ExecuteFormation message.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request * output);

/// Initialize array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the number of elements and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * array, size_t size);

/// Finalize array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * array);

/// Create array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the array and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__create(size_t size);

/// Destroy array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * array);

/// Check for action/ExecuteFormation message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * rhs);

/// Copy an array of action/ExecuteFormation messages.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__Sequence * output);

/// Initialize action/ExecuteFormation message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response
 * )) before or use
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__init(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * msg);

/// Finalize action/ExecuteFormation message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * msg);

/// Create action/ExecuteFormation message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response *
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__create();

/// Destroy action/ExecuteFormation message.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * msg);

/// Check for action/ExecuteFormation message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * rhs);

/// Copy a action/ExecuteFormation message.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response * output);

/// Initialize array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the number of elements and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * array, size_t size);

/// Finalize array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * array);

/// Create array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the array and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__create(size_t size);

/// Destroy array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * array);

/// Check for action/ExecuteFormation message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * rhs);

/// Copy an array of action/ExecuteFormation messages.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__Sequence * output);

/// Initialize action/ExecuteFormation message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request
 * )) before or use
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__init(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * msg);

/// Finalize action/ExecuteFormation message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * msg);

/// Create action/ExecuteFormation message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request *
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__create();

/// Destroy action/ExecuteFormation message.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * msg);

/// Check for action/ExecuteFormation message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * rhs);

/// Copy a action/ExecuteFormation message.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request * output);

/// Initialize array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the number of elements and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * array, size_t size);

/// Finalize array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * array);

/// Create array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the array and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__create(size_t size);

/// Destroy array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * array);

/// Check for action/ExecuteFormation message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * rhs);

/// Copy an array of action/ExecuteFormation messages.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__Sequence * output);

/// Initialize action/ExecuteFormation message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response
 * )) before or use
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__init(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * msg);

/// Finalize action/ExecuteFormation message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * msg);

/// Create action/ExecuteFormation message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response *
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__create();

/// Destroy action/ExecuteFormation message.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * msg);

/// Check for action/ExecuteFormation message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * rhs);

/// Copy a action/ExecuteFormation message.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response * output);

/// Initialize array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the number of elements and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * array, size_t size);

/// Finalize array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * array);

/// Create array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the array and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__create(size_t size);

/// Destroy array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * array);

/// Check for action/ExecuteFormation message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * rhs);

/// Copy an array of action/ExecuteFormation messages.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__Sequence * output);

/// Initialize action/ExecuteFormation message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage
 * )) before or use
 * omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__init(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * msg);

/// Finalize action/ExecuteFormation message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * msg);

/// Create action/ExecuteFormation message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage *
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__create();

/// Destroy action/ExecuteFormation message.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * msg);

/// Check for action/ExecuteFormation message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * rhs);

/// Copy a action/ExecuteFormation message.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage * output);

/// Initialize array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the number of elements and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__init(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * array, size_t size);

/// Finalize array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__fini(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * array);

/// Create array of action/ExecuteFormation messages.
/**
 * It allocates the memory for the array and calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence *
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__create(size_t size);

/// Destroy array of action/ExecuteFormation messages.
/**
 * It calls
 * omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
void
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__destroy(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * array);

/// Check for action/ExecuteFormation message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_omnifleet_navigation_interfaces
bool
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__are_equal(const omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * lhs, const omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * rhs);

/// Copy an array of action/ExecuteFormation messages.
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
omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence__copy(
  const omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * input,
  omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_FORMATION__FUNCTIONS_H_
