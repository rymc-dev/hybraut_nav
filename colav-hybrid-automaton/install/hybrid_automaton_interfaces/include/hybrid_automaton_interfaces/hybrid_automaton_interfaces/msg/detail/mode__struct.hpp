// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from hybrid_automaton_interfaces:msg/Mode.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__MODE__STRUCT_HPP_
#define HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__MODE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'mode_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hybrid_automaton_interfaces__msg__Mode __attribute__((deprecated))
#else
# define DEPRECATED__hybrid_automaton_interfaces__msg__Mode __declspec(deprecated)
#endif

namespace hybrid_automaton_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct Mode_
{
  using Type = Mode_<ContainerAllocator>;

  explicit Mode_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : mode_uuid(_init),
    stamp(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mode = "";
      this->origin_transition = "";
    }
  }

  explicit Mode_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : mode_uuid(_alloc, _init),
    mode(_alloc),
    stamp(_alloc, _init),
    origin_transition(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mode = "";
      this->origin_transition = "";
    }
  }

  // field types and members
  using _mode_uuid_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _mode_uuid_type mode_uuid;
  using _mode_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _mode_type mode;
  using _stamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _stamp_type stamp;
  using _origin_transition_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _origin_transition_type origin_transition;

  // setters for named parameter idiom
  Type & set__mode_uuid(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->mode_uuid = _arg;
    return *this;
  }
  Type & set__mode(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->mode = _arg;
    return *this;
  }
  Type & set__stamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->stamp = _arg;
    return *this;
  }
  Type & set__origin_transition(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->origin_transition = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hybrid_automaton_interfaces::msg::Mode_<ContainerAllocator> *;
  using ConstRawPtr =
    const hybrid_automaton_interfaces::msg::Mode_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::msg::Mode_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::msg::Mode_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::msg::Mode_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::msg::Mode_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::msg::Mode_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::msg::Mode_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::msg::Mode_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::msg::Mode_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hybrid_automaton_interfaces__msg__Mode
    std::shared_ptr<hybrid_automaton_interfaces::msg::Mode_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hybrid_automaton_interfaces__msg__Mode
    std::shared_ptr<hybrid_automaton_interfaces::msg::Mode_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Mode_ & other) const
  {
    if (this->mode_uuid != other.mode_uuid) {
      return false;
    }
    if (this->mode != other.mode) {
      return false;
    }
    if (this->stamp != other.stamp) {
      return false;
    }
    if (this->origin_transition != other.origin_transition) {
      return false;
    }
    return true;
  }
  bool operator!=(const Mode_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Mode_

// alias to use template instance with default allocator
using Mode =
  hybrid_automaton_interfaces::msg::Mode_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__MSG__DETAIL__MODE__STRUCT_HPP_
