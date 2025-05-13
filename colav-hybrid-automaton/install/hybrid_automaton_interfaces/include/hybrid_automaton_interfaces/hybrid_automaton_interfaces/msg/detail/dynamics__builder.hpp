// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hybrid_automaton_interfaces:msg/Dynamics.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS__BUILDER_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hybrid_automaton_interfaces/msg/detail/dynamics__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hybrid_automaton_interfaces
{

namespace msg
{

namespace builder
{

class Init_Dynamics_error_message
{
public:
  explicit Init_Dynamics_error_message(::hybrid_automaton_interfaces::msg::Dynamics & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::msg::Dynamics error_message(::hybrid_automaton_interfaces::msg::Dynamics::_error_message_type arg)
  {
    msg_.error_message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Dynamics msg_;
};

class Init_Dynamics_success
{
public:
  explicit Init_Dynamics_success(::hybrid_automaton_interfaces::msg::Dynamics & msg)
  : msg_(msg)
  {}
  Init_Dynamics_error_message success(::hybrid_automaton_interfaces::msg::Dynamics::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_Dynamics_error_message(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Dynamics msg_;
};

class Init_Dynamics_stamp
{
public:
  explicit Init_Dynamics_stamp(::hybrid_automaton_interfaces::msg::Dynamics & msg)
  : msg_(msg)
  {}
  Init_Dynamics_success stamp(::hybrid_automaton_interfaces::msg::Dynamics::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return Init_Dynamics_success(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Dynamics msg_;
};

class Init_Dynamics_dynamic_parameters
{
public:
  explicit Init_Dynamics_dynamic_parameters(::hybrid_automaton_interfaces::msg::Dynamics & msg)
  : msg_(msg)
  {}
  Init_Dynamics_stamp dynamic_parameters(::hybrid_automaton_interfaces::msg::Dynamics::_dynamic_parameters_type arg)
  {
    msg_.dynamic_parameters = std::move(arg);
    return Init_Dynamics_stamp(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Dynamics msg_;
};

class Init_Dynamics_mode
{
public:
  explicit Init_Dynamics_mode(::hybrid_automaton_interfaces::msg::Dynamics & msg)
  : msg_(msg)
  {}
  Init_Dynamics_dynamic_parameters mode(::hybrid_automaton_interfaces::msg::Dynamics::_mode_type arg)
  {
    msg_.mode = std::move(arg);
    return Init_Dynamics_dynamic_parameters(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Dynamics msg_;
};

class Init_Dynamics_dynamic_uuid
{
public:
  Init_Dynamics_dynamic_uuid()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Dynamics_mode dynamic_uuid(::hybrid_automaton_interfaces::msg::Dynamics::_dynamic_uuid_type arg)
  {
    msg_.dynamic_uuid = std::move(arg);
    return Init_Dynamics_mode(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::Dynamics msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::msg::Dynamics>()
{
  return hybrid_automaton_interfaces::msg::builder::Init_Dynamics_dynamic_uuid();
}

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS__BUILDER_HPP_
