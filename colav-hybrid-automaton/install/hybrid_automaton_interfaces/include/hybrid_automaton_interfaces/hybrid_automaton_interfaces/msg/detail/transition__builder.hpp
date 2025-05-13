// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hybrid_automaton_interfaces:msg/Transition.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION__BUILDER_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hybrid_automaton_interfaces/msg/detail/transition__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hybrid_automaton_interfaces
{

namespace msg
{

namespace builder
{

class Init_Transition_error_message
{
public:
  explicit Init_Transition_error_message(::hybrid_automaton_interfaces::msg::Transition & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::msg::Transition error_message(::hybrid_automaton_interfaces::msg::Transition::_error_message_type arg)
  {
    msg_.error_message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Transition msg_;
};

class Init_Transition_success
{
public:
  explicit Init_Transition_success(::hybrid_automaton_interfaces::msg::Transition & msg)
  : msg_(msg)
  {}
  Init_Transition_error_message success(::hybrid_automaton_interfaces::msg::Transition::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_Transition_error_message(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Transition msg_;
};

class Init_Transition_stamp
{
public:
  explicit Init_Transition_stamp(::hybrid_automaton_interfaces::msg::Transition & msg)
  : msg_(msg)
  {}
  Init_Transition_success stamp(::hybrid_automaton_interfaces::msg::Transition::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return Init_Transition_success(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Transition msg_;
};

class Init_Transition_transition_priority
{
public:
  explicit Init_Transition_transition_priority(::hybrid_automaton_interfaces::msg::Transition & msg)
  : msg_(msg)
  {}
  Init_Transition_stamp transition_priority(::hybrid_automaton_interfaces::msg::Transition::_transition_priority_type arg)
  {
    msg_.transition_priority = std::move(arg);
    return Init_Transition_stamp(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Transition msg_;
};

class Init_Transition_transition_values
{
public:
  explicit Init_Transition_transition_values(::hybrid_automaton_interfaces::msg::Transition & msg)
  : msg_(msg)
  {}
  Init_Transition_transition_priority transition_values(::hybrid_automaton_interfaces::msg::Transition::_transition_values_type arg)
  {
    msg_.transition_values = std::move(arg);
    return Init_Transition_transition_priority(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Transition msg_;
};

class Init_Transition_transition_names
{
public:
  explicit Init_Transition_transition_names(::hybrid_automaton_interfaces::msg::Transition & msg)
  : msg_(msg)
  {}
  Init_Transition_transition_values transition_names(::hybrid_automaton_interfaces::msg::Transition::_transition_names_type arg)
  {
    msg_.transition_names = std::move(arg);
    return Init_Transition_transition_values(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Transition msg_;
};

class Init_Transition_mode
{
public:
  explicit Init_Transition_mode(::hybrid_automaton_interfaces::msg::Transition & msg)
  : msg_(msg)
  {}
  Init_Transition_transition_names mode(::hybrid_automaton_interfaces::msg::Transition::_mode_type arg)
  {
    msg_.mode = std::move(arg);
    return Init_Transition_transition_names(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Transition msg_;
};

class Init_Transition_transition_uuid
{
public:
  Init_Transition_transition_uuid()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Transition_mode transition_uuid(::hybrid_automaton_interfaces::msg::Transition::_transition_uuid_type arg)
  {
    msg_.transition_uuid = std::move(arg);
    return Init_Transition_mode(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Transition msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::msg::Transition>()
{
  return hybrid_automaton_interfaces::msg::builder::Init_Transition_transition_uuid();
}

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION__BUILDER_HPP_
