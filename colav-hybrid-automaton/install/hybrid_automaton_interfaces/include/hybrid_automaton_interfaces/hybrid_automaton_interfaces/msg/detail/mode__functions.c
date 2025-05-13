// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from hybrid_automaton_interfaces:msg/Mode.idl
// generated code does not contain a copyright notice
#include "hybrid_automaton_interfaces/msg/detail/mode__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `mode_uuid`
#include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `mode`
// Member `origin_transition`
#include "rosidl_runtime_c/string_functions.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"

bool
hybrid_automaton_interfaces__msg__Mode__init(hybrid_automaton_interfaces__msg__Mode * msg)
{
  if (!msg) {
    return false;
  }
  // mode_uuid
  if (!unique_identifier_msgs__msg__UUID__init(&msg->mode_uuid)) {
    hybrid_automaton_interfaces__msg__Mode__fini(msg);
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__init(&msg->mode)) {
    hybrid_automaton_interfaces__msg__Mode__fini(msg);
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    hybrid_automaton_interfaces__msg__Mode__fini(msg);
    return false;
  }
  // origin_transition
  if (!rosidl_runtime_c__String__init(&msg->origin_transition)) {
    hybrid_automaton_interfaces__msg__Mode__fini(msg);
    return false;
  }
  return true;
}

void
hybrid_automaton_interfaces__msg__Mode__fini(hybrid_automaton_interfaces__msg__Mode * msg)
{
  if (!msg) {
    return;
  }
  // mode_uuid
  unique_identifier_msgs__msg__UUID__fini(&msg->mode_uuid);
  // mode
  rosidl_runtime_c__String__fini(&msg->mode);
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
  // origin_transition
  rosidl_runtime_c__String__fini(&msg->origin_transition);
}

bool
hybrid_automaton_interfaces__msg__Mode__are_equal(const hybrid_automaton_interfaces__msg__Mode * lhs, const hybrid_automaton_interfaces__msg__Mode * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // mode_uuid
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->mode_uuid), &(rhs->mode_uuid)))
  {
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->mode), &(rhs->mode)))
  {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->stamp), &(rhs->stamp)))
  {
    return false;
  }
  // origin_transition
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->origin_transition), &(rhs->origin_transition)))
  {
    return false;
  }
  return true;
}

bool
hybrid_automaton_interfaces__msg__Mode__copy(
  const hybrid_automaton_interfaces__msg__Mode * input,
  hybrid_automaton_interfaces__msg__Mode * output)
{
  if (!input || !output) {
    return false;
  }
  // mode_uuid
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->mode_uuid), &(output->mode_uuid)))
  {
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__copy(
      &(input->mode), &(output->mode)))
  {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__copy(
      &(input->stamp), &(output->stamp)))
  {
    return false;
  }
  // origin_transition
  if (!rosidl_runtime_c__String__copy(
      &(input->origin_transition), &(output->origin_transition)))
  {
    return false;
  }
  return true;
}

hybrid_automaton_interfaces__msg__Mode *
hybrid_automaton_interfaces__msg__Mode__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__Mode * msg = (hybrid_automaton_interfaces__msg__Mode *)allocator.allocate(sizeof(hybrid_automaton_interfaces__msg__Mode), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(hybrid_automaton_interfaces__msg__Mode));
  bool success = hybrid_automaton_interfaces__msg__Mode__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
hybrid_automaton_interfaces__msg__Mode__destroy(hybrid_automaton_interfaces__msg__Mode * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    hybrid_automaton_interfaces__msg__Mode__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
hybrid_automaton_interfaces__msg__Mode__Sequence__init(hybrid_automaton_interfaces__msg__Mode__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__Mode * data = NULL;

  if (size) {
    data = (hybrid_automaton_interfaces__msg__Mode *)allocator.zero_allocate(size, sizeof(hybrid_automaton_interfaces__msg__Mode), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = hybrid_automaton_interfaces__msg__Mode__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        hybrid_automaton_interfaces__msg__Mode__fini(&data[i - 1]);
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
hybrid_automaton_interfaces__msg__Mode__Sequence__fini(hybrid_automaton_interfaces__msg__Mode__Sequence * array)
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
      hybrid_automaton_interfaces__msg__Mode__fini(&array->data[i]);
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

hybrid_automaton_interfaces__msg__Mode__Sequence *
hybrid_automaton_interfaces__msg__Mode__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__Mode__Sequence * array = (hybrid_automaton_interfaces__msg__Mode__Sequence *)allocator.allocate(sizeof(hybrid_automaton_interfaces__msg__Mode__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = hybrid_automaton_interfaces__msg__Mode__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
hybrid_automaton_interfaces__msg__Mode__Sequence__destroy(hybrid_automaton_interfaces__msg__Mode__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    hybrid_automaton_interfaces__msg__Mode__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
hybrid_automaton_interfaces__msg__Mode__Sequence__are_equal(const hybrid_automaton_interfaces__msg__Mode__Sequence * lhs, const hybrid_automaton_interfaces__msg__Mode__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!hybrid_automaton_interfaces__msg__Mode__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
hybrid_automaton_interfaces__msg__Mode__Sequence__copy(
  const hybrid_automaton_interfaces__msg__Mode__Sequence * input,
  hybrid_automaton_interfaces__msg__Mode__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(hybrid_automaton_interfaces__msg__Mode);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    hybrid_automaton_interfaces__msg__Mode * data =
      (hybrid_automaton_interfaces__msg__Mode *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!hybrid_automaton_interfaces__msg__Mode__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          hybrid_automaton_interfaces__msg__Mode__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!hybrid_automaton_interfaces__msg__Mode__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
