// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hybrid_automaton_interfaces:msg/DynamicsTimer.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS_TIMER__BUILDER_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS_TIMER__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hybrid_automaton_interfaces/msg/detail/dynamics_timer__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hybrid_automaton_interfaces
{

namespace msg
{

namespace builder
{

class Init_DynamicsTimer_expired
{
public:
  explicit Init_DynamicsTimer_expired(::hybrid_automaton_interfaces::msg::DynamicsTimer & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::msg::DynamicsTimer expired(::hybrid_automaton_interfaces::msg::DynamicsTimer::_expired_type arg)
  {
    msg_.expired = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::DynamicsTimer msg_;
};

class Init_DynamicsTimer_timeout_sec
{
public:
  explicit Init_DynamicsTimer_timeout_sec(::hybrid_automaton_interfaces::msg::DynamicsTimer & msg)
  : msg_(msg)
  {}
  Init_DynamicsTimer_expired timeout_sec(::hybrid_automaton_interfaces::msg::DynamicsTimer::_timeout_sec_type arg)
  {
    msg_.timeout_sec = std::move(arg);
    return Init_DynamicsTimer_expired(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::DynamicsTimer msg_;
};

class Init_DynamicsTimer_timeout
{
public:
  explicit Init_DynamicsTimer_timeout(::hybrid_automaton_interfaces::msg::DynamicsTimer & msg)
  : msg_(msg)
  {}
  Init_DynamicsTimer_timeout_sec timeout(::hybrid_automaton_interfaces::msg::DynamicsTimer::_timeout_type arg)
  {
    msg_.timeout = std::move(arg);
    return Init_DynamicsTimer_timeout_sec(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::DynamicsTimer msg_;
};

class Init_DynamicsTimer_elapsed
{
public:
  explicit Init_DynamicsTimer_elapsed(::hybrid_automaton_interfaces::msg::DynamicsTimer & msg)
  : msg_(msg)
  {}
  Init_DynamicsTimer_timeout elapsed(::hybrid_automaton_interfaces::msg::DynamicsTimer::_elapsed_type arg)
  {
    msg_.elapsed = std::move(arg);
    return Init_DynamicsTimer_timeout(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::DynamicsTimer msg_;
};

class Init_DynamicsTimer_previous_dynamic_uuid
{
public:
  Init_DynamicsTimer_previous_dynamic_uuid()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DynamicsTimer_elapsed previous_dynamic_uuid(::hybrid_automaton_interfaces::msg::DynamicsTimer::_previous_dynamic_uuid_type arg)
  {
    msg_.previous_dynamic_uuid = std::move(arg);
    return Init_DynamicsTimer_elapsed(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::DynamicsTimer msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::msg::DynamicsTimer>()
{
  return hybrid_automaton_interfaces::msg::builder::Init_DynamicsTimer_previous_dynamic_uuid();
}

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS_TIMER__BUILDER_HPP_
