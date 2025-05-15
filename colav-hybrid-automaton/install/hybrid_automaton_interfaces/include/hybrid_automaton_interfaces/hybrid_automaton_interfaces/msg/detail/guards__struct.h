// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hybrid_automaton_interfaces:msg/Guards.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__GUARDS__STRUCT_H_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__GUARDS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'control_mode'
// Member 'transition_eval_id'
// Member 'guard_names'
// Member 'error_message'
#include "rosidl_runtime_c/string.h"
// Member 'timestamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in msg/Guards in the package hybrid_automaton_interfaces.
/**
  * Guards.msg
  * A ROS 2 interface utilized by colav_hybrid_eval for publishing guard statuses continuously.
 */
typedef struct hybrid_automaton_interfaces__msg__Guards
{
  /// Current control mode (e.g., CRUISE, T2LOS, etc.)
  rosidl_runtime_c__String control_mode;
  /// Stores the guard names evaluated for the current control mode # guard eval id is given for each unique transition evaluation to help the asynchronous system
  /// transition_pending is a boolean state triggered when a guard condition is only set false again when
  rosidl_runtime_c__String transition_eval_id;
  bool transition_pending;
  rosidl_runtime_c__String__Sequence guard_names;
  /// Guard statuses for each transition (true = guard passed, false = guard failed)
  bool cruise_to_t2los_1;
  bool cruise_to_t2los_2;
  bool cruise_to_waypoint_reached;
  /// Fallback guard for CRUISE mode
  bool cruise_to_fb;
  bool t2los_to_cruise;
  /// Fallback guard for T2LOS mode
  bool t2los_to_fb;
  bool t2los_to_waypoint_reached;
  /// Transition from WAYPOINT_REACHED to CRUISE mode
  bool waypoint_reached_to_cruise;
  /// Fallback Guards
  /// No Fallback Guards currently
  /// Optionally, include timestamps if you need to track when each transition was evaluated
  builtin_interfaces__msg__Time timestamp;
  /// error indication
  bool error;
  rosidl_runtime_c__String error_message;
} hybrid_automaton_interfaces__msg__Guards;

// Struct for a sequence of hybrid_automaton_interfaces__msg__Guards.
typedef struct hybrid_automaton_interfaces__msg__Guards__Sequence
{
  hybrid_automaton_interfaces__msg__Guards * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__msg__Guards__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__GUARDS__STRUCT_H_
