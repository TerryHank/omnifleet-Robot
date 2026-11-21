// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from mola_msgs:srv/MolaRuntimeParamSet.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_SET__BUILDER_HPP_
#define MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_SET__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "mola_msgs/srv/detail/mola_runtime_param_set__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace mola_msgs
{

namespace srv
{

namespace builder
{

class Init_MolaRuntimeParamSet_Request_parameters
{
public:
  Init_MolaRuntimeParamSet_Request_parameters()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::mola_msgs::srv::MolaRuntimeParamSet_Request parameters(::mola_msgs::srv::MolaRuntimeParamSet_Request::_parameters_type arg)
  {
    msg_.parameters = std::move(arg);
    return std::move(msg_);
  }

private:
  ::mola_msgs::srv::MolaRuntimeParamSet_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::mola_msgs::srv::MolaRuntimeParamSet_Request>()
{
  return mola_msgs::srv::builder::Init_MolaRuntimeParamSet_Request_parameters();
}

}  // namespace mola_msgs


namespace mola_msgs
{

namespace srv
{

namespace builder
{

class Init_MolaRuntimeParamSet_Response_error_message
{
public:
  explicit Init_MolaRuntimeParamSet_Response_error_message(::mola_msgs::srv::MolaRuntimeParamSet_Response & msg)
  : msg_(msg)
  {}
  ::mola_msgs::srv::MolaRuntimeParamSet_Response error_message(::mola_msgs::srv::MolaRuntimeParamSet_Response::_error_message_type arg)
  {
    msg_.error_message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::mola_msgs::srv::MolaRuntimeParamSet_Response msg_;
};

class Init_MolaRuntimeParamSet_Response_success
{
public:
  Init_MolaRuntimeParamSet_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_MolaRuntimeParamSet_Response_error_message success(::mola_msgs::srv::MolaRuntimeParamSet_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_MolaRuntimeParamSet_Response_error_message(msg_);
  }

private:
  ::mola_msgs::srv::MolaRuntimeParamSet_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::mola_msgs::srv::MolaRuntimeParamSet_Response>()
{
  return mola_msgs::srv::builder::Init_MolaRuntimeParamSet_Response_success();
}

}  // namespace mola_msgs

#endif  // MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_SET__BUILDER_HPP_
