// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hybrid_automaton_interfaces:msg/TransitionPending.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_PENDING__TRAITS_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_PENDING__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "hybrid_automaton_interfaces/msg/detail/transition_pending__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'transition_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace hybrid_automaton_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const TransitionPending & msg,
  std::ostream & out)
{
  out << "{";
  // member: transition_uuid
  {
    out << "transition_uuid: ";
    to_flow_style_yaml(msg.transition_uuid, out);
    out << ", ";
  }

  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
    out << ", ";
  }

  // member: transition_pending
  {
    out << "transition_pending: ";
    rosidl_generator_traits::value_to_yaml(msg.transition_pending, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const TransitionPending & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: transition_uuid
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "transition_uuid:\n";
    to_block_style_yaml(msg.transition_uuid, out, indentation + 2);
  }

  // member: stamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stamp:\n";
    to_block_style_yaml(msg.stamp, out, indentation + 2);
  }

  // member: transition_pending
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "transition_pending: ";
    rosidl_generator_traits::value_to_yaml(msg.transition_pending, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const TransitionPending & msg, bool use_flow_style = false)
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
  const hybrid_automaton_interfaces::msg::TransitionPending & msg,
  std::ostream & out, size_t indentation = 0)
{
  hybrid_automaton_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hybrid_automaton_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const hybrid_automaton_interfaces::msg::TransitionPending & msg)
{
  return hybrid_automaton_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<hybrid_automaton_interfaces::msg::TransitionPending>()
{
  return "hybrid_automaton_interfaces::msg::TransitionPending";
}

template<>
inline const char * name<hybrid_automaton_interfaces::msg::TransitionPending>()
{
  return "hybrid_automaton_interfaces/msg/TransitionPending";
}

template<>
struct has_fixed_size<hybrid_automaton_interfaces::msg::TransitionPending>
  : std::integral_constant<bool, has_fixed_size<builtin_interfaces::msg::Time>::value && has_fixed_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct has_bounded_size<hybrid_automaton_interfaces::msg::TransitionPending>
  : std::integral_constant<bool, has_bounded_size<builtin_interfaces::msg::Time>::value && has_bounded_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct is_message<hybrid_automaton_interfaces::msg::TransitionPending>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_PENDING__TRAITS_HPP_
