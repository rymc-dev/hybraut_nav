// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from hybrid_automaton_interfaces:msg/TransitionPending.idl
// generated code does not contain a copyright notice
#include "hybrid_automaton_interfaces/msg/detail/transition_pending__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `transition_uuid`
#include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"

bool
hybrid_automaton_interfaces__msg__TransitionPending__init(hybrid_automaton_interfaces__msg__TransitionPending * msg)
{
  if (!msg) {
    return false;
  }
  // transition_uuid
  if (!unique_identifier_msgs__msg__UUID__init(&msg->transition_uuid)) {
    hybrid_automaton_interfaces__msg__TransitionPending__fini(msg);
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    hybrid_automaton_interfaces__msg__TransitionPending__fini(msg);
    return false;
  }
  // transition_pending
  return true;
}

void
hybrid_automaton_interfaces__msg__TransitionPending__fini(hybrid_automaton_interfaces__msg__TransitionPending * msg)
{
  if (!msg) {
    return;
  }
  // transition_uuid
  unique_identifier_msgs__msg__UUID__fini(&msg->transition_uuid);
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
  // transition_pending
}

bool
hybrid_automaton_interfaces__msg__TransitionPending__are_equal(const hybrid_automaton_interfaces__msg__TransitionPending * lhs, const hybrid_automaton_interfaces__msg__TransitionPending * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // transition_uuid
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->transition_uuid), &(rhs->transition_uuid)))
  {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->stamp), &(rhs->stamp)))
  {
    return false;
  }
  // transition_pending
  if (lhs->transition_pending != rhs->transition_pending) {
    return false;
  }
  return true;
}

bool
hybrid_automaton_interfaces__msg__TransitionPending__copy(
  const hybrid_automaton_interfaces__msg__TransitionPending * input,
  hybrid_automaton_interfaces__msg__TransitionPending * output)
{
  if (!input || !output) {
    return false;
  }
  // transition_uuid
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->transition_uuid), &(output->transition_uuid)))
  {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__copy(
      &(input->stamp), &(output->stamp)))
  {
    return false;
  }
  // transition_pending
  output->transition_pending = input->transition_pending;
  return true;
}

hybrid_automaton_interfaces__msg__TransitionPending *
hybrid_automaton_interfaces__msg__TransitionPending__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__TransitionPending * msg = (hybrid_automaton_interfaces__msg__TransitionPending *)allocator.allocate(sizeof(hybrid_automaton_interfaces__msg__TransitionPending), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(hybrid_automaton_interfaces__msg__TransitionPending));
  bool success = hybrid_automaton_interfaces__msg__TransitionPending__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
hybrid_automaton_interfaces__msg__TransitionPending__destroy(hybrid_automaton_interfaces__msg__TransitionPending * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    hybrid_automaton_interfaces__msg__TransitionPending__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
hybrid_automaton_interfaces__msg__TransitionPending__Sequence__init(hybrid_automaton_interfaces__msg__TransitionPending__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__TransitionPending * data = NULL;

  if (size) {
    data = (hybrid_automaton_interfaces__msg__TransitionPending *)allocator.zero_allocate(size, sizeof(hybrid_automaton_interfaces__msg__TransitionPending), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = hybrid_automaton_interfaces__msg__TransitionPending__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        hybrid_automaton_interfaces__msg__TransitionPending__fini(&data[i - 1]);
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
hybrid_automaton_interfaces__msg__TransitionPending__Sequence__fini(hybrid_automaton_interfaces__msg__TransitionPending__Sequence * array)
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
      hybrid_automaton_interfaces__msg__TransitionPending__fini(&array->data[i]);
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

hybrid_automaton_interfaces__msg__TransitionPending__Sequence *
hybrid_automaton_interfaces__msg__TransitionPending__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__TransitionPending__Sequence * array = (hybrid_automaton_interfaces__msg__TransitionPending__Sequence *)allocator.allocate(sizeof(hybrid_automaton_interfaces__msg__TransitionPending__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = hybrid_automaton_interfaces__msg__TransitionPending__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
hybrid_automaton_interfaces__msg__TransitionPending__Sequence__destroy(hybrid_automaton_interfaces__msg__TransitionPending__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    hybrid_automaton_interfaces__msg__TransitionPending__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
hybrid_automaton_interfaces__msg__TransitionPending__Sequence__are_equal(const hybrid_automaton_interfaces__msg__TransitionPending__Sequence * lhs, const hybrid_automaton_interfaces__msg__TransitionPending__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!hybrid_automaton_interfaces__msg__TransitionPending__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
hybrid_automaton_interfaces__msg__TransitionPending__Sequence__copy(
  const hybrid_automaton_interfaces__msg__TransitionPending__Sequence * input,
  hybrid_automaton_interfaces__msg__TransitionPending__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(hybrid_automaton_interfaces__msg__TransitionPending);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    hybrid_automaton_interfaces__msg__TransitionPending * data =
      (hybrid_automaton_interfaces__msg__TransitionPending *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!hybrid_automaton_interfaces__msg__TransitionPending__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          hybrid_automaton_interfaces__msg__TransitionPending__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!hybrid_automaton_interfaces__msg__TransitionPending__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
