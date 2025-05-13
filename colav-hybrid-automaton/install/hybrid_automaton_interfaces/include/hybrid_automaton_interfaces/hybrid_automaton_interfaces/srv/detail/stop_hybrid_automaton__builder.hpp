// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hybrid_automaton_interfaces:srv/StopHybridAutomaton.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__STOP_HYBRID_AUTOMATON__BUILDER_HPP_
#define HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__STOP_HYBRID_AUTOMATON__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hybrid_automaton_interfaces/srv/detail/stop_hybrid_automaton__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hybrid_automaton_interfaces
{

namespace srv
{

namespace builder
{

class Init_StopHybridAutomaton_Request_stop_reason
{
public:
  explicit Init_StopHybridAutomaton_Request_stop_reason(::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request stop_reason(::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request::_stop_reason_type arg)
  {
    msg_.stop_reason = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request msg_;
};

class Init_StopHybridAutomaton_Request_automaton_uuid
{
public:
  explicit Init_StopHybridAutomaton_Request_automaton_uuid(::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request & msg)
  : msg_(msg)
  {}
  Init_StopHybridAutomaton_Request_stop_reason automaton_uuid(::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request::_automaton_uuid_type arg)
  {
    msg_.automaton_uuid = std::move(arg);
    return Init_StopHybridAutomaton_Request_stop_reason(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request msg_;
};

class Init_StopHybridAutomaton_Request_stamp
{
public:
  Init_StopHybridAutomaton_Request_stamp()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StopHybridAutomaton_Request_automaton_uuid stamp(::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return Init_StopHybridAutomaton_Request_automaton_uuid(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Request>()
{
  return hybrid_automaton_interfaces::srv::builder::Init_StopHybridAutomaton_Request_stamp();
}

}  // namespace hybrid_automaton_interfaces


namespace hybrid_automaton_interfaces
{

namespace srv
{

namespace builder
{

class Init_StopHybridAutomaton_Response_message
{
public:
  explicit Init_StopHybridAutomaton_Response_message(::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response message(::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response msg_;
};

class Init_StopHybridAutomaton_Response_success
{
public:
  explicit Init_StopHybridAutomaton_Response_success(::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response & msg)
  : msg_(msg)
  {}
  Init_StopHybridAutomaton_Response_message success(::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_StopHybridAutomaton_Response_message(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response msg_;
};

class Init_StopHybridAutomaton_Response_automaton_uuid
{
public:
  Init_StopHybridAutomaton_Response_automaton_uuid()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StopHybridAutomaton_Response_success automaton_uuid(::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response::_automaton_uuid_type arg)
  {
    msg_.automaton_uuid = std::move(arg);
    return Init_StopHybridAutomaton_Response_success(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::srv::StopHybridAutomaton_Response>()
{
  return hybrid_automaton_interfaces::srv::builder::Init_StopHybridAutomaton_Response_automaton_uuid();
}

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__STOP_HYBRID_AUTOMATON__BUILDER_HPP_
