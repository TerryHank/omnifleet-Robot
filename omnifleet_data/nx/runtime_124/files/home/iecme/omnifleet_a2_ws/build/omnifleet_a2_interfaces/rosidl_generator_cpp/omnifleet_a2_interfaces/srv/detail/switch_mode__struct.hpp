// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from omnifleet_a2_interfaces:srv/SwitchMode.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_A2_INTERFACES__SRV__DETAIL__SWITCH_MODE__STRUCT_HPP_
#define OMNIFLEET_A2_INTERFACES__SRV__DETAIL__SWITCH_MODE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__omnifleet_a2_interfaces__srv__SwitchMode_Request __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_a2_interfaces__srv__SwitchMode_Request __declspec(deprecated)
#endif

namespace omnifleet_a2_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct SwitchMode_Request_
{
  using Type = SwitchMode_Request_<ContainerAllocator>;

  explicit SwitchMode_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mode = "";
      this->operation = "";
      this->map_id = "";
    }
  }

  explicit SwitchMode_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : mode(_alloc),
    operation(_alloc),
    map_id(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mode = "";
      this->operation = "";
      this->map_id = "";
    }
  }

  // field types and members
  using _mode_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _mode_type mode;
  using _operation_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _operation_type operation;
  using _map_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _map_id_type map_id;

  // setters for named parameter idiom
  Type & set__mode(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->mode = _arg;
    return *this;
  }
  Type & set__operation(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->operation = _arg;
    return *this;
  }
  Type & set__map_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->map_id = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    omnifleet_a2_interfaces::srv::SwitchMode_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_a2_interfaces::srv::SwitchMode_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_a2_interfaces::srv::SwitchMode_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_a2_interfaces::srv::SwitchMode_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_a2_interfaces__srv__SwitchMode_Request
    std::shared_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_a2_interfaces__srv__SwitchMode_Request
    std::shared_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SwitchMode_Request_ & other) const
  {
    if (this->mode != other.mode) {
      return false;
    }
    if (this->operation != other.operation) {
      return false;
    }
    if (this->map_id != other.map_id) {
      return false;
    }
    return true;
  }
  bool operator!=(const SwitchMode_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SwitchMode_Request_

// alias to use template instance with default allocator
using SwitchMode_Request =
  omnifleet_a2_interfaces::srv::SwitchMode_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace omnifleet_a2_interfaces


#ifndef _WIN32
# define DEPRECATED__omnifleet_a2_interfaces__srv__SwitchMode_Response __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_a2_interfaces__srv__SwitchMode_Response __declspec(deprecated)
#endif

namespace omnifleet_a2_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct SwitchMode_Response_
{
  using Type = SwitchMode_Response_<ContainerAllocator>;

  explicit SwitchMode_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->accepted = false;
      this->transaction_id = "";
      this->message = "";
    }
  }

  explicit SwitchMode_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : transaction_id(_alloc),
    message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->accepted = false;
      this->transaction_id = "";
      this->message = "";
    }
  }

  // field types and members
  using _accepted_type =
    bool;
  _accepted_type accepted;
  using _transaction_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _transaction_id_type transaction_id;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;

  // setters for named parameter idiom
  Type & set__accepted(
    const bool & _arg)
  {
    this->accepted = _arg;
    return *this;
  }
  Type & set__transaction_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->transaction_id = _arg;
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
    omnifleet_a2_interfaces::srv::SwitchMode_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_a2_interfaces::srv::SwitchMode_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_a2_interfaces::srv::SwitchMode_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_a2_interfaces::srv::SwitchMode_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_a2_interfaces__srv__SwitchMode_Response
    std::shared_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_a2_interfaces__srv__SwitchMode_Response
    std::shared_ptr<omnifleet_a2_interfaces::srv::SwitchMode_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SwitchMode_Response_ & other) const
  {
    if (this->accepted != other.accepted) {
      return false;
    }
    if (this->transaction_id != other.transaction_id) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const SwitchMode_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SwitchMode_Response_

// alias to use template instance with default allocator
using SwitchMode_Response =
  omnifleet_a2_interfaces::srv::SwitchMode_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace omnifleet_a2_interfaces

namespace omnifleet_a2_interfaces
{

namespace srv
{

struct SwitchMode
{
  using Request = omnifleet_a2_interfaces::srv::SwitchMode_Request;
  using Response = omnifleet_a2_interfaces::srv::SwitchMode_Response;
};

}  // namespace srv

}  // namespace omnifleet_a2_interfaces

#endif  // OMNIFLEET_A2_INTERFACES__SRV__DETAIL__SWITCH_MODE__STRUCT_HPP_
