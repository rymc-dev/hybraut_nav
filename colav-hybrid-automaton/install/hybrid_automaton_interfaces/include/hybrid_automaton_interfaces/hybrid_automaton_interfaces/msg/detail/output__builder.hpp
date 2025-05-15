// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hybrid_automaton_interfaces:msg/Output.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__OUTPUT__BUILDER_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__OUTPUT__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hybrid_automaton_interfaces/msg/detail/output__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hybrid_automaton_interfaces
{

namespace msg
{

namespace builder
{

class Init_Output_message
{
public:
  explicit Init_Output_message(::hybrid_automaton_interfaces::msg::Output & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::msg::Output message(::hybrid_automaton_interfaces::msg::Output::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Output msg_;
};

class Init_Output_error
{
public:
  explicit Init_Output_error(::hybrid_automaton_interfaces::msg::Output & msg)
  : msg_(msg)
  {}
  Init_Output_message error(::hybrid_automaton_interfaces::msg::Output::_error_type arg)
  {
    msg_.error = std::move(arg);
    return Init_Output_message(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Output msg_;
};

class Init_Output_waypoints
{
public:
  explicit Init_Output_waypoints(::hybrid_automaton_interfaces::msg::Output & msg)
  : msg_(msg)
  {}
  Init_Output_error waypoints(::hybrid_automaton_interfaces::msg::Output::_waypoints_type arg)
  {
    msg_.waypoints = std::move(arg);
    return Init_Output_error(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Output msg_;
};

class Init_Output_elapsed_time
{
public:
  explicit Init_Output_elapsed_time(::hybrid_automaton_interfaces::msg::Output & msg)
  : msg_(msg)
  {}
  Init_Output_waypoints elapsed_time(::hybrid_automaton_interfaces::msg::Output::_elapsed_time_type arg)
  {
    msg_.elapsed_time = std::move(arg);
    return Init_Output_waypoints(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Output msg_;
};

class Init_Output_stamp
{
public:
  explicit Init_Output_stamp(::hybrid_automaton_interfaces::msg::Output & msg)
  : msg_(msg)
  {}
  Init_Output_elapsed_time stamp(::hybrid_automaton_interfaces::msg::Output::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return Init_Output_elapsed_time(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Output msg_;
};

class Init_Output_transition_pending
{
public:
  explicit Init_Output_transition_pending(::hybrid_automaton_interfaces::msg::Output & msg)
  : msg_(msg)
  {}
  Init_Output_stamp transition_pending(::hybrid_automaton_interfaces::msg::Output::_transition_pending_type arg)
  {
    msg_.transition_pending = std::move(arg);
    return Init_Output_stamp(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Output msg_;
};

class Init_Output_time_since_last_transition
{
public:
  explicit Init_Output_time_since_last_transition(::hybrid_automaton_interfaces::msg::Output & msg)
  : msg_(msg)
  {}
  Init_Output_transition_pending time_since_last_transition(::hybrid_automaton_interfaces::msg::Output::_time_since_last_transition_type arg)
  {
    msg_.time_since_last_transition = std::move(arg);
    return Init_Output_transition_pending(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Output msg_;
};

class Init_Output_dynamics
{
public:
  explicit Init_Output_dynamics(::hybrid_automaton_interfaces::msg::Output & msg)
  : msg_(msg)
  {}
  Init_Output_time_since_last_transition dynamics(::hybrid_automaton_interfaces::msg::Output::_dynamics_type arg)
  {
    msg_.dynamics = std::move(arg);
    return Init_Output_time_since_last_transition(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Output msg_;
};

class Init_Output_status
{
public:
  explicit Init_Output_status(::hybrid_automaton_interfaces::msg::Output & msg)
  : msg_(msg)
  {}
  Init_Output_dynamics status(::hybrid_automaton_interfaces::msg::Output::_status_type arg)
  {
    msg_.status = std::move(arg);
    return Init_Output_dynamics(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Output msg_;
};

class Init_Output_mode
{
public:
  explicit Init_Output_mode(::hybrid_automaton_interfaces::msg::Output & msg)
  : msg_(msg)
  {}
  Init_Output_status mode(::hybrid_automaton_interfaces::msg::Output::_mode_type arg)
  {
    msg_.mode = std::move(arg);
    return Init_Output_status(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Output msg_;
};

class Init_Output_automaton_uuid
{
public:
  Init_Output_automaton_uuid()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Output_mode automaton_uuid(::hybrid_automaton_interfaces::msg::Output::_automaton_uuid_type arg)
  {
    msg_.automaton_uuid = std::move(arg);
    return Init_Output_mode(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Output msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::msg::Output>()
{
  return hybrid_automaton_interfaces::msg::builder::Init_Output_automaton_uuid();
}

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__OUTPUT__BUILDER_HPP_
