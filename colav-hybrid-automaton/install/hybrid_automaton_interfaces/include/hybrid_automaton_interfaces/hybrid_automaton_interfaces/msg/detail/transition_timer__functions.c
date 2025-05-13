// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from hybrid_automaton_interfaces:msg/TransitionTimer.idl
// generated code does not contain a copyright notice
#include "hybrid_automaton_interfaces/msg/detail/transition_timer__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `previous_transition_uuid`
#include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `elapsed`
// Member `timeout`
#include "builtin_interfaces/msg/detail/duration__functions.h"

bool
hybrid_automaton_interfaces__msg__TransitionTimer__init(hybrid_automaton_interfaces__msg__TransitionTimer * msg)
{
  if (!msg) {
    return false;
  }
  // previous_transition_uuid
  if (!unique_identifier_msgs__msg__UUID__init(&msg->previous_transition_uuid)) {
    hybrid_automaton_interfaces__msg__TransitionTimer__fini(msg);
    return false;
  }
  // elapsed
  if (!builtin_interfaces__msg__Duration__init(&msg->elapsed)) {
    hybrid_automaton_interfaces__msg__TransitionTimer__fini(msg);
    return false;
  }
  // timeout
  if (!builtin_interfaces__msg__Duration__init(&msg->timeout)) {
    hybrid_automaton_interfaces__msg__TransitionTimer__fini(msg);
    return false;
  }
  // timeout_sec
  // expired
  return true;
}

void
hybrid_automaton_interfaces__msg__TransitionTimer__fini(hybrid_automaton_interfaces__msg__TransitionTimer * msg)
{
  if (!msg) {
    return;
  }
  // previous_transition_uuid
  unique_identifier_msgs__msg__UUID__fini(&msg->previous_transition_uuid);
  // elapsed
  builtin_interfaces__msg__Duration__fini(&msg->elapsed);
  // timeout
  builtin_interfaces__msg__Duration__fini(&msg->timeout);
  // timeout_sec
  // expired
}

bool
hybrid_automaton_interfaces__msg__TransitionTimer__are_equal(const hybrid_automaton_interfaces__msg__TransitionTimer * lhs, const hybrid_automaton_interfaces__msg__TransitionTimer * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // previous_transition_uuid
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->previous_transition_uuid), &(rhs->previous_transition_uuid)))
  {
    return false;
  }
  // elapsed
  if (!builtin_interfaces__msg__Duration__are_equal(
      &(lhs->elapsed), &(rhs->elapsed)))
  {
    return false;
  }
  // timeout
  if (!builtin_interfaces__msg__Duration__are_equal(
      &(lhs->timeout), &(rhs->timeout)))
  {
    return false;
  }
  // timeout_sec
  if (lhs->timeout_sec != rhs->timeout_sec) {
    return false;
  }
  // expired
  if (lhs->expired != rhs->expired) {
    return false;
  }
  return true;
}

bool
hybrid_automaton_interfaces__msg__TransitionTimer__copy(
  const hybrid_automaton_interfaces__msg__TransitionTimer * input,
  hybrid_automaton_interfaces__msg__TransitionTimer * output)
{
  if (!input || !output) {
    return false;
  }
  // previous_transition_uuid
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->previous_transition_uuid), &(output->previous_transition_uuid)))
  {
    return false;
  }
  // elapsed
  if (!builtin_interfaces__msg__Duration__copy(
      &(input->elapsed), &(output->elapsed)))
  {
    return false;
  }
  // timeout
  if (!builtin_interfaces__msg__Duration__copy(
      &(input->timeout), &(output->timeout)))
  {
    return false;
  }
  // timeout_sec
  output->timeout_sec = input->timeout_sec;
  // expired
  output->expired = input->expired;
  return true;
}

hybrid_automaton_interfaces__msg__TransitionTimer *
hybrid_automaton_interfaces__msg__TransitionTimer__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__TransitionTimer * msg = (hybrid_automaton_interfaces__msg__TransitionTimer *)allocator.allocate(sizeof(hybrid_automaton_interfaces__msg__TransitionTimer), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(hybrid_automaton_interfaces__msg__TransitionTimer));
  bool success = hybrid_automaton_interfaces__msg__TransitionTimer__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
hybrid_automaton_interfaces__msg__TransitionTimer__destroy(hybrid_automaton_interfaces__msg__TransitionTimer * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    hybrid_automaton_interfaces__msg__TransitionTimer__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
hybrid_automaton_interfaces__msg__TransitionTimer__Sequence__init(hybrid_automaton_interfaces__msg__TransitionTimer__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__TransitionTimer * data = NULL;

  if (size) {
    data = (hybrid_automaton_interfaces__msg__TransitionTimer *)allocator.zero_allocate(size, sizeof(hybrid_automaton_interfaces__msg__TransitionTimer), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = hybrid_automaton_interfaces__msg__TransitionTimer__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        hybrid_automaton_interfaces__msg__TransitionTimer__fini(&data[i - 1]);
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
hybrid_automaton_interfaces__msg__TransitionTimer__Sequence__fini(hybrid_automaton_interfaces__msg__TransitionTimer__Sequence * array)
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
      hybrid_automaton_interfaces__msg__TransitionTimer__fini(&array->data[i]);
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

hybrid_automaton_interfaces__msg__TransitionTimer__Sequence *
hybrid_automaton_interfaces__msg__TransitionTimer__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__TransitionTimer__Sequence * array = (hybrid_automaton_interfaces__msg__TransitionTimer__Sequence *)allocator.allocate(sizeof(hybrid_automaton_interfaces__msg__TransitionTimer__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = hybrid_automaton_interfaces__msg__TransitionTimer__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
hybrid_automaton_interfaces__msg__TransitionTimer__Sequence__destroy(hybrid_automaton_interfaces__msg__TransitionTimer__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    hybrid_automaton_interfaces__msg__TransitionTimer__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
hybrid_automaton_interfaces__msg__TransitionTimer__Sequence__are_equal(const hybrid_automaton_interfaces__msg__TransitionTimer__Sequence * lhs, const hybrid_automaton_interfaces__msg__TransitionTimer__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!hybrid_automaton_interfaces__msg__TransitionTimer__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
hybrid_automaton_interfaces__msg__TransitionTimer__Sequence__copy(
  const hybrid_automaton_interfaces__msg__TransitionTimer__Sequence * input,
  hybrid_automaton_interfaces__msg__TransitionTimer__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(hybrid_automaton_interfaces__msg__TransitionTimer);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    hybrid_automaton_interfaces__msg__TransitionTimer * data =
      (hybrid_automaton_interfaces__msg__TransitionTimer *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!hybrid_automaton_interfaces__msg__TransitionTimer__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          hybrid_automaton_interfaces__msg__TransitionTimer__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!hybrid_automaton_interfaces__msg__TransitionTimer__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
