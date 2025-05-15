// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hybrid_automaton_interfaces:action/HybridAutomaton.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__ACTION__DETAIL__HYBRID_AUTOMATON__STRUCT_H_
#define HYBRID_AUTOMATON_INTERFACES__ACTION__DETAIL__HYBRID_AUTOMATON__STRUCT_H_

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

/// Struct defined in action/HybridAutomaton in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_Goal
{
  /// Goal
  /// Timestamp for synchronization
  builtin_interfaces__msg__Time stamp;
  /// Unique identifier for the mission
  unique_identifier_msgs__msg__UUID mission_uuid;
  /// Define the type of mission (e.g., "fastest_path", "safe_navigation")
  rosidl_runtime_c__String mission_profile;
  /// Unique identifier for the agent (e.g., vessel, drone)
  unique_identifier_msgs__msg__UUID agent_uuid;
  /// Target waypoint for the agent to reach
  colav_interfaces__msg__Waypoint goal_waypoint;
} hybrid_automaton_interfaces__action__HybridAutomaton_Goal;

// Struct for a sequence of hybrid_automaton_interfaces__action__HybridAutomaton_Goal.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_Goal__Sequence
{
  hybrid_automaton_interfaces__action__HybridAutomaton_Goal * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__action__HybridAutomaton_Goal__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in action/HybridAutomaton in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_Result
{
  bool success;
  rosidl_runtime_c__String message;
} hybrid_automaton_interfaces__action__HybridAutomaton_Result;

// Struct for a sequence of hybrid_automaton_interfaces__action__HybridAutomaton_Result.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_Result__Sequence
{
  hybrid_automaton_interfaces__action__HybridAutomaton_Result * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__action__HybridAutomaton_Result__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'feedback'
#include "hybrid_automaton_interfaces/msg/detail/output__struct.h"

/// Struct defined in action/HybridAutomaton in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_Feedback
{
  /// Response
  hybrid_automaton_interfaces__msg__Output feedback;
} hybrid_automaton_interfaces__action__HybridAutomaton_Feedback;

// Struct for a sequence of hybrid_automaton_interfaces__action__HybridAutomaton_Feedback.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__Sequence
{
  hybrid_automaton_interfaces__action__HybridAutomaton_Feedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__action__HybridAutomaton_Feedback__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'goal'
#include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.h"

/// Struct defined in action/HybridAutomaton in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
  hybrid_automaton_interfaces__action__HybridAutomaton_Goal goal;
} hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request;

// Struct for a sequence of hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__Sequence
{
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
// already included above
// #include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in action/HybridAutomaton in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response
{
  bool accepted;
  builtin_interfaces__msg__Time stamp;
} hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response;

// Struct for a sequence of hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__Sequence
{
  hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__action__HybridAutomaton_SendGoal_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"

/// Struct defined in action/HybridAutomaton in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
} hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request;

// Struct for a sequence of hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__Sequence
{
  hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'result'
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.h"

/// Struct defined in action/HybridAutomaton in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response
{
  int8_t status;
  hybrid_automaton_interfaces__action__HybridAutomaton_Result result;
} hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response;

// Struct for a sequence of hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__Sequence
{
  hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__action__HybridAutomaton_GetResult_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'feedback'
// already included above
// #include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.h"

/// Struct defined in action/HybridAutomaton in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage
{
  unique_identifier_msgs__msg__UUID goal_id;
  hybrid_automaton_interfaces__action__HybridAutomaton_Feedback feedback;
} hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage;

// Struct for a sequence of hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage.
typedef struct hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__Sequence
{
  hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__action__HybridAutomaton_FeedbackMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HYBRID_AUTOMATON_INTERFACES__ACTION__DETAIL__HYBRID_AUTOMATON__STRUCT_H_
