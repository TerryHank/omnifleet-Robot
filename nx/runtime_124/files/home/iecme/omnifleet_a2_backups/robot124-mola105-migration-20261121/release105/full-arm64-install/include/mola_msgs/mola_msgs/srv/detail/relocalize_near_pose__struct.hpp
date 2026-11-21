// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from mola_msgs:srv/RelocalizeNearPose.idl
// generated code does not contain a copyright notice

#ifndef MOLA_MSGS__SRV__DETAIL__RELOCALIZE_NEAR_POSE__STRUCT_HPP_
#define MOLA_MSGS__SRV__DETAIL__RELOCALIZE_NEAR_POSE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_with_covariance_stamped__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__mola_msgs__srv__RelocalizeNearPose_Request __attribute__((deprecated))
#else
# define DEPRECATED__mola_msgs__srv__RelocalizeNearPose_Request __declspec(deprecated)
#endif

namespace mola_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct RelocalizeNearPose_Request_
{
  using Type = RelocalizeNearPose_Request_<ContainerAllocator>;

  explicit RelocalizeNearPose_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_init)
  {
    (void)_init;
  }

  explicit RelocalizeNearPose_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : pose(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _pose_type =
    geometry_msgs::msg::PoseWithCovarianceStamped_<ContainerAllocator>;
  _pose_type pose;

  // setters for named parameter idiom
  Type & set__pose(
    const geometry_msgs::msg::PoseWithCovarianceStamped_<ContainerAllocator> & _arg)
  {
    this->pose = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    mola_msgs::srv::RelocalizeNearPose_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const mola_msgs::srv::RelocalizeNearPose_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<mola_msgs::srv::RelocalizeNearPose_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<mola_msgs::srv::RelocalizeNearPose_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      mola_msgs::srv::RelocalizeNearPose_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<mola_msgs::srv::RelocalizeNearPose_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      mola_msgs::srv::RelocalizeNearPose_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<mola_msgs::srv::RelocalizeNearPose_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<mola_msgs::srv::RelocalizeNearPose_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<mola_msgs::srv::RelocalizeNearPose_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__mola_msgs__srv__RelocalizeNearPose_Request
    std::shared_ptr<mola_msgs::srv::RelocalizeNearPose_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__mola_msgs__srv__RelocalizeNearPose_Request
    std::shared_ptr<mola_msgs::srv::RelocalizeNearPose_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RelocalizeNearPose_Request_ & other) const
  {
    if (this->pose != other.pose) {
      return false;
    }
    return true;
  }
  bool operator!=(const RelocalizeNearPose_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RelocalizeNearPose_Request_

// alias to use template instance with default allocator
using RelocalizeNearPose_Request =
  mola_msgs::srv::RelocalizeNearPose_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace mola_msgs


#ifndef _WIN32
# define DEPRECATED__mola_msgs__srv__RelocalizeNearPose_Response __attribute__((deprecated))
#else
# define DEPRECATED__mola_msgs__srv__RelocalizeNearPose_Response __declspec(deprecated)
#endif

namespace mola_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct RelocalizeNearPose_Response_
{
  using Type = RelocalizeNearPose_Response_<ContainerAllocator>;

  explicit RelocalizeNearPose_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->accepted = false;
    }
  }

  explicit RelocalizeNearPose_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
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
    mola_msgs::srv::RelocalizeNearPose_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const mola_msgs::srv::RelocalizeNearPose_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<mola_msgs::srv::RelocalizeNearPose_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<mola_msgs::srv::RelocalizeNearPose_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      mola_msgs::srv::RelocalizeNearPose_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<mola_msgs::srv::RelocalizeNearPose_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      mola_msgs::srv::RelocalizeNearPose_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<mola_msgs::srv::RelocalizeNearPose_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<mola_msgs::srv::RelocalizeNearPose_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<mola_msgs::srv::RelocalizeNearPose_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__mola_msgs__srv__RelocalizeNearPose_Response
    std::shared_ptr<mola_msgs::srv::RelocalizeNearPose_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__mola_msgs__srv__RelocalizeNearPose_Response
    std::shared_ptr<mola_msgs::srv::RelocalizeNearPose_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RelocalizeNearPose_Response_ & other) const
  {
    if (this->accepted != other.accepted) {
      return false;
    }
    return true;
  }
  bool operator!=(const RelocalizeNearPose_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RelocalizeNearPose_Response_

// alias to use template instance with default allocator
using RelocalizeNearPose_Response =
  mola_msgs::srv::RelocalizeNearPose_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace mola_msgs

namespace mola_msgs
{

namespace srv
{

struct RelocalizeNearPose
{
  using Request = mola_msgs::srv::RelocalizeNearPose_Request;
  using Response = mola_msgs::srv::RelocalizeNearPose_Response;
};

}  // namespace srv

}  // namespace mola_msgs

#endif  // MOLA_MSGS__SRV__DETAIL__RELOCALIZE_NEAR_POSE__STRUCT_HPP_
