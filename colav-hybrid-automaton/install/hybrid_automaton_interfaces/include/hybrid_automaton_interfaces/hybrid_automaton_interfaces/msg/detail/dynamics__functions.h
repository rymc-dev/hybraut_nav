// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from hybrid_automaton_interfaces:msg/Dynamics.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS__FUNCTIONS_H_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "hybrid_automaton_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "hybrid_automaton_interfaces/msg/detail/dynamics__struct.h"

/// Initialize msg/Dynamics message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * hybrid_automaton_interfaces__msg__Dynamics
 * )) before or use
 * hybrid_automaton_interfaces__msg__Dynamics__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_hybrid_automaton_interfaces
bool
hybrid_automaton_interfaces__msg__Dynamics__init(hybrid_automaton_interfaces__msg__Dynamics * msg);

/// Finalize msg/Dynamics message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_hybrid_automaton_interfaces
void
hybrid_automaton_interfaces__msg__Dynamics__fini(hybrid_automaton_interfaces__msg__Dynamics * msg);

/// Create msg/Dynamics message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * hybrid_automaton_interfaces__msg__Dynamics__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_hybrid_automaton_interfaces
hybrid_automaton_interfaces__msg__Dynamics *
hybrid_automaton_interfaces__msg__Dynamics__create();

/// Destroy msg/Dynamics message.
/**
 * It calls
 * hybrid_automaton_interfaces__msg__Dynamics__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_hybrid_automaton_interfaces
void
hybrid_automaton_interfaces__msg__Dynamics__destroy(hybrid_automaton_interfaces__msg__Dynamics * msg);

/// Check for msg/Dynamics message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_hybrid_automaton_interfaces
bool
hybrid_automaton_interfaces__msg__Dynamics__are_equal(const hybrid_automaton_interfaces__msg__Dynamics * lhs, const hybrid_automaton_interfaces__msg__Dynamics * rhs);

/// Copy a msg/Dynamics message.
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
ROSIDL_GENERATOR_C_PUBLIC_hybrid_automaton_interfaces
bool
hybrid_automaton_interfaces__msg__Dynamics__copy(
  const hybrid_automaton_interfaces__msg__Dynamics * input,
  hybrid_automaton_interfaces__msg__Dynamics * output);

/// Initialize array of msg/Dynamics messages.
/**
 * It allocates the memory for the number of elements and calls
 * hybrid_automaton_interfaces__msg__Dynamics__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_hybrid_automaton_interfaces
bool
hybrid_automaton_interfaces__msg__Dynamics__Sequence__init(hybrid_automaton_interfaces__msg__Dynamics__Sequence * array, size_t size);

/// Finalize array of msg/Dynamics messages.
/**
 * It calls
 * hybrid_automaton_interfaces__msg__Dynamics__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_hybrid_automaton_interfaces
void
hybrid_automaton_interfaces__msg__Dynamics__Sequence__fini(hybrid_automaton_interfaces__msg__Dynamics__Sequence * array);

/// Create array of msg/Dynamics messages.
/**
 * It allocates the memory for the array and calls
 * hybrid_automaton_interfaces__msg__Dynamics__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_hybrid_automaton_interfaces
hybrid_automaton_interfaces__msg__Dynamics__Sequence *
hybrid_automaton_interfaces__msg__Dynamics__Sequence__create(size_t size);

/// Destroy array of msg/Dynamics messages.
/**
 * It calls
 * hybrid_automaton_interfaces__msg__Dynamics__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_hybrid_automaton_interfaces
void
hybrid_automaton_interfaces__msg__Dynamics__Sequence__destroy(hybrid_automaton_interfaces__msg__Dynamics__Sequence * array);

/// Check for msg/Dynamics message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_hybrid_automaton_interfaces
bool
hybrid_automaton_interfaces__msg__Dynamics__Sequence__are_equal(const hybrid_automaton_interfaces__msg__Dynamics__Sequence * lhs, const hybrid_automaton_interfaces__msg__Dynamics__Sequence * rhs);

/// Copy an array of msg/Dynamics messages.
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
ROSIDL_GENERATOR_C_PUBLIC_hybrid_automaton_interfaces
bool
hybrid_automaton_interfaces__msg__Dynamics__Sequence__copy(
  const hybrid_automaton_interfaces__msg__Dynamics__Sequence * input,
  hybrid_automaton_interfaces__msg__Dynamics__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS__FUNCTIONS_H_
