// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hybrid_automaton_interfaces:msg/DynamicsTimer.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS_TIMER__TRAITS_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS_TIMER__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "hybrid_automaton_interfaces/msg/detail/dynamics_timer__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'previous_dynamic_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"
// Member 'elapsed'
// Member 'timeout'
#include "builtin_interfaces/msg/detail/duration__traits.hpp"

namespace hybrid_automaton_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const DynamicsTimer & msg,
  std::ostream & out)
{
  out << "{";
  // member: previous_dynamic_uuid
  {
    out << "previous_dynamic_uuid: ";
    to_flow_style_yaml(msg.previous_dynamic_uuid, out);
    out << ", ";
  }

  // member: elapsed
  {
    out << "elapsed: ";
    to_flow_style_yaml(msg.elapsed, out);
    out << ", ";
  }

  // member: timeout
  {
    out << "timeout: ";
    to_flow_style_yaml(msg.timeout, out);
    out << ", ";
  }

  // member: timeout_sec
  {
    out << "timeout_sec: ";
    rosidl_generator_traits::value_to_yaml(msg.timeout_sec, out);
    out << ", ";
  }

  // member: expired
  {
    out << "expired: ";
    rosidl_generator_traits::value_to_yaml(msg.expired, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const DynamicsTimer & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: previous_dynamic_uuid
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "previous_dynamic_uuid:\n";
    to_block_style_yaml(msg.previous_dynamic_uuid, out, indentation + 2);
  }

  // member: elapsed
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "elapsed:\n";
    to_block_style_yaml(msg.elapsed, out, indentation + 2);
  }

  // member: timeout
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "timeout:\n";
    to_block_style_yaml(msg.timeout, out, indentation + 2);
  }

  // member: timeout_sec
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "timeout_sec: ";
    rosidl_generator_traits::value_to_yaml(msg.timeout_sec, out);
    out << "\n";
  }

  // member: expired
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "expired: ";
    rosidl_generator_traits::value_to_yaml(msg.expired, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const DynamicsTimer & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace hybrid_automaton_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use hybrid_automaton_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const hybrid_automaton_interfaces::msg::DynamicsTimer & msg,
  std::ostream & out, size_t indentation = 0)
{
  hybrid_automaton_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hybrid_automaton_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const hybrid_automaton_interfaces::msg::DynamicsTimer & msg)
{
  return hybrid_automaton_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<hybrid_automaton_interfaces::msg::DynamicsTimer>()
{
  return "hybrid_automaton_interfaces::msg::DynamicsTimer";
}

template<>
inline const char * name<hybrid_automaton_interfaces::msg::DynamicsTimer>()
{
  return "hybrid_automaton_interfaces/msg/DynamicsTimer";
}

template<>
struct has_fixed_size<hybrid_automaton_interfaces::msg::DynamicsTimer>
  : std::integral_constant<bool, has_fixed_size<builtin_interfaces::msg::Duration>::value && has_fixed_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct has_bounded_size<hybrid_automaton_interfaces::msg::DynamicsTimer>
  : std::integral_constant<bool, has_bounded_size<builtin_interfaces::msg::Duration>::value && has_bounded_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct is_message<hybrid_automaton_interfaces::msg::DynamicsTimer>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS_TIMER__TRAITS_HPP_
