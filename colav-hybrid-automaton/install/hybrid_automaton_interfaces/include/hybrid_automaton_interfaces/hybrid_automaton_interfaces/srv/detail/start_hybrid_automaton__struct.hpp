// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from hybrid_automaton_interfaces:srv/StartHybridAutomaton.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__START_HYBRID_AUTOMATON__STRUCT_HPP_
#define HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__START_HYBRID_AUTOMATON__STRUCT_HPP_

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
// Member 'mission_uuid'
// Member 'agent_uuid'
#include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"
// Member 'goal_waypoint'
#include "colav_interfaces/msg/detail/waypoint__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hybrid_automaton_interfaces__srv__StartHybridAutomaton_Request __attribute__((deprecated))
#else
# define DEPRECATED__hybrid_automaton_interfaces__srv__StartHybridAutomaton_Request __declspec(deprecated)
#endif

namespace hybrid_automaton_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct StartHybridAutomaton_Request_
{
  using Type = StartHybridAutomaton_Request_<ContainerAllocator>;

  explicit StartHybridAutomaton_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_init),
    mission_uuid(_init),
    agent_uuid(_init),
    goal_waypoint(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mission_profile = "";
    }
  }

  explicit StartHybridAutomaton_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_alloc, _init),
    mission_uuid(_alloc, _init),
    mission_profile(_alloc),
    agent_uuid(_alloc, _init),
    goal_waypoint(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mission_profile = "";
    }
  }

  // field types and members
  using _stamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _stamp_type stamp;
  using _mission_uuid_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _mission_uuid_type mission_uuid;
  using _mission_profile_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _mission_profile_type mission_profile;
  using _agent_uuid_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _agent_uuid_type agent_uuid;
  using _goal_waypoint_type =
    colav_interfaces::msg::Waypoint_<ContainerAllocator>;
  _goal_waypoint_type goal_waypoint;

  // setters for named parameter idiom
  Type & set__stamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->stamp = _arg;
    return *this;
  }
  Type & set__mission_uuid(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->mission_uuid = _arg;
    return *this;
  }
  Type & set__mission_profile(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->mission_profile = _arg;
    return *this;
  }
  Type & set__agent_uuid(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->agent_uuid = _arg;
    return *this;
  }
  Type & set__goal_waypoint(
    const colav_interfaces::msg::Waypoint_<ContainerAllocator> & _arg)
  {
    this->goal_waypoint = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hybrid_automaton_interfaces__srv__StartHybridAutomaton_Request
    std::shared_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hybrid_automaton_interfaces__srv__StartHybridAutomaton_Request
    std::shared_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const StartHybridAutomaton_Request_ & other) const
  {
    if (this->stamp != other.stamp) {
      return false;
    }
    if (this->mission_uuid != other.mission_uuid) {
      return false;
    }
    if (this->mission_profile != other.mission_profile) {
      return false;
    }
    if (this->agent_uuid != other.agent_uuid) {
      return false;
    }
    if (this->goal_waypoint != other.goal_waypoint) {
      return false;
    }
    return true;
  }
  bool operator!=(const StartHybridAutomaton_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct StartHybridAutomaton_Request_

// alias to use template instance with default allocator
using StartHybridAutomaton_Request =
  hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace hybrid_automaton_interfaces


// Include directives for member types
// Member 'automaton_uuid'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__hybrid_automaton_interfaces__srv__StartHybridAutomaton_Response __attribute__((deprecated))
#else
# define DEPRECATED__hybrid_automaton_interfaces__srv__StartHybridAutomaton_Response __declspec(deprecated)
#endif

namespace hybrid_automaton_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct StartHybridAutomaton_Response_
{
  using Type = StartHybridAutomaton_Response_<ContainerAllocator>;

  explicit StartHybridAutomaton_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : automaton_uuid(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit StartHybridAutomaton_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
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
    hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__hybrid_automaton_interfaces__srv__StartHybridAutomaton_Response
    std::shared_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__hybrid_automaton_interfaces__srv__StartHybridAutomaton_Response
    std::shared_ptr<hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const StartHybridAutomaton_Response_ & other) const
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
  bool operator!=(const StartHybridAutomaton_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct StartHybridAutomaton_Response_

// alias to use template instance with default allocator
using StartHybridAutomaton_Response =
  hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace hybrid_automaton_interfaces

namespace hybrid_automaton_interfaces
{

namespace srv
{

struct StartHybridAutomaton
{
  using Request = hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request;
  using Response = hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response;
};

}  // namespace srv

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__START_HYBRID_AUTOMATON__STRUCT_HPP_
