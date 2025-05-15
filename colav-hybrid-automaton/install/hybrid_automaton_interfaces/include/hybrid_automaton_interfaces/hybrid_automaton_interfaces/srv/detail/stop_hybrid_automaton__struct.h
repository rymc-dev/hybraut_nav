// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hybrid_automaton_interfaces:srv/StopHybridAutomaton.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__STOP_HYBRID_AUTOMATON__STRUCT_H_
#define HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__STOP_HYBRID_AUTOMATON__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"
// Member 'automaton_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'stop_reason'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/StopHybridAutomaton in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request
{
  /// --- Request ---
  /// Timestamp for synchronization of the request
  builtin_interfaces__msg__Time stamp;
  /// Unique identifier for the Hybrid Automaton instance to be stopped
  unique_identifier_msgs__msg__UUID automaton_uuid;
  /// Optional: A reason for stopping the automaton (e.g., "mission_complete", "manual_stop", "error")
  rosidl_runtime_c__String stop_reason;
} hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request;

// Struct for a sequence of hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request.
typedef struct hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence
{
  hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'automaton_uuid'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/StopHybridAutomaton in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response
{
  /// Echo the automaton_uuid to confirm which automaton was stopped
  unique_identifier_msgs__msg__UUID automaton_uuid;
  /// Indicates whether the Hybrid Automaton was successfully terminated
  bool success;
  /// Optional: Detailed message providing additional information (e.g., "Successfully stopped", "Error: automaton not found")
  rosidl_runtime_c__String message;
} hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response;

// Struct for a sequence of hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response.
typedef struct hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence
{
  hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__STOP_HYBRID_AUTOMATON__STRUCT_H_
