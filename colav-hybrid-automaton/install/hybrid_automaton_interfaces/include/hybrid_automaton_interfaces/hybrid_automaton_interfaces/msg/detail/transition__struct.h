// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hybrid_automaton_interfaces:msg/Transition.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION__STRUCT_H_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION__STRUCT_H_

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
// Member 'mode'
// Member 'transition_names'
// Member 'error_message'
#include "rosidl_runtime_c/string.h"
// Member 'transition_values'
// Member 'transition_priority'
#include "rosidl_runtime_c/primitives_sequence.h"
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in msg/Transition in the package hybrid_automaton_interfaces.
/**
  * Transitions.msg
  * ROS 2 interface for the Hybrid Automaton framework.
  *
  * This message enables real-time evaluation of control mode transitions 
  * based on the current operational state. Each transition corresponds to one 
  * of the control modes defined in the configuration file:
  * `/hybrid_automaton/config/hybrid_automaton_config.yml` 
  * (e.g., GO_FORWARD, GO_RIGHT, etc.).
  *
  * NOTE: Do not modify anything outside the boundaries marked 
  * 'Custom Transition Parameters Start' and 'Custom Transition Parameters End'.
  * Only edit within that section to define or update your custom transition parameters.
 */
typedef struct hybrid_automaton_interfaces__msg__Transition
{
  /// Unique identifier for this transition evaluation instance.
  unique_identifier_msgs__msg__UUID transition_uuid;
  /// Current Hybrid Automaton mode (e.g., GO_FORWARD, GO_RIGHT, etc.).
  rosidl_runtime_c__String mode;
  /// Names of transitions evaluated in this update cycle.
  /// key
  rosidl_runtime_c__String__Sequence transition_names;
  /// value
  rosidl_runtime_c__boolean__Sequence transition_values;
  /// priorite for transitions
  rosidl_runtime_c__int32__Sequence transition_priority;
  /// Timestamp when this transition update was published.
  builtin_interfaces__msg__Time stamp;
  /// Metadata indicating success of the update.
  /// If unsuccessful, the error message will describe the issue.
  bool success;
  rosidl_runtime_c__String error_message;
} hybrid_automaton_interfaces__msg__Transition;

// Struct for a sequence of hybrid_automaton_interfaces__msg__Transition.
typedef struct hybrid_automaton_interfaces__msg__Transition__Sequence
{
  hybrid_automaton_interfaces__msg__Transition * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__msg__Transition__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION__STRUCT_H_
