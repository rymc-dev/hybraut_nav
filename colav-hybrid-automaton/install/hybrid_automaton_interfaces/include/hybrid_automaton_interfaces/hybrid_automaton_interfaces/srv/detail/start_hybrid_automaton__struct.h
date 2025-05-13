// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hybrid_automaton_interfaces:srv/StartHybridAutomaton.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__START_HYBRID_AUTOMATON__STRUCT_H_
#define HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__START_HYBRID_AUTOMATON__STRUCT_H_

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
// Member 'mission_uuid'
// Member 'agent_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'mission_profile'
#include "rosidl_runtime_c/string.h"
// Member 'goal_waypoint'
#include "colav_interfaces/msg/detail/waypoint__struct.h"

/// Struct defined in srv/StartHybridAutomaton in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__srv__StartHybridAutomaton_Request
{
  /// --- Request ---
  /// Timestamp for synchronization
  builtin_interfaces__msg__Time stamp;
  /// Unique identifier for the mission
  unique_identifier_msgs__msg__UUID mission_uuid;
  /// Define the type of mission (e.g., "fastest_path", "safe_navigation")
  rosidl_runtime_c__String mission_profile;
  /// Unique identifier for the agent (e.g., vessel, drone)
  unique_identifier_msgs__msg__UUID agent_uuid;
  /// --- Control Inputs Start ---
  /// Target waypoint for the agent to reach
  colav_interfaces__msg__Waypoint goal_waypoint;
} hybrid_automaton_interfaces__srv__StartHybridAutomaton_Request;

// Struct for a sequence of hybrid_automaton_interfaces__srv__StartHybridAutomaton_Request.
typedef struct hybrid_automaton_interfaces__srv__StartHybridAutomaton_Request__Sequence
{
  hybrid_automaton_interfaces__srv__StartHybridAutomaton_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__srv__StartHybridAutomaton_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'automaton_uuid'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/StartHybridAutomaton in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__srv__StartHybridAutomaton_Response
{
  /// Unique identifier for the initiated Hybrid Automaton instance
  unique_identifier_msgs__msg__UUID automaton_uuid;
  /// Indicates whether the Hybrid Automaton was successfully started
  bool success;
  /// Optional message with additional information (e.g., success details, error information)
  rosidl_runtime_c__String message;
} hybrid_automaton_interfaces__srv__StartHybridAutomaton_Response;

// Struct for a sequence of hybrid_automaton_interfaces__srv__StartHybridAutomaton_Response.
typedef struct hybrid_automaton_interfaces__srv__StartHybridAutomaton_Response__Sequence
{
  hybrid_automaton_interfaces__srv__StartHybridAutomaton_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__srv__StartHybridAutomaton_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__START_HYBRID_AUTOMATON__STRUCT_H_
