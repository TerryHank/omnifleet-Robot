// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from omnifleet_interfaces:srv/Capability.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__SRV__DETAIL__CAPABILITY__STRUCT_HPP_
#define OMNIFLEET_INTERFACES__SRV__DETAIL__CAPABILITY__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__omnifleet_interfaces__srv__Capability_Request __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_interfaces__srv__Capability_Request __declspec(deprecated)
#endif

namespace omnifleet_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct Capability_Request_
{
  using Type = Capability_Request_<ContainerAllocator>;

  explicit Capability_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->capability = "";
    }
  }

  explicit Capability_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : capability(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->capability = "";
    }
  }

  // field types and members
  using _capability_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _capability_type capability;

  // setters for named parameter idiom
  Type & set__capability(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->capability = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    omnifleet_interfaces::srv::Capability_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_interfaces::srv::Capability_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_interfaces::srv::Capability_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_interfaces::srv::Capability_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_interfaces::srv::Capability_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_interfaces::srv::Capability_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_interfaces::srv::Capability_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_interfaces::srv::Capability_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_interfaces::srv::Capability_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_interfaces::srv::Capability_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_interfaces__srv__Capability_Request
    std::shared_ptr<omnifleet_interfaces::srv::Capability_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_interfaces__srv__Capability_Request
    std::shared_ptr<omnifleet_interfaces::srv::Capability_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Capability_Request_ & other) const
  {
    if (this->capability != other.capability) {
      return false;
    }
    return true;
  }
  bool operator!=(const Capability_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Capability_Request_

// alias to use template instance with default allocator
using Capability_Request =
  omnifleet_interfaces::srv::Capability_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace omnifleet_interfaces


#ifndef _WIN32
# define DEPRECATED__omnifleet_interfaces__srv__Capability_Response __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_interfaces__srv__Capability_Response __declspec(deprecated)
#endif

namespace omnifleet_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct Capability_Response_
{
  using Type = Capability_Response_<ContainerAllocator>;

  explicit Capability_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->available = false;
      this->accepted = false;
      this->transaction_id = "";
      this->message = "";
    }
  }

  explicit Capability_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : transaction_id(_alloc),
    message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->available = false;
      this->accepted = false;
      this->transaction_id = "";
      this->message = "";
    }
  }

  // field types and members
  using _available_type =
    bool;
  _available_type available;
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
  Type & set__available(
    const bool & _arg)
  {
    this->available = _arg;
    return *this;
  }
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
    omnifleet_interfaces::srv::Capability_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_interfaces::srv::Capability_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_interfaces::srv::Capability_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_interfaces::srv::Capability_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_interfaces::srv::Capability_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_interfaces::srv::Capability_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_interfaces::srv::Capability_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_interfaces::srv::Capability_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_interfaces::srv::Capability_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_interfaces::srv::Capability_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_interfaces__srv__Capability_Response
    std::shared_ptr<omnifleet_interfaces::srv::Capability_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_interfaces__srv__Capability_Response
    std::shared_ptr<omnifleet_interfaces::srv::Capability_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const Capability_Response_ & other) const
  {
    if (this->available != other.available) {
      return false;
    }
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
  bool operator!=(const Capability_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct Capability_Response_

// alias to use template instance with default allocator
using Capability_Response =
  omnifleet_interfaces::srv::Capability_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace omnifleet_interfaces

namespace omnifleet_interfaces
{

namespace srv
{

struct Capability
{
  using Request = omnifleet_interfaces::srv::Capability_Request;
  using Response = omnifleet_interfaces::srv::Capability_Response;
};

}  // namespace srv

}  // namespace omnifleet_interfaces

#endif  // OMNIFLEET_INTERFACES__SRV__DETAIL__CAPABILITY__STRUCT_HPP_
