// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from hybrid_automaton_interfaces:msg/Mode.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "hybrid_automaton_interfaces/msg/detail/mode__rosidl_typesupport_introspection_c.h"
#include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "hybrid_automaton_interfaces/msg/detail/mode__functions.h"
#include "hybrid_automaton_interfaces/msg/detail/mode__struct.h"


// Include directives for member types
// Member `mode_uuid`
#include "unique_identifier_msgs/msg/uuid.h"
// Member `mode_uuid`
#include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"
// Member `mode`
// Member `origin_transition`
#include "rosidl_runtime_c/string_functions.h"
// Member `stamp`
#include "builtin_interfaces/msg/time.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__msg__Mode__rosidl_typesupport_introspection_c__Mode_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__msg__Mode__init(message_memory);
}

void hybrid_automaton_interfaces__msg__Mode__rosidl_typesupport_introspection_c__Mode_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__msg__Mode__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__msg__Mode__rosidl_typesupport_introspection_c__Mode_message_member_array[4] = {
  {
    "mode_uuid",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Mode, mode_uuid),  // bytes offset in struct
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
    offsetof(hybrid_automaton_interfaces__msg__Mode, mode),  // bytes offset in struct
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
    offsetof(hybrid_automaton_interfaces__msg__Mode, stamp),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "origin_transition",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Mode, origin_transition),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__msg__Mode__rosidl_typesupport_introspection_c__Mode_message_members = {
  "hybrid_automaton_interfaces__msg",  // message namespace
  "Mode",  // message name
  4,  // number of fields
  sizeof(hybrid_automaton_interfaces__msg__Mode),
  hybrid_automaton_interfaces__msg__Mode__rosidl_typesupport_introspection_c__Mode_message_member_array,  // message members
  hybrid_automaton_interfaces__msg__Mode__rosidl_typesupport_introspection_c__Mode_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__msg__Mode__rosidl_typesupport_introspection_c__Mode_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__msg__Mode__rosidl_typesupport_introspection_c__Mode_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__msg__Mode__rosidl_typesupport_introspection_c__Mode_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, msg, Mode)() {
  hybrid_automaton_interfaces__msg__Mode__rosidl_typesupport_introspection_c__Mode_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  hybrid_automaton_interfaces__msg__Mode__rosidl_typesupport_introspection_c__Mode_message_member_array[2].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Time)();
  if (!hybrid_automaton_interfaces__msg__Mode__rosidl_typesupport_introspection_c__Mode_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__msg__Mode__rosidl_typesupport_introspection_c__Mode_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__msg__Mode__rosidl_typesupport_introspection_c__Mode_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
