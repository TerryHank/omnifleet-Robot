// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from omnifleet_navigation_interfaces:action/ExecuteFormation.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_FORMATION__BUILDER_HPP_
#define OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_FORMATION__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "omnifleet_navigation_interfaces/action/detail/execute_formation__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace builder
{

class Init_ExecuteFormation_Goal_pass_radius
{
public:
  explicit Init_ExecuteFormation_Goal_pass_radius(::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal & msg)
  : msg_(msg)
  {}
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal pass_radius(::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal::_pass_radius_type arg)
  {
    msg_.pass_radius = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal msg_;
};

class Init_ExecuteFormation_Goal_waypoints
{
public:
  explicit Init_ExecuteFormation_Goal_waypoints(::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal & msg)
  : msg_(msg)
  {}
  Init_ExecuteFormation_Goal_pass_radius waypoints(::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal::_waypoints_type arg)
  {
    msg_.waypoints = std::move(arg);
    return Init_ExecuteFormation_Goal_pass_radius(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal msg_;
};

class Init_ExecuteFormation_Goal_revision
{
public:
  explicit Init_ExecuteFormation_Goal_revision(::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal & msg)
  : msg_(msg)
  {}
  Init_ExecuteFormation_Goal_waypoints revision(::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal::_revision_type arg)
  {
    msg_.revision = std::move(arg);
    return Init_ExecuteFormation_Goal_waypoints(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal msg_;
};

class Init_ExecuteFormation_Goal_command_epoch
{
public:
  explicit Init_ExecuteFormation_Goal_command_epoch(::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal & msg)
  : msg_(msg)
  {}
  Init_ExecuteFormation_Goal_revision command_epoch(::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal::_command_epoch_type arg)
  {
    msg_.command_epoch = std::move(arg);
    return Init_ExecuteFormation_Goal_revision(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal msg_;
};

class Init_ExecuteFormation_Goal_task_id
{
public:
  Init_ExecuteFormation_Goal_task_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ExecuteFormation_Goal_command_epoch task_id(::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal::_task_id_type arg)
  {
    msg_.task_id = std::move(arg);
    return Init_ExecuteFormation_Goal_command_epoch(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_navigation_interfaces::action::ExecuteFormation_Goal>()
{
  return omnifleet_navigation_interfaces::action::builder::Init_ExecuteFormation_Goal_task_id();
}

}  // namespace omnifleet_navigation_interfaces


namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace builder
{

class Init_ExecuteFormation_Result_message
{
public:
  explicit Init_ExecuteFormation_Result_message(::omnifleet_navigation_interfaces::action::ExecuteFormation_Result & msg)
  : msg_(msg)
  {}
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Result message(::omnifleet_navigation_interfaces::action::ExecuteFormation_Result::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Result msg_;
};

class Init_ExecuteFormation_Result_code
{
public:
  explicit Init_ExecuteFormation_Result_code(::omnifleet_navigation_interfaces::action::ExecuteFormation_Result & msg)
  : msg_(msg)
  {}
  Init_ExecuteFormation_Result_message code(::omnifleet_navigation_interfaces::action::ExecuteFormation_Result::_code_type arg)
  {
    msg_.code = std::move(arg);
    return Init_ExecuteFormation_Result_message(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Result msg_;
};

class Init_ExecuteFormation_Result_success
{
public:
  Init_ExecuteFormation_Result_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ExecuteFormation_Result_code success(::omnifleet_navigation_interfaces::action::ExecuteFormation_Result::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_ExecuteFormation_Result_code(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Result msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_navigation_interfaces::action::ExecuteFormation_Result>()
{
  return omnifleet_navigation_interfaces::action::builder::Init_ExecuteFormation_Result_success();
}

}  // namespace omnifleet_navigation_interfaces


namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace builder
{

class Init_ExecuteFormation_Feedback_tf_age_ms
{
public:
  explicit Init_ExecuteFormation_Feedback_tf_age_ms(::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback & msg)
  : msg_(msg)
  {}
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback tf_age_ms(::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback::_tf_age_ms_type arg)
  {
    msg_.tf_age_ms = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback msg_;
};

class Init_ExecuteFormation_Feedback_passed_points
{
public:
  explicit Init_ExecuteFormation_Feedback_passed_points(::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback & msg)
  : msg_(msg)
  {}
  Init_ExecuteFormation_Feedback_tf_age_ms passed_points(::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback::_passed_points_type arg)
  {
    msg_.passed_points = std::move(arg);
    return Init_ExecuteFormation_Feedback_tf_age_ms(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback msg_;
};

class Init_ExecuteFormation_Feedback_message
{
public:
  explicit Init_ExecuteFormation_Feedback_message(::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback & msg)
  : msg_(msg)
  {}
  Init_ExecuteFormation_Feedback_passed_points message(::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback::_message_type arg)
  {
    msg_.message = std::move(arg);
    return Init_ExecuteFormation_Feedback_passed_points(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback msg_;
};

class Init_ExecuteFormation_Feedback_phase
{
public:
  explicit Init_ExecuteFormation_Feedback_phase(::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback & msg)
  : msg_(msg)
  {}
  Init_ExecuteFormation_Feedback_message phase(::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback::_phase_type arg)
  {
    msg_.phase = std::move(arg);
    return Init_ExecuteFormation_Feedback_message(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback msg_;
};

class Init_ExecuteFormation_Feedback_task_id
{
public:
  Init_ExecuteFormation_Feedback_task_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ExecuteFormation_Feedback_phase task_id(::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback::_task_id_type arg)
  {
    msg_.task_id = std::move(arg);
    return Init_ExecuteFormation_Feedback_phase(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback>()
{
  return omnifleet_navigation_interfaces::action::builder::Init_ExecuteFormation_Feedback_task_id();
}

}  // namespace omnifleet_navigation_interfaces


namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace builder
{

class Init_ExecuteFormation_SendGoal_Request_goal
{
public:
  explicit Init_ExecuteFormation_SendGoal_Request_goal(::omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request & msg)
  : msg_(msg)
  {}
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request goal(::omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request::_goal_type arg)
  {
    msg_.goal = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request msg_;
};

class Init_ExecuteFormation_SendGoal_Request_goal_id
{
public:
  Init_ExecuteFormation_SendGoal_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ExecuteFormation_SendGoal_Request_goal goal_id(::omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_ExecuteFormation_SendGoal_Request_goal(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request>()
{
  return omnifleet_navigation_interfaces::action::builder::Init_ExecuteFormation_SendGoal_Request_goal_id();
}

}  // namespace omnifleet_navigation_interfaces


namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace builder
{

class Init_ExecuteFormation_SendGoal_Response_stamp
{
public:
  explicit Init_ExecuteFormation_SendGoal_Response_stamp(::omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response & msg)
  : msg_(msg)
  {}
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response stamp(::omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response::_stamp_type arg)
  {
    msg_.stamp = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response msg_;
};

class Init_ExecuteFormation_SendGoal_Response_accepted
{
public:
  Init_ExecuteFormation_SendGoal_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ExecuteFormation_SendGoal_Response_stamp accepted(::omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return Init_ExecuteFormation_SendGoal_Response_stamp(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response>()
{
  return omnifleet_navigation_interfaces::action::builder::Init_ExecuteFormation_SendGoal_Response_accepted();
}

}  // namespace omnifleet_navigation_interfaces


namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace builder
{

class Init_ExecuteFormation_GetResult_Request_goal_id
{
public:
  Init_ExecuteFormation_GetResult_Request_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request goal_id(::omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request>()
{
  return omnifleet_navigation_interfaces::action::builder::Init_ExecuteFormation_GetResult_Request_goal_id();
}

}  // namespace omnifleet_navigation_interfaces


namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace builder
{

class Init_ExecuteFormation_GetResult_Response_result
{
public:
  explicit Init_ExecuteFormation_GetResult_Response_result(::omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response & msg)
  : msg_(msg)
  {}
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response result(::omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response::_result_type arg)
  {
    msg_.result = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response msg_;
};

class Init_ExecuteFormation_GetResult_Response_status
{
public:
  Init_ExecuteFormation_GetResult_Response_status()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ExecuteFormation_GetResult_Response_result status(::omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response::_status_type arg)
  {
    msg_.status = std::move(arg);
    return Init_ExecuteFormation_GetResult_Response_result(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response>()
{
  return omnifleet_navigation_interfaces::action::builder::Init_ExecuteFormation_GetResult_Response_status();
}

}  // namespace omnifleet_navigation_interfaces


namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace builder
{

class Init_ExecuteFormation_FeedbackMessage_feedback
{
public:
  explicit Init_ExecuteFormation_FeedbackMessage_feedback(::omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage & msg)
  : msg_(msg)
  {}
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage feedback(::omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage::_feedback_type arg)
  {
    msg_.feedback = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage msg_;
};

class Init_ExecuteFormation_FeedbackMessage_goal_id
{
public:
  Init_ExecuteFormation_FeedbackMessage_goal_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ExecuteFormation_FeedbackMessage_feedback goal_id(::omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage::_goal_id_type arg)
  {
    msg_.goal_id = std::move(arg);
    return Init_ExecuteFormation_FeedbackMessage_feedback(msg_);
  }

private:
  ::omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage msg_;
};

}  // namespace builder

}  // namespace action

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage>()
{
  return omnifleet_navigation_interfaces::action::builder::Init_ExecuteFormation_FeedbackMessage_goal_id();
}

}  // namespace omnifleet_navigation_interfaces

#endif  // OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_FORMATION__BUILDER_HPP_
