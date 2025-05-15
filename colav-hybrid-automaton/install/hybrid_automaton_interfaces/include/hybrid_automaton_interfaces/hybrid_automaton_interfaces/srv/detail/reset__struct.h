// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hybrid_automaton_interfaces:srv/Reset.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__RESET__STRUCT_H_
#define HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__RESET__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'transition_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'reset_name'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/Reset in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__srv__Reset_Request
{
  /// NOTE: Do not modify this file.
  /// --- Request ---
  /// UUID of the transition to apply the reset to
  unique_identifier_msgs__msg__UUID transition_uuid;
  /// Name of the reset function to invoke
  rosidl_runtime_c__String reset_name;
} hybrid_automaton_interfaces__srv__Reset_Request;

// Struct for a sequence of hybrid_automaton_interfaces__srv__Reset_Request.
typedef struct hybrid_automaton_interfaces__srv__Reset_Request__Sequence
{
  hybrid_automaton_interfaces__srv__Reset_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__srv__Reset_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'transition_uuid'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'reset_name'
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/Reset in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__srv__Reset_Response
{
  /// --- Response ---
  /// UUID of the transition that was evaluated
  unique_identifier_msgs__msg__UUID transition_uuid;
  /// Name of the transition that was evaluated
  rosidl_runtime_c__String reset_name;
  /// Indicates whether the reset was applied successfully
  bool success;
  /// Summary message describing the result or error, if any
  rosidl_runtime_c__String message;
} hybrid_automaton_interfaces__srv__Reset_Response;

// Struct for a sequence of hybrid_automaton_interfaces__srv__Reset_Response.
typedef struct hybrid_automaton_interfaces__srv__Reset_Response__Sequence
{
  hybrid_automaton_interfaces__srv__Reset_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__srv__Reset_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__RESET__STRUCT_H_
