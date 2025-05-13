// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hybrid_automaton_interfaces:msg/Output.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__OUTPUT__STRUCT_H_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__OUTPUT__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'automaton_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'mode'
// Member 'status'
// Member 'message'
#include "rosidl_runtime_c/string.h"
// Member 'dynamics'
#include "hybrid_automaton_interfaces/msg/detail/dynamic_parameter__struct.h"
// Member 'time_since_last_transition'
// Member 'elapsed_time'
#include "builtin_interfaces/msg/detail/duration__struct.h"
// Member 'transition_pending'
#include "hybrid_automaton_interfaces/msg/detail/transition_pending__struct.h"
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"
// Member 'waypoints'
#include "colav_interfaces/msg/detail/waypoints__struct.h"

/// Struct defined in msg/Output in the package hybrid_automaton_interfaces.
/**
  * Output.msg
  * ROS 2 message for the hybrid automaton framework output
  *
  * This message provides the output of the hybrid automaton, allowing external agents 
  * to receive system state information, including dynamics, status, and relevant metadata 
  * such as the automaton UUID and timestamp.
  *
  * NOTE: Do not modify anything outside the boundaries marked
  * 'Additional Output Data Start' to 'Additional Output Data End'
 */
typedef struct hybrid_automaton_interfaces__msg__Output
{
  /// Unique identifier for the automaton instance
  unique_identifier_msgs__msg__UUID automaton_uuid;
  /// Current system mode of the automaton
  rosidl_runtime_c__String mode;
  /// Status string (e.g., "ACTIVE", "COMPLETE", etc.)
  rosidl_runtime_c__String status;
  /// Current system dynamics
  hybrid_automaton_interfaces__msg__DynamicParameter dynamics;
  /// Time since the last mode transition
  builtin_interfaces__msg__Duration time_since_last_transition;
  /// Indicates if a transition is pending
  hybrid_automaton_interfaces__msg__TransitionPending transition_pending;
  /// Timestamp of this output message
  builtin_interfaces__msg__Time stamp;
  /// Elapsed time since automaton started
  builtin_interfaces__msg__Duration elapsed_time;
  /// --- Additional Output Data Start ---
  /// Internal state waypoints for COLAV Hybrid Automaton
  colav_interfaces__msg__Waypoints waypoints;
  /// --- Additional Output Data End ---
  /// True if an error has occurred
  bool error;
  /// Additional context or information (e.g., success details or error descriptions)
  rosidl_runtime_c__String message;
} hybrid_automaton_interfaces__msg__Output;

// Struct for a sequence of hybrid_automaton_interfaces__msg__Output.
typedef struct hybrid_automaton_interfaces__msg__Output__Sequence
{
  hybrid_automaton_interfaces__msg__Output * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__msg__Output__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__OUTPUT__STRUCT_H_
