// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from hybrid_automaton_interfaces:action/HybridAutomaton.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace hybrid_automaton_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void HybridAutomaton_Goal_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) hybrid_automaton_interfaces::action::HybridAutomaton_Goal(_init);
}

void HybridAutomaton_Goal_fini_function(void * message_memory)
{
  auto typed_message = static_cast<hybrid_automaton_interfaces::action::HybridAutomaton_Goal *>(message_memory);
  typed_message->~HybridAutomaton_Goal();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember HybridAutomaton_Goal_message_member_array[5] = {
  {
    "stamp",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<builtin_interfaces::msg::Time>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_Goal, stamp),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "mission_uuid",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<unique_identifier_msgs::msg::UUID>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_Goal, mission_uuid),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "mission_profile",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_Goal, mission_profile),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "agent_uuid",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<unique_identifier_msgs::msg::UUID>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_Goal, agent_uuid),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "goal_waypoint",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<colav_interfaces::msg::Waypoint>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_Goal, goal_waypoint),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers HybridAutomaton_Goal_message_members = {
  "hybrid_automaton_interfaces::action",  // message namespace
  "HybridAutomaton_Goal",  // message name
  5,  // number of fields
  sizeof(hybrid_automaton_interfaces::action::HybridAutomaton_Goal),
  HybridAutomaton_Goal_message_member_array,  // message members
  HybridAutomaton_Goal_init_function,  // function to initialize message memory (memory has to be allocated)
  HybridAutomaton_Goal_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t HybridAutomaton_Goal_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &HybridAutomaton_Goal_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace hybrid_automaton_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_Goal>()
{
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_Goal_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, hybrid_automaton_interfaces, action, HybridAutomaton_Goal)() {
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_Goal_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace hybrid_automaton_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void HybridAutomaton_Result_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) hybrid_automaton_interfaces::action::HybridAutomaton_Result(_init);
}

