// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hybrid_automaton_interfaces:msg/Guards.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__GUARDS__BUILDER_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__GUARDS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hybrid_automaton_interfaces/msg/detail/guards__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hybrid_automaton_interfaces
{

namespace msg
{

namespace builder
{

class Init_Guards_error_message
{
public:
  explicit Init_Guards_error_message(::hybrid_automaton_interfaces::msg::Guards & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::msg::Guards error_message(::hybrid_automaton_interfaces::msg::Guards::_error_message_type arg)
  {
    msg_.error_message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

class Init_Guards_error
{
public:
  explicit Init_Guards_error(::hybrid_automaton_interfaces::msg::Guards & msg)
  : msg_(msg)
  {}
  Init_Guards_error_message error(::hybrid_automaton_interfaces::msg::Guards::_error_type arg)
  {
    msg_.error = std::move(arg);
    return Init_Guards_error_message(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

class Init_Guards_timestamp
{
public:
  explicit Init_Guards_timestamp(::hybrid_automaton_interfaces::msg::Guards & msg)
  : msg_(msg)
  {}
  Init_Guards_error timestamp(::hybrid_automaton_interfaces::msg::Guards::_timestamp_type arg)
  {
    msg_.timestamp = std::move(arg);
    return Init_Guards_error(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

class Init_Guards_waypoint_reached_to_cruise
{
public:
  explicit Init_Guards_waypoint_reached_to_cruise(::hybrid_automaton_interfaces::msg::Guards & msg)
  : msg_(msg)
  {}
  Init_Guards_timestamp waypoint_reached_to_cruise(::hybrid_automaton_interfaces::msg::Guards::_waypoint_reached_to_cruise_type arg)
  {
    msg_.waypoint_reached_to_cruise = std::move(arg);
    return Init_Guards_timestamp(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

class Init_Guards_t2los_to_waypoint_reached
{
public:
  explicit Init_Guards_t2los_to_waypoint_reached(::hybrid_automaton_interfaces::msg::Guards & msg)
  : msg_(msg)
  {}
  Init_Guards_waypoint_reached_to_cruise t2los_to_waypoint_reached(::hybrid_automaton_interfaces::msg::Guards::_t2los_to_waypoint_reached_type arg)
  {
    msg_.t2los_to_waypoint_reached = std::move(arg);
    return Init_Guards_waypoint_reached_to_cruise(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

class Init_Guards_t2los_to_fb
{
public:
  explicit Init_Guards_t2los_to_fb(::hybrid_automaton_interfaces::msg::Guards & msg)
  : msg_(msg)
  {}
  Init_Guards_t2los_to_waypoint_reached t2los_to_fb(::hybrid_automaton_interfaces::msg::Guards::_t2los_to_fb_type arg)
  {
    msg_.t2los_to_fb = std::move(arg);
    return Init_Guards_t2los_to_waypoint_reached(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

class Init_Guards_t2los_to_cruise
{
public:
  explicit Init_Guards_t2los_to_cruise(::hybrid_automaton_interfaces::msg::Guards & msg)
  : msg_(msg)
  {}
  Init_Guards_t2los_to_fb t2los_to_cruise(::hybrid_automaton_interfaces::msg::Guards::_t2los_to_cruise_type arg)
  {
    msg_.t2los_to_cruise = std::move(arg);
    return Init_Guards_t2los_to_fb(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

class Init_Guards_cruise_to_fb
{
public:
  explicit Init_Guards_cruise_to_fb(::hybrid_automaton_interfaces::msg::Guards & msg)
  : msg_(msg)
  {}
  Init_Guards_t2los_to_cruise cruise_to_fb(::hybrid_automaton_interfaces::msg::Guards::_cruise_to_fb_type arg)
  {
    msg_.cruise_to_fb = std::move(arg);
    return Init_Guards_t2los_to_cruise(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

class Init_Guards_cruise_to_waypoint_reached
{
public:
  explicit Init_Guards_cruise_to_waypoint_reached(::hybrid_automaton_interfaces::msg::Guards & msg)
  : msg_(msg)
  {}
  Init_Guards_cruise_to_fb cruise_to_waypoint_reached(::hybrid_automaton_interfaces::msg::Guards::_cruise_to_waypoint_reached_type arg)
  {
    msg_.cruise_to_waypoint_reached = std::move(arg);
    return Init_Guards_cruise_to_fb(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

class Init_Guards_cruise_to_t2los_2
{
public:
  explicit Init_Guards_cruise_to_t2los_2(::hybrid_automaton_interfaces::msg::Guards & msg)
  : msg_(msg)
  {}
  Init_Guards_cruise_to_waypoint_reached cruise_to_t2los_2(::hybrid_automaton_interfaces::msg::Guards::_cruise_to_t2los_2_type arg)
  {
    msg_.cruise_to_t2los_2 = std::move(arg);
    return Init_Guards_cruise_to_waypoint_reached(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

class Init_Guards_cruise_to_t2los_1
{
public:
  explicit Init_Guards_cruise_to_t2los_1(::hybrid_automaton_interfaces::msg::Guards & msg)
  : msg_(msg)
  {}
  Init_Guards_cruise_to_t2los_2 cruise_to_t2los_1(::hybrid_automaton_interfaces::msg::Guards::_cruise_to_t2los_1_type arg)
  {
    msg_.cruise_to_t2los_1 = std::move(arg);
    return Init_Guards_cruise_to_t2los_2(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

class Init_Guards_guard_names
{
public:
  explicit Init_Guards_guard_names(::hybrid_automaton_interfaces::msg::Guards & msg)
  : msg_(msg)
  {}
  Init_Guards_cruise_to_t2los_1 guard_names(::hybrid_automaton_interfaces::msg::Guards::_guard_names_type arg)
  {
    msg_.guard_names = std::move(arg);
    return Init_Guards_cruise_to_t2los_1(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

class Init_Guards_transition_pending
{
public:
  explicit Init_Guards_transition_pending(::hybrid_automaton_interfaces::msg::Guards & msg)
  : msg_(msg)
  {}
  Init_Guards_guard_names transition_pending(::hybrid_automaton_interfaces::msg::Guards::_transition_pending_type arg)
  {
    msg_.transition_pending = std::move(arg);
    return Init_Guards_guard_names(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

class Init_Guards_transition_eval_id
{
public:
  explicit Init_Guards_transition_eval_id(::hybrid_automaton_interfaces::msg::Guards & msg)
  : msg_(msg)
  {}
  Init_Guards_transition_pending transition_eval_id(::hybrid_automaton_interfaces::msg::Guards::_transition_eval_id_type arg)
  {
    msg_.transition_eval_id = std::move(arg);
    return Init_Guards_transition_pending(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

class Init_Guards_control_mode
{
public:
  Init_Guards_control_mode()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Guards_transition_eval_id control_mode(::hybrid_automaton_interfaces::msg::Guards::_control_mode_type arg)
  {
    msg_.control_mode = std::move(arg);
    return Init_Guards_transition_eval_id(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Guards msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::msg::Guards>()
{
  return hybrid_automaton_interfaces::msg::builder::Init_Guards_control_mode();
}

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__GUARDS__BUILDER_HPP_
