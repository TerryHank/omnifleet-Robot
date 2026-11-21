// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from omnifleet_interfaces:srv/LoadMission.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__SRV__DETAIL__LOAD_MISSION__STRUCT_HPP_
#define OMNIFLEET_INTERFACES__SRV__DETAIL__LOAD_MISSION__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__omnifleet_interfaces__srv__LoadMission_Request __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_interfaces__srv__LoadMission_Request __declspec(deprecated)
#endif

namespace omnifleet_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct LoadMission_Request_
{
  using Type = LoadMission_Request_<ContainerAllocator>;

  explicit LoadMission_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mission_id = "";
    }
  }

  explicit LoadMission_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : mission_id(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mission_id = "";
    }
  }

  // field types and members
  using _mission_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _mission_id_type mission_id;

  // setters for named parameter idiom
  Type & set__mission_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->mission_id = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    omnifleet_interfaces::srv::LoadMission_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_interfaces::srv::LoadMission_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_interfaces::srv::LoadMission_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_interfaces::srv::LoadMission_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_interfaces::srv::LoadMission_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_interfaces::srv::LoadMission_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_interfaces::srv::LoadMission_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_interfaces::srv::LoadMission_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_interfaces::srv::LoadMission_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_interfaces::srv::LoadMission_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_interfaces__srv__LoadMission_Request
    std::shared_ptr<omnifleet_interfaces::srv::LoadMission_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_interfaces__srv__LoadMission_Request
    std::shared_ptr<omnifleet_interfaces::srv::LoadMission_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const LoadMission_Request_ & other) const
  {
    if (this->mission_id != other.mission_id) {
      return false;
    }
    return true;
  }
  bool operator!=(const LoadMission_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct LoadMission_Request_

// alias to use template instance with default allocator
using LoadMission_Request =
  omnifleet_interfaces::srv::LoadMission_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace omnifleet_interfaces


// Include directives for member types
// Member 'poses'
#include "geometry_msgs/msg/detail/pose__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__omnifleet_interfaces__srv__LoadMission_Response __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_interfaces__srv__LoadMission_Response __declspec(deprecated)
#endif

namespace omnifleet_interfaces
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct LoadMission_Response_
{
  using Type = LoadMission_Response_<ContainerAllocator>;

  explicit LoadMission_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->accepted = false;
      this->revision = 0ull;
      this->map_id = "";
      this->map_sha256 = "";
      this->frame = "";
      this->loop = false;
      this->message = "";
    }
  }

  explicit LoadMission_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : map_id(_alloc),
    map_sha256(_alloc),
    frame(_alloc),
    message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->accepted = false;
      this->revision = 0ull;
      this->map_id = "";
      this->map_sha256 = "";
      this->frame = "";
      this->loop = false;
      this->message = "";
    }
  }

  // field types and members
  using _accepted_type =
    bool;
  _accepted_type accepted;
  using _revision_type =
    uint64_t;
  _revision_type revision;
  using _map_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _map_id_type map_id;
  using _map_sha256_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _map_sha256_type map_sha256;
  using _frame_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _frame_type frame;
  using _poses_type =
    std::vector<geometry_msgs::msg::Pose_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Pose_<ContainerAllocator>>>;
  _poses_type poses;
  using _loop_type =
    bool;
  _loop_type loop;
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
  Type & set__revision(
    const uint64_t & _arg)
  {
    this->revision = _arg;
    return *this;
  }
  Type & set__map_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->map_id = _arg;
    return *this;
  }
  Type & set__map_sha256(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->map_sha256 = _arg;
    return *this;
  }
  Type & set__frame(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->frame = _arg;
    return *this;
  }
  Type & set__poses(
    const std::vector<geometry_msgs::msg::Pose_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<geometry_msgs::msg::Pose_<ContainerAllocator>>> & _arg)
  {
    this->poses = _arg;
    return *this;
  }
  Type & set__loop(
    const bool & _arg)
  {
    this->loop = _arg;
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
    omnifleet_interfaces::srv::LoadMission_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_interfaces::srv::LoadMission_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_interfaces::srv::LoadMission_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_interfaces::srv::LoadMission_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_interfaces::srv::LoadMission_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_interfaces::srv::LoadMission_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_interfaces::srv::LoadMission_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_interfaces::srv::LoadMission_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_interfaces::srv::LoadMission_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_interfaces::srv::LoadMission_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_interfaces__srv__LoadMission_Response
    std::shared_ptr<omnifleet_interfaces::srv::LoadMission_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_interfaces__srv__LoadMission_Response
    std::shared_ptr<omnifleet_interfaces::srv::LoadMission_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const LoadMission_Response_ & other) const
  {
    if (this->accepted != other.accepted) {
      return false;
    }
    if (this->revision != other.revision) {
      return false;
    }
    if (this->map_id != other.map_id) {
      return false;
    }
    if (this->map_sha256 != other.map_sha256) {
      return false;
    }
    if (this->frame != other.frame) {
      return false;
    }
    if (this->poses != other.poses) {
      return false;
    }
    if (this->loop != other.loop) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const LoadMission_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct LoadMission_Response_

// alias to use template instance with default allocator
using LoadMission_Response =
  omnifleet_interfaces::srv::LoadMission_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace omnifleet_interfaces

namespace omnifleet_interfaces
{

namespace srv
{

struct LoadMission
{
  using Request = omnifleet_interfaces::srv::LoadMission_Request;
  using Response = omnifleet_interfaces::srv::LoadMission_Response;
};

}  // namespace srv

}  // namespace omnifleet_interfaces

#endif  // OMNIFLEET_INTERFACES__SRV__DETAIL__LOAD_MISSION__STRUCT_HPP_
