// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from hybrid_automaton_interfaces:action/HybridAutomaton.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__rosidl_typesupport_introspection_c.h"
#include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__functions.h"
#include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.h"


// Include directives for member types
// Member `stamp`
#include "builtin_interfaces/msg/time.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__rosidl_typesupport_introspection_c.h"
// Member `mission_uuid`
// Member `agent_uuid`
#include "unique_identifier_msgs/msg/uuid.h"
// Member `mission_uuid`
// Member `agent_uuid`
#include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"
// Member `mission_profile`
#include "rosidl_runtime_c/string_functions.h"
// Member `goal_waypoint`
#include "colav_interfaces/msg/waypoint.h"
// Member `goal_waypoint`
#include "colav_interfaces/msg/detail/waypoint__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__action__HybridAutomaton_Goal__init(message_memory);
}

void hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__action__HybridAutomaton_Goal__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_message_member_array[5] = {
  {
    "stamp",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_Goal, stamp),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "mission_uuid",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_Goal, mission_uuid),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "mission_profile",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_Goal, mission_profile),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "agent_uuid",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_Goal, agent_uuid),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "goal_waypoint",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_Goal, goal_waypoint),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_message_members = {
  "hybrid_automaton_interfaces__action",  // message namespace
  "HybridAutomaton_Goal",  // message name
  5,  // number of fields
  sizeof(hybrid_automaton_interfaces__action__HybridAutomaton_Goal),
  hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_message_member_array,  // message members
  hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_Goal)() {
  hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Time)();
  hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_message_member_array[3].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_message_member_array[4].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, colav_interfaces, msg, Waypoint)();
  if (!hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__action__HybridAutomaton_Goal__rosidl_typesupport_introspection_c__HybridAutomaton_Goal_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__rosidl_typesupport_introspection_c.h"
// already included above
// #include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__functions.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.h"


// Include directives for member types
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__action__HybridAutomaton_Result__rosidl_typesupport_introspection_c__HybridAutomaton_Result_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__action__HybridAutomaton_Result__init(message_memory);
}

