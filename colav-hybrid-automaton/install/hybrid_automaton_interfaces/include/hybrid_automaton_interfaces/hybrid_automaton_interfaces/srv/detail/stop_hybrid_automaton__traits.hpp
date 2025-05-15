// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hybrid_automaton_interfaces:srv/StopHybridAutomaton.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__STOP_HYBRID_AUTOMATON__TRAITS_HPP_
#define HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__STOP_HYBRID_AUTOMATON__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "hybrid_automaton_interfaces/srv/detail/stop_hybrid_automaton__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"
// Member 'automaton_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"

namespace hybrid_automaton_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const StopHybridAutomaton_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
    out << ", ";
  }

  // member: automaton_uuid
  {
    out << "automaton_uuid: ";
    to_flow_style_yaml(msg.automaton_uuid, out);
    out << ", ";
  }

  // member: stop_reason
  {
    out << "stop_reason: ";
    rosidl_generator_traits::value_to_yaml(msg.stop_reason, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const StopHybridAutomaton_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: stamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stamp:\n";
    to_block_style_yaml(msg.stamp, out, indentation + 2);
  }

  // member: automaton_uuid
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "automaton_uuid:\n";
    to_block_style_yaml(msg.automaton_uuid, out, indentation + 2);
  }

  // member: stop_reason
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stop_reason: ";
    rosidl_generator_traits::value_to_yaml(msg.stop_reason, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const StopHybridAutomaton_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace hybrid_automaton_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use hybrid_automaton_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  hybrid_automaton_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hybrid_automaton_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request & msg)
{
  return hybrid_automaton_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request>()
{
  return "hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request";
}

template<>
inline const char * name<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request>()
{
  return "hybrid_automaton_interfaces/srv/StopHybridAutomaton_Request";
}

template<>
struct has_fixed_size<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'automaton_uuid'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"

namespace hybrid_automaton_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const StopHybridAutomaton_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: automaton_uuid
  {
    out << "automaton_uuid: ";
    to_flow_style_yaml(msg.automaton_uuid, out);
    out << ", ";
  }

  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
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
  const StopHybridAutomaton_Response & msg,
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

  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
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

inline std::string to_yaml(const StopHybridAutomaton_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace hybrid_automaton_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use hybrid_automaton_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  hybrid_automaton_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hybrid_automaton_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response & msg)
{
  return hybrid_automaton_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response>()
{
  return "hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response";
}

template<>
inline const char * name<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response>()
{
  return "hybrid_automaton_interfaces/srv/StopHybridAutomaton_Response";
}

template<>
struct has_fixed_size<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<hybrid_automaton_interfaces::srv::StopHybridAutomaton>()
{
  return "hybrid_automaton_interfaces::srv::StopHybridAutomaton";
}

template<>
inline const char * name<hybrid_automaton_interfaces::srv::StopHybridAutomaton>()
{
  return "hybrid_automaton_interfaces/srv/StopHybridAutomaton";
}

template<>
struct has_fixed_size<hybrid_automaton_interfaces::srv::StopHybridAutomaton>
  : std::integral_constant<
    bool,
    has_fixed_size<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request>::value &&
    has_fixed_size<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response>::value
  >
{
};

template<>
struct has_bounded_size<hybrid_automaton_interfaces::srv::StopHybridAutomaton>
  : std::integral_constant<
    bool,
    has_bounded_size<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request>::value &&
    has_bounded_size<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response>::value
  >
{
};

template<>
struct is_service<hybrid_automaton_interfaces::srv::StopHybridAutomaton>
  : std::true_type
{
};

template<>
struct is_service_request<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request>
  : std::true_type
{
};

template<>
struct is_service_response<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__STOP_HYBRID_AUTOMATON__TRAITS_HPP_
