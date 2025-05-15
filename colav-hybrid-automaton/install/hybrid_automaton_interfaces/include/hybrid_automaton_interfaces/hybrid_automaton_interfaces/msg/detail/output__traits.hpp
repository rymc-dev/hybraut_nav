// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hybrid_automaton_interfaces:msg/Output.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__OUTPUT__TRAITS_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__OUTPUT__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "hybrid_automaton_interfaces/msg/detail/output__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'automaton_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"
// Member 'dynamics'
#include "hybrid_automaton_interfaces/msg/detail/dynamic_parameter__traits.hpp"
// Member 'time_since_last_transition'
// Member 'elapsed_time'
#include "builtin_interfaces/msg/detail/duration__traits.hpp"
// Member 'transition_pending'
#include "hybrid_automaton_interfaces/msg/detail/transition_pending__traits.hpp"
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"
// Member 'waypoints'
#include "colav_interfaces/msg/detail/waypoints__traits.hpp"

namespace hybrid_automaton_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const Output & msg,
  std::ostream & out)
{
  out << "{";
  // member: automaton_uuid
  {
    out << "automaton_uuid: ";
    to_flow_style_yaml(msg.automaton_uuid, out);
    out << ", ";
  }

  // member: mode
  {
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
    out << ", ";
  }

  // member: status
  {
    out << "status: ";
    rosidl_generator_traits::value_to_yaml(msg.status, out);
    out << ", ";
  }

  // member: dynamics
  {
    out << "dynamics: ";
    to_flow_style_yaml(msg.dynamics, out);
    out << ", ";
  }

  // member: time_since_last_transition
  {
    out << "time_since_last_transition: ";
    to_flow_style_yaml(msg.time_since_last_transition, out);
    out << ", ";
  }

  // member: transition_pending
  {
    out << "transition_pending: ";
    to_flow_style_yaml(msg.transition_pending, out);
    out << ", ";
  }

  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
    out << ", ";
  }

  // member: elapsed_time
  {
    out << "elapsed_time: ";
    to_flow_style_yaml(msg.elapsed_time, out);
    out << ", ";
  }

  // member: waypoints
  {
    out << "waypoints: ";
    to_flow_style_yaml(msg.waypoints, out);
    out << ", ";
  }

  // member: error
  {
    out << "error: ";
    rosidl_generator_traits::value_to_yaml(msg.error, out);
    out << ", ";
  }

  // member: message
  {
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Output & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: automaton_uuid
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "automaton_uuid:\n";
    to_block_style_yaml(msg.automaton_uuid, out, indentation + 2);
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

  // member: status
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "status: ";
    rosidl_generator_traits::value_to_yaml(msg.status, out);
    out << "\n";
  }

  // member: dynamics
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "dynamics:\n";
    to_block_style_yaml(msg.dynamics, out, indentation + 2);
  }

  // member: time_since_last_transition
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "time_since_last_transition:\n";
    to_block_style_yaml(msg.time_since_last_transition, out, indentation + 2);
  }

  // member: transition_pending
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "transition_pending:\n";
    to_block_style_yaml(msg.transition_pending, out, indentation + 2);
  }

  // member: stamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stamp:\n";
    to_block_style_yaml(msg.stamp, out, indentation + 2);
  }

  // member: elapsed_time
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "elapsed_time:\n";
    to_block_style_yaml(msg.elapsed_time, out, indentation + 2);
  }

  // member: waypoints
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "waypoints:\n";
    to_block_style_yaml(msg.waypoints, out, indentation + 2);
  }

  // member: error
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "error: ";
    rosidl_generator_traits::value_to_yaml(msg.error, out);
    out << "\n";
  }

  // member: message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Output & msg, bool use_flow_style = false)
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
  const hybrid_automaton_interfaces::msg::Output & msg,
  std::ostream & out, size_t indentation = 0)
{
  hybrid_automaton_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hybrid_automaton_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const hybrid_automaton_interfaces::msg::Output & msg)
{
  return hybrid_automaton_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<hybrid_automaton_interfaces::msg::Output>()
{
  return "hybrid_automaton_interfaces::msg::Output";
}

template<>
inline const char * name<hybrid_automaton_interfaces::msg::Output>()
{
  return "hybrid_automaton_interfaces/msg/Output";
}

template<>
struct has_fixed_size<hybrid_automaton_interfaces::msg::Output>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hybrid_automaton_interfaces::msg::Output>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hybrid_automaton_interfaces::msg::Output>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__OUTPUT__TRAITS_HPP_
