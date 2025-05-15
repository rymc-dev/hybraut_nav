// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from hybrid_automaton_interfaces:msg/Output.idl
// generated code does not contain a copyright notice
#include "hybrid_automaton_interfaces/msg/detail/output__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `automaton_uuid`
#include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `mode`
// Member `status`
// Member `message`
#include "rosidl_runtime_c/string_functions.h"
// Member `dynamics`
#include "hybrid_automaton_interfaces/msg/detail/dynamic_parameter__functions.h"
// Member `time_since_last_transition`
// Member `elapsed_time`
#include "builtin_interfaces/msg/detail/duration__functions.h"
// Member `transition_pending`
#include "hybrid_automaton_interfaces/msg/detail/transition_pending__functions.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"
// Member `waypoints`
#include "colav_interfaces/msg/detail/waypoints__functions.h"

bool
hybrid_automaton_interfaces__msg__Output__init(hybrid_automaton_interfaces__msg__Output * msg)
{
  if (!msg) {
    return false;
  }
  // automaton_uuid
  if (!unique_identifier_msgs__msg__UUID__init(&msg->automaton_uuid)) {
    hybrid_automaton_interfaces__msg__Output__fini(msg);
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__init(&msg->mode)) {
    hybrid_automaton_interfaces__msg__Output__fini(msg);
    return false;
  }
  // status
  if (!rosidl_runtime_c__String__init(&msg->status)) {
    hybrid_automaton_interfaces__msg__Output__fini(msg);
    return false;
  }
  // dynamics
  if (!hybrid_automaton_interfaces__msg__DynamicParameter__init(&msg->dynamics)) {
    hybrid_automaton_interfaces__msg__Output__fini(msg);
    return false;
  }
  // time_since_last_transition
  if (!builtin_interfaces__msg__Duration__init(&msg->time_since_last_transition)) {
    hybrid_automaton_interfaces__msg__Output__fini(msg);
    return false;
  }
  // transition_pending
  if (!hybrid_automaton_interfaces__msg__TransitionPending__init(&msg->transition_pending)) {
    hybrid_automaton_interfaces__msg__Output__fini(msg);
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    hybrid_automaton_interfaces__msg__Output__fini(msg);
    return false;
  }
  // elapsed_time
  if (!builtin_interfaces__msg__Duration__init(&msg->elapsed_time)) {
    hybrid_automaton_interfaces__msg__Output__fini(msg);
    return false;
  }
  // waypoints
  if (!colav_interfaces__msg__Waypoints__init(&msg->waypoints)) {
    hybrid_automaton_interfaces__msg__Output__fini(msg);
    return false;
  }
  // error
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    hybrid_automaton_interfaces__msg__Output__fini(msg);
    return false;
  }
  return true;
}

