// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from mola_msgs:srv/MolaRuntimeParamSet.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_SET__STRUCT_HPP_
#define MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_SET__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__mola_msgs__srv__MolaRuntimeParamSet_Request __attribute__((deprecated))
#else
# define DEPRECATED__mola_msgs__srv__MolaRuntimeParamSet_Request __declspec(deprecated)
#endif

namespace mola_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct MolaRuntimeParamSet_Request_
{
  using Type = MolaRuntimeParamSet_Request_<ContainerAllocator>;

  explicit MolaRuntimeParamSet_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->parameters = "";
    }
  }

  explicit MolaRuntimeParamSet_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : parameters(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->parameters = "";
    }
  }

  // field types and members
  using _parameters_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _parameters_type parameters;

  // setters for named parameter idiom
  Type & set__parameters(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->parameters = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    mola_msgs::srv::MolaRuntimeParamSet_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const mola_msgs::srv::MolaRuntimeParamSet_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<mola_msgs::srv::MolaRuntimeParamSet_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<mola_msgs::srv::MolaRuntimeParamSet_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      mola_msgs::srv::MolaRuntimeParamSet_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<mola_msgs::srv::MolaRuntimeParamSet_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      mola_msgs::srv::MolaRuntimeParamSet_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<mola_msgs::srv::MolaRuntimeParamSet_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<mola_msgs::srv::MolaRuntimeParamSet_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<mola_msgs::srv::MolaRuntimeParamSet_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__mola_msgs__srv__MolaRuntimeParamSet_Request
    std::shared_ptr<mola_msgs::srv::MolaRuntimeParamSet_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__mola_msgs__srv__MolaRuntimeParamSet_Request
    std::shared_ptr<mola_msgs::srv::MolaRuntimeParamSet_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MolaRuntimeParamSet_Request_ & other) const
  {
    if (this->parameters != other.parameters) {
      return false;
    }
    return true;
  }
  bool operator!=(const MolaRuntimeParamSet_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MolaRuntimeParamSet_Request_

// alias to use template instance with default allocator
using MolaRuntimeParamSet_Request =
  mola_msgs::srv::MolaRuntimeParamSet_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace mola_msgs


#ifndef _WIN32
# define DEPRECATED__mola_msgs__srv__MolaRuntimeParamSet_Response __attribute__((deprecated))
#else
# define DEPRECATED__mola_msgs__srv__MolaRuntimeParamSet_Response __declspec(deprecated)
#endif

namespace mola_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct MolaRuntimeParamSet_Response_
{
  using Type = MolaRuntimeParamSet_Response_<ContainerAllocator>;

  explicit MolaRuntimeParamSet_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->error_message = "";
    }
  }

  explicit MolaRuntimeParamSet_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : error_message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->error_message = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _error_message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _error_message_type error_message;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__error_message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->error_message = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    mola_msgs::srv::MolaRuntimeParamSet_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const mola_msgs::srv::MolaRuntimeParamSet_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<mola_msgs::srv::MolaRuntimeParamSet_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<mola_msgs::srv::MolaRuntimeParamSet_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      mola_msgs::srv::MolaRuntimeParamSet_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<mola_msgs::srv::MolaRuntimeParamSet_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      mola_msgs::srv::MolaRuntimeParamSet_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<mola_msgs::srv::MolaRuntimeParamSet_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<mola_msgs::srv::MolaRuntimeParamSet_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<mola_msgs::srv::MolaRuntimeParamSet_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__mola_msgs__srv__MolaRuntimeParamSet_Response
    std::shared_ptr<mola_msgs::srv::MolaRuntimeParamSet_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__mola_msgs__srv__MolaRuntimeParamSet_Response
    std::shared_ptr<mola_msgs::srv::MolaRuntimeParamSet_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const MolaRuntimeParamSet_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->error_message != other.error_message) {
      return false;
    }
    return true;
  }
  bool operator!=(const MolaRuntimeParamSet_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct MolaRuntimeParamSet_Response_

// alias to use template instance with default allocator
using MolaRuntimeParamSet_Response =
  mola_msgs::srv::MolaRuntimeParamSet_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace mola_msgs

namespace mola_msgs
{

namespace srv
{

struct MolaRuntimeParamSet
{
  using Request = mola_msgs::srv::MolaRuntimeParamSet_Request;
  using Response = mola_msgs::srv::MolaRuntimeParamSet_Response;
};

}  // namespace srv

}  // namespace mola_msgs

#endif  // MOLA_MSGS__SRV__DETAIL__MOLA_RUNTIME_PARAM_SET__STRUCT_HPP_
