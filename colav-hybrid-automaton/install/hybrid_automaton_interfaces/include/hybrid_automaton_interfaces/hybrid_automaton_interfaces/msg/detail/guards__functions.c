// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from hybrid_automaton_interfaces:msg/Guards.idl
// generated code does not contain a copyright notice
#include "hybrid_automaton_interfaces/msg/detail/guards__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `control_mode`
// Member `transition_eval_id`
// Member `guard_names`
// Member `error_message`
#include "rosidl_runtime_c/string_functions.h"
// Member `timestamp`
#include "builtin_interfaces/msg/detail/time__functions.h"

bool
hybrid_automaton_interfaces__msg__Guards__init(hybrid_automaton_interfaces__msg__Guards * msg)
{
  if (!msg) {
    return false;
  }
  // control_mode
  if (!rosidl_runtime_c__String__init(&msg->control_mode)) {
    hybrid_automaton_interfaces__msg__Guards__fini(msg);
    return false;
  }
  // transition_eval_id
  if (!rosidl_runtime_c__String__init(&msg->transition_eval_id)) {
    hybrid_automaton_interfaces__msg__Guards__fini(msg);
    return false;
  }
  // transition_pending
  // guard_names
  if (!rosidl_runtime_c__String__Sequence__init(&msg->guard_names, 0)) {
    hybrid_automaton_interfaces__msg__Guards__fini(msg);
    return false;
  }
  // cruise_to_t2los_1
  // cruise_to_t2los_2
  // cruise_to_waypoint_reached
  // cruise_to_fb
  // t2los_to_cruise
  // t2los_to_fb
  // t2los_to_waypoint_reached
  // waypoint_reached_to_cruise
  // timestamp
  if (!builtin_interfaces__msg__Time__init(&msg->timestamp)) {
    hybrid_automaton_interfaces__msg__Guards__fini(msg);
    return false;
  }
  // error
  // error_message
  if (!rosidl_runtime_c__String__init(&msg->error_message)) {
    hybrid_automaton_interfaces__msg__Guards__fini(msg);
    return false;
  }
  return true;
}

void
hybrid_automaton_interfaces__msg__Guards__fini(hybrid_automaton_interfaces__msg__Guards * msg)
{
  if (!msg) {
    return;
  }
  // control_mode
  rosidl_runtime_c__String__fini(&msg->control_mode);
  // transition_eval_id
  rosidl_runtime_c__String__fini(&msg->transition_eval_id);
  // transition_pending
  // guard_names
  rosidl_runtime_c__String__Sequence__fini(&msg->guard_names);
  // cruise_to_t2los_1
  // cruise_to_t2los_2
  // cruise_to_waypoint_reached
  // cruise_to_fb
  // t2los_to_cruise
  // t2los_to_fb
  // t2los_to_waypoint_reached
  // waypoint_reached_to_cruise
  // timestamp
  builtin_interfaces__msg__Time__fini(&msg->timestamp);
  // error
  // error_message
  rosidl_runtime_c__String__fini(&msg->error_message);
}

