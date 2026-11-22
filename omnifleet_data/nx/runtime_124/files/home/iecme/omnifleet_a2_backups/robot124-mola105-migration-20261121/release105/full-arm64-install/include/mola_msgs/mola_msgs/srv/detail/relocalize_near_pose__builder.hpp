// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from mola_msgs:srv/RelocalizeNearPose.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__RELOCALIZE_NEAR_POSE__BUILDER_HPP_
#define MOLA_MSGS__SRV__DETAIL__RELOCALIZE_NEAR_POSE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "mola_msgs/srv/detail/relocalize_near_pose__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace mola_msgs
{

namespace srv
{

namespace builder
{

class Init_RelocalizeNearPose_Request_pose
{
public:
  Init_RelocalizeNearPose_Request_pose()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::mola_msgs::srv::RelocalizeNearPose_Request pose(::mola_msgs::srv::RelocalizeNearPose_Request::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return std::move(msg_);
  }

private:
  ::mola_msgs::srv::RelocalizeNearPose_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::mola_msgs::srv::RelocalizeNearPose_Request>()
{
  return mola_msgs::srv::builder::Init_RelocalizeNearPose_Request_pose();
}

}  // namespace mola_msgs


namespace mola_msgs
{

namespace srv
{

namespace builder
{

class Init_RelocalizeNearPose_Response_accepted
{
public:
  Init_RelocalizeNearPose_Response_accepted()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::mola_msgs::srv::RelocalizeNearPose_Response accepted(::mola_msgs::srv::RelocalizeNearPose_Response::_accepted_type arg)
  {
    msg_.accepted = std::move(arg);
    return std::move(msg_);
  }

private:
  ::mola_msgs::srv::RelocalizeNearPose_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::mola_msgs::srv::RelocalizeNearPose_Response>()
{
  return mola_msgs::srv::builder::Init_RelocalizeNearPose_Response_accepted();
}

}  // namespace mola_msgs

#endif  // MOLA_MSGS__SRV__DETAIL__RELOCALIZE_NEAR_POSE__BUILDER_HPP_
