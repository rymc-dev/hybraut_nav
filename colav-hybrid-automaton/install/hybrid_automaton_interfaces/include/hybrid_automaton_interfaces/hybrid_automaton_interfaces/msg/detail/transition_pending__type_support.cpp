// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from hybrid_automaton_interfaces:msg/TransitionPending.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "hybrid_automaton_interfaces/msg/detail/transition_pending__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace hybrid_automaton_interfaces
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void TransitionPending_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) hybrid_automaton_interfaces::msg::TransitionPending(_init);
}

void TransitionPending_fini_function(void * message_memory)
{
  auto typed_message = static_cast<hybrid_automaton_interfaces::msg::TransitionPending *>(message_memory);
  typed_message->~TransitionPending();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember TransitionPending_message_member_array[3] = {
  {
    "transition_uuid",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<unique_identifier_msgs::msg::UUID>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::msg::TransitionPending, transition_uuid),  // bytes offset in struct
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
    offsetof(hybrid_automaton_interfaces::msg::TransitionPending, stamp),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "transition_pending",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(hybrid_automaton_interfaces::msg::TransitionPending, transition_pending),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers TransitionPending_message_members = {
  "hybrid_automaton_interfaces::msg",  // message namespace
  "TransitionPending",  // message name
  3,  // number of fields
  sizeof(hybrid_automaton_interfaces::msg::TransitionPending),
  TransitionPending_message_member_array,  // message members
  TransitionPending_init_function,  // function to initialize message memory (memory has to be allocated)
  TransitionPending_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t TransitionPending_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &TransitionPending_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace hybrid_automaton_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<hybrid_automaton_interfaces::msg::TransitionPending>()
{
  return &::hybrid_automaton_interfaces::msg::rosidl_typesupport_introspection_cpp::TransitionPending_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, hybrid_automaton_interfaces, msg, TransitionPending)() {
  return &::hybrid_automaton_interfaces::msg::rosidl_typesupport_introspection_cpp::TransitionPending_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
