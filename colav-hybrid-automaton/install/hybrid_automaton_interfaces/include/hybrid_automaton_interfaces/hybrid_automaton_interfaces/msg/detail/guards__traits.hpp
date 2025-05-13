// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hybrid_automaton_interfaces:msg/Guards.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__GUARDS__TRAITS_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__GUARDS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "hybrid_automaton_interfaces/msg/detail/guards__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'timestamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace hybrid_automaton_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const Guards & msg,
  std::ostream & out)
{
  out << "{";
  // member: control_mode
  {
    out << "control_mode: ";
    rosidl_generator_traits::value_to_yaml(msg.control_mode, out);
    out << ", ";
  }

  // member: transition_eval_id
  {
    out << "transition_eval_id: ";
    rosidl_generator_traits::value_to_yaml(msg.transition_eval_id, out);
    out << ", ";
  }

  // member: transition_pending
  {
    out << "transition_pending: ";
    rosidl_generator_traits::value_to_yaml(msg.transition_pending, out);
    out << ", ";
  }

  // member: guard_names
  {
    if (msg.guard_names.size() == 0) {
      out << "guard_names: []";
    } else {
      out << "guard_names: [";
      size_t pending_items = msg.guard_names.size();
      for (auto item : msg.guard_names) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: cruise_to_t2los_1
  {
    out << "cruise_to_t2los_1: ";
    rosidl_generator_traits::value_to_yaml(msg.cruise_to_t2los_1, out);
    out << ", ";
  }

  // member: cruise_to_t2los_2
  {
    out << "cruise_to_t2los_2: ";
    rosidl_generator_traits::value_to_yaml(msg.cruise_to_t2los_2, out);
    out << ", ";
  }

  // member: cruise_to_waypoint_reached
  {
    out << "cruise_to_waypoint_reached: ";
    rosidl_generator_traits::value_to_yaml(msg.cruise_to_waypoint_reached, out);
    out << ", ";
  }

  // member: cruise_to_fb
  {
    out << "cruise_to_fb: ";
    rosidl_generator_traits::value_to_yaml(msg.cruise_to_fb, out);
    out << ", ";
  }

  // member: t2los_to_cruise
  {
    out << "t2los_to_cruise: ";
    rosidl_generator_traits::value_to_yaml(msg.t2los_to_cruise, out);
    out << ", ";
  }

  // member: t2los_to_fb
  {
    out << "t2los_to_fb: ";
    rosidl_generator_traits::value_to_yaml(msg.t2los_to_fb, out);
    out << ", ";
  }

  // member: t2los_to_waypoint_reached
  {
    out << "t2los_to_waypoint_reached: ";
    rosidl_generator_traits::value_to_yaml(msg.t2los_to_waypoint_reached, out);
    out << ", ";
  }

  // member: waypoint_reached_to_cruise
  {
    out << "waypoint_reached_to_cruise: ";
    rosidl_generator_traits::value_to_yaml(msg.waypoint_reached_to_cruise, out);
    out << ", ";
  }

  // member: timestamp
  {
    out << "timestamp: ";
    to_flow_style_yaml(msg.timestamp, out);
    out << ", ";
  }

  // member: error
  {
    out << "error: ";
    rosidl_generator_traits::value_to_yaml(msg.error, out);
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
  const Guards & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: control_mode
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "control_mode: ";
    rosidl_generator_traits::value_to_yaml(msg.control_mode, out);
    out << "\n";
  }

  // member: transition_eval_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "transition_eval_id: ";
    rosidl_generator_traits::value_to_yaml(msg.transition_eval_id, out);
    out << "\n";
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

  // member: guard_names
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.guard_names.size() == 0) {
      out << "guard_names: []\n";
    } else {
      out << "guard_names:\n";
      for (auto item : msg.guard_names) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: cruise_to_t2los_1
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "cruise_to_t2los_1: ";
    rosidl_generator_traits::value_to_yaml(msg.cruise_to_t2los_1, out);
    out << "\n";
  }

  // member: cruise_to_t2los_2
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "cruise_to_t2los_2: ";
    rosidl_generator_traits::value_to_yaml(msg.cruise_to_t2los_2, out);
    out << "\n";
  }

  // member: cruise_to_waypoint_reached
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "cruise_to_waypoint_reached: ";
    rosidl_generator_traits::value_to_yaml(msg.cruise_to_waypoint_reached, out);
    out << "\n";
  }

  // member: cruise_to_fb
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "cruise_to_fb: ";
    rosidl_generator_traits::value_to_yaml(msg.cruise_to_fb, out);
    out << "\n";
  }

  // member: t2los_to_cruise
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "t2los_to_cruise: ";
    rosidl_generator_traits::value_to_yaml(msg.t2los_to_cruise, out);
    out << "\n";
  }

  // member: t2los_to_fb
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "t2los_to_fb: ";
    rosidl_generator_traits::value_to_yaml(msg.t2los_to_fb, out);
    out << "\n";
  }

  // member: t2los_to_waypoint_reached
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "t2los_to_waypoint_reached: ";
    rosidl_generator_traits::value_to_yaml(msg.t2los_to_waypoint_reached, out);
    out << "\n";
  }

  // member: waypoint_reached_to_cruise
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "waypoint_reached_to_cruise: ";
    rosidl_generator_traits::value_to_yaml(msg.waypoint_reached_to_cruise, out);
    out << "\n";
  }

  // member: timestamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "timestamp:\n";
    to_block_style_yaml(msg.timestamp, out, indentation + 2);
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

inline std::string to_yaml(const Guards & msg, bool use_flow_style = false)
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
  const hybrid_automaton_interfaces::msg::Guards & msg,
  std::ostream & out, size_t indentation = 0)
{
  hybrid_automaton_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hybrid_automaton_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const hybrid_automaton_interfaces::msg::Guards & msg)
{
  return hybrid_automaton_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<hybrid_automaton_interfaces::msg::Guards>()
{
  return "hybrid_automaton_interfaces::msg::Guards";
}

template<>
inline const char * name<hybrid_automaton_interfaces::msg::Guards>()
{
  return "hybrid_automaton_interfaces/msg/Guards";
}

template<>
struct has_fixed_size<hybrid_automaton_interfaces::msg::Guards>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hybrid_automaton_interfaces::msg::Guards>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hybrid_automaton_interfaces::msg::Guards>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__GUARDS__TRAITS_HPP_
