// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from hybrid_automaton_interfaces:msg/Transition.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "hybrid_automaton_interfaces/msg/detail/transition__rosidl_typesupport_introspection_c.h"
#include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "hybrid_automaton_interfaces/msg/detail/transition__functions.h"
#include "hybrid_automaton_interfaces/msg/detail/transition__struct.h"


// Include directives for member types
// Member `transition_uuid`
#include "unique_identifier_msgs/msg/uuid.h"
// Member `transition_uuid`
#include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"
// Member `mode`
// Member `transition_names`
// Member `error_message`
#include "rosidl_runtime_c/string_functions.h"
// Member `transition_values`
// Member `transition_priority`
#include "rosidl_runtime_c/primitives_sequence_functions.h"
// Member `stamp`
#include "builtin_interfaces/msg/time.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__Transition_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__msg__Transition__init(message_memory);
}

void hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__Transition_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__msg__Transition__fini(message_memory);
}

size_t hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__size_function__Transition__transition_names(
  const void * untyped_member)
{
  const rosidl_runtime_c__String__Sequence * member =
    (const rosidl_runtime_c__String__Sequence *)(untyped_member);
  return member->size;
}

const void * hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_const_function__Transition__transition_names(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__String__Sequence * member =
    (const rosidl_runtime_c__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void * hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_function__Transition__transition_names(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__String__Sequence * member =
    (rosidl_runtime_c__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__fetch_function__Transition__transition_names(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const rosidl_runtime_c__String * item =
    ((const rosidl_runtime_c__String *)
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_const_function__Transition__transition_names(untyped_member, index));
  rosidl_runtime_c__String * value =
    (rosidl_runtime_c__String *)(untyped_value);
  *value = *item;
}

void hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__assign_function__Transition__transition_names(
  void * untyped_member, size_t index, const void * untyped_value)
{
  rosidl_runtime_c__String * item =
    ((rosidl_runtime_c__String *)
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_function__Transition__transition_names(untyped_member, index));
  const rosidl_runtime_c__String * value =
    (const rosidl_runtime_c__String *)(untyped_value);
  *item = *value;
}

bool hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__resize_function__Transition__transition_names(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__String__Sequence * member =
    (rosidl_runtime_c__String__Sequence *)(untyped_member);
  rosidl_runtime_c__String__Sequence__fini(member);
  return rosidl_runtime_c__String__Sequence__init(member, size);
}

size_t hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__size_function__Transition__transition_values(
  const void * untyped_member)
{
  const rosidl_runtime_c__boolean__Sequence * member =
    (const rosidl_runtime_c__boolean__Sequence *)(untyped_member);
  return member->size;
}

const void * hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_const_function__Transition__transition_values(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__boolean__Sequence * member =
    (const rosidl_runtime_c__boolean__Sequence *)(untyped_member);
  return &member->data[index];
}

void * hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_function__Transition__transition_values(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__boolean__Sequence * member =
    (rosidl_runtime_c__boolean__Sequence *)(untyped_member);
  return &member->data[index];
}

void hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__fetch_function__Transition__transition_values(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const bool * item =
    ((const bool *)
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_const_function__Transition__transition_values(untyped_member, index));
  bool * value =
    (bool *)(untyped_value);
  *value = *item;
}

void hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__assign_function__Transition__transition_values(
  void * untyped_member, size_t index, const void * untyped_value)
{
  bool * item =
    ((bool *)
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_function__Transition__transition_values(untyped_member, index));
  const bool * value =
    (const bool *)(untyped_value);
  *item = *value;
}

bool hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__resize_function__Transition__transition_values(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__boolean__Sequence * member =
    (rosidl_runtime_c__boolean__Sequence *)(untyped_member);
  rosidl_runtime_c__boolean__Sequence__fini(member);
  return rosidl_runtime_c__boolean__Sequence__init(member, size);
}

size_t hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__size_function__Transition__transition_priority(
  const void * untyped_member)
{
  const rosidl_runtime_c__int32__Sequence * member =
    (const rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return member->size;
}

const void * hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_const_function__Transition__transition_priority(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__int32__Sequence * member =
    (const rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return &member->data[index];
}

void * hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_function__Transition__transition_priority(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__int32__Sequence * member =
    (rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return &member->data[index];
}

void hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__fetch_function__Transition__transition_priority(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int32_t * item =
    ((const int32_t *)
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_const_function__Transition__transition_priority(untyped_member, index));
  int32_t * value =
    (int32_t *)(untyped_value);
  *value = *item;
}

void hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__assign_function__Transition__transition_priority(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int32_t * item =
    ((int32_t *)
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_function__Transition__transition_priority(untyped_member, index));
  const int32_t * value =
    (const int32_t *)(untyped_value);
  *item = *value;
}

bool hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__resize_function__Transition__transition_priority(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__int32__Sequence * member =
    (rosidl_runtime_c__int32__Sequence *)(untyped_member);
  rosidl_runtime_c__int32__Sequence__fini(member);
  return rosidl_runtime_c__int32__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__Transition_message_member_array[8] = {
  {
    "transition_uuid",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Transition, transition_uuid),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "mode",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Transition, mode),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "transition_names",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Transition, transition_names),  // bytes offset in struct
    NULL,  // default value
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__size_function__Transition__transition_names,  // size() function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_const_function__Transition__transition_names,  // get_const(index) function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_function__Transition__transition_names,  // get(index) function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__fetch_function__Transition__transition_names,  // fetch(index, &value) function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__assign_function__Transition__transition_names,  // assign(index, value) function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__resize_function__Transition__transition_names  // resize(index) function pointer
  },
  {
    "transition_values",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Transition, transition_values),  // bytes offset in struct
    NULL,  // default value
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__size_function__Transition__transition_values,  // size() function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_const_function__Transition__transition_values,  // get_const(index) function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_function__Transition__transition_values,  // get(index) function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__fetch_function__Transition__transition_values,  // fetch(index, &value) function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__assign_function__Transition__transition_values,  // assign(index, value) function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__resize_function__Transition__transition_values  // resize(index) function pointer
  },
  {
    "transition_priority",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Transition, transition_priority),  // bytes offset in struct
    NULL,  // default value
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__size_function__Transition__transition_priority,  // size() function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_const_function__Transition__transition_priority,  // get_const(index) function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__get_function__Transition__transition_priority,  // get(index) function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__fetch_function__Transition__transition_priority,  // fetch(index, &value) function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__assign_function__Transition__transition_priority,  // assign(index, value) function pointer
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__resize_function__Transition__transition_priority  // resize(index) function pointer
  },
  {
    "stamp",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Transition, stamp),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "success",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Transition, success),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "error_message",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Transition, error_message),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__Transition_message_members = {
  "hybrid_automaton_interfaces__msg",  // message namespace
  "Transition",  // message name
  8,  // number of fields
  sizeof(hybrid_automaton_interfaces__msg__Transition),
  hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__Transition_message_member_array,  // message members
  hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__Transition_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__Transition_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__Transition_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__Transition_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, msg, Transition)() {
  hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__Transition_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__Transition_message_member_array[5].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Time)();
  if (!hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__Transition_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__Transition_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__msg__Transition__rosidl_typesupport_introspection_c__Transition_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
