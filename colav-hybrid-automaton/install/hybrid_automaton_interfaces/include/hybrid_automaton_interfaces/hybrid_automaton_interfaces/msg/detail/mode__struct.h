// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hybrid_automaton_interfaces:msg/Mode.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__MODE__STRUCT_H_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__MODE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'mode_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'mode'
// Member 'origin_transition'
#include "rosidl_runtime_c/string.h"
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in msg/Mode in the package hybrid_automaton_interfaces.
/**
  * Mode.msg 
  * ROS 2 interface for the Hybrid Automaton Framework.
  * Provides real-time updates of the current Hybrid Automaton mode.
 */
typedef struct hybrid_automaton_interfaces__msg__Mode
{
  /// NOTE: Do not modify this .msg definition.
  /// Unique identifier for this mode update instance
  unique_identifier_msgs__msg__UUID mode_uuid;
  /// The current Hybrid Automaton mode (e.g., "GO_FORWARD", "GO_RIGHT", etc.)
  rosidl_runtime_c__String mode;
  /// Timestamp indicating when the mode was last updated
  builtin_interfaces__msg__Time stamp;
  /// The transition that triggered the mode change (e.g., "cruise_to_waypoint_reached")
  rosidl_runtime_c__String origin_transition;
} hybrid_automaton_interfaces__msg__Mode;

// Struct for a sequence of hybrid_automaton_interfaces__msg__Mode.
typedef struct hybrid_automaton_interfaces__msg__Mode__Sequence
{
  hybrid_automaton_interfaces__msg__Mode * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__msg__Mode__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__MODE__STRUCT_H_
