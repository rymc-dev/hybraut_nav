// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from hybrid_automaton_interfaces:msg/Transition.idl
// generated code does not contain a copyright notice
#include "hybrid_automaton_interfaces/msg/detail/transition__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `transition_uuid`
#include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `mode`
// Member `transition_names`
// Member `error_message`
#include "rosidl_runtime_c/string_functions.h"
// Member `transition_values`
// Member `transition_priority`
#include "rosidl_runtime_c/primitives_sequence_functions.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"

bool
hybrid_automaton_interfaces__msg__Transition__init(hybrid_automaton_interfaces__msg__Transition * msg)
{
  if (!msg) {
    return false;
  }
  // transition_uuid
  if (!unique_identifier_msgs__msg__UUID__init(&msg->transition_uuid)) {
    hybrid_automaton_interfaces__msg__Transition__fini(msg);
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__init(&msg->mode)) {
    hybrid_automaton_interfaces__msg__Transition__fini(msg);
    return false;
  }
  // transition_names
  if (!rosidl_runtime_c__String__Sequence__init(&msg->transition_names, 0)) {
    hybrid_automaton_interfaces__msg__Transition__fini(msg);
    return false;
  }
  // transition_values
  if (!rosidl_runtime_c__boolean__Sequence__init(&msg->transition_values, 0)) {
    hybrid_automaton_interfaces__msg__Transition__fini(msg);
    return false;
  }
  // transition_priority
  if (!rosidl_runtime_c__int32__Sequence__init(&msg->transition_priority, 0)) {
    hybrid_automaton_interfaces__msg__Transition__fini(msg);
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    hybrid_automaton_interfaces__msg__Transition__fini(msg);
    return false;
  }
  // success
  // error_message
  if (!rosidl_runtime_c__String__init(&msg->error_message)) {
    hybrid_automaton_interfaces__msg__Transition__fini(msg);
    return false;
  }
  return true;
}

void
hybrid_automaton_interfaces__msg__Transition__fini(hybrid_automaton_interfaces__msg__Transition * msg)
{
  if (!msg) {
    return;
  }
  // transition_uuid
  unique_identifier_msgs__msg__UUID__fini(&msg->transition_uuid);
  // mode
  rosidl_runtime_c__String__fini(&msg->mode);
  // transition_names
  rosidl_runtime_c__String__Sequence__fini(&msg->transition_names);
  // transition_values
  rosidl_runtime_c__boolean__Sequence__fini(&msg->transition_values);
  // transition_priority
  rosidl_runtime_c__int32__Sequence__fini(&msg->transition_priority);
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
  // success
  // error_message
  rosidl_runtime_c__String__fini(&msg->error_message);
}

bool
hybrid_automaton_interfaces__msg__Transition__are_equal(const hybrid_automaton_interfaces__msg__Transition * lhs, const hybrid_automaton_interfaces__msg__Transition * rhs)
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
  // mode
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->mode), &(rhs->mode)))
  {
    return false;
  }
  // transition_names
  if (!rosidl_runtime_c__String__Sequence__are_equal(
      &(lhs->transition_names), &(rhs->transition_names)))
  {
    return false;
  }
  // transition_values
  if (!rosidl_runtime_c__boolean__Sequence__are_equal(
      &(lhs->transition_values), &(rhs->transition_values)))
  {
    return false;
  }
  // transition_priority
  if (!rosidl_runtime_c__int32__Sequence__are_equal(
      &(lhs->transition_priority), &(rhs->transition_priority)))
  {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->stamp), &(rhs->stamp)))
  {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // error_message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->error_message), &(rhs->error_message)))
  {
    return false;
  }
  return true;
}

bool
hybrid_automaton_interfaces__msg__Transition__copy(
  const hybrid_automaton_interfaces__msg__Transition * input,
  hybrid_automaton_interfaces__msg__Transition * output)
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
  // mode
  if (!rosidl_runtime_c__String__copy(
      &(input->mode), &(output->mode)))
  {
    return false;
  }
  // transition_names
  if (!rosidl_runtime_c__String__Sequence__copy(
      &(input->transition_names), &(output->transition_names)))
  {
    return false;
  }
  // transition_values
  if (!rosidl_runtime_c__boolean__Sequence__copy(
      &(input->transition_values), &(output->transition_values)))
  {
    return false;
  }
  // transition_priority
  if (!rosidl_runtime_c__int32__Sequence__copy(
      &(input->transition_priority), &(output->transition_priority)))
  {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__copy(
      &(input->stamp), &(output->stamp)))
  {
    return false;
  }
  // success
  output->success = input->success;
  // error_message
  if (!rosidl_runtime_c__String__copy(
      &(input->error_message), &(output->error_message)))
  {
    return false;
  }
  return true;
}

hybrid_automaton_interfaces__msg__Transition *
hybrid_automaton_interfaces__msg__Transition__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__Transition * msg = (hybrid_automaton_interfaces__msg__Transition *)allocator.allocate(sizeof(hybrid_automaton_interfaces__msg__Transition), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(hybrid_automaton_interfaces__msg__Transition));
  bool success = hybrid_automaton_interfaces__msg__Transition__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
hybrid_automaton_interfaces__msg__Transition__destroy(hybrid_automaton_interfaces__msg__Transition * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    hybrid_automaton_interfaces__msg__Transition__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
hybrid_automaton_interfaces__msg__Transition__Sequence__init(hybrid_automaton_interfaces__msg__Transition__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__Transition * data = NULL;

  if (size) {
    data = (hybrid_automaton_interfaces__msg__Transition *)allocator.zero_allocate(size, sizeof(hybrid_automaton_interfaces__msg__Transition), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = hybrid_automaton_interfaces__msg__Transition__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        hybrid_automaton_interfaces__msg__Transition__fini(&data[i - 1]);
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
hybrid_automaton_interfaces__msg__Transition__Sequence__fini(hybrid_automaton_interfaces__msg__Transition__Sequence * array)
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
      hybrid_automaton_interfaces__msg__Transition__fini(&array->data[i]);
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

hybrid_automaton_interfaces__msg__Transition__Sequence *
hybrid_automaton_interfaces__msg__Transition__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__Transition__Sequence * array = (hybrid_automaton_interfaces__msg__Transition__Sequence *)allocator.allocate(sizeof(hybrid_automaton_interfaces__msg__Transition__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = hybrid_automaton_interfaces__msg__Transition__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
hybrid_automaton_interfaces__msg__Transition__Sequence__destroy(hybrid_automaton_interfaces__msg__Transition__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    hybrid_automaton_interfaces__msg__Transition__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
hybrid_automaton_interfaces__msg__Transition__Sequence__are_equal(const hybrid_automaton_interfaces__msg__Transition__Sequence * lhs, const hybrid_automaton_interfaces__msg__Transition__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!hybrid_automaton_interfaces__msg__Transition__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
hybrid_automaton_interfaces__msg__Transition__Sequence__copy(
  const hybrid_automaton_interfaces__msg__Transition__Sequence * input,
  hybrid_automaton_interfaces__msg__Transition__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(hybrid_automaton_interfaces__msg__Transition);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    hybrid_automaton_interfaces__msg__Transition * data =
      (hybrid_automaton_interfaces__msg__Transition *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!hybrid_automaton_interfaces__msg__Transition__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          hybrid_automaton_interfaces__msg__Transition__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!hybrid_automaton_interfaces__msg__Transition__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
