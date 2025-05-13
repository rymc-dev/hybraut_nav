// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hybrid_automaton_interfaces:msg/Mode.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__MODE__TRAITS_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__MODE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "hybrid_automaton_interfaces/msg/detail/mode__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'mode_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace hybrid_automaton_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const Mode & msg,
  std::ostream & out)
{
  out << "{";
  // member: mode_uuid
  {
    out << "mode_uuid: ";
    to_flow_style_yaml(msg.mode_uuid, out);
    out << ", ";
  }

  // member: mode
  {
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
    out << ", ";
  }

  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
    out << ", ";
  }

  // member: origin_transition
  {
    out << "origin_transition: ";
    rosidl_generator_traits::value_to_yaml(msg.origin_transition, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Mode & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: mode_uuid
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mode_uuid:\n";
    to_block_style_yaml(msg.mode_uuid, out, indentation + 2);
  }

  // member: mode
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
    out << "\n";
  }

  // member: stamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stamp:\n";
    to_block_style_yaml(msg.stamp, out, indentation + 2);
  }

  // member: origin_transition
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "origin_transition: ";
    rosidl_generator_traits::value_to_yaml(msg.origin_transition, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Mode & msg, bool use_flow_style = false)
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
  const hybrid_automaton_interfaces::msg::Mode & msg,
  std::ostream & out, size_t indentation = 0)
{
  hybrid_automaton_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hybrid_automaton_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const hybrid_automaton_interfaces::msg::Mode & msg)
{
  return hybrid_automaton_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<hybrid_automaton_interfaces::msg::Mode>()
{
  return "hybrid_automaton_interfaces::msg::Mode";
}

template<>
inline const char * name<hybrid_automaton_interfaces::msg::Mode>()
{
  return "hybrid_automaton_interfaces/msg/Mode";
}

template<>
struct has_fixed_size<hybrid_automaton_interfaces::msg::Mode>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hybrid_automaton_interfaces::msg::Mode>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hybrid_automaton_interfaces::msg::Mode>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__MODE__TRAITS_HPP_
