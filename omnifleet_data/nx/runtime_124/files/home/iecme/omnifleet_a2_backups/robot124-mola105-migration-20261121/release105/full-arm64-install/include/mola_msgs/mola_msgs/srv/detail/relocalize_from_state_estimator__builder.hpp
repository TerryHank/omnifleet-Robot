// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from mola_msgs:srv/RelocalizeFromStateEstimator.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__RELOCALIZE_FROM_STATE_ESTIMATOR__BUILDER_HPP_
#define MOLA_MSGS__SRV__DETAIL__RELOCALIZE_FROM_STATE_ESTIMATOR__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "mola_msgs/srv/detail/relocalize_from_state_estimator__struct.hpp"
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
auto build<::mola_msgs::srv::RelocalizeFromStateEstimator_Request>()
{
  return ::mola_msgs::srv::RelocalizeFromStateEstimator_Request(rosidl_runtime_cpp::MessageInitialization::ZERO);
}

}  // namespace mola_msgs


namespace mola_msgs
{

namespace srv
{

namespace builder
{

class Init_RelocalizeFromStateEstimator_Response_accepted
{
public:
  Init_RelocalizeFromStateEstimator_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::mola_msgs::srv::RelocalizeFromStateEstimator_Response accepted(::mola_msgs::srv::RelocalizeFromStateEstimator_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return std::move(msg_);
  }

private:
  ::mola_msgs::srv::RelocalizeFromStateEstimator_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::mola_msgs::srv::RelocalizeFromStateEstimator_Response>()
{
  return mola_msgs::srv::builder::Init_RelocalizeFromStateEstimator_Response_accepted();
}

}  // namespace mola_msgs

#endif  // MOLA_MSGS__SRV__DETAIL__RELOCALIZE_FROM_STATE_ESTIMATOR__BUILDER_HPP_
