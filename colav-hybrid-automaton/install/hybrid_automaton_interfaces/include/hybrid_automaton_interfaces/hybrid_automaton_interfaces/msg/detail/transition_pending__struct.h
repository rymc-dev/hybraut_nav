// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hybrid_automaton_interfaces:msg/TransitionPending.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_PENDING__STRUCT_H_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_PENDING__STRUCT_H_

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
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in msg/TransitionPending in the package hybrid_automaton_interfaces.
/**
  * TransitionPending.msg
  * ROS2 interface for the Hybrid Automaton Framework.
  * Enables Hybrid Automaton chart to recognize a transition
  * is pending
 */
typedef struct hybrid_automaton_interfaces__msg__TransitionPending
{
  /// NOTE: Do not modify this file
  /// UUID uniquely identifying this dynamic update instance
  unique_identifier_msgs__msg__UUID transition_uuid;
  builtin_interfaces__msg__Time stamp;
  bool transition_pending;
} hybrid_automaton_interfaces__msg__TransitionPending;

// Struct for a sequence of hybrid_automaton_interfaces__msg__TransitionPending.
typedef struct hybrid_automaton_interfaces__msg__TransitionPending__Sequence
{
  hybrid_automaton_interfaces__msg__TransitionPending * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__msg__TransitionPending__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_PENDING__STRUCT_H_
