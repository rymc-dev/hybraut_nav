// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hybrid_automaton_interfaces:srv/StartHybridAutomaton.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__START_HYBRID_AUTOMATON__BUILDER_HPP_
#define HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__START_HYBRID_AUTOMATON__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hybrid_automaton_interfaces/srv/detail/start_hybrid_automaton__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hybrid_automaton_interfaces
{

namespace srv
{

namespace builder
{

class Init_StartHybridAutomaton_Request_goal_waypoint
{
public:
  explicit Init_StartHybridAutomaton_Request_goal_waypoint(::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request goal_waypoint(::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request::_goal_waypoint_type arg)
  {
    msg_.goal_waypoint = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request msg_;
};

class Init_StartHybridAutomaton_Request_agent_uuid
{
public:
  explicit Init_StartHybridAutomaton_Request_agent_uuid(::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request & msg)
  : msg_(msg)
  {}
  Init_StartHybridAutomaton_Request_goal_waypoint agent_uuid(::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request::_agent_uuid_type arg)
  {
    msg_.agent_uuid = std::move(arg);
    return Init_StartHybridAutomaton_Request_goal_waypoint(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request msg_;
};

class Init_StartHybridAutomaton_Request_mission_profile
{
public:
  explicit Init_StartHybridAutomaton_Request_mission_profile(::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request & msg)
  : msg_(msg)
  {}
  Init_StartHybridAutomaton_Request_agent_uuid mission_profile(::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request::_mission_profile_type arg)
  {
    msg_.mission_profile = std::move(arg);
    return Init_StartHybridAutomaton_Request_agent_uuid(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request msg_;
};

class Init_StartHybridAutomaton_Request_mission_uuid
{
public:
  explicit Init_StartHybridAutomaton_Request_mission_uuid(::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request & msg)
  : msg_(msg)
  {}
  Init_StartHybridAutomaton_Request_mission_profile mission_uuid(::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request::_mission_uuid_type arg)
  {
    msg_.mission_uuid = std::move(arg);
    return Init_StartHybridAutomaton_Request_mission_profile(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request msg_;
};

class Init_StartHybridAutomaton_Request_stamp
{
public:
  Init_StartHybridAutomaton_Request_stamp()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StartHybridAutomaton_Request_mission_uuid stamp(::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return Init_StartHybridAutomaton_Request_mission_uuid(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Request>()
{
  return hybrid_automaton_interfaces::srv::builder::Init_StartHybridAutomaton_Request_stamp();
}

}  // namespace hybrid_automaton_interfaces


namespace hybrid_automaton_interfaces
{

namespace srv
{

namespace builder
{

class Init_StartHybridAutomaton_Response_message
{
public:
  explicit Init_StartHybridAutomaton_Response_message(::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response message(::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response msg_;
};

class Init_StartHybridAutomaton_Response_success
{
public:
  explicit Init_StartHybridAutomaton_Response_success(::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response & msg)
  : msg_(msg)
  {}
  Init_StartHybridAutomaton_Response_message success(::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_StartHybridAutomaton_Response_message(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response msg_;
};

class Init_StartHybridAutomaton_Response_automaton_uuid
{
public:
  Init_StartHybridAutomaton_Response_automaton_uuid()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StartHybridAutomaton_Response_success automaton_uuid(::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response::_automaton_uuid_type arg)
  {
    msg_.automaton_uuid = std::move(arg);
    return Init_StartHybridAutomaton_Response_success(msg_);
  }

private:
  ::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::srv::StartHybridAutomaton_Response>()
{
  return hybrid_automaton_interfaces::srv::builder::Init_StartHybridAutomaton_Response_automaton_uuid();
}

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__SRV__DETAIL__START_HYBRID_AUTOMATON__BUILDER_HPP_
