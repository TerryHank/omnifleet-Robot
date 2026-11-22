// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from mola_msgs:srv/RelocalizeFromStateEstimator.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__RELOCALIZE_FROM_STATE_ESTIMATOR__STRUCT_HPP_
#define MOLA_MSGS__SRV__DETAIL__RELOCALIZE_FROM_STATE_ESTIMATOR__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__mola_msgs__srv__RelocalizeFromStateEstimator_Request __attribute__((deprecated))
#else
# define DEPRECATED__mola_msgs__srv__RelocalizeFromStateEstimator_Request __declspec(deprecated)
#endif

namespace mola_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct RelocalizeFromStateEstimator_Request_
{
  using Type = RelocalizeFromStateEstimator_Request_<ContainerAllocator>;

  explicit RelocalizeFromStateEstimator_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  explicit RelocalizeFromStateEstimator_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  // field types and members
  using _structure_needs_at_least_one_member_type =
    uint8_t;
  _structure_needs_at_least_one_member_type structure_needs_at_least_one_member;


  // constant declarations

  // pointer types
  using RawPtr =
    mola_msgs::srv::RelocalizeFromStateEstimator_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const mola_msgs::srv::RelocalizeFromStateEstimator_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      mola_msgs::srv::RelocalizeFromStateEstimator_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      mola_msgs::srv::RelocalizeFromStateEstimator_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__mola_msgs__srv__RelocalizeFromStateEstimator_Request
    std::shared_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__mola_msgs__srv__RelocalizeFromStateEstimator_Request
    std::shared_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RelocalizeFromStateEstimator_Request_ & other) const
  {
    if (this->structure_needs_at_least_one_member != other.structure_needs_at_least_one_member) {
      return false;
    }
    return true;
  }
  bool operator!=(const RelocalizeFromStateEstimator_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RelocalizeFromStateEstimator_Request_

// alias to use template instance with default allocator
using RelocalizeFromStateEstimator_Request =
  mola_msgs::srv::RelocalizeFromStateEstimator_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace mola_msgs


#ifndef _WIN32
# define DEPRECATED__mola_msgs__srv__RelocalizeFromStateEstimator_Response __attribute__((deprecated))
#else
# define DEPRECATED__mola_msgs__srv__RelocalizeFromStateEstimator_Response __declspec(deprecated)
#endif

namespace mola_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct RelocalizeFromStateEstimator_Response_
{
  using Type = RelocalizeFromStateEstimator_Response_<ContainerAllocator>;

  explicit RelocalizeFromStateEstimator_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->accepted = false;
    }
  }

  explicit RelocalizeFromStateEstimator_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->accepted = false;
    }
  }

  // field types and members
  using _accepted_type =
    bool;
  _accepted_type accepted;

  // setters for named parameter idiom
  Type & set__accepted(
    const bool & _arg)
  {
    this->accepted = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    mola_msgs::srv::RelocalizeFromStateEstimator_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const mola_msgs::srv::RelocalizeFromStateEstimator_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      mola_msgs::srv::RelocalizeFromStateEstimator_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      mola_msgs::srv::RelocalizeFromStateEstimator_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__mola_msgs__srv__RelocalizeFromStateEstimator_Response
    std::shared_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__mola_msgs__srv__RelocalizeFromStateEstimator_Response
    std::shared_ptr<mola_msgs::srv::RelocalizeFromStateEstimator_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RelocalizeFromStateEstimator_Response_ & other) const
  {
    if (this->accepted != other.accepted) {
      return false;
    }
    return true;
  }
  bool operator!=(const RelocalizeFromStateEstimator_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RelocalizeFromStateEstimator_Response_

// alias to use template instance with default allocator
using RelocalizeFromStateEstimator_Response =
  mola_msgs::srv::RelocalizeFromStateEstimator_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace mola_msgs

namespace mola_msgs
{

namespace srv
{

struct RelocalizeFromStateEstimator
{
  using Request = mola_msgs::srv::RelocalizeFromStateEstimator_Request;
  using Response = mola_msgs::srv::RelocalizeFromStateEstimator_Response;
};

}  // namespace srv

}  // namespace mola_msgs

#endif  // MOLA_MSGS__SRV__DETAIL__RELOCALIZE_FROM_STATE_ESTIMATOR__STRUCT_HPP_
