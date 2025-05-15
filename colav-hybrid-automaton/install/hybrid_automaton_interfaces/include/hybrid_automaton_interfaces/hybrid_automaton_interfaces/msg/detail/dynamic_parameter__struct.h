// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from hybrid_automaton_interfaces:msg/DynamicParameter.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMIC_PARAMETER__STRUCT_H_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMIC_PARAMETER__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'controller_name'
// Member 'dynamic_name'
// Member 'dynamic_units'
#include "rosidl_runtime_c/string.h"
// Member 'dynamic_value'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in msg/DynamicParameter in the package hybrid_automaton_interfaces.
typedef struct hybrid_automaton_interfaces__msg__DynamicParameter
{
  rosidl_runtime_c__String controller_name;
  /// for example (velocity, yaw_rate, acceleration, .... e.g.... depending on the controller
  rosidl_runtime_c__String__Sequence dynamic_name;
  rosidl_runtime_c__double__Sequence dynamic_value;
  /// e.g. ["m/s", "rad/s"]
  rosidl_runtime_c__String__Sequence dynamic_units;
} hybrid_automaton_interfaces__msg__DynamicParameter;

// Struct for a sequence of hybrid_automaton_interfaces__msg__DynamicParameter.
typedef struct hybrid_automaton_interfaces__msg__DynamicParameter__Sequence
{
  hybrid_automaton_interfaces__msg__DynamicParameter * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} hybrid_automaton_interfaces__msg__DynamicParameter__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMIC_PARAMETER__STRUCT_H_
