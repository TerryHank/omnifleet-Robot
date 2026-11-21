// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from omnifleet_interfaces:srv/ServoCommand.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__SRV__DETAIL__SERVO_COMMAND__BUILDER_HPP_
#define OMNIFLEET_INTERFACES__SRV__DETAIL__SERVO_COMMAND__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "omnifleet_interfaces/srv/detail/servo_command__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace omnifleet_interfaces
{

namespace srv
{

namespace builder
{

class Init_ServoCommand_Request_arg2
{
public:
  explicit Init_ServoCommand_Request_arg2(::omnifleet_interfaces::srv::ServoCommand_Request & msg)
  : msg_(msg)
  {}
  ::omnifleet_interfaces::srv::ServoCommand_Request arg2(::omnifleet_interfaces::srv::ServoCommand_Request::_arg2_type arg)
  {
    msg_.arg2 = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_interfaces::srv::ServoCommand_Request msg_;
};

class Init_ServoCommand_Request_arg1
{
public:
  explicit Init_ServoCommand_Request_arg1(::omnifleet_interfaces::srv::ServoCommand_Request & msg)
  : msg_(msg)
  {}
  Init_ServoCommand_Request_arg2 arg1(::omnifleet_interfaces::srv::ServoCommand_Request::_arg1_type arg)
  {
    msg_.arg1 = std::move(arg);
    return Init_ServoCommand_Request_arg2(msg_);
  }

private:
  ::omnifleet_interfaces::srv::ServoCommand_Request msg_;
};

class Init_ServoCommand_Request_arg0
{
public:
  explicit Init_ServoCommand_Request_arg0(::omnifleet_interfaces::srv::ServoCommand_Request & msg)
  : msg_(msg)
  {}
  Init_ServoCommand_Request_arg1 arg0(::omnifleet_interfaces::srv::ServoCommand_Request::_arg0_type arg)
  {
    msg_.arg0 = std::move(arg);
    return Init_ServoCommand_Request_arg1(msg_);
  }

private:
  ::omnifleet_interfaces::srv::ServoCommand_Request msg_;
};

class Init_ServoCommand_Request_id
{
public:
  explicit Init_ServoCommand_Request_id(::omnifleet_interfaces::srv::ServoCommand_Request & msg)
  : msg_(msg)
  {}
  Init_ServoCommand_Request_arg0 id(::omnifleet_interfaces::srv::ServoCommand_Request::_id_type arg)
  {
    msg_.id = std::move(arg);
    return Init_ServoCommand_Request_arg0(msg_);
  }

private:
  ::omnifleet_interfaces::srv::ServoCommand_Request msg_;
};

class Init_ServoCommand_Request_operation
{
public:
  Init_ServoCommand_Request_operation()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ServoCommand_Request_id operation(::omnifleet_interfaces::srv::ServoCommand_Request::_operation_type arg)
  {
    msg_.operation = std::move(arg);
    return Init_ServoCommand_Request_id(msg_);
  }

private:
  ::omnifleet_interfaces::srv::ServoCommand_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_interfaces::srv::ServoCommand_Request>()
{
  return omnifleet_interfaces::srv::builder::Init_ServoCommand_Request_operation();
}

}  // namespace omnifleet_interfaces


namespace omnifleet_interfaces
{

namespace srv
{

namespace builder
{

class Init_ServoCommand_Response_message
{
public:
  explicit Init_ServoCommand_Response_message(::omnifleet_interfaces::srv::ServoCommand_Response & msg)
  : msg_(msg)
  {}
  ::omnifleet_interfaces::srv::ServoCommand_Response message(::omnifleet_interfaces::srv::ServoCommand_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::omnifleet_interfaces::srv::ServoCommand_Response msg_;
};

class Init_ServoCommand_Response_value2
{
public:
  explicit Init_ServoCommand_Response_value2(::omnifleet_interfaces::srv::ServoCommand_Response & msg)
  : msg_(msg)
  {}
  Init_ServoCommand_Response_message value2(::omnifleet_interfaces::srv::ServoCommand_Response::_value2_type arg)
  {
    msg_.value2 = std::move(arg);
    return Init_ServoCommand_Response_message(msg_);
  }

private:
  ::omnifleet_interfaces::srv::ServoCommand_Response msg_;
};

class Init_ServoCommand_Response_value1
{
public:
  explicit Init_ServoCommand_Response_value1(::omnifleet_interfaces::srv::ServoCommand_Response & msg)
  : msg_(msg)
  {}
  Init_ServoCommand_Response_value2 value1(::omnifleet_interfaces::srv::ServoCommand_Response::_value1_type arg)
  {
    msg_.value1 = std::move(arg);
    return Init_ServoCommand_Response_value2(msg_);
  }

private:
  ::omnifleet_interfaces::srv::ServoCommand_Response msg_;
};

class Init_ServoCommand_Response_value0
{
public:
  explicit Init_ServoCommand_Response_value0(::omnifleet_interfaces::srv::ServoCommand_Response & msg)
  : msg_(msg)
  {}
  Init_ServoCommand_Response_value1 value0(::omnifleet_interfaces::srv::ServoCommand_Response::_value0_type arg)
  {
    msg_.value0 = std::move(arg);
    return Init_ServoCommand_Response_value1(msg_);
  }

private:
  ::omnifleet_interfaces::srv::ServoCommand_Response msg_;
};

class Init_ServoCommand_Response_success
{
public:
  Init_ServoCommand_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_ServoCommand_Response_value0 success(::omnifleet_interfaces::srv::ServoCommand_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_ServoCommand_Response_value0(msg_);
  }

private:
  ::omnifleet_interfaces::srv::ServoCommand_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::omnifleet_interfaces::srv::ServoCommand_Response>()
{
  return omnifleet_interfaces::srv::builder::Init_ServoCommand_Response_success();
}

}  // namespace omnifleet_interfaces

#endif  // OMNIFLEET_INTERFACES__SRV__DETAIL__SERVO_COMMAND__BUILDER_HPP_
