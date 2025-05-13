// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from hybrid_automaton_interfaces:msg/DynamicParameter.idl
// generated code does not contain a copyright notice
#include "hybrid_automaton_interfaces/msg/detail/dynamic_parameter__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `controller_name`
// Member `dynamic_name`
// Member `dynamic_units`
#include "rosidl_runtime_c/string_functions.h"
// Member `dynamic_value`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
hybrid_automaton_interfaces__msg__DynamicParameter__init(hybrid_automaton_interfaces__msg__DynamicParameter * msg)
{
  if (!msg) {
    return false;
  }
  // controller_name
  if (!rosidl_runtime_c__String__init(&msg->controller_name)) {
    hybrid_automaton_interfaces__msg__DynamicParameter__fini(msg);
    return false;
  }
  // dynamic_name
  if (!rosidl_runtime_c__String__Sequence__init(&msg->dynamic_name, 0)) {
    hybrid_automaton_interfaces__msg__DynamicParameter__fini(msg);
    return false;
  }
  // dynamic_value
  if (!rosidl_runtime_c__double__Sequence__init(&msg->dynamic_value, 0)) {
    hybrid_automaton_interfaces__msg__DynamicParameter__fini(msg);
    return false;
  }
  // dynamic_units
  if (!rosidl_runtime_c__String__Sequence__init(&msg->dynamic_units, 0)) {
    hybrid_automaton_interfaces__msg__DynamicParameter__fini(msg);
    return false;
  }
  return true;
}

void
hybrid_automaton_interfaces__msg__DynamicParameter__fini(hybrid_automaton_interfaces__msg__DynamicParameter * msg)
{
  if (!msg) {
    return;
  }
  // controller_name
  rosidl_runtime_c__String__fini(&msg->controller_name);
  // dynamic_name
  rosidl_runtime_c__String__Sequence__fini(&msg->dynamic_name);
  // dynamic_value
  rosidl_runtime_c__double__Sequence__fini(&msg->dynamic_value);
  // dynamic_units
  rosidl_runtime_c__String__Sequence__fini(&msg->dynamic_units);
}

bool
hybrid_automaton_interfaces__msg__DynamicParameter__are_equal(const hybrid_automaton_interfaces__msg__DynamicParameter * lhs, const hybrid_automaton_interfaces__msg__DynamicParameter * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // controller_name
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->controller_name), &(rhs->controller_name)))
  {
    return false;
  }
  // dynamic_name
  if (!rosidl_runtime_c__String__Sequence__are_equal(
      &(lhs->dynamic_name), &(rhs->dynamic_name)))
  {
    return false;
  }
  // dynamic_value
  if (!rosidl_runtime_c__double__Sequence__are_equal(
      &(lhs->dynamic_value), &(rhs->dynamic_value)))
  {
    return false;
  }
  // dynamic_units
  if (!rosidl_runtime_c__String__Sequence__are_equal(
      &(lhs->dynamic_units), &(rhs->dynamic_units)))
  {
    return false;
  }
  return true;
}

bool
hybrid_automaton_interfaces__msg__DynamicParameter__copy(
  const hybrid_automaton_interfaces__msg__DynamicParameter * input,
  hybrid_automaton_interfaces__msg__DynamicParameter * output)
{
  if (!input || !output) {
    return false;
  }
  // controller_name
  if (!rosidl_runtime_c__String__copy(
      &(input->controller_name), &(output->controller_name)))
  {
    return false;
  }
  // dynamic_name
  if (!rosidl_runtime_c__String__Sequence__copy(
      &(input->dynamic_name), &(output->dynamic_name)))
  {
    return false;
  }
  // dynamic_value
  if (!rosidl_runtime_c__double__Sequence__copy(
      &(input->dynamic_value), &(output->dynamic_value)))
  {
    return false;
  }
  // dynamic_units
  if (!rosidl_runtime_c__String__Sequence__copy(
      &(input->dynamic_units), &(output->dynamic_units)))
  {
    return false;
  }
  return true;
}

hybrid_automaton_interfaces__msg__DynamicParameter *
hybrid_automaton_interfaces__msg__DynamicParameter__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__DynamicParameter * msg = (hybrid_automaton_interfaces__msg__DynamicParameter *)allocator.allocate(sizeof(hybrid_automaton_interfaces__msg__DynamicParameter), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(hybrid_automaton_interfaces__msg__DynamicParameter));
  bool success = hybrid_automaton_interfaces__msg__DynamicParameter__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
hybrid_automaton_interfaces__msg__DynamicParameter__destroy(hybrid_automaton_interfaces__msg__DynamicParameter * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    hybrid_automaton_interfaces__msg__DynamicParameter__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
hybrid_automaton_interfaces__msg__DynamicParameter__Sequence__init(hybrid_automaton_interfaces__msg__DynamicParameter__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__DynamicParameter * data = NULL;

  if (size) {
    data = (hybrid_automaton_interfaces__msg__DynamicParameter *)allocator.zero_allocate(size, sizeof(hybrid_automaton_interfaces__msg__DynamicParameter), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = hybrid_automaton_interfaces__msg__DynamicParameter__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        hybrid_automaton_interfaces__msg__DynamicParameter__fini(&data[i - 1]);
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
hybrid_automaton_interfaces__msg__DynamicParameter__Sequence__fini(hybrid_automaton_interfaces__msg__DynamicParameter__Sequence * array)
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
      hybrid_automaton_interfaces__msg__DynamicParameter__fini(&array->data[i]);
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

hybrid_automaton_interfaces__msg__DynamicParameter__Sequence *
hybrid_automaton_interfaces__msg__DynamicParameter__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__DynamicParameter__Sequence * array = (hybrid_automaton_interfaces__msg__DynamicParameter__Sequence *)allocator.allocate(sizeof(hybrid_automaton_interfaces__msg__DynamicParameter__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = hybrid_automaton_interfaces__msg__DynamicParameter__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
hybrid_automaton_interfaces__msg__DynamicParameter__Sequence__destroy(hybrid_automaton_interfaces__msg__DynamicParameter__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    hybrid_automaton_interfaces__msg__DynamicParameter__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
hybrid_automaton_interfaces__msg__DynamicParameter__Sequence__are_equal(const hybrid_automaton_interfaces__msg__DynamicParameter__Sequence * lhs, const hybrid_automaton_interfaces__msg__DynamicParameter__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!hybrid_automaton_interfaces__msg__DynamicParameter__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
hybrid_automaton_interfaces__msg__DynamicParameter__Sequence__copy(
  const hybrid_automaton_interfaces__msg__DynamicParameter__Sequence * input,
  hybrid_automaton_interfaces__msg__DynamicParameter__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(hybrid_automaton_interfaces__msg__DynamicParameter);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    hybrid_automaton_interfaces__msg__DynamicParameter * data =
      (hybrid_automaton_interfaces__msg__DynamicParameter *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!hybrid_automaton_interfaces__msg__DynamicParameter__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          hybrid_automaton_interfaces__msg__DynamicParameter__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!hybrid_automaton_interfaces__msg__DynamicParameter__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