void hybrid_automaton_interfaces__action__HybridAutomaton_Result__rosidl_typesupport_introspection_c__HybridAutomaton_Result_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__action__HybridAutomaton_Result__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__action__HybridAutomaton_Result__rosidl_typesupport_introspection_c__HybridAutomaton_Result_message_member_array[2] = {
  {
    "success",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_Result, success),  // bytes offset in struct
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
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_Result, message),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__action__HybridAutomaton_Result__rosidl_typesupport_introspection_c__HybridAutomaton_Result_message_members = {
  "hybrid_automaton_interfaces__action",  // message namespace
  "HybridAutomaton_Result",  // message name
  2,  // number of fields
  sizeof(hybrid_automaton_interfaces__action__HybridAutomaton_Result),
  hybrid_automaton_interfaces__action__HybridAutomaton_Result__rosidl_typesupport_introspection_c__HybridAutomaton_Result_message_member_array,  // message members
  hybrid_automaton_interfaces__action__HybridAutomaton_Result__rosidl_typesupport_introspection_c__HybridAutomaton_Result_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__action__HybridAutomaton_Result__rosidl_typesupport_introspection_c__HybridAutomaton_Result_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__action__HybridAutomaton_Result__rosidl_typesupport_introspection_c__HybridAutomaton_Result_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__action__HybridAutomaton_Result__rosidl_typesupport_introspection_c__HybridAutomaton_Result_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_Result)() {
  if (!hybrid_automaton_interfaces__action__HybridAutomaton_Result__rosidl_typesupport_introspection_c__HybridAutomaton_Result_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__action__HybridAutomaton_Result__rosidl_typesupport_introspection_c__HybridAutomaton_Result_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__action__HybridAutomaton_Result__rosidl_typesupport_introspection_c__HybridAutomaton_Result_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__rosidl_typesupport_introspection_c.h"
// already included above
// #include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__functions.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.h"


// Include directives for member types
// Member `feedback`
#include "hybrid_automaton_interfaces/msg/output.h"
// Member `feedback`
#include "hybrid_automaton_interfaces/msg/detail/output__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__rosidl_typesupport_introspection_c__HybridAutomaton_Feedback_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__init(message_memory);
}

void hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__rosidl_typesupport_introspection_c__HybridAutomaton_Feedback_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__rosidl_typesupport_introspection_c__HybridAutomaton_Feedback_message_member_array[1] = {
  {
    "feedback",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_Feedback, feedback),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__rosidl_typesupport_introspection_c__HybridAutomaton_Feedback_message_members = {
  "hybrid_automaton_interfaces__action",  // message namespace
  "HybridAutomaton_Feedback",  // message name
  1,  // number of fields
  sizeof(hybrid_automaton_interfaces__action__HybridAutomaton_Feedback),
  hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__rosidl_typesupport_introspection_c__HybridAutomaton_Feedback_message_member_array,  // message members
  hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__rosidl_typesupport_introspection_c__HybridAutomaton_Feedback_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__rosidl_typesupport_introspection_c__HybridAutomaton_Feedback_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__rosidl_typesupport_introspection_c__HybridAutomaton_Feedback_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__rosidl_typesupport_introspection_c__HybridAutomaton_Feedback_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_Feedback)() {
  hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__rosidl_typesupport_introspection_c__HybridAutomaton_Feedback_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, msg, Output)();
  if (!hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__rosidl_typesupport_introspection_c__HybridAutomaton_Feedback_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__rosidl_typesupport_introspection_c__HybridAutomaton_Feedback_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__rosidl_typesupport_introspection_c__HybridAutomaton_Feedback_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__rosidl_typesupport_introspection_c.h"
// already included above
// #include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__functions.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.h"


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/uuid.h"
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"
// Member `goal`
#include "hybrid_automaton_interfaces/action/hybrid_automaton.h"
// Member `goal`
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__init(message_memory);
}

void hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_message_member_array[2] = {
  {
    "goal_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request, goal_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "goal",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request, goal),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_message_members = {
  "hybrid_automaton_interfaces__action",  // message namespace
  "HybridAutomaton_SendGoal_Request",  // message name
  2,  // number of fields
  sizeof(hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request),
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_message_member_array,  // message members
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_SendGoal_Request)() {
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_Goal)();
  if (!hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__rosidl_typesupport_introspection_c.h"
// already included above
// #include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__functions.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.h"


// Include directives for member types
// Member `stamp`
// already included above
// #include "builtin_interfaces/msg/time.h"
// Member `stamp`
// already included above
// #include "builtin_interfaces/msg/detail/time__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__init(message_memory);
}

void hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Response_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Response_message_member_array[2] = {
  {
    "accepted",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response, accepted),  // bytes offset in struct
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
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response, stamp),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Response_message_members = {
  "hybrid_automaton_interfaces__action",  // message namespace
  "HybridAutomaton_SendGoal_Response",  // message name
  2,  // number of fields
  sizeof(hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response),
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Response_message_member_array,  // message members
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Response_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_SendGoal_Response)() {
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Response_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Time)();
  if (!hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Response_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_service_members = {
  "hybrid_automaton_interfaces__action",  // service namespace
  "HybridAutomaton_SendGoal",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Request_message_type_support_handle,
  NULL  // response message
  // hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_Response_message_type_support_handle
};

static rosidl_service_type_support_t hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_service_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_SendGoal_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_SendGoal_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_SendGoal)() {
  if (!hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_service_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_SendGoal_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_SendGoal_Response)()->data;
  }

  return &hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_SendGoal_service_type_support_handle;
}

// already included above
// #include <stddef.h>
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__rosidl_typesupport_introspection_c.h"
// already included above
// #include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__functions.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.h"


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/uuid.h"
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__init(message_memory);
}

void hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Request_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Request_message_member_array[1] = {
  {
    "goal_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request, goal_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Request_message_members = {
  "hybrid_automaton_interfaces__action",  // message namespace
  "HybridAutomaton_GetResult_Request",  // message name
  1,  // number of fields
  sizeof(hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request),
  hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Request_message_member_array,  // message members
  hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Request_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_GetResult_Request)() {
  hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Request_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  if (!hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Request_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__rosidl_typesupport_introspection_c.h"
// already included above
// #include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__functions.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.h"


// Include directives for member types
// Member `result`
// already included above
// #include "hybrid_automaton_interfaces/action/hybrid_automaton.h"
// Member `result`
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__init(message_memory);
}

void hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Response_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Response_message_member_array[2] = {
  {
    "status",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response, status),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "result",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response, result),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Response_message_members = {
  "hybrid_automaton_interfaces__action",  // message namespace
  "HybridAutomaton_GetResult_Response",  // message name
  2,  // number of fields
  sizeof(hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response),
  hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Response_message_member_array,  // message members
  hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Response_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_GetResult_Response)() {
  hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Response_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_Result)();
  if (!hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Response_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_service_members = {
  "hybrid_automaton_interfaces__action",  // service namespace
  "HybridAutomaton_GetResult",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Request_message_type_support_handle,
  NULL  // response message
  // hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_Response_message_type_support_handle
};

static rosidl_service_type_support_t hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_service_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_GetResult_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_GetResult_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_GetResult)() {
  if (!hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_service_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_GetResult_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_GetResult_Response)()->data;
  }

  return &hybrid_automaton_interfaces__action__detail__hybrid_automaton__rosidl_typesupport_introspection_c__HybridAutomaton_GetResult_service_type_support_handle;
}

// already included above
// #include <stddef.h>
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__rosidl_typesupport_introspection_c.h"
// already included above
// #include "hybrid_automaton_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__functions.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.h"


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/uuid.h"
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"
// Member `feedback`
// already included above
// #include "hybrid_automaton_interfaces/action/hybrid_automaton.h"
// Member `feedback`
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__rosidl_typesupport_introspection_c__HybridAutomaton_FeedbackMessage_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__init(message_memory);
}

void hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__rosidl_typesupport_introspection_c__HybridAutomaton_FeedbackMessage_fini_function(void * message_memory)
{
  hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__rosidl_typesupport_introspection_c__HybridAutomaton_FeedbackMessage_message_member_array[2] = {
  {
    "goal_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage, goal_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "feedback",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage, feedback),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__rosidl_typesupport_introspection_c__HybridAutomaton_FeedbackMessage_message_members = {
  "hybrid_automaton_interfaces__action",  // message namespace
  "HybridAutomaton_FeedbackMessage",  // message name
  2,  // number of fields
  sizeof(hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage),
  hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__rosidl_typesupport_introspection_c__HybridAutomaton_FeedbackMessage_message_member_array,  // message members
  hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__rosidl_typesupport_introspection_c__HybridAutomaton_FeedbackMessage_init_function,  // function to initialize message memory (memory has to be allocated)
  hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__rosidl_typesupport_introspection_c__HybridAutomaton_FeedbackMessage_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__rosidl_typesupport_introspection_c__HybridAutomaton_FeedbackMessage_message_type_support_handle = {
  0,
  &hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__rosidl_typesupport_introspection_c__HybridAutomaton_FeedbackMessage_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_hybrid_automaton_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_FeedbackMessage)() {
  hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__rosidl_typesupport_introspection_c__HybridAutomaton_FeedbackMessage_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__rosidl_typesupport_introspection_c__HybridAutomaton_FeedbackMessage_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, hybrid_automaton_interfaces, action, HybridAutomaton_Feedback)();
  if (!hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__rosidl_typesupport_introspection_c__HybridAutomaton_FeedbackMessage_message_type_support_handle.typesupport_identifier) {
    hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__rosidl_typesupport_introspection_c__HybridAutomaton_FeedbackMessage_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__rosidl_typesupport_introspection_c__HybridAutomaton_FeedbackMessage_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
