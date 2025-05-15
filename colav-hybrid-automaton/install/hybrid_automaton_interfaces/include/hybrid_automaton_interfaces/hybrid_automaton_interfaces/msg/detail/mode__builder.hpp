// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hybrid_automaton_interfaces:msg/Mode.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__MODE__BUILDER_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__MODE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hybrid_automaton_interfaces/msg/detail/mode__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hybrid_automaton_interfaces
{

namespace msg
{

namespace builder
{

class Init_Mode_origin_transition
{
public:
  explicit Init_Mode_origin_transition(::hybrid_automaton_interfaces::msg::Mode & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::msg::Mode origin_transition(::hybrid_automaton_interfaces::msg::Mode::_origin_transition_type arg)
  {
    msg_.origin_transition = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Mode msg_;
};

class Init_Mode_stamp
{
public:
  explicit Init_Mode_stamp(::hybrid_automaton_interfaces::msg::Mode & msg)
  : msg_(msg)
  {}
  Init_Mode_origin_transition stamp(::hybrid_automaton_interfaces::msg::Mode::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return Init_Mode_origin_transition(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Mode msg_;
};

class Init_Mode_mode
{
public:
  explicit Init_Mode_mode(::hybrid_automaton_interfaces::msg::Mode & msg)
  : msg_(msg)
  {}
  Init_Mode_stamp mode(::hybrid_automaton_interfaces::msg::Mode::_mode_type arg)
  {
    msg_.mode = std::move(arg);
    return Init_Mode_stamp(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Mode msg_;
};

class Init_Mode_mode_uuid
{
public:
  Init_Mode_mode_uuid()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Mode_mode mode_uuid(::hybrid_automaton_interfaces::msg::Mode::_mode_uuid_type arg)
  {
    msg_.mode_uuid = std::move(arg);
    return Init_Mode_mode(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Mode msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::msg::Mode>()
{
  return hybrid_automaton_interfaces::msg::builder::Init_Mode_mode_uuid();
}

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__MODE__BUILDER_HPP_
