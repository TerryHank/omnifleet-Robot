// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from omnifleet_a2_interfaces:msg/SteeringAngleCommand.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_A2_INTERFACES__MSG__DETAIL__STEERING_ANGLE_COMMAND__STRUCT_HPP_
#define OMNIFLEET_A2_INTERFACES__MSG__DETAIL__STEERING_ANGLE_COMMAND__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__omnifleet_a2_interfaces__msg__SteeringAngleCommand __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_a2_interfaces__msg__SteeringAngleCommand __declspec(deprecated)
#endif

namespace omnifleet_a2_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct SteeringAngleCommand_
{
  using Type = SteeringAngleCommand_<ContainerAllocator>;

  explicit SteeringAngleCommand_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->steering_angle_rad = 0.0f;
    }
  }

  explicit SteeringAngleCommand_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->steering_angle_rad = 0.0f;
    }
  }

  // field types and members
  using _steering_angle_rad_type =
    float;
  _steering_angle_rad_type steering_angle_rad;

  // setters for named parameter idiom
  Type & set__steering_angle_rad(
    const float & _arg)
  {
    this->steering_angle_rad = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    omnifleet_a2_interfaces::msg::SteeringAngleCommand_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_a2_interfaces::msg::SteeringAngleCommand_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_a2_interfaces::msg::SteeringAngleCommand_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_a2_interfaces::msg::SteeringAngleCommand_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_a2_interfaces::msg::SteeringAngleCommand_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_a2_interfaces::msg::SteeringAngleCommand_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_a2_interfaces::msg::SteeringAngleCommand_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_a2_interfaces::msg::SteeringAngleCommand_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_a2_interfaces::msg::SteeringAngleCommand_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_a2_interfaces::msg::SteeringAngleCommand_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_a2_interfaces__msg__SteeringAngleCommand
    std::shared_ptr<omnifleet_a2_interfaces::msg::SteeringAngleCommand_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_a2_interfaces__msg__SteeringAngleCommand
    std::shared_ptr<omnifleet_a2_interfaces::msg::SteeringAngleCommand_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SteeringAngleCommand_ & other) const
  {
    if (this->steering_angle_rad != other.steering_angle_rad) {
      return false;
    }
    return true;
  }
  bool operator!=(const SteeringAngleCommand_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SteeringAngleCommand_

// alias to use template instance with default allocator
using SteeringAngleCommand =
  omnifleet_a2_interfaces::msg::SteeringAngleCommand_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace omnifleet_a2_interfaces

#endif  // OMNIFLEET_A2_INTERFACES__MSG__DETAIL__STEERING_ANGLE_COMMAND__STRUCT_HPP_
