// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hybrid_automaton_interfaces:msg/DynamicsTimer.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS_TIMER__STRUCT_H_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS_TIMER__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'previous_dynamic_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'elapsed'
// Member 'timeout'
#include "builtin_interfaces/msg/detail/duration__struct.h"

/// Struct defined in msg/DynamicsTimer in the package hybrid_automaton_interfaces.
/**
  * DynamicsTimer.msg
  * ROS 2 interface for the Hybrid Automaton framework.
  * Publishes timing information related to dynamic updates.
  * Used to monitor synchronization and detect delays or missed updates 
  * in the hybrid automaton's control modes.
 */
typedef struct hybrid_automaton_interfaces__msg__DynamicsTimer
{
  /// PURPOSE: This message tracks the elapsed time since the last dynamics update.
  /// It supports runtime evaluation of system responsiveness and timeout detection.
  /// NOTE: Do not modify this file.
  /// UUID of the most recent dynamic update
  unique_identifier_msgs__msg__UUID previous_dynamic_uuid;
  /// Duration since the last dynamics update was received
  builtin_interfaces__msg__Duration elapsed;
  /// Configured timeout duration for dynamics updates
  builtin_interfaces__msg__Duration timeout;
  /// Timeout value in seconds (for convenience or compatibility)
  double timeout_sec;
  /// True if the elapsed time has exceeded the timeout threshold
  bool expired;
} hybrid_automaton_interfaces__msg__DynamicsTimer;

// Struct for a sequence of hybrid_automaton_interfaces__msg__DynamicsTimer.
typedef struct hybrid_automaton_interfaces__msg__DynamicsTimer__Sequence
{
  hybrid_automaton_interfaces__msg__DynamicsTimer * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__msg__DynamicsTimer__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS_TIMER__STRUCT_H_
