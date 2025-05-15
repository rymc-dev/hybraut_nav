// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from hybrid_automaton_interfaces:action/HybridAutomaton.idl
// generated code does not contain a copyright notice

#ifndef HYBRID_AUTOMATON_INTERFACES__ACTION__DETAIL__HYBRID_AUTOMATON__BUILDER_HPP_
#define HYBRID_AUTOMATON_INTERFACES__ACTION__DETAIL__HYBRID_AUTOMATON__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "hybrid_automaton_interfaces/action/detail/hybrid_automaton__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace hybrid_automaton_interfaces
{

namespace action
{

namespace builder
{

class Init_HybridAutomaton_Goal_goal_waypoint
{
public:
  explicit Init_HybridAutomaton_Goal_goal_waypoint(::hybrid_automaton_interfaces::action::HybridAutomaton_Goal & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::action::HybridAutomaton_Goal goal_waypoint(::hybrid_automaton_interfaces::action::HybridAutomaton_Goal::_goal_waypoint_type arg)
  {
    msg_.goal_waypoint = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_Goal msg_;
};

class Init_HybridAutomaton_Goal_agent_uuid
{
public:
  explicit Init_HybridAutomaton_Goal_agent_uuid(::hybrid_automaton_interfaces::action::HybridAutomaton_Goal & msg)
  : msg_(msg)
  {}
  Init_HybridAutomaton_Goal_goal_waypoint agent_uuid(::hybrid_automaton_interfaces::action::HybridAutomaton_Goal::_agent_uuid_type arg)
  {
    msg_.agent_uuid = std::move(arg);
    return Init_HybridAutomaton_Goal_goal_waypoint(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_Goal msg_;
};

class Init_HybridAutomaton_Goal_mission_profile
{
public:
  explicit Init_HybridAutomaton_Goal_mission_profile(::hybrid_automaton_interfaces::action::HybridAutomaton_Goal & msg)
  : msg_(msg)
  {}
  Init_HybridAutomaton_Goal_agent_uuid mission_profile(::hybrid_automaton_interfaces::action::HybridAutomaton_Goal::_mission_profile_type arg)
  {
    msg_.mission_profile = std::move(arg);
    return Init_HybridAutomaton_Goal_agent_uuid(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_Goal msg_;
};

class Init_HybridAutomaton_Goal_mission_uuid
{
public:
  explicit Init_HybridAutomaton_Goal_mission_uuid(::hybrid_automaton_interfaces::action::HybridAutomaton_Goal & msg)
  : msg_(msg)
  {}
  Init_HybridAutomaton_Goal_mission_profile mission_uuid(::hybrid_automaton_interfaces::action::HybridAutomaton_Goal::_mission_uuid_type arg)
  {
    msg_.mission_uuid = std::move(arg);
    return Init_HybridAutomaton_Goal_mission_profile(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_Goal msg_;
};

class Init_HybridAutomaton_Goal_stamp
{
public:
  Init_HybridAutomaton_Goal_stamp()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_HybridAutomaton_Goal_mission_uuid stamp(::hybrid_automaton_interfaces::action::HybridAutomaton_Goal::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return Init_HybridAutomaton_Goal_mission_uuid(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_Goal msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::action::HybridAutomaton_Goal>()
{
  return hybrid_automaton_interfaces::action::builder::Init_HybridAutomaton_Goal_stamp();
}

}  // namespace hybrid_automaton_interfaces


namespace hybrid_automaton_interfaces
{

namespace action
{

namespace builder
{

class Init_HybridAutomaton_Result_message
{
public:
  explicit Init_HybridAutomaton_Result_message(::hybrid_automaton_interfaces::action::HybridAutomaton_Result & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::action::HybridAutomaton_Result message(::hybrid_automaton_interfaces::action::HybridAutomaton_Result::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_Result msg_;
};

class Init_HybridAutomaton_Result_success
{
public:
  Init_HybridAutomaton_Result_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_HybridAutomaton_Result_message success(::hybrid_automaton_interfaces::action::HybridAutomaton_Result::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_HybridAutomaton_Result_message(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_Result msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::action::HybridAutomaton_Result>()
{
  return hybrid_automaton_interfaces::action::builder::Init_HybridAutomaton_Result_success();
}

}  // namespace hybrid_automaton_interfaces


namespace hybrid_automaton_interfaces
{

namespace action
{

namespace builder
{

class Init_HybridAutomaton_Feedback_feedback
{
public:
  Init_HybridAutomaton_Feedback_feedback()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::hybrid_automaton_interfaces::action::HybridAutomaton_Feedback feedback(::hybrid_automaton_interfaces::action::HybridAutomaton_Feedback::_feedback_type arg)
  {
    msg_.feedback = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_Feedback msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::action::HybridAutomaton_Feedback>()
{
  return hybrid_automaton_interfaces::action::builder::Init_HybridAutomaton_Feedback_feedback();
}

}  // namespace hybrid_automaton_interfaces


namespace hybrid_automaton_interfaces
{

namespace action
{

namespace builder
{

class Init_HybridAutomaton_SendGoal_Request_goal
{
public:
  explicit Init_HybridAutomaton_SendGoal_Request_goal(::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Request & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Request goal(::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Request::_goal_type arg)
  {
    msg_.goal = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Request msg_;
};

class Init_HybridAutomaton_SendGoal_Request_goal_id
{
public:
  Init_HybridAutomaton_SendGoal_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_HybridAutomaton_SendGoal_Request_goal goal_id(::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_HybridAutomaton_SendGoal_Request_goal(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Request>()
{
  return hybrid_automaton_interfaces::action::builder::Init_HybridAutomaton_SendGoal_Request_goal_id();
}

}  // namespace hybrid_automaton_interfaces


namespace hybrid_automaton_interfaces
{

namespace action
{

namespace builder
{

class Init_HybridAutomaton_SendGoal_Response_stamp
{
public:
  explicit Init_HybridAutomaton_SendGoal_Response_stamp(::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Response & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Response stamp(::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Response::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Response msg_;
};

class Init_HybridAutomaton_SendGoal_Response_accepted
{
public:
  Init_HybridAutomaton_SendGoal_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_HybridAutomaton_SendGoal_Response_stamp accepted(::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_HybridAutomaton_SendGoal_Response_stamp(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::action::HybridAutomaton_SendGoal_Response>()
{
  return hybrid_automaton_interfaces::action::builder::Init_HybridAutomaton_SendGoal_Response_accepted();
}

}  // namespace hybrid_automaton_interfaces


namespace hybrid_automaton_interfaces
{

namespace action
{

namespace builder
{

class Init_HybridAutomaton_GetResult_Request_goal_id
{
public:
  Init_HybridAutomaton_GetResult_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Request goal_id(::hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Request>()
{
  return hybrid_automaton_interfaces::action::builder::Init_HybridAutomaton_GetResult_Request_goal_id();
}

}  // namespace hybrid_automaton_interfaces


namespace hybrid_automaton_interfaces
{

namespace action
{

namespace builder
{

class Init_HybridAutomaton_GetResult_Response_result
{
public:
  explicit Init_HybridAutomaton_GetResult_Response_result(::hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Response & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Response result(::hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Response::_result_type arg)
  {
    msg_.result = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Response msg_;
};

class Init_HybridAutomaton_GetResult_Response_status
{
public:
  Init_HybridAutomaton_GetResult_Response_status()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_HybridAutomaton_GetResult_Response_result status(::hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Response::_status_type arg)
  {
    msg_.status = std::move(arg);
    return Init_HybridAutomaton_GetResult_Response_result(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::action::HybridAutomaton_GetResult_Response>()
{
  return hybrid_automaton_interfaces::action::builder::Init_HybridAutomaton_GetResult_Response_status();
}

}  // namespace hybrid_automaton_interfaces


namespace hybrid_automaton_interfaces
{

namespace action
{

namespace builder
{

class Init_HybridAutomaton_FeedbackMessage_feedback
{
public:
  explicit Init_HybridAutomaton_FeedbackMessage_feedback(::hybrid_automaton_interfaces::action::HybridAutomaton_FeedbackMessage & msg)
  : msg_(msg)
  {}
  ::hybrid_automaton_interfaces::action::HybridAutomaton_FeedbackMessage feedback(::hybrid_automaton_interfaces::action::HybridAutomaton_FeedbackMessage::_feedback_type arg)
  {
    msg_.feedback = std::move(arg);
    return std::move(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_FeedbackMessage msg_;
};

class Init_HybridAutomaton_FeedbackMessage_goal_id
{
public:
  Init_HybridAutomaton_FeedbackMessage_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_HybridAutomaton_FeedbackMessage_feedback goal_id(::hybrid_automaton_interfaces::action::HybridAutomaton_FeedbackMessage::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_HybridAutomaton_FeedbackMessage_feedback(msg_);
  }

private:
  ::hybrid_automaton_interfaces::action::HybridAutomaton_FeedbackMessage msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::hybrid_automaton_interfaces::action::HybridAutomaton_FeedbackMessage>()
{
  return hybrid_automaton_interfaces::action::builder::Init_HybridAutomaton_FeedbackMessage_goal_id();
}

}  // namespace hybrid_automaton_interfaces

#endif  // HYBRID_AUTOMATON_INTERFACES__ACTION__DETAIL__HYBRID_AUTOMATON__BUILDER_HPP_
