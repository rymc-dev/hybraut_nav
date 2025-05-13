// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hybrid_automaton_interfaces:srv/Reset.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__RESET__BUILDER_HPP_
#define HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__RESET__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hybrid_automaton_interfaces/srv/detail/reset__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hybrid_automaton_interfaces
{

namespace srv
{

namespace builder
{

class Init_Reset_Request_reset_name
{
public:
  explicit Init_Reset_Request_reset_name(::hybrid_automaton_interfaces::srv::Reset_Request & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::srv::Reset_Request reset_name(::hybrid_automaton_interfaces::srv::Reset_Request::_reset_name_type arg)
  {
    msg_.reset_name = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::Reset_Request msg_;
};

class Init_Reset_Request_transition_uuid
{
public:
  Init_Reset_Request_transition_uuid()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Reset_Request_reset_name transition_uuid(::hybrid_automaton_interfaces::srv::Reset_Request::_transition_uuid_type arg)
  {
    msg_.transition_uuid = std::move(arg);
    return Init_Reset_Request_reset_name(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::Reset_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::srv::Reset_Request>()
{
  return hybrid_automaton_interfaces::srv::builder::Init_Reset_Request_transition_uuid();
}

}  // namespace hybrid_automaton_interfaces


namespace hybrid_automaton_interfaces
{

namespace srv
{

namespace builder
{

class Init_Reset_Response_message
{
public:
  explicit Init_Reset_Response_message(::hybrid_automaton_interfaces::srv::Reset_Response & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::srv::Reset_Response message(::hybrid_automaton_interfaces::srv::Reset_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::Reset_Response msg_;
};

class Init_Reset_Response_success
{
public:
  explicit Init_Reset_Response_success(::hybrid_automaton_interfaces::srv::Reset_Response & msg)
  : msg_(msg)
  {}
  Init_Reset_Response_message success(::hybrid_automaton_interfaces::srv::Reset_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_Reset_Response_message(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::Reset_Response msg_;
};

class Init_Reset_Response_reset_name
{
public:
  explicit Init_Reset_Response_reset_name(::hybrid_automaton_interfaces::srv::Reset_Response & msg)
  : msg_(msg)
  {}
  Init_Reset_Response_success reset_name(::hybrid_automaton_interfaces::srv::Reset_Response::_reset_name_type arg)
  {
    msg_.reset_name = std::move(arg);
    return Init_Reset_Response_success(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::Reset_Response msg_;
};

class Init_Reset_Response_transition_uuid
{
public:
  Init_Reset_Response_transition_uuid()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Reset_Response_reset_name transition_uuid(::hybrid_automaton_interfaces::srv::Reset_Response::_transition_uuid_type arg)
  {
    msg_.transition_uuid = std::move(arg);
    return Init_Reset_Response_reset_name(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::Reset_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::srv::Reset_Response>()
{
  return hybrid_automaton_interfaces::srv::builder::Init_Reset_Response_transition_uuid();
}

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__RESET__BUILDER_HPP_
