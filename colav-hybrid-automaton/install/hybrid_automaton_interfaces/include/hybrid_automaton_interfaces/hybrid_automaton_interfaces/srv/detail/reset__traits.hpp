// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hybrid_automaton_interfaces:srv/Reset.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__RESET__TRAITS_HPP_
#define HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__RESET__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "hybrid_automaton_interfaces/srv/detail/reset__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'transition_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"

namespace hybrid_automaton_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const Reset_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: transition_uuid
  {
    out << "transition_uuid: ";
    to_flow_style_yaml(msg.transition_uuid, out);
    out << ", ";
  }

  // member: reset_name
  {
    out << "reset_name: ";
    rosidl_generator_traits::value_to_yaml(msg.reset_name, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Reset_Request & msg,
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

  // member: reset_name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "reset_name: ";
    rosidl_generator_traits::value_to_yaml(msg.reset_name, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Reset_Request & msg, bool use_flow_style = false)
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
  const hybrid_automaton_interfaces::srv::Reset_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  hybrid_automaton_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hybrid_automaton_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const hybrid_automaton_interfaces::srv::Reset_Request & msg)
{
  return hybrid_automaton_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<hybrid_automaton_interfaces::srv::Reset_Request>()
{
  return "hybrid_automaton_interfaces::srv::Reset_Request";
}

template<>
inline const char * name<hybrid_automaton_interfaces::srv::Reset_Request>()
{
  return "hybrid_automaton_interfaces/srv/Reset_Request";
}

template<>
struct has_fixed_size<hybrid_automaton_interfaces::srv::Reset_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hybrid_automaton_interfaces::srv::Reset_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hybrid_automaton_interfaces::srv::Reset_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'transition_uuid'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"

namespace hybrid_automaton_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const Reset_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: transition_uuid
  {
    out << "transition_uuid: ";
    to_flow_style_yaml(msg.transition_uuid, out);
    out << ", ";
  }

  // member: reset_name
  {
    out << "reset_name: ";
    rosidl_generator_traits::value_to_yaml(msg.reset_name, out);
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
  const Reset_Response & msg,
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

  // member: reset_name
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "reset_name: ";
    rosidl_generator_traits::value_to_yaml(msg.reset_name, out);
    out << "\n";
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

inline std::string to_yaml(const Reset_Response & msg, bool use_flow_style = false)
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
  const hybrid_automaton_interfaces::srv::Reset_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  hybrid_automaton_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use hybrid_automaton_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const hybrid_automaton_interfaces::srv::Reset_Response & msg)
{
  return hybrid_automaton_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<hybrid_automaton_interfaces::srv::Reset_Response>()
{
  return "hybrid_automaton_interfaces::srv::Reset_Response";
}

template<>
inline const char * name<hybrid_automaton_interfaces::srv::Reset_Response>()
{
  return "hybrid_automaton_interfaces/srv/Reset_Response";
}

template<>
struct has_fixed_size<hybrid_automaton_interfaces::srv::Reset_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hybrid_automaton_interfaces::srv::Reset_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hybrid_automaton_interfaces::srv::Reset_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<hybrid_automaton_interfaces::srv::Reset>()
{
  return "hybrid_automaton_interfaces::srv::Reset";
}

template<>
inline const char * name<hybrid_automaton_interfaces::srv::Reset>()
{
  return "hybrid_automaton_interfaces/srv/Reset";
}

template<>
struct has_fixed_size<hybrid_automaton_interfaces::srv::Reset>
  : std::integral_constant<
    bool,
    has_fixed_size<hybrid_automaton_interfaces::srv::Reset_Request>::value &&
    has_fixed_size<hybrid_automaton_interfaces::srv::Reset_Response>::value
  >
{
};

template<>
struct has_bounded_size<hybrid_automaton_interfaces::srv::Reset>
  : std::integral_constant<
    bool,
    has_bounded_size<hybrid_automaton_interfaces::srv::Reset_Request>::value &&
    has_bounded_size<hybrid_automaton_interfaces::srv::Reset_Response>::value
  >
{
};

template<>
struct is_service<hybrid_automaton_interfaces::srv::Reset>
  : std::true_type
{
};

template<>
struct is_service_request<hybrid_automaton_interfaces::srv::Reset_Request>
  : std::true_type
{
};

template<>
struct is_service_response<hybrid_automaton_interfaces::srv::Reset_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__RESET__TRAITS_HPP_
