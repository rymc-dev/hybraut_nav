// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from hybrid_automaton_interfaces:msg/Dynamics.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "hybrid_automaton_interfaces/msg/detail/dynamics__rosidl_typesupport_introspection_c.h"
#include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "hybrid_automaton_interfaces/msg/detail/dynamics__functions.h"
#include "hybrid_automaton_interfaces/msg/detail/dynamics__struct.h"


// Include directives for member types
// Member `dynamic_uuid`
#include "unique_identifier_msgs/msg/uuid.h"
// Member `dynamic_uuid`
#include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"
// Member `mode`
// Member `error_message`
#include "rosidl_runtime_c/string_functions.h"
// Member `dynamic_parameters`
#include "hybrid_automaton_interfaces/msg/dynamic_parameter.h"
// Member `dynamic_parameters`
#include "hybrid_automaton_interfaces/msg/detail/dynamic_parameter__rosidl_typesupport_introspection_c.h"
// Member `stamp`
#include "builtin_interfaces/msg/time.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__msg__Dynamics__init(message_memory);
}

void hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__msg__Dynamics__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_message_member_array[6] = {
  {
    "dynamic_uuid",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Dynamics, dynamic_uuid),  // bytes offset in struct
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
    offsetof(hybrid_automaton_interfaces__msg__Dynamics, mode),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "dynamic_parameters",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Dynamics, dynamic_parameters),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "stamp",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Dynamics, stamp),  // bytes offset in struct
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
    offsetof(hybrid_automaton_interfaces__msg__Dynamics, success),  // bytes offset in struct
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
    offsetof(hybrid_automaton_interfaces__msg__Dynamics, error_message),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_message_members = {
  "hybrid_automaton_interfaces__msg",  // message namespace
  "Dynamics",  // message name
  6,  // number of fields
  sizeof(hybrid_automaton_interfaces__msg__Dynamics),
  hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_message_member_array,  // message members
  hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, msg, Dynamics)() {
  hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_message_member_array[2].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, msg, DynamicParameter)();
  hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_message_member_array[3].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Time)();
  if (!hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__msg__Dynamics__rosidl_typesupport_introspection_c__Dynamics_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
