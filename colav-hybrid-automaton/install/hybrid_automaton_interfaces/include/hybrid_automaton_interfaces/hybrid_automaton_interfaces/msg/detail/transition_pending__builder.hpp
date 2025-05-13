// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hybrid_automaton_interfaces:msg/TransitionPending.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_PENDING__BUILDER_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_PENDING__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hybrid_automaton_interfaces/msg/detail/transition_pending__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hybrid_automaton_interfaces
{

namespace msg
{

namespace builder
{

class Init_TransitionPending_transition_pending
{
public:
  explicit Init_TransitionPending_transition_pending(::hybrid_automaton_interfaces::msg::TransitionPending & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::msg::TransitionPending transition_pending(::hybrid_automaton_interfaces::msg::TransitionPending::_transition_pending_type arg)
  {
    msg_.transition_pending = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::TransitionPending msg_;
};

class Init_TransitionPending_stamp
{
public:
  explicit Init_TransitionPending_stamp(::hybrid_automaton_interfaces::msg::TransitionPending & msg)
  : msg_(msg)
  {}
  Init_TransitionPending_transition_pending stamp(::hybrid_automaton_interfaces::msg::TransitionPending::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return Init_TransitionPending_transition_pending(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::TransitionPending msg_;
};

class Init_TransitionPending_transition_uuid
{
public:
  Init_TransitionPending_transition_uuid()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TransitionPending_stamp transition_uuid(::hybrid_automaton_interfaces::msg::TransitionPending::_transition_uuid_type arg)
  {
    msg_.transition_uuid = std::move(arg);
    return Init_TransitionPending_stamp(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::TransitionPending msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::msg::TransitionPending>()
{
  return hybrid_automaton_interfaces::msg::builder::Init_TransitionPending_transition_uuid();
}

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_PENDING__BUILDER_HPP_