bool
hybrid_automaton_interfaces__msg__Guards__are_equal(const hybrid_automaton_interfaces__msg__Guards * lhs, const hybrid_automaton_interfaces__msg__Guards * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // control_mode
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->control_mode), &(rhs->control_mode)))
  {
    return false;
  }
  // transition_eval_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->transition_eval_id), &(rhs->transition_eval_id)))
  {
    return false;
  }
  // transition_pending
  if (lhs->transition_pending != rhs->transition_pending) {
    return false;
  }
  // guard_names
  if (!rosidl_runtime_c__String__Sequence__are_equal(
      &(lhs->guard_names), &(rhs->guard_names)))
  {
    return false;
  }
  // cruise_to_t2los_1
  if (lhs->cruise_to_t2los_1 != rhs->cruise_to_t2los_1) {
    return false;
  }
  // cruise_to_t2los_2
  if (lhs->cruise_to_t2los_2 != rhs->cruise_to_t2los_2) {
    return false;
  }
  // cruise_to_waypoint_reached
  if (lhs->cruise_to_waypoint_reached != rhs->cruise_to_waypoint_reached) {
    return false;
  }
  // cruise_to_fb
  if (lhs->cruise_to_fb != rhs->cruise_to_fb) {
    return false;
  }
  // t2los_to_cruise
  if (lhs->t2los_to_cruise != rhs->t2los_to_cruise) {
    return false;
  }
  // t2los_to_fb
  if (lhs->t2los_to_fb != rhs->t2los_to_fb) {
    return false;
  }
  // t2los_to_waypoint_reached
  if (lhs->t2los_to_waypoint_reached != rhs->t2los_to_waypoint_reached) {
    return false;
  }
  // waypoint_reached_to_cruise
  if (lhs->waypoint_reached_to_cruise != rhs->waypoint_reached_to_cruise) {
    return false;
  }
  // timestamp
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->timestamp), &(rhs->timestamp)))
  {
    return false;
  }
  // error
  if (lhs->error != rhs->error) {
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
hybrid_automaton_interfaces__msg__Guards__copy(
  const hybrid_automaton_interfaces__msg__Guards * input,
  hybrid_automaton_interfaces__msg__Guards * output)
{
  if (!input || !output) {
    return false;
  }
  // control_mode
  if (!rosidl_runtime_c__String__copy(
      &(input->control_mode), &(output->control_mode)))
  {
    return false;
  }
  // transition_eval_id
  if (!rosidl_runtime_c__String__copy(
      &(input->transition_eval_id), &(output->transition_eval_id)))
  {
    return false;
  }
  // transition_pending
  output->transition_pending = input->transition_pending;
  // guard_names
  if (!rosidl_runtime_c__String__Sequence__copy(
      &(input->guard_names), &(output->guard_names)))
  {
    return false;
  }
  // cruise_to_t2los_1
  output->cruise_to_t2los_1 = input->cruise_to_t2los_1;
  // cruise_to_t2los_2
  output->cruise_to_t2los_2 = input->cruise_to_t2los_2;
  // cruise_to_waypoint_reached
  output->cruise_to_waypoint_reached = input->cruise_to_waypoint_reached;
  // cruise_to_fb
  output->cruise_to_fb = input->cruise_to_fb;
  // t2los_to_cruise
  output->t2los_to_cruise = input->t2los_to_cruise;
  // t2los_to_fb
  output->t2los_to_fb = input->t2los_to_fb;
  // t2los_to_waypoint_reached
  output->t2los_to_waypoint_reached = input->t2los_to_waypoint_reached;
  // waypoint_reached_to_cruise
  output->waypoint_reached_to_cruise = input->waypoint_reached_to_cruise;
  // timestamp
  if (!builtin_interfaces__msg__Time__copy(
      &(input->timestamp), &(output->timestamp)))
  {
    return false;
  }
  // error
  output->error = input->error;
  // error_message
  if (!rosidl_runtime_c__String__copy(
      &(input->error_message), &(output->error_message)))
  {
    return false;
  }
  return true;
}

hybrid_automaton_interfaces__msg__Guards *
hybrid_automaton_interfaces__msg__Guards__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__Guards * msg = (hybrid_automaton_interfaces__msg__Guards *)allocator.allocate(sizeof(hybrid_automaton_interfaces__msg__Guards), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(hybrid_automaton_interfaces__msg__Guards));
  bool success = hybrid_automaton_interfaces__msg__Guards__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
hybrid_automaton_interfaces__msg__Guards__destroy(hybrid_automaton_interfaces__msg__Guards * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    hybrid_automaton_interfaces__msg__Guards__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
hybrid_automaton_interfaces__msg__Guards__Sequence__init(hybrid_automaton_interfaces__msg__Guards__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__Guards * data = NULL;

  if (size) {
    data = (hybrid_automaton_interfaces__msg__Guards *)allocator.zero_allocate(size, sizeof(hybrid_automaton_interfaces__msg__Guards), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = hybrid_automaton_interfaces__msg__Guards__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        hybrid_automaton_interfaces__msg__Guards__fini(&data[i - 1]);
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
hybrid_automaton_interfaces__msg__Guards__Sequence__fini(hybrid_automaton_interfaces__msg__Guards__Sequence * array)
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
      hybrid_automaton_interfaces__msg__Guards__fini(&array->data[i]);
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

hybrid_automaton_interfaces__msg__Guards__Sequence *
hybrid_automaton_interfaces__msg__Guards__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__Guards__Sequence * array = (hybrid_automaton_interfaces__msg__Guards__Sequence *)allocator.allocate(sizeof(hybrid_automaton_interfaces__msg__Guards__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = hybrid_automaton_interfaces__msg__Guards__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
hybrid_automaton_interfaces__msg__Guards__Sequence__destroy(hybrid_automaton_interfaces__msg__Guards__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    hybrid_automaton_interfaces__msg__Guards__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
hybrid_automaton_interfaces__msg__Guards__Sequence__are_equal(const hybrid_automaton_interfaces__msg__Guards__Sequence * lhs, const hybrid_automaton_interfaces__msg__Guards__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!hybrid_automaton_interfaces__msg__Guards__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
hybrid_automaton_interfaces__msg__Guards__Sequence__copy(
  const hybrid_automaton_interfaces__msg__Guards__Sequence * input,
  hybrid_automaton_interfaces__msg__Guards__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(hybrid_automaton_interfaces__msg__Guards);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    hybrid_automaton_interfaces__msg__Guards * data =
      (hybrid_automaton_interfaces__msg__Guards *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!hybrid_automaton_interfaces__msg__Guards__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          hybrid_automaton_interfaces__msg__Guards__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!hybrid_automaton_interfaces__msg__Guards__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
