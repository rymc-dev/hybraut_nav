// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hybrid_automaton_interfaces:msg/DynamicParameter.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMIC_PARAMETER__BUILDER_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMIC_PARAMETER__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hybrid_automaton_interfaces/msg/detail/dynamic_parameter__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hybrid_automaton_interfaces
{

namespace msg
{

namespace builder
{

class Init_DynamicParameter_dynamic_units
{
public:
  explicit Init_DynamicParameter_dynamic_units(::hybrid_automaton_interfaces::msg::DynamicParameter & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::msg::DynamicParameter dynamic_units(::hybrid_automaton_interfaces::msg::DynamicParameter::_dynamic_units_type arg)
  {
    msg_.dynamic_units = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::DynamicParameter msg_;
};

class Init_DynamicParameter_dynamic_value
{
public:
  explicit Init_DynamicParameter_dynamic_value(::hybrid_automaton_interfaces::msg::DynamicParameter & msg)
  : msg_(msg)
  {}
  Init_DynamicParameter_dynamic_units dynamic_value(::hybrid_automaton_interfaces::msg::DynamicParameter::_dynamic_value_type arg)
  {
    msg_.dynamic_value = std::move(arg);
    return Init_DynamicParameter_dynamic_units(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::DynamicParameter msg_;
};

class Init_DynamicParameter_dynamic_name
{
public:
  explicit Init_DynamicParameter_dynamic_name(::hybrid_automaton_interfaces::msg::DynamicParameter & msg)
  : msg_(msg)
  {}
  Init_DynamicParameter_dynamic_value dynamic_name(::hybrid_automaton_interfaces::msg::DynamicParameter::_dynamic_name_type arg)
  {
    msg_.dynamic_name = std::move(arg);
    return Init_DynamicParameter_dynamic_value(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::DynamicParameter msg_;
};

class Init_DynamicParameter_controller_name
{
public:
  Init_DynamicParameter_controller_name()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DynamicParameter_dynamic_name controller_name(::hybrid_automaton_interfaces::msg::DynamicParameter::_controller_name_type arg)
  {
    msg_.controller_name = std::move(arg);
    return Init_DynamicParameter_dynamic_name(msg_);
  }

private:
  ::hybrid_automaton_interfaces::msg::DynamicParameter msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::msg::DynamicParameter>()
{
  return hybrid_automaton_interfaces::msg::builder::Init_DynamicParameter_controller_name();
}

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMIC_PARAMETER__BUILDER_HPP_
