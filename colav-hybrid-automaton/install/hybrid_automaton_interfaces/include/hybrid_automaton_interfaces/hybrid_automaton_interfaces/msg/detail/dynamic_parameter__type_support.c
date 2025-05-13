// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from hybrid_automaton_interfaces:msg/DynamicParameter.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "hybrid_automaton_interfaces/msg/detail/dynamic_parameter__rosidl_typesupport_introspection_c.h"
#include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "hybrid_automaton_interfaces/msg/detail/dynamic_parameter__functions.h"
#include "hybrid_automaton_interfaces/msg/detail/dynamic_parameter__struct.h"


// Include directives for member types
// Member `controller_name`
// Member `dynamic_name`
// Member `dynamic_units`
#include "rosidl_runtime_c/string_functions.h"
// Member `dynamic_value`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__DynamicParameter_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__msg__DynamicParameter__init(message_memory);
}

void hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__DynamicParameter_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__msg__DynamicParameter__fini(message_memory);
}

size_t hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__size_function__DynamicParameter__dynamic_name(
  const void * untyped_member)
{
  const rosidl_runtime_c__String__Sequence * member =
    (const rosidl_runtime_c__String__Sequence *)(untyped_member);
  return member->size;
}

const void * hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_const_function__DynamicParameter__dynamic_name(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__String__Sequence * member =
    (const rosidl_runtime_c__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void * hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_function__DynamicParameter__dynamic_name(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__String__Sequence * member =
    (rosidl_runtime_c__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__fetch_function__DynamicParameter__dynamic_name(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const rosidl_runtime_c__String * item =
    ((const rosidl_runtime_c__String *)
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_const_function__DynamicParameter__dynamic_name(untyped_member, index));
  rosidl_runtime_c__String * value =
    (rosidl_runtime_c__String *)(untyped_value);
  *value = *item;
}

void hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__assign_function__DynamicParameter__dynamic_name(
  void * untyped_member, size_t index, const void * untyped_value)
{
  rosidl_runtime_c__String * item =
    ((rosidl_runtime_c__String *)
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_function__DynamicParameter__dynamic_name(untyped_member, index));
  const rosidl_runtime_c__String * value =
    (const rosidl_runtime_c__String *)(untyped_value);
  *item = *value;
}

bool hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__resize_function__DynamicParameter__dynamic_name(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__String__Sequence * member =
    (rosidl_runtime_c__String__Sequence *)(untyped_member);
  rosidl_runtime_c__String__Sequence__fini(member);
  return rosidl_runtime_c__String__Sequence__init(member, size);
}

size_t hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__size_function__DynamicParameter__dynamic_value(
  const void * untyped_member)
{
  const rosidl_runtime_c__double__Sequence * member =
    (const rosidl_runtime_c__double__Sequence *)(untyped_member);
  return member->size;
}

const void * hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_const_function__DynamicParameter__dynamic_value(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__double__Sequence * member =
    (const rosidl_runtime_c__double__Sequence *)(untyped_member);
  return &member->data[index];
}

void * hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_function__DynamicParameter__dynamic_value(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__double__Sequence * member =
    (rosidl_runtime_c__double__Sequence *)(untyped_member);
  return &member->data[index];
}

void hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__fetch_function__DynamicParameter__dynamic_value(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const double * item =
    ((const double *)
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_const_function__DynamicParameter__dynamic_value(untyped_member, index));
  double * value =
    (double *)(untyped_value);
  *value = *item;
}

void hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__assign_function__DynamicParameter__dynamic_value(
  void * untyped_member, size_t index, const void * untyped_value)
{
  double * item =
    ((double *)
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_function__DynamicParameter__dynamic_value(untyped_member, index));
  const double * value =
    (const double *)(untyped_value);
  *item = *value;
}

bool hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__resize_function__DynamicParameter__dynamic_value(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__double__Sequence * member =
    (rosidl_runtime_c__double__Sequence *)(untyped_member);
  rosidl_runtime_c__double__Sequence__fini(member);
  return rosidl_runtime_c__double__Sequence__init(member, size);
}

size_t hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__size_function__DynamicParameter__dynamic_units(
  const void * untyped_member)
{
  const rosidl_runtime_c__String__Sequence * member =
    (const rosidl_runtime_c__String__Sequence *)(untyped_member);
  return member->size;
}

const void * hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_const_function__DynamicParameter__dynamic_units(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__String__Sequence * member =
    (const rosidl_runtime_c__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void * hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_function__DynamicParameter__dynamic_units(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__String__Sequence * member =
    (rosidl_runtime_c__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__fetch_function__DynamicParameter__dynamic_units(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const rosidl_runtime_c__String * item =
    ((const rosidl_runtime_c__String *)
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_const_function__DynamicParameter__dynamic_units(untyped_member, index));
  rosidl_runtime_c__String * value =
    (rosidl_runtime_c__String *)(untyped_value);
  *value = *item;
}

void hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__assign_function__DynamicParameter__dynamic_units(
  void * untyped_member, size_t index, const void * untyped_value)
{
  rosidl_runtime_c__String * item =
    ((rosidl_runtime_c__String *)
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_function__DynamicParameter__dynamic_units(untyped_member, index));
  const rosidl_runtime_c__String * value =
    (const rosidl_runtime_c__String *)(untyped_value);
  *item = *value;
}

bool hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__resize_function__DynamicParameter__dynamic_units(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__String__Sequence * member =
    (rosidl_runtime_c__String__Sequence *)(untyped_member);
  rosidl_runtime_c__String__Sequence__fini(member);
  return rosidl_runtime_c__String__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__DynamicParameter_message_member_array[4] = {
  {
    "controller_name",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__DynamicParameter, controller_name),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "dynamic_name",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__DynamicParameter, dynamic_name),  // bytes offset in struct
    NULL,  // default value
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__size_function__DynamicParameter__dynamic_name,  // size() function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_const_function__DynamicParameter__dynamic_name,  // get_const(index) function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_function__DynamicParameter__dynamic_name,  // get(index) function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__fetch_function__DynamicParameter__dynamic_name,  // fetch(index, &value) function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__assign_function__DynamicParameter__dynamic_name,  // assign(index, value) function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__resize_function__DynamicParameter__dynamic_name  // resize(index) function pointer
  },
  {
    "dynamic_value",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__DynamicParameter, dynamic_value),  // bytes offset in struct
    NULL,  // default value
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__size_function__DynamicParameter__dynamic_value,  // size() function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_const_function__DynamicParameter__dynamic_value,  // get_const(index) function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_function__DynamicParameter__dynamic_value,  // get(index) function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__fetch_function__DynamicParameter__dynamic_value,  // fetch(index, &value) function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__assign_function__DynamicParameter__dynamic_value,  // assign(index, value) function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__resize_function__DynamicParameter__dynamic_value  // resize(index) function pointer
  },
  {
    "dynamic_units",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__DynamicParameter, dynamic_units),  // bytes offset in struct
    NULL,  // default value
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__size_function__DynamicParameter__dynamic_units,  // size() function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_const_function__DynamicParameter__dynamic_units,  // get_const(index) function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__get_function__DynamicParameter__dynamic_units,  // get(index) function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__fetch_function__DynamicParameter__dynamic_units,  // fetch(index, &value) function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__assign_function__DynamicParameter__dynamic_units,  // assign(index, value) function pointer
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__resize_function__DynamicParameter__dynamic_units  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__DynamicParameter_message_members = {
  "hybrid_automaton_interfaces__msg",  // message namespace
  "DynamicParameter",  // message name
  4,  // number of fields
  sizeof(hybrid_automaton_interfaces__msg__DynamicParameter),
  hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__DynamicParameter_message_member_array,  // message members
  hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__DynamicParameter_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__DynamicParameter_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__DynamicParameter_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__DynamicParameter_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, msg, DynamicParameter)() {
  if (!hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__DynamicParameter_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__DynamicParameter_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__msg__DynamicParameter__rosidl_typesupport_introspection_c__DynamicParameter_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