void
hybrid_automaton_interfaces__msg__Output__fini(hybrid_automaton_interfaces__msg__Output * msg)
{
  if (!msg) {
    return;
  }
  // automaton_uuid
  unique_identifier_msgs__msg__UUID__fini(&msg->automaton_uuid);
  // mode
  rosidl_runtime_c__String__fini(&msg->mode);
  // status
  rosidl_runtime_c__String__fini(&msg->status);
  // dynamics
  hybrid_automaton_interfaces__msg__DynamicParameter__fini(&msg->dynamics);
  // time_since_last_transition
  builtin_interfaces__msg__Duration__fini(&msg->time_since_last_transition);
  // transition_pending
  hybrid_automaton_interfaces__msg__TransitionPending__fini(&msg->transition_pending);
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
  // elapsed_time
  builtin_interfaces__msg__Duration__fini(&msg->elapsed_time);
  // waypoints
  colav_interfaces__msg__Waypoints__fini(&msg->waypoints);
  // error
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
hybrid_automaton_interfaces__msg__Output__are_equal(const hybrid_automaton_interfaces__msg__Output * lhs, const hybrid_automaton_interfaces__msg__Output * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // automaton_uuid
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->automaton_uuid), &(rhs->automaton_uuid)))
  {
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->mode), &(rhs->mode)))
  {
    return false;
  }
  // status
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->status), &(rhs->status)))
  {
    return false;
  }
  // dynamics
  if (!hybrid_automaton_interfaces__msg__DynamicParameter__are_equal(
      &(lhs->dynamics), &(rhs->dynamics)))
  {
    return false;
  }
  // time_since_last_transition
  if (!builtin_interfaces__msg__Duration__are_equal(
      &(lhs->time_since_last_transition), &(rhs->time_since_last_transition)))
  {
    return false;
  }
  // transition_pending
  if (!hybrid_automaton_interfaces__msg__TransitionPending__are_equal(
      &(lhs->transition_pending), &(rhs->transition_pending)))
  {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->stamp), &(rhs->stamp)))
  {
    return false;
  }
  // elapsed_time
  if (!builtin_interfaces__msg__Duration__are_equal(
      &(lhs->elapsed_time), &(rhs->elapsed_time)))
  {
    return false;
  }
  // waypoints
  if (!colav_interfaces__msg__Waypoints__are_equal(
      &(lhs->waypoints), &(rhs->waypoints)))
  {
    return false;
  }
  // error
  if (lhs->error != rhs->error) {
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
hybrid_automaton_interfaces__msg__Output__copy(
  const hybrid_automaton_interfaces__msg__Output * input,
  hybrid_automaton_interfaces__msg__Output * output)
{
  if (!input || !output) {
    return false;
  }
  // automaton_uuid
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->automaton_uuid), &(output->automaton_uuid)))
  {
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__copy(
      &(input->mode), &(output->mode)))
  {
    return false;
  }
  // status
  if (!rosidl_runtime_c__String__copy(
      &(input->status), &(output->status)))
  {
    return false;
  }
  // dynamics
  if (!hybrid_automaton_interfaces__msg__DynamicParameter__copy(
      &(input->dynamics), &(output->dynamics)))
  {
    return false;
  }
  // time_since_last_transition
  if (!builtin_interfaces__msg__Duration__copy(
      &(input->time_since_last_transition), &(output->time_since_last_transition)))
  {
    return false;
  }
  // transition_pending
  if (!hybrid_automaton_interfaces__msg__TransitionPending__copy(
      &(input->transition_pending), &(output->transition_pending)))
  {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__copy(
      &(input->stamp), &(output->stamp)))
  {
    return false;
  }
  // elapsed_time
  if (!builtin_interfaces__msg__Duration__copy(
      &(input->elapsed_time), &(output->elapsed_time)))
  {
    return false;
  }
  // waypoints
  if (!colav_interfaces__msg__Waypoints__copy(
      &(input->waypoints), &(output->waypoints)))
  {
    return false;
  }
  // error
  output->error = input->error;
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  return true;
}

hybrid_automaton_interfaces__msg__Output *
hybrid_automaton_interfaces__msg__Output__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__Output * msg = (hybrid_automaton_interfaces__msg__Output *)allocator.allocate(sizeof(hybrid_automaton_interfaces__msg__Output), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(hybrid_automaton_interfaces__msg__Output));
  bool success = hybrid_automaton_interfaces__msg__Output__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
hybrid_automaton_interfaces__msg__Output__destroy(hybrid_automaton_interfaces__msg__Output * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    hybrid_automaton_interfaces__msg__Output__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
hybrid_automaton_interfaces__msg__Output__Sequence__init(hybrid_automaton_interfaces__msg__Output__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__Output * data = NULL;

  if (size) {
    data = (hybrid_automaton_interfaces__msg__Output *)allocator.zero_allocate(size, sizeof(hybrid_automaton_interfaces__msg__Output), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = hybrid_automaton_interfaces__msg__Output__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        hybrid_automaton_interfaces__msg__Output__fini(&data[i - 1]);
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
hybrid_automaton_interfaces__msg__Output__Sequence__fini(hybrid_automaton_interfaces__msg__Output__Sequence * array)
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
      hybrid_automaton_interfaces__msg__Output__fini(&array->data[i]);
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

hybrid_automaton_interfaces__msg__Output__Sequence *
hybrid_automaton_interfaces__msg__Output__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__msg__Output__Sequence * array = (hybrid_automaton_interfaces__msg__Output__Sequence *)allocator.allocate(sizeof(hybrid_automaton_interfaces__msg__Output__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = hybrid_automaton_interfaces__msg__Output__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
hybrid_automaton_interfaces__msg__Output__Sequence__destroy(hybrid_automaton_interfaces__msg__Output__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    hybrid_automaton_interfaces__msg__Output__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
hybrid_automaton_interfaces__msg__Output__Sequence__are_equal(const hybrid_automaton_interfaces__msg__Output__Sequence * lhs, const hybrid_automaton_interfaces__msg__Output__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!hybrid_automaton_interfaces__msg__Output__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
hybrid_automaton_interfaces__msg__Output__Sequence__copy(
  const hybrid_automaton_interfaces__msg__Output__Sequence * input,
  hybrid_automaton_interfaces__msg__Output__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(hybrid_automaton_interfaces__msg__Output);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    hybrid_automaton_interfaces__msg__Output * data =
      (hybrid_automaton_interfaces__msg__Output *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!hybrid_automaton_interfaces__msg__Output__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          hybrid_automaton_interfaces__msg__Output__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!hybrid_automaton_interfaces__msg__Output__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
