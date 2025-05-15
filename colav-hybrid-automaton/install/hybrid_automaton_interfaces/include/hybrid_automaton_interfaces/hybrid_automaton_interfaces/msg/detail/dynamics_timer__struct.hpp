// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from hybrid_automaton_interfaces:msg/DynamicsTimer.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS_TIMER__STRUCT_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS_TIMER__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'previous_dynamic_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"
// Member 'elapsed'
// Member 'timeout'
#include "builtin_interfaces/msg/detail/duration__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hybrid_automaton_interfaces__msg__DynamicsTimer __attribute__((deprecated))
#else
# define DEPRECATED__hybrid_automaton_interfaces__msg__DynamicsTimer __declspec(deprecated)
#endif

namespace hybrid_automaton_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct DynamicsTimer_
{
  using Type = DynamicsTimer_<ContainerAllocator>;

  explicit DynamicsTimer_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : previous_dynamic_uuid(_init),
    elapsed(_init),
    timeout(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->timeout_sec = 0.0;
      this->expired = false;
    }
  }

  explicit DynamicsTimer_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : previous_dynamic_uuid(_alloc, _init),
    elapsed(_alloc, _init),
    timeout(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->timeout_sec = 0.0;
      this->expired = false;
    }
  }

  // field types and members
  using _previous_dynamic_uuid_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _previous_dynamic_uuid_type previous_dynamic_uuid;
  using _elapsed_type =
    builtin_interfaces::msg::Duration_<ContainerAllocator>;
  _elapsed_type elapsed;
  using _timeout_type =
    builtin_interfaces::msg::Duration_<ContainerAllocator>;
  _timeout_type timeout;
  using _timeout_sec_type =
    double;
  _timeout_sec_type timeout_sec;
  using _expired_type =
    bool;
  _expired_type expired;

  // setters for named parameter idiom
  Type & set__previous_dynamic_uuid(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->previous_dynamic_uuid = _arg;
    return *this;
  }
  Type & set__elapsed(
    const builtin_interfaces::msg::Duration_<ContainerAllocator> & _arg)
  {
    this->elapsed = _arg;
    return *this;
  }
  Type & set__timeout(
    const builtin_interfaces::msg::Duration_<ContainerAllocator> & _arg)
  {
    this->timeout = _arg;
    return *this;
  }
  Type & set__timeout_sec(
    const double & _arg)
  {
    this->timeout_sec = _arg;
    return *this;
  }
  Type & set__expired(
    const bool & _arg)
  {
    this->expired = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hybrid_automaton_interfaces::msg::DynamicsTimer_<ContainerAllocator> *;
  using ConstRawPtr =
    const hybrid_automaton_interfaces::msg::DynamicsTimer_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::msg::DynamicsTimer_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::msg::DynamicsTimer_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::msg::DynamicsTimer_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::msg::DynamicsTimer_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::msg::DynamicsTimer_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::msg::DynamicsTimer_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::msg::DynamicsTimer_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::msg::DynamicsTimer_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hybrid_automaton_interfaces__msg__DynamicsTimer
    std::shared_ptr<hybrid_automaton_interfaces::msg::DynamicsTimer_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hybrid_automaton_interfaces__msg__DynamicsTimer
    std::shared_ptr<hybrid_automaton_interfaces::msg::DynamicsTimer_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const DynamicsTimer_ & other) const
  {
    if (this->previous_dynamic_uuid != other.previous_dynamic_uuid) {
      return false;
    }
    if (this->elapsed != other.elapsed) {
      return false;
    }
    if (this->timeout != other.timeout) {
      return false;
    }
    if (this->timeout_sec != other.timeout_sec) {
      return false;
    }
    if (this->expired != other.expired) {
      return false;
    }
    return true;
  }
  bool operator!=(const DynamicsTimer_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct DynamicsTimer_

// alias to use template instance with default allocator
using DynamicsTimer =
  hybrid_automaton_interfaces::msg::DynamicsTimer_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__DYNAMICS_TIMER__STRUCT_HPP_
