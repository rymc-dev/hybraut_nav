// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from hybrid_automaton_interfaces:msg/Output.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "hybrid_automaton_interfaces/msg/detail/output__rosidl_typesupport_introspection_c.h"
#include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "hybrid_automaton_interfaces/msg/detail/output__functions.h"
#include "hybrid_automaton_interfaces/msg/detail/output__struct.h"


// Include directives for member types
// Member `automaton_uuid`
#include "unique_identifier_msgs/msg/uuid.h"
// Member `automaton_uuid`
#include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"
// Member `mode`
// Member `status`
// Member `message`
#include "rosidl_runtime_c/string_functions.h"
// Member `dynamics`
#include "hybrid_automaton_interfaces/msg/dynamic_parameter.h"
// Member `dynamics`
#include "hybrid_automaton_interfaces/msg/detail/dynamic_parameter__rosidl_typesupport_introspection_c.h"
// Member `time_since_last_transition`
// Member `elapsed_time`
#include "builtin_interfaces/msg/duration.h"
// Member `time_since_last_transition`
// Member `elapsed_time`
#include "builtin_interfaces/msg/detail/duration__rosidl_typesupport_introspection_c.h"
// Member `transition_pending`
#include "hybrid_automaton_interfaces/msg/transition_pending.h"
// Member `transition_pending`
#include "hybrid_automaton_interfaces/msg/detail/transition_pending__rosidl_typesupport_introspection_c.h"
// Member `stamp`
#include "builtin_interfaces/msg/time.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__rosidl_typesupport_introspection_c.h"
// Member `waypoints`
#include "colav_interfaces/msg/waypoints.h"
// Member `waypoints`
#include "colav_interfaces/msg/detail/waypoints__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__msg__Output__init(message_memory);
}

void hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__msg__Output__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_member_array[11] = {
  {
    "automaton_uuid",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Output, automaton_uuid),  // bytes offset in struct
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
    offsetof(hybrid_automaton_interfaces__msg__Output, mode),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "status",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Output, status),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "dynamics",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Output, dynamics),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "time_since_last_transition",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Output, time_since_last_transition),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "transition_pending",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Output, transition_pending),  // bytes offset in struct
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
    offsetof(hybrid_automaton_interfaces__msg__Output, stamp),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "elapsed_time",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Output, elapsed_time),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "waypoints",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Output, waypoints),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "error",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Output, error),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "message",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__msg__Output, message),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_members = {
  "hybrid_automaton_interfaces__msg",  // message namespace
  "Output",  // message name
  11,  // number of fields
  sizeof(hybrid_automaton_interfaces__msg__Output),
  hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_member_array,  // message members
  hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, msg, Output)() {
  hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_member_array[3].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, msg, DynamicParameter)();
  hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_member_array[4].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Duration)();
  hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_member_array[5].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, msg, TransitionPending)();
  hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_member_array[6].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Time)();
  hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_member_array[7].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Duration)();
  hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_member_array[8].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, colav_interfaces, msg, Waypoints)();
  if (!hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__msg__Output__rosidl_typesupport_introspection_c__Output_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
