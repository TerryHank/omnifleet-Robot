// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from mola_msgs:srv/MolaRuntimeParamGet.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_GET__BUILDER_HPP_
#define MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_GET__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "mola_msgs/srv/detail/mola_runtime_param_get__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace mola_msgs
{

namespace srv
{


}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::mola_msgs::srv::MolaRuntimeParamGet_Request>()
{
  return ::mola_msgs::srv::MolaRuntimeParamGet_Request(rosidl_runtime_cpp::MessageInitialization::ZERO);
}

}  // namespace mola_msgs


namespace mola_msgs
{

namespace srv
{

namespace builder
{

class Init_MolaRuntimeParamGet_Response_parameters
{
public:
  Init_MolaRuntimeParamGet_Response_parameters()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::mola_msgs::srv::MolaRuntimeParamGet_Response parameters(::mola_msgs::srv::MolaRuntimeParamGet_Response::_parameters_type arg)
  {
    msg_.parameters = std::move(arg);
    return std::move(msg_);
  }

private:
  ::mola_msgs::srv::MolaRuntimeParamGet_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::mola_msgs::srv::MolaRuntimeParamGet_Response>()
{
  return mola_msgs::srv::builder::Init_MolaRuntimeParamGet_Response_parameters();
}

}  // namespace mola_msgs

#endif  // MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_GET__BUILDER_HPP_
