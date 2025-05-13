// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hybrid_automaton_interfaces:msg/Transition.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION__TRAITS_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "hybrid_automaton_interfaces/msg/detail/transition__struct.hpp"
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
  const Transition & msg,
  std::ostream & out)
{
  out << "{";
  // member: transition_uuid
  {
    out << "transition_uuid: ";
    to_flow_style_yaml(msg.transition_uuid, out);
    out << ", ";
  }

  // member: mode
  {
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
    out << ", ";
  }

  // member: transition_names
  {
    if (msg.transition_names.size() == 0) {
      out << "transition_names: []";
    } else {
      out << "transition_names: [";
      size_t pending_items = msg.transition_names.size();
      for (auto item : msg.transition_names) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: transition_values
  {
    if (msg.transition_values.size() == 0) {
      out << "transition_values: []";
    } else {
      out << "transition_values: [";
      size_t pending_items = msg.transition_values.size();
      for (auto item : msg.transition_values) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: transition_priority
  {
    if (msg.transition_priority.size() == 0) {
      out << "transition_priority: []";
    } else {
      out << "transition_priority: [";
      size_t pending_items = msg.transition_priority.size();
      for (auto item : msg.transition_priority) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
    out << ", ";
  }

  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: error_message
  {
    out << "error_message: ";
    rosidl_generator_traits::value_to_yaml(msg.error_message, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Transition & msg,
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

  // member: mode
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
    out << "\n";
  }

  // member: transition_names
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.transition_names.size() == 0) {
      out << "transition_names: []\n";
    } else {
      out << "transition_names:\n";
      for (auto item : msg.transition_names) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: transition_values
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.transition_values.size() == 0) {
      out << "transition_values: []\n";
    } else {
      out << "transition_values:\n";
      for (auto item : msg.transition_values) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: transition_priority
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.transition_priority.size() == 0) {
      out << "transition_priority: []\n";
    } else {
      out << "transition_priority:\n";
      for (auto item : msg.transition_priority) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: stamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stamp:\n";
    to_block_style_yaml(msg.stamp, out, indentation + 2);
  }

  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }

  // member: error_message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "error_message: ";
    rosidl_generator_traits::value_to_yaml(msg.error_message, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Transition & msg, bool use_flow_style = false)
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
  const hybrid_automaton_interfaces::msg::Transition & msg,
  std::ostream & out, size_t indentation = 0)
{
  hybrid_automaton_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hybrid_automaton_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const hybrid_automaton_interfaces::msg::Transition & msg)
{
  return hybrid_automaton_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<hybrid_automaton_interfaces::msg::Transition>()
{
  return "hybrid_automaton_interfaces::msg::Transition";
}

template<>
inline const char * name<hybrid_automaton_interfaces::msg::Transition>()
{
  return "hybrid_automaton_interfaces/msg/Transition";
}

template<>
struct has_fixed_size<hybrid_automaton_interfaces::msg::Transition>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hybrid_automaton_interfaces::msg::Transition>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hybrid_automaton_interfaces::msg::Transition>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION__TRAITS_HPP_
