// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hybrid_automaton_interfaces:msg/DynamicParameter.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMIC_PARAMETER__TRAITS_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMIC_PARAMETER__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "hybrid_automaton_interfaces/msg/detail/dynamic_parameter__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace hybrid_automaton_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const DynamicParameter & msg,
  std::ostream & out)
{
  out << "{";
  // member: controller_name
  {
    out << "controller_name: ";
    rosidl_generator_traits::value_to_yaml(msg.controller_name, out);
    out << ", ";
  }

  // member: dynamic_name
  {
    if (msg.dynamic_name.size() == 0) {
      out << "dynamic_name: []";
    } else {
      out << "dynamic_name: [";
      size_t pending_items = msg.dynamic_name.size();
      for (auto item : msg.dynamic_name) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: dynamic_value
  {
    if (msg.dynamic_value.size() == 0) {
      out << "dynamic_value: []";
    } else {
      out << "dynamic_value: [";
      size_t pending_items = msg.dynamic_value.size();
      for (auto item : msg.dynamic_value) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: dynamic_units
  {
    if (msg.dynamic_units.size() == 0) {
      out << "dynamic_units: []";
    } else {
      out << "dynamic_units: [";
      size_t pending_items = msg.dynamic_units.size();
      for (auto item : msg.dynamic_units) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const DynamicParameter & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: controller_name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "controller_name: ";
    rosidl_generator_traits::value_to_yaml(msg.controller_name, out);
    out << "\n";
  }

  // member: dynamic_name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.dynamic_name.size() == 0) {
      out << "dynamic_name: []\n";
    } else {
      out << "dynamic_name:\n";
      for (auto item : msg.dynamic_name) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: dynamic_value
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.dynamic_value.size() == 0) {
      out << "dynamic_value: []\n";
    } else {
      out << "dynamic_value:\n";
      for (auto item : msg.dynamic_value) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: dynamic_units
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.dynamic_units.size() == 0) {
      out << "dynamic_units: []\n";
    } else {
      out << "dynamic_units:\n";
      for (auto item : msg.dynamic_units) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const DynamicParameter & msg, bool use_flow_style = false)
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
  const hybrid_automaton_interfaces::msg::DynamicParameter & msg,
  std::ostream & out, size_t indentation = 0)
{
  hybrid_automaton_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hybrid_automaton_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const hybrid_automaton_interfaces::msg::DynamicParameter & msg)
{
  return hybrid_automaton_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<hybrid_automaton_interfaces::msg::DynamicParameter>()
{
  return "hybrid_automaton_interfaces::msg::DynamicParameter";
}

template<>
inline const char * name<hybrid_automaton_interfaces::msg::DynamicParameter>()
{
  return "hybrid_automaton_interfaces/msg/DynamicParameter";
}

template<>
struct has_fixed_size<hybrid_automaton_interfaces::msg::DynamicParameter>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hybrid_automaton_interfaces::msg::DynamicParameter>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hybrid_automaton_interfaces::msg::DynamicParameter>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMIC_PARAMETER__TRAITS_HPP_
