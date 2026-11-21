// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from omnifleet_interfaces:srv/ServoCommand.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__SRV__DETAIL__SERVO_COMMAND__STRUCT_HPP_
#define OMNIFLEET_INTERFACES__SRV__DETAIL__SERVO_COMMAND__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__omnifleet_interfaces__srv__ServoCommand_Request __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_interfaces__srv__ServoCommand_Request __declspec(deprecated)
#endif

namespace omnifleet_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct ServoCommand_Request_
{
  using Type = ServoCommand_Request_<ContainerAllocator>;

  explicit ServoCommand_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->operation = 0;
      this->id = 0;
      this->arg0 = 0l;
      this->arg1 = 0l;
      this->arg2 = 0l;
    }
  }

  explicit ServoCommand_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->operation = 0;
      this->id = 0;
      this->arg0 = 0l;
      this->arg1 = 0l;
      this->arg2 = 0l;
    }
  }

  // field types and members
  using _operation_type =
    uint8_t;
  _operation_type operation;
  using _id_type =
    uint8_t;
  _id_type id;
  using _arg0_type =
    int32_t;
  _arg0_type arg0;
  using _arg1_type =
    int32_t;
  _arg1_type arg1;
  using _arg2_type =
    int32_t;
  _arg2_type arg2;

  // setters for named parameter idiom
  Type & set__operation(
    const uint8_t & _arg)
  {
    this->operation = _arg;
    return *this;
  }
  Type & set__id(
    const uint8_t & _arg)
  {
    this->id = _arg;
    return *this;
  }
  Type & set__arg0(
    const int32_t & _arg)
  {
    this->arg0 = _arg;
    return *this;
  }
  Type & set__arg1(
    const int32_t & _arg)
  {
    this->arg1 = _arg;
    return *this;
  }
  Type & set__arg2(
    const int32_t & _arg)
  {
    this->arg2 = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    omnifleet_interfaces::srv::ServoCommand_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_interfaces::srv::ServoCommand_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_interfaces::srv::ServoCommand_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_interfaces::srv::ServoCommand_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_interfaces::srv::ServoCommand_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_interfaces::srv::ServoCommand_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_interfaces::srv::ServoCommand_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_interfaces::srv::ServoCommand_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_interfaces::srv::ServoCommand_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_interfaces::srv::ServoCommand_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_interfaces__srv__ServoCommand_Request
    std::shared_ptr<omnifleet_interfaces::srv::ServoCommand_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_interfaces__srv__ServoCommand_Request
    std::shared_ptr<omnifleet_interfaces::srv::ServoCommand_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ServoCommand_Request_ & other) const
  {
    if (this->operation != other.operation) {
      return false;
    }
    if (this->id != other.id) {
      return false;
    }
    if (this->arg0 != other.arg0) {
      return false;
    }
    if (this->arg1 != other.arg1) {
      return false;
    }
    if (this->arg2 != other.arg2) {
      return false;
    }
    return true;
  }
  bool operator!=(const ServoCommand_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ServoCommand_Request_

// alias to use template instance with default allocator
using ServoCommand_Request =
  omnifleet_interfaces::srv::ServoCommand_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace omnifleet_interfaces


#ifndef _WIN32
# define DEPRECATED__omnifleet_interfaces__srv__ServoCommand_Response __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_interfaces__srv__ServoCommand_Response __declspec(deprecated)
#endif

namespace omnifleet_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct ServoCommand_Response_
{
  using Type = ServoCommand_Response_<ContainerAllocator>;

  explicit ServoCommand_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->value0 = 0l;
      this->value1 = 0l;
      this->value2 = 0l;
      this->message = "";
    }
  }

  explicit ServoCommand_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->value0 = 0l;
      this->value1 = 0l;
      this->value2 = 0l;
      this->message = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _value0_type =
    int32_t;
  _value0_type value0;
  using _value1_type =
    int32_t;
  _value1_type value1;
  using _value2_type =
    int32_t;
  _value2_type value2;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__value0(
    const int32_t & _arg)
  {
    this->value0 = _arg;
    return *this;
  }
  Type & set__value1(
    const int32_t & _arg)
  {
    this->value1 = _arg;
    return *this;
  }
  Type & set__value2(
    const int32_t & _arg)
  {
    this->value2 = _arg;
    return *this;
  }
  Type & set__message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->message = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    omnifleet_interfaces::srv::ServoCommand_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_interfaces::srv::ServoCommand_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_interfaces::srv::ServoCommand_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_interfaces::srv::ServoCommand_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_interfaces::srv::ServoCommand_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_interfaces::srv::ServoCommand_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_interfaces::srv::ServoCommand_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_interfaces::srv::ServoCommand_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_interfaces::srv::ServoCommand_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_interfaces::srv::ServoCommand_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_interfaces__srv__ServoCommand_Response
    std::shared_ptr<omnifleet_interfaces::srv::ServoCommand_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_interfaces__srv__ServoCommand_Response
    std::shared_ptr<omnifleet_interfaces::srv::ServoCommand_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ServoCommand_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->value0 != other.value0) {
      return false;
    }
    if (this->value1 != other.value1) {
      return false;
    }
    if (this->value2 != other.value2) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const ServoCommand_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ServoCommand_Response_

// alias to use template instance with default allocator
using ServoCommand_Response =
  omnifleet_interfaces::srv::ServoCommand_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace omnifleet_interfaces

namespace omnifleet_interfaces
{

namespace srv
{

struct ServoCommand
{
  using Request = omnifleet_interfaces::srv::ServoCommand_Request;
  using Response = omnifleet_interfaces::srv::ServoCommand_Response;
};

}  // namespace srv

}  // namespace omnifleet_interfaces

#endif  // OMNIFLEET_INTERFACES__SRV__DETAIL__SERVO_COMMAND__STRUCT_HPP_