void HybridAutomaton_Result_fini_function(void * message_memory)
{
  auto typed_message = static_cast<hybrid_automaton_interfaces::action::HybridAutomaton_Result *>(message_memory);
  typed_message->~HybridAutomaton_Result();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember HybridAutomaton_Result_message_member_array[2] = {
  {
    "success",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_Result, success),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "message",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_Result, message),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers HybridAutomaton_Result_message_members = {
  "hybrid_automaton_interfaces::action",  // message namespace
  "HybridAutomaton_Result",  // message name
  2,  // number of fields
  sizeof(hybrid_automaton_interfaces::action::HybridAutomaton_Result),
  HybridAutomaton_Result_message_member_array,  // message members
  HybridAutomaton_Result_init_function,  // function to initialize message memory (memory has to be allocated)
  HybridAutomaton_Result_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t HybridAutomaton_Result_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &HybridAutomaton_Result_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace hybrid_automaton_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_Result>()
{
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_Result_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, hybrid_automaton_interfaces, action, HybridAutomaton_Result)() {
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_Result_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace hybrid_automaton_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void HybridAutomaton_Feedback_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) hybrid_automaton_interfaces::action::HybridAutomaton_Feedback(_init);
}

void HybridAutomaton_Feedback_fini_function(void * message_memory)
{
  auto typed_message = static_cast<hybrid_automaton_interfaces::action::HybridAutomaton_Feedback *>(message_memory);
  typed_message->~HybridAutomaton_Feedback();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember HybridAutomaton_Feedback_message_member_array[1] = {
  {
    "feedback",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<hybrid_automaton_interfaces::msg::Output>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_Feedback, feedback),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers HybridAutomaton_Feedback_message_members = {
  "hybrid_automaton_interfaces::action",  // message namespace
  "HybridAutomaton_Feedback",  // message name
  1,  // number of fields
  sizeof(hybrid_automaton_interfaces::action::HybridAutomaton_Feedback),
  HybridAutomaton_Feedback_message_member_array,  // message members
  HybridAutomaton_Feedback_init_function,  // function to initialize message memory (memory has to be allocated)
  HybridAutomaton_Feedback_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t HybridAutomaton_Feedback_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &HybridAutomaton_Feedback_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace hybrid_automaton_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_Feedback>()
{
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_Feedback_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, hybrid_automaton_interfaces, action, HybridAutomaton_Feedback)() {
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_Feedback_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace hybrid_automaton_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void HybridAutomaton_SendGoal_Request_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Request(_init);
}

void HybridAutomaton_SendGoal_Request_fini_function(void * message_memory)
{
  auto typed_message = static_cast<hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Request *>(message_memory);
  typed_message->~HybridAutomaton_SendGoal_Request();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember HybridAutomaton_SendGoal_Request_message_member_array[2] = {
  {
    "goal_id",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<unique_identifier_msgs::msg::UUID>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Request, goal_id),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "goal",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_Goal>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Request, goal),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers HybridAutomaton_SendGoal_Request_message_members = {
  "hybrid_automaton_interfaces::action",  // message namespace
  "HybridAutomaton_SendGoal_Request",  // message name
  2,  // number of fields
  sizeof(hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Request),
  HybridAutomaton_SendGoal_Request_message_member_array,  // message members
  HybridAutomaton_SendGoal_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  HybridAutomaton_SendGoal_Request_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t HybridAutomaton_SendGoal_Request_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &HybridAutomaton_SendGoal_Request_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace hybrid_automaton_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Request>()
{
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_SendGoal_Request_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, hybrid_automaton_interfaces, action, HybridAutomaton_SendGoal_Request)() {
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_SendGoal_Request_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace hybrid_automaton_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void HybridAutomaton_SendGoal_Response_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Response(_init);
}

void HybridAutomaton_SendGoal_Response_fini_function(void * message_memory)
{
  auto typed_message = static_cast<hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Response *>(message_memory);
  typed_message->~HybridAutomaton_SendGoal_Response();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember HybridAutomaton_SendGoal_Response_message_member_array[2] = {
  {
    "accepted",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Response, accepted),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "stamp",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<builtin_interfaces::msg::Time>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Response, stamp),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers HybridAutomaton_SendGoal_Response_message_members = {
  "hybrid_automaton_interfaces::action",  // message namespace
  "HybridAutomaton_SendGoal_Response",  // message name
  2,  // number of fields
  sizeof(hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Response),
  HybridAutomaton_SendGoal_Response_message_member_array,  // message members
  HybridAutomaton_SendGoal_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  HybridAutomaton_SendGoal_Response_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t HybridAutomaton_SendGoal_Response_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &HybridAutomaton_SendGoal_Response_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace hybrid_automaton_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Response>()
{
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_SendGoal_Response_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, hybrid_automaton_interfaces, action, HybridAutomaton_SendGoal_Response)() {
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_SendGoal_Response_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/service_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/service_type_support_decl.hpp"

namespace hybrid_automaton_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

// this is intentionally not const to allow initialization later to prevent an initialization race
static ::rosidl_typesupport_introspection_cpp::ServiceMembers HybridAutomaton_SendGoal_service_members = {
  "hybrid_automaton_interfaces::action",  // service namespace
  "HybridAutomaton_SendGoal",  // service name
  // these two fields are initialized below on the first access
  // see get_service_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal>()
  nullptr,  // request message
  nullptr  // response message
};

static const rosidl_service_type_support_t HybridAutomaton_SendGoal_service_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &HybridAutomaton_SendGoal_service_members,
  get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace hybrid_automaton_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_service_type_support_t *
get_service_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal>()
{
  // get a handle to the value to be returned
  auto service_type_support =
    &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_SendGoal_service_type_support_handle;
  // get a non-const and properly typed version of the data void *
  auto service_members = const_cast<::rosidl_typesupport_introspection_cpp::ServiceMembers *>(
    static_cast<const ::rosidl_typesupport_introspection_cpp::ServiceMembers *>(
      service_type_support->data));
  // make sure that both the request_members_ and the response_members_ are initialized
  // if they are not, initialize them
  if (
    service_members->request_members_ == nullptr ||
    service_members->response_members_ == nullptr)
  {
    // initialize the request_members_ with the static function from the external library
    service_members->request_members_ = static_cast<
      const ::rosidl_typesupport_introspection_cpp::MessageMembers *
      >(
      ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<
        ::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Request
      >()->data
      );
    // initialize the response_members_ with the static function from the external library
    service_members->response_members_ = static_cast<
      const ::rosidl_typesupport_introspection_cpp::MessageMembers *
      >(
      ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<
        ::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Response
      >()->data
      );
  }
  // finally return the properly initialized service_type_support handle
  return service_type_support;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, hybrid_automaton_interfaces, action, HybridAutomaton_SendGoal)() {
  return ::rosidl_typesupport_introspection_cpp::get_service_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal>();
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace hybrid_automaton_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void HybridAutomaton_GetResult_Request_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Request(_init);
}

void HybridAutomaton_GetResult_Request_fini_function(void * message_memory)
{
  auto typed_message = static_cast<hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Request *>(message_memory);
  typed_message->~HybridAutomaton_GetResult_Request();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember HybridAutomaton_GetResult_Request_message_member_array[1] = {
  {
    "goal_id",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<unique_identifier_msgs::msg::UUID>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Request, goal_id),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers HybridAutomaton_GetResult_Request_message_members = {
  "hybrid_automaton_interfaces::action",  // message namespace
  "HybridAutomaton_GetResult_Request",  // message name
  1,  // number of fields
  sizeof(hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Request),
  HybridAutomaton_GetResult_Request_message_member_array,  // message members
  HybridAutomaton_GetResult_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  HybridAutomaton_GetResult_Request_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t HybridAutomaton_GetResult_Request_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &HybridAutomaton_GetResult_Request_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace hybrid_automaton_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Request>()
{
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_GetResult_Request_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, hybrid_automaton_interfaces, action, HybridAutomaton_GetResult_Request)() {
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_GetResult_Request_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace hybrid_automaton_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void HybridAutomaton_GetResult_Response_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Response(_init);
}

void HybridAutomaton_GetResult_Response_fini_function(void * message_memory)
{
  auto typed_message = static_cast<hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Response *>(message_memory);
  typed_message->~HybridAutomaton_GetResult_Response();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember HybridAutomaton_GetResult_Response_message_member_array[2] = {
  {
    "status",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Response, status),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "result",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_Result>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Response, result),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers HybridAutomaton_GetResult_Response_message_members = {
  "hybrid_automaton_interfaces::action",  // message namespace
  "HybridAutomaton_GetResult_Response",  // message name
  2,  // number of fields
  sizeof(hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Response),
  HybridAutomaton_GetResult_Response_message_member_array,  // message members
  HybridAutomaton_GetResult_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  HybridAutomaton_GetResult_Response_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t HybridAutomaton_GetResult_Response_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &HybridAutomaton_GetResult_Response_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace hybrid_automaton_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Response>()
{
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_GetResult_Response_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, hybrid_automaton_interfaces, action, HybridAutomaton_GetResult_Response)() {
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_GetResult_Response_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/service_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/service_type_support_decl.hpp"

namespace hybrid_automaton_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

// this is intentionally not const to allow initialization later to prevent an initialization race
static ::rosidl_typesupport_introspection_cpp::ServiceMembers HybridAutomaton_GetResult_service_members = {
  "hybrid_automaton_interfaces::action",  // service namespace
  "HybridAutomaton_GetResult",  // service name
  // these two fields are initialized below on the first access
  // see get_service_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_GetResult>()
  nullptr,  // request message
  nullptr  // response message
};

static const rosidl_service_type_support_t HybridAutomaton_GetResult_service_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &HybridAutomaton_GetResult_service_members,
  get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace hybrid_automaton_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_service_type_support_t *
get_service_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_GetResult>()
{
  // get a handle to the value to be returned
  auto service_type_support =
    &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_GetResult_service_type_support_handle;
  // get a non-const and properly typed version of the data void *
  auto service_members = const_cast<::rosidl_typesupport_introspection_cpp::ServiceMembers *>(
    static_cast<const ::rosidl_typesupport_introspection_cpp::ServiceMembers *>(
      service_type_support->data));
  // make sure that both the request_members_ and the response_members_ are initialized
  // if they are not, initialize them
  if (
    service_members->request_members_ == nullptr ||
    service_members->response_members_ == nullptr)
  {
    // initialize the request_members_ with the static function from the external library
    service_members->request_members_ = static_cast<
      const ::rosidl_typesupport_introspection_cpp::MessageMembers *
      >(
      ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<
        ::hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Request
      >()->data
      );
    // initialize the response_members_ with the static function from the external library
    service_members->response_members_ = static_cast<
      const ::rosidl_typesupport_introspection_cpp::MessageMembers *
      >(
      ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<
        ::hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Response
      >()->data
      );
  }
  // finally return the properly initialized service_type_support handle
  return service_type_support;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, hybrid_automaton_interfaces, action, HybridAutomaton_GetResult)() {
  return ::rosidl_typesupport_introspection_cpp::get_service_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_GetResult>();
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace hybrid_automaton_interfaces
{

namespace action
{

namespace rosidl_typesupport_introspection_cpp
{

void HybridAutomaton_FeedbackMessage_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) hybrid_automaton_interfaces::action::HybridAutomaton_FeedbackMessage(_init);
}

void HybridAutomaton_FeedbackMessage_fini_function(void * message_memory)
{
  auto typed_message = static_cast<hybrid_automaton_interfaces::action::HybridAutomaton_FeedbackMessage *>(message_memory);
  typed_message->~HybridAutomaton_FeedbackMessage();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember HybridAutomaton_FeedbackMessage_message_member_array[2] = {
  {
    "goal_id",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<unique_identifier_msgs::msg::UUID>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_FeedbackMessage, goal_id),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "feedback",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_Feedback>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::action::HybridAutomaton_FeedbackMessage, feedback),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers HybridAutomaton_FeedbackMessage_message_members = {
  "hybrid_automaton_interfaces::action",  // message namespace
  "HybridAutomaton_FeedbackMessage",  // message name
  2,  // number of fields
  sizeof(hybrid_automaton_interfaces::action::HybridAutomaton_FeedbackMessage),
  HybridAutomaton_FeedbackMessage_message_member_array,  // message members
  HybridAutomaton_FeedbackMessage_init_function,  // function to initialize message memory (memory has to be allocated)
  HybridAutomaton_FeedbackMessage_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t HybridAutomaton_FeedbackMessage_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &HybridAutomaton_FeedbackMessage_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace action

}  // namespace hybrid_automaton_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<hybrid_automaton_interfaces::action::HybridAutomaton_FeedbackMessage>()
{
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_FeedbackMessage_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, hybrid_automaton_interfaces, action, HybridAutomaton_FeedbackMessage)() {
  return &::hybrid_automaton_interfaces::action::rosidl_typesupport_introspection_cpp::HybridAutomaton_FeedbackMessage_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
