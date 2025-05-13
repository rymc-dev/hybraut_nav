// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from hybrid_automaton_interfaces:srv/StopHybridAutomaton.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__STOP_HYBRID_AUTOMATON__STRUCT_HPP_
#define HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__STOP_HYBRID_AUTOMATON__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.hpp"
// Member 'automaton_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request __attribute__((deprecated))
#else
# define DEPRECATED__hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request __declspec(deprecated)
#endif

namespace hybrid_automaton_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct StopHybridAutomaton_Request_
{
  using Type = StopHybridAutomaton_Request_<ContainerAllocator>;

  explicit StopHybridAutomaton_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_init),
    automaton_uuid(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->stop_reason = "";
    }
  }

  explicit StopHybridAutomaton_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_alloc, _init),
    automaton_uuid(_alloc, _init),
    stop_reason(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->stop_reason = "";
    }
  }

  // field types and members
  using _stamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _stamp_type stamp;
  using _automaton_uuid_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _automaton_uuid_type automaton_uuid;
  using _stop_reason_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _stop_reason_type stop_reason;

  // setters for named parameter idiom
  Type & set__stamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->stamp = _arg;
    return *this;
  }
  Type & set__automaton_uuid(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->automaton_uuid = _arg;
    return *this;
  }
  Type & set__stop_reason(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->stop_reason = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request
    std::shared_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hybrid_automaton_interfaces__srv__StopHybridAutomaton_Request
    std::shared_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const StopHybridAutomaton_Request_ & other) const
  {
    if (this->stamp != other.stamp) {
      return false;
    }
    if (this->automaton_uuid != other.automaton_uuid) {
      return false;
    }
    if (this->stop_reason != other.stop_reason) {
      return false;
    }
    return true;
  }
  bool operator!=(const StopHybridAutomaton_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct StopHybridAutomaton_Request_

// alias to use template instance with default allocator
using StopHybridAutomaton_Request =
  hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace hybrid_automaton_interfaces


// Include directives for member types
// Member 'automaton_uuid'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response __attribute__((deprecated))
#else
# define DEPRECATED__hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response __declspec(deprecated)
#endif

namespace hybrid_automaton_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct StopHybridAutomaton_Response_
{
  using Type = StopHybridAutomaton_Response_<ContainerAllocator>;

  explicit StopHybridAutomaton_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : automaton_uuid(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit StopHybridAutomaton_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : automaton_uuid(_alloc, _init),
    message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  // field types and members
  using _automaton_uuid_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _automaton_uuid_type automaton_uuid;
  using _success_type =
    bool;
  _success_type success;
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
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
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
    hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response
    std::shared_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hybrid_automaton_interfaces__srv__StopHybridAutomaton_Response
    std::shared_ptr<hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const StopHybridAutomaton_Response_ & other) const
  {
    if (this->automaton_uuid != other.automaton_uuid) {
      return false;
    }
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const StopHybridAutomaton_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct StopHybridAutomaton_Response_

// alias to use template instance with default allocator
using StopHybridAutomaton_Response =
  hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace hybrid_automaton_interfaces

namespace hybrid_automaton_interfaces
{

namespace srv
{

struct StopHybridAutomaton
{
  using Request = hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request;
  using Response = hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response;
};

}  // namespace srv

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__STOP_HYBRID_AUTOMATON__STRUCT_HPP_
