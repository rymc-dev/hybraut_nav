// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from hybrid_automaton_interfaces:msg/Guards.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__GUARDS__STRUCT_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__GUARDS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'timestamp'
#include "builtin_interfaces/msg/detail/time__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hybrid_automaton_interfaces__msg__Guards __attribute__((deprecated))
#else
# define DEPRECATED__hybrid_automaton_interfaces__msg__Guards __declspec(deprecated)
#endif

namespace hybrid_automaton_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Guards_
{
  using Type = Guards_<ContainerAllocator>;

  explicit Guards_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : timestamp(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->control_mode = "";
      this->transition_eval_id = "";
      this->transition_pending = false;
      this->cruise_to_t2los_1 = false;
      this->cruise_to_t2los_2 = false;
      this->cruise_to_waypoint_reached = false;
      this->cruise_to_fb = false;
      this->t2los_to_cruise = false;
      this->t2los_to_fb = false;
      this->t2los_to_waypoint_reached = false;
      this->waypoint_reached_to_cruise = false;
      this->error = false;
      this->error_message = "";
    }
  }

  explicit Guards_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : control_mode(_alloc),
    transition_eval_id(_alloc),
    timestamp(_alloc, _init),
    error_message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->control_mode = "";
      this->transition_eval_id = "";
      this->transition_pending = false;
      this->cruise_to_t2los_1 = false;
      this->cruise_to_t2los_2 = false;
      this->cruise_to_waypoint_reached = false;
      this->cruise_to_fb = false;
      this->t2los_to_cruise = false;
      this->t2los_to_fb = false;
      this->t2los_to_waypoint_reached = false;
      this->waypoint_reached_to_cruise = false;
      this->error = false;
      this->error_message = "";
    }
  }

  // field types and members
  using _control_mode_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _control_mode_type control_mode;
  using _transition_eval_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _transition_eval_id_type transition_eval_id;
  using _transition_pending_type =
    bool;
  _transition_pending_type transition_pending;
  using _guard_names_type =
    std::vector<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>>;
  _guard_names_type guard_names;
  using _cruise_to_t2los_1_type =
    bool;
  _cruise_to_t2los_1_type cruise_to_t2los_1;
  using _cruise_to_t2los_2_type =
    bool;
  _cruise_to_t2los_2_type cruise_to_t2los_2;
  using _cruise_to_waypoint_reached_type =
    bool;
  _cruise_to_waypoint_reached_type cruise_to_waypoint_reached;
  using _cruise_to_fb_type =
    bool;
  _cruise_to_fb_type cruise_to_fb;
  using _t2los_to_cruise_type =
    bool;
  _t2los_to_cruise_type t2los_to_cruise;
  using _t2los_to_fb_type =
    bool;
  _t2los_to_fb_type t2los_to_fb;
  using _t2los_to_waypoint_reached_type =
    bool;
  _t2los_to_waypoint_reached_type t2los_to_waypoint_reached;
  using _waypoint_reached_to_cruise_type =
    bool;
  _waypoint_reached_to_cruise_type waypoint_reached_to_cruise;
  using _timestamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _timestamp_type timestamp;
  using _error_type =
    bool;
  _error_type error;
  using _error_message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _error_message_type error_message;

  // setters for named parameter idiom
  Type & set__control_mode(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->control_mode = _arg;
    return *this;
  }
  Type & set__transition_eval_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->transition_eval_id = _arg;
    return *this;
  }
  Type & set__transition_pending(
    const bool & _arg)
  {
    this->transition_pending = _arg;
    return *this;
  }
  Type & set__guard_names(
    const std::vector<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>>> & _arg)
  {
    this->guard_names = _arg;
    return *this;
  }
  Type & set__cruise_to_t2los_1(
    const bool & _arg)
  {
    this->cruise_to_t2los_1 = _arg;
    return *this;
  }
  Type & set__cruise_to_t2los_2(
    const bool & _arg)
  {
    this->cruise_to_t2los_2 = _arg;
    return *this;
  }
  Type & set__cruise_to_waypoint_reached(
    const bool & _arg)
  {
    this->cruise_to_waypoint_reached = _arg;
    return *this;
  }
  Type & set__cruise_to_fb(
    const bool & _arg)
  {
    this->cruise_to_fb = _arg;
    return *this;
  }
  Type & set__t2los_to_cruise(
    const bool & _arg)
  {
    this->t2los_to_cruise = _arg;
    return *this;
  }
  Type & set__t2los_to_fb(
    const bool & _arg)
  {
    this->t2los_to_fb = _arg;
    return *this;
  }
  Type & set__t2los_to_waypoint_reached(
    const bool & _arg)
  {
    this->t2los_to_waypoint_reached = _arg;
    return *this;
  }
  Type & set__waypoint_reached_to_cruise(
    const bool & _arg)
  {
    this->waypoint_reached_to_cruise = _arg;
    return *this;
  }
  Type & set__timestamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->timestamp = _arg;
    return *this;
  }
  Type & set__error(
    const bool & _arg)
  {
    this->error = _arg;
    return *this;
  }
  Type & set__error_message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->error_message = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hybrid_automaton_interfaces::msg::Guards_<ContainerAllocator> *;
  using ConstRawPtr =
    const hybrid_automaton_interfaces::msg::Guards_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::msg::Guards_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::msg::Guards_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::msg::Guards_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::msg::Guards_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::msg::Guards_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::msg::Guards_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::msg::Guards_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::msg::Guards_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hybrid_automaton_interfaces__msg__Guards
    std::shared_ptr<hybrid_automaton_interfaces::msg::Guards_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hybrid_automaton_interfaces__msg__Guards
    std::shared_ptr<hybrid_automaton_interfaces::msg::Guards_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Guards_ & other) const
  {
    if (this->control_mode != other.control_mode) {
      return false;
    }
    if (this->transition_eval_id != other.transition_eval_id) {
      return false;
    }
    if (this->transition_pending != other.transition_pending) {
      return false;
    }
    if (this->guard_names != other.guard_names) {
      return false;
    }
    if (this->cruise_to_t2los_1 != other.cruise_to_t2los_1) {
      return false;
    }
    if (this->cruise_to_t2los_2 != other.cruise_to_t2los_2) {
      return false;
    }
    if (this->cruise_to_waypoint_reached != other.cruise_to_waypoint_reached) {
      return false;
    }
    if (this->cruise_to_fb != other.cruise_to_fb) {
      return false;
    }
    if (this->t2los_to_cruise != other.t2los_to_cruise) {
      return false;
    }
    if (this->t2los_to_fb != other.t2los_to_fb) {
      return false;
    }
    if (this->t2los_to_waypoint_reached != other.t2los_to_waypoint_reached) {
      return false;
    }
    if (this->waypoint_reached_to_cruise != other.waypoint_reached_to_cruise) {
      return false;
    }
    if (this->timestamp != other.timestamp) {
      return false;
    }
    if (this->error != other.error) {
      return false;
    }
    if (this->error_message != other.error_message) {
      return false;
    }
    return true;
  }
  bool operator!=(const Guards_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Guards_

// alias to use template instance with default allocator
using Guards =
  hybrid_automaton_interfaces::msg::Guards_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__GUARDS__STRUCT_HPP_
