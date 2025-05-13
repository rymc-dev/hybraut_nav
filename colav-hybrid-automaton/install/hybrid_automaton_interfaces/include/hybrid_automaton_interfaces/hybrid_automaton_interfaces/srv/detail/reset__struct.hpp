// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from hybrid_automaton_interfaces:srv/Reset.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__RESET__STRUCT_HPP_
#define HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__RESET__STRUCT_HPP_

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

#ifndef _WIN32
# define DEPRECATED__hybrid_automaton_interfaces__srv__Reset_Request __attribute__((deprecated))
#else
# define DEPRECATED__hybrid_automaton_interfaces__srv__Reset_Request __declspec(deprecated)
#endif

namespace hybrid_automaton_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct Reset_Request_
{
  using Type = Reset_Request_<ContainerAllocator>;

  explicit Reset_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : transition_uuid(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->reset_name = "";
    }
  }

  explicit Reset_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : transition_uuid(_alloc, _init),
    reset_name(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->reset_name = "";
    }
  }

  // field types and members
  using _transition_uuid_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _transition_uuid_type transition_uuid;
  using _reset_name_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _reset_name_type reset_name;

  // setters for named parameter idiom
  Type & set__transition_uuid(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->transition_uuid = _arg;
    return *this;
  }
  Type & set__reset_name(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->reset_name = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hybrid_automaton_interfaces::srv::Reset_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const hybrid_automaton_interfaces::srv::Reset_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::srv::Reset_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::srv::Reset_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::srv::Reset_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::srv::Reset_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::srv::Reset_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::srv::Reset_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::srv::Reset_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::srv::Reset_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hybrid_automaton_interfaces__srv__Reset_Request
    std::shared_ptr<hybrid_automaton_interfaces::srv::Reset_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hybrid_automaton_interfaces__srv__Reset_Request
    std::shared_ptr<hybrid_automaton_interfaces::srv::Reset_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Reset_Request_ & other) const
  {
    if (this->transition_uuid != other.transition_uuid) {
      return false;
    }
    if (this->reset_name != other.reset_name) {
      return false;
    }
    return true;
  }
  bool operator!=(const Reset_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Reset_Request_

// alias to use template instance with default allocator
using Reset_Request =
  hybrid_automaton_interfaces::srv::Reset_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace hybrid_automaton_interfaces


// Include directives for member types
// Member 'transition_uuid'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hybrid_automaton_interfaces__srv__Reset_Response __attribute__((deprecated))
#else
# define DEPRECATED__hybrid_automaton_interfaces__srv__Reset_Response __declspec(deprecated)
#endif

namespace hybrid_automaton_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct Reset_Response_
{
  using Type = Reset_Response_<ContainerAllocator>;

  explicit Reset_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : transition_uuid(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->reset_name = "";
      this->success = false;
      this->message = "";
    }
  }

  explicit Reset_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : transition_uuid(_alloc, _init),
    reset_name(_alloc),
    message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->reset_name = "";
      this->success = false;
      this->message = "";
    }
  }

  // field types and members
  using _transition_uuid_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _transition_uuid_type transition_uuid;
  using _reset_name_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _reset_name_type reset_name;
  using _success_type =
    bool;
  _success_type success;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;

  // setters for named parameter idiom
  Type & set__transition_uuid(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->transition_uuid = _arg;
    return *this;
  }
  Type & set__reset_name(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->reset_name = _arg;
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
    hybrid_automaton_interfaces::srv::Reset_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const hybrid_automaton_interfaces::srv::Reset_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::srv::Reset_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::srv::Reset_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::srv::Reset_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::srv::Reset_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::srv::Reset_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::srv::Reset_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::srv::Reset_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::srv::Reset_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hybrid_automaton_interfaces__srv__Reset_Response
    std::shared_ptr<hybrid_automaton_interfaces::srv::Reset_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hybrid_automaton_interfaces__srv__Reset_Response
    std::shared_ptr<hybrid_automaton_interfaces::srv::Reset_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Reset_Response_ & other) const
  {
    if (this->transition_uuid != other.transition_uuid) {
      return false;
    }
    if (this->reset_name != other.reset_name) {
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
  bool operator!=(const Reset_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Reset_Response_

// alias to use template instance with default allocator
using Reset_Response =
  hybrid_automaton_interfaces::srv::Reset_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace hybrid_automaton_interfaces

namespace hybrid_automaton_interfaces
{

namespace srv
{

struct Reset
{
  using Request = hybrid_automaton_interfaces::srv::Reset_Request;
  using Response = hybrid_automaton_interfaces::srv::Reset_Response;
};

}  // namespace srv

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__RESET__STRUCT_HPP_
