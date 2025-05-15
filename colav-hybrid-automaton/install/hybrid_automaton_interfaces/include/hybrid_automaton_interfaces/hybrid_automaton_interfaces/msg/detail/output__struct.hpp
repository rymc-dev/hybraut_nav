// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from hybrid_automaton_interfaces:msg/Output.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__OUTPUT__STRUCT_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__OUTPUT__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'automaton_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"
// Member 'dynamics'
#include "hybrid_automaton_interfaces/msg/detail/dynamic_parameter__struct.hpp"
// Member 'time_since_last_transition'
// Member 'elapsed_time'
#include "builtin_interfaces/msg/detail/duration__struct.hpp"
// Member 'transition_pending'
#include "hybrid_automaton_interfaces/msg/detail/transition_pending__struct.hpp"
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.hpp"
// Member 'waypoints'
#include "colav_interfaces/msg/detail/waypoints__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hybrid_automaton_interfaces__msg__Output __attribute__((deprecated))
#else
# define DEPRECATED__hybrid_automaton_interfaces__msg__Output __declspec(deprecated)
#endif

namespace hybrid_automaton_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Output_
{
  using Type = Output_<ContainerAllocator>;

  explicit Output_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : automaton_uuid(_init),
    dynamics(_init),
    time_since_last_transition(_init),
    transition_pending(_init),
    stamp(_init),
    elapsed_time(_init),
    waypoints(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mode = "";
      this->status = "";
      this->error = false;
      this->message = "";
    }
  }

  explicit Output_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : automaton_uuid(_alloc, _init),
    mode(_alloc),
    status(_alloc),
    dynamics(_alloc, _init),
    time_since_last_transition(_alloc, _init),
    transition_pending(_alloc, _init),
    stamp(_alloc, _init),
    elapsed_time(_alloc, _init),
    waypoints(_alloc, _init),
    message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mode = "";
      this->status = "";
      this->error = false;
      this->message = "";
    }
  }

  // field types and members
  using _automaton_uuid_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _automaton_uuid_type automaton_uuid;
  using _mode_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _mode_type mode;
  using _status_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _status_type status;
  using _dynamics_type =
    hybrid_automaton_interfaces::msg::DynamicParameter_<ContainerAllocator>;
  _dynamics_type dynamics;
  using _time_since_last_transition_type =
    builtin_interfaces::msg::Duration_<ContainerAllocator>;
  _time_since_last_transition_type time_since_last_transition;
  using _transition_pending_type =
    hybrid_automaton_interfaces::msg::TransitionPending_<ContainerAllocator>;
  _transition_pending_type transition_pending;
  using _stamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _stamp_type stamp;
  using _elapsed_time_type =
    builtin_interfaces::msg::Duration_<ContainerAllocator>;
  _elapsed_time_type elapsed_time;
  using _waypoints_type =
    colav_interfaces::msg::Waypoints_<ContainerAllocator>;
  _waypoints_type waypoints;
  using _error_type =
    bool;
  _error_type error;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;

  // setters for named parameter idiom
  Type & set__automaton_uuid(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->automaton_uuid = _arg;
    return *this;
  }
  Type & set__mode(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->mode = _arg;
    return *this;
  }
  Type & set__status(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->status = _arg;
    return *this;
  }
  Type & set__dynamics(
    const hybrid_automaton_interfaces::msg::DynamicParameter_<ContainerAllocator> & _arg)
  {
    this->dynamics = _arg;
    return *this;
  }
  Type & set__time_since_last_transition(
    const builtin_interfaces::msg::Duration_<ContainerAllocator> & _arg)
  {
    this->time_since_last_transition = _arg;
    return *this;
  }
  Type & set__transition_pending(
    const hybrid_automaton_interfaces::msg::TransitionPending_<ContainerAllocator> & _arg)
  {
    this->transition_pending = _arg;
    return *this;
  }
  Type & set__stamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->stamp = _arg;
    return *this;
  }
  Type & set__elapsed_time(
    const builtin_interfaces::msg::Duration_<ContainerAllocator> & _arg)
  {
    this->elapsed_time = _arg;
    return *this;
  }
  Type & set__waypoints(
    const colav_interfaces::msg::Waypoints_<ContainerAllocator> & _arg)
  {
    this->waypoints = _arg;
    return *this;
  }
  Type & set__error(
    const bool & _arg)
  {
    this->error = _arg;
    return *this;
  }
  Type & set__message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->message = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hybrid_automaton_interfaces::msg::Output_<ContainerAllocator> *;
  using ConstRawPtr =
    const hybrid_automaton_interfaces::msg::Output_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::msg::Output_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::msg::Output_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::msg::Output_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::msg::Output_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::msg::Output_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::msg::Output_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::msg::Output_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::msg::Output_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hybrid_automaton_interfaces__msg__Output
    std::shared_ptr<hybrid_automaton_interfaces::msg::Output_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hybrid_automaton_interfaces__msg__Output
    std::shared_ptr<hybrid_automaton_interfaces::msg::Output_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Output_ & other) const
  {
    if (this->automaton_uuid != other.automaton_uuid) {
      return false;
    }
    if (this->mode != other.mode) {
      return false;
    }
    if (this->status != other.status) {
      return false;
    }
    if (this->dynamics != other.dynamics) {
      return false;
    }
    if (this->time_since_last_transition != other.time_since_last_transition) {
      return false;
    }
    if (this->transition_pending != other.transition_pending) {
      return false;
    }
    if (this->stamp != other.stamp) {
      return false;
    }
    if (this->elapsed_time != other.elapsed_time) {
      return false;
    }
    if (this->waypoints != other.waypoints) {
      return false;
    }
    if (this->error != other.error) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const Output_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Output_

// alias to use template instance with default allocator
using Output =
  hybrid_automaton_interfaces::msg::Output_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__OUTPUT__STRUCT_HPP_
