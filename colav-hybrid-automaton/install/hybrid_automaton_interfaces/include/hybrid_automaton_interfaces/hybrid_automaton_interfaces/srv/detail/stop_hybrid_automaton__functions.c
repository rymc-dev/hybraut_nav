// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from hybrid_automaton_interfaces:srv/StopHybridAutomaton.idl
// generated code does not contain a copyright notice
#include "hybrid_automaton_interfaces/srv/detail/stop_hybrid_automaton__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"
// Member `automaton_uuid`
#include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `stop_reason`
#include "rosidl_runtime_c/string_functions.h"

bool
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__init(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request * msg)
{
  if (!msg) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__init(&msg->stamp)) {
    hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__fini(msg);
    return false;
  }
  // automaton_uuid
  if (!unique_identifier_msgs__msg__UUID__init(&msg->automaton_uuid)) {
    hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__fini(msg);
    return false;
  }
  // stop_reason
  if (!rosidl_runtime_c__String__init(&msg->stop_reason)) {
    hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__fini(msg);
    return false;
  }
  return true;
}

void
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__fini(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request * msg)
{
  if (!msg) {
    return;
  }
  // stamp
  builtin_interfaces__msg__Time__fini(&msg->stamp);
  // automaton_uuid
  unique_identifier_msgs__msg__UUID__fini(&msg->automaton_uuid);
  // stop_reason
  rosidl_runtime_c__String__fini(&msg->stop_reason);
}

bool
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__are_equal(const hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request * lhs, const hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->stamp), &(rhs->stamp)))
  {
    return false;
  }
  // automaton_uuid
  if (!unique_identifier_msgs__msg__UUID__are_equal(
      &(lhs->automaton_uuid), &(rhs->automaton_uuid)))
  {
    return false;
  }
  // stop_reason
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->stop_reason), &(rhs->stop_reason)))
  {
    return false;
  }
  return true;
}

bool
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__copy(
  const hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request * input,
  hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request * output)
{
  if (!input || !output) {
    return false;
  }
  // stamp
  if (!builtin_interfaces__msg__Time__copy(
      &(input->stamp), &(output->stamp)))
  {
    return false;
  }
  // automaton_uuid
  if (!unique_identifier_msgs__msg__UUID__copy(
      &(input->automaton_uuid), &(output->automaton_uuid)))
  {
    return false;
  }
  // stop_reason
  if (!rosidl_runtime_c__String__copy(
      &(input->stop_reason), &(output->stop_reason)))
  {
    return false;
  }
  return true;
}

hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request *
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request * msg = (hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request *)allocator.allocate(sizeof(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request));
  bool success = hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__destroy(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence__init(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request * data = NULL;

  if (size) {
    data = (hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request *)allocator.zero_allocate(size, sizeof(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__fini(&data[i - 1]);
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
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence__fini(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence * array)
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
      hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__fini(&array->data[i]);
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

hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence *
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence * array = (hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence *)allocator.allocate(sizeof(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence__destroy(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence__are_equal(const hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence * lhs, const hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence__copy(
  const hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence * input,
  hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request * data =
      (hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `automaton_uuid`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__functions.h"
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

bool
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__init(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response * msg)
{
  if (!msg) {
    return false;
  }
  // automaton_uuid
  if (!unique_identifier_msgs__msg__UUID__init(&msg->automaton_uuid)) {
    hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__fini(msg);
    return false;
  }
  // success
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__fini(msg);
    return false;
  }
  return true;
}

void
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__fini(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response * msg)
{
  if (!msg) {
    return;
  }
  // automaton_uuid
  unique_identifier_msgs__msg__UUID__fini(&msg->automaton_uuid);
  // success
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__are_equal(const hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response * lhs, const hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response * rhs)
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
  // success
  if (lhs->success != rhs->success) {
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
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__copy(
  const hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response * input,
  hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response * output)
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
  // success
  output->success = input->success;
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  return true;
}

hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response *
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response * msg = (hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response *)allocator.allocate(sizeof(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response));
  bool success = hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__destroy(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence__init(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response * data = NULL;

  if (size) {
    data = (hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response *)allocator.zero_allocate(size, sizeof(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__fini(&data[i - 1]);
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
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence__fini(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence * array)
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
      hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__fini(&array->data[i]);
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

hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence *
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence * array = (hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence *)allocator.allocate(sizeof(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence__destroy(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence__are_equal(const hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence * lhs, const hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence__copy(
  const hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence * input,
  hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response * data =
      (hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
