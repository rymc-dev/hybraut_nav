// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hybrid_automaton_interfaces:msg/TransitionTimer.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_TIMER__BUILDER_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_TIMER__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hybrid_automaton_interfaces/msg/detail/transition_timer__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hybrid_automaton_interfaces
{

namespace msg
{

namespace builder
{

class Init_TransitionTimer_expired
{
public:
  explicit Init_TransitionTimer_expired(::hybrid_automaton_interfaces::msg::TransitionTimer & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::msg::TransitionTimer expired(::hybrid_automaton_interfaces::msg::TransitionTimer::_expired_type arg)
  {
    msg_.expired = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::TransitionTimer msg_;
};

class Init_TransitionTimer_timeout_sec
{
public:
  explicit Init_TransitionTimer_timeout_sec(::hybrid_automaton_interfaces::msg::TransitionTimer & msg)
  : msg_(msg)
  {}
  Init_TransitionTimer_expired timeout_sec(::hybrid_automaton_interfaces::msg::TransitionTimer::_timeout_sec_type arg)
  {
    msg_.timeout_sec = std::move(arg);
    return Init_TransitionTimer_expired(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::TransitionTimer msg_;
};

class Init_TransitionTimer_timeout
{
public:
  explicit Init_TransitionTimer_timeout(::hybrid_automaton_interfaces::msg::TransitionTimer & msg)
  : msg_(msg)
  {}
  Init_TransitionTimer_timeout_sec timeout(::hybrid_automaton_interfaces::msg::TransitionTimer::_timeout_type arg)
  {
    msg_.timeout = std::move(arg);
    return Init_TransitionTimer_timeout_sec(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::TransitionTimer msg_;
};

class Init_TransitionTimer_elapsed
{
public:
  explicit Init_TransitionTimer_elapsed(::hybrid_automaton_interfaces::msg::TransitionTimer & msg)
  : msg_(msg)
  {}
  Init_TransitionTimer_timeout elapsed(::hybrid_automaton_interfaces::msg::TransitionTimer::_elapsed_type arg)
  {
    msg_.elapsed = std::move(arg);
    return Init_TransitionTimer_timeout(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::TransitionTimer msg_;
};

class Init_TransitionTimer_previous_transition_uuid
{
public:
  Init_TransitionTimer_previous_transition_uuid()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TransitionTimer_elapsed previous_transition_uuid(::hybrid_automaton_interfaces::msg::TransitionTimer::_previous_transition_uuid_type arg)
  {
    msg_.previous_transition_uuid = std::move(arg);
    return Init_TransitionTimer_elapsed(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::TransitionTimer msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::msg::TransitionTimer>()
{
  return hybrid_automaton_interfaces::msg::builder::Init_TransitionTimer_previous_transition_uuid();
}

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_TIMER__BUILDER_HPP_
