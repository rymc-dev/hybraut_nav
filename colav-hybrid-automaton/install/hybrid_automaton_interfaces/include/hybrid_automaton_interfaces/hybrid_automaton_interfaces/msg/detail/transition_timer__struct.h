// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hybrid_automaton_interfaces:msg/TransitionTimer.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_TIMER__STRUCT_H_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_TIMER__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'previous_transition_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'elapsed'
// Member 'timeout'
#include "builtin_interfaces/msg/detail/duration__struct.h"

/// Struct defined in msg/TransitionTimer in the package hybrid_automaton_interfaces.
/**
  * TransitionTimer.msg
  * ROS 2 interface for the Hybrid Automaton framework.
  * Publishes timing information related to dynamic updates.
  * Used to monitor synchronization and detect delays or missed updates 
  * in the hybrid automaton's control modes.
 */
typedef struct hybrid_automaton_interfaces__msg__TransitionTimer
{
  /// PURPOSE: This message tracks the elapsed time since the last transition evaluation.
  /// It supports runtime evalution of system responsiveness and  timeout detection.
  /// NOTE: Do not modify this file.
  /// UUID of previous transition_evaluation
  unique_identifier_msgs__msg__UUID previous_transition_uuid;
  /// Duration since the last transition evaluation
  builtin_interfaces__msg__Duration elapsed;
  /// Configured timeout duration for transition evaluation
  builtin_interfaces__msg__Duration timeout;
  /// Timeout value in seconds (for comvenience of compatibility)
  double timeout_sec;
  /// True if elapsed time has exceeded the timeout threshold
  bool expired;
} hybrid_automaton_interfaces__msg__TransitionTimer;

// Struct for a sequence of hybrid_automaton_interfaces__msg__TransitionTimer.
typedef struct hybrid_automaton_interfaces__msg__TransitionTimer__Sequence
{
  hybrid_automaton_interfaces__msg__TransitionTimer * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__msg__TransitionTimer__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_TIMER__STRUCT_H_
