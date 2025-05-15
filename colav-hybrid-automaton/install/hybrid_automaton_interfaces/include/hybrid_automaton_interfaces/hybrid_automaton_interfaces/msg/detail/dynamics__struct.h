// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hybrid_automaton_interfaces:msg/Dynamics.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS__STRUCT_H_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'dynamic_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'mode'
// Member 'error_message'
#include "rosidl_runtime_c/string.h"
// Member 'dynamic_parameters'
#include "hybrid_automaton_interfaces/msg/detail/dynamic_parameter__struct.h"
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in msg/Dynamics in the package hybrid_automaton_interfaces.
/**
  * Dynamics.msg
  * ROS 2 interface for the Hybrid Automaton framework.
  * Enables real-time updates of control mode dynamics based on the current operational state.
  * Each update corresponds to one of the control modes defined in the 
  * `/hybrid_automaton/config/hybrid_automaton_config.yml` (e.g., GO_FORWARD, GO_RIGHT, etc.).
 */
typedef struct hybrid_automaton_interfaces__msg__Dynamics
{
  /// NOTE: Do not modify anything outside the boundaries marked
  /// 'Custom Dynamics Parameters Start' and 'Custom Dynamics Parameters End'.
  /// Only edit within that section to define or update your custom dynamics.
  /// UUID uniquely identifying this dynamic update instance
  unique_identifier_msgs__msg__UUID dynamic_uuid;
  /// The name of the current control mode. Must match one of the configured mode names.
  rosidl_runtime_c__String mode;
  hybrid_automaton_interfaces__msg__DynamicParameter dynamic_parameters;
  /// Timestamp of when the dynamic update was published.
  builtin_interfaces__msg__Time stamp;
  /// Metadata for update status.
  /// Indicates whether the update was successfully applied, and provides error details if not.
  bool success;
  rosidl_runtime_c__String error_message;
} hybrid_automaton_interfaces__msg__Dynamics;

// Struct for a sequence of hybrid_automaton_interfaces__msg__Dynamics.
typedef struct hybrid_automaton_interfaces__msg__Dynamics__Sequence
{
  hybrid_automaton_interfaces__msg__Dynamics * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__msg__Dynamics__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS__STRUCT_H_
