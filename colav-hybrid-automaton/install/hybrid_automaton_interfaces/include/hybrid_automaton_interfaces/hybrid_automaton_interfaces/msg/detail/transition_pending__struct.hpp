// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from hybrid_automaton_interfaces:msg/TransitionPending.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_PENDING__STRUCT_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_PENDING__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'transition_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hybrid_automaton_interfaces__msg__TransitionPending __attribute__((deprecated))
#else
# define DEPRECATED__hybrid_automaton_interfaces__msg__TransitionPending __declspec(deprecated)
#endif

namespace hybrid_automaton_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct TransitionPending_
{
  using Type = TransitionPending_<ContainerAllocator>;

  explicit TransitionPending_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : transition_uuid(_init),
    stamp(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->transition_pending = false;
    }
  }

  explicit TransitionPending_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : transition_uuid(_alloc, _init),
    stamp(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->transition_pending = false;
    }
  }

  // field types and members
  using _transition_uuid_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _transition_uuid_type transition_uuid;
  using _stamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _stamp_type stamp;
  using _transition_pending_type =
    bool;
  _transition_pending_type transition_pending;

  // setters for named parameter idiom
  Type & set__transition_uuid(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->transition_uuid = _arg;
    return *this;
  }
  Type & set__stamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->stamp = _arg;
    return *this;
  }
  Type & set__transition_pending(
    const bool & _arg)
  {
    this->transition_pending = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hybrid_automaton_interfaces::msg::TransitionPending_<ContainerAllocator> *;
  using ConstRawPtr =
    const hybrid_automaton_interfaces::msg::TransitionPending_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::msg::TransitionPending_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::msg::TransitionPending_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::msg::TransitionPending_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::msg::TransitionPending_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::msg::TransitionPending_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::msg::TransitionPending_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::msg::TransitionPending_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::msg::TransitionPending_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hybrid_automaton_interfaces__msg__TransitionPending
    std::shared_ptr<hybrid_automaton_interfaces::msg::TransitionPending_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hybrid_automaton_interfaces__msg__TransitionPending
    std::shared_ptr<hybrid_automaton_interfaces::msg::TransitionPending_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const TransitionPending_ & other) const
  {
    if (this->transition_uuid != other.transition_uuid) {
      return false;
    }
    if (this->stamp != other.stamp) {
      return false;
    }
    if (this->transition_pending != other.transition_pending) {
      return false;
    }
    return true;
  }
  bool operator!=(const TransitionPending_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct TransitionPending_

// alias to use template instance with default allocator
using TransitionPending =
  hybrid_automaton_interfaces::msg::TransitionPending_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__TRANSITION_PENDING__STRUCT_HPP_
