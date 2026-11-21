// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from omnifleet_navigation_interfaces:action/ExecuteFormation.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_FORMATION__STRUCT_HPP_
#define OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_FORMATION__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'waypoints'
#include "omnifleet_navigation_interfaces/msg/detail/navigation_point__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_Goal __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_Goal __declspec(deprecated)
#endif

namespace omnifleet_navigation_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct ExecuteFormation_Goal_
{
  using Type = ExecuteFormation_Goal_<ContainerAllocator>;

  explicit ExecuteFormation_Goal_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::DEFAULTS_ONLY == _init)
    {
      this->pass_radius = 0.25f;
    } else if (rosidl_runtime_cpp::MessageInitialization::ZERO == _init) {
      this->task_id = "";
      this->command_epoch = "";
      this->revision = 0ull;
      this->pass_radius = 0.0f;
    }
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->task_id = "";
      this->command_epoch = "";
      this->revision = 0ull;
    }
  }

  explicit ExecuteFormation_Goal_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : task_id(_alloc),
    command_epoch(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::DEFAULTS_ONLY == _init)
    {
      this->pass_radius = 0.25f;
    } else if (rosidl_runtime_cpp::MessageInitialization::ZERO == _init) {
      this->task_id = "";
      this->command_epoch = "";
      this->revision = 0ull;
      this->pass_radius = 0.0f;
    }
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->task_id = "";
      this->command_epoch = "";
      this->revision = 0ull;
    }
  }

  // field types and members
  using _task_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _task_id_type task_id;
  using _command_epoch_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _command_epoch_type command_epoch;
  using _revision_type =
    uint64_t;
  _revision_type revision;
  using _waypoints_type =
    std::vector<omnifleet_navigation_interfaces::msg::NavigationPoint_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<omnifleet_navigation_interfaces::msg::NavigationPoint_<ContainerAllocator>>>;
  _waypoints_type waypoints;
  using _pass_radius_type =
    float;
  _pass_radius_type pass_radius;

  // setters for named parameter idiom
  Type & set__task_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->task_id = _arg;
    return *this;
  }
  Type & set__command_epoch(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->command_epoch = _arg;
    return *this;
  }
  Type & set__revision(
    const uint64_t & _arg)
  {
    this->revision = _arg;
    return *this;
  }
  Type & set__waypoints(
    const std::vector<omnifleet_navigation_interfaces::msg::NavigationPoint_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<omnifleet_navigation_interfaces::msg::NavigationPoint_<ContainerAllocator>>> & _arg)
  {
    this->waypoints = _arg;
    return *this;
  }
  Type & set__pass_radius(
    const float & _arg)
  {
    this->pass_radius = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_Goal
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_Goal
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ExecuteFormation_Goal_ & other) const
  {
    if (this->task_id != other.task_id) {
      return false;
    }
    if (this->command_epoch != other.command_epoch) {
      return false;
    }
    if (this->revision != other.revision) {
      return false;
    }
    if (this->waypoints != other.waypoints) {
      return false;
    }
    if (this->pass_radius != other.pass_radius) {
      return false;
    }
    return true;
  }
  bool operator!=(const ExecuteFormation_Goal_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ExecuteFormation_Goal_

// alias to use template instance with default allocator
using ExecuteFormation_Goal =
  omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace omnifleet_navigation_interfaces


#ifndef _WIN32
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_Result __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_Result __declspec(deprecated)
#endif

namespace omnifleet_navigation_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct ExecuteFormation_Result_
{
  using Type = ExecuteFormation_Result_<ContainerAllocator>;

  explicit ExecuteFormation_Result_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->code = "";
      this->message = "";
    }
  }

  explicit ExecuteFormation_Result_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : code(_alloc),
    message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->code = "";
      this->message = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _code_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _code_type code;
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
  Type & set__code(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->code = _arg;
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
    omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_Result
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_Result
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ExecuteFormation_Result_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->code != other.code) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const ExecuteFormation_Result_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ExecuteFormation_Result_

// alias to use template instance with default allocator
using ExecuteFormation_Result =
  omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace omnifleet_navigation_interfaces


#ifndef _WIN32
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback __declspec(deprecated)
#endif

namespace omnifleet_navigation_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct ExecuteFormation_Feedback_
{
  using Type = ExecuteFormation_Feedback_<ContainerAllocator>;

  explicit ExecuteFormation_Feedback_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->task_id = "";
      this->phase = "";
      this->message = "";
      this->passed_points = 0ul;
      this->tf_age_ms = 0.0f;
    }
  }

  explicit ExecuteFormation_Feedback_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : task_id(_alloc),
    phase(_alloc),
    message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->task_id = "";
      this->phase = "";
      this->message = "";
      this->passed_points = 0ul;
      this->tf_age_ms = 0.0f;
    }
  }

  // field types and members
  using _task_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _task_id_type task_id;
  using _phase_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _phase_type phase;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;
  using _passed_points_type =
    uint32_t;
  _passed_points_type passed_points;
  using _tf_age_ms_type =
    float;
  _tf_age_ms_type tf_age_ms;

  // setters for named parameter idiom
  Type & set__task_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->task_id = _arg;
    return *this;
  }
  Type & set__phase(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->phase = _arg;
    return *this;
  }
  Type & set__message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->message = _arg;
    return *this;
  }
  Type & set__passed_points(
    const uint32_t & _arg)
  {
    this->passed_points = _arg;
    return *this;
  }
  Type & set__tf_age_ms(
    const float & _arg)
  {
    this->tf_age_ms = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ExecuteFormation_Feedback_ & other) const
  {
    if (this->task_id != other.task_id) {
      return false;
    }
    if (this->phase != other.phase) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    if (this->passed_points != other.passed_points) {
      return false;
    }
    if (this->tf_age_ms != other.tf_age_ms) {
      return false;
    }
    return true;
  }
  bool operator!=(const ExecuteFormation_Feedback_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ExecuteFormation_Feedback_

// alias to use template instance with default allocator
using ExecuteFormation_Feedback =
  omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace omnifleet_navigation_interfaces


// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"
// Member 'goal'
#include "omnifleet_navigation_interfaces/action/detail/execute_formation__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request __declspec(deprecated)
#endif

namespace omnifleet_navigation_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct ExecuteFormation_SendGoal_Request_
{
  using Type = ExecuteFormation_SendGoal_Request_<ContainerAllocator>;

  explicit ExecuteFormation_SendGoal_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_init),
    goal(_init)
  {
    (void)_init;
  }

  explicit ExecuteFormation_SendGoal_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_alloc, _init),
    goal(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _goal_id_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _goal_id_type goal_id;
  using _goal_type =
    omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<ContainerAllocator>;
  _goal_type goal;

  // setters for named parameter idiom
  Type & set__goal_id(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->goal_id = _arg;
    return *this;
  }
  Type & set__goal(
    const omnifleet_navigation_interfaces::action::ExecuteFormation_Goal_<ContainerAllocator> & _arg)
  {
    this->goal = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ExecuteFormation_SendGoal_Request_ & other) const
  {
    if (this->goal_id != other.goal_id) {
      return false;
    }
    if (this->goal != other.goal) {
      return false;
    }
    return true;
  }
  bool operator!=(const ExecuteFormation_SendGoal_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ExecuteFormation_SendGoal_Request_

// alias to use template instance with default allocator
using ExecuteFormation_SendGoal_Request =
  omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace omnifleet_navigation_interfaces


// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response __declspec(deprecated)
#endif

namespace omnifleet_navigation_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct ExecuteFormation_SendGoal_Response_
{
  using Type = ExecuteFormation_SendGoal_Response_<ContainerAllocator>;

  explicit ExecuteFormation_SendGoal_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->accepted = false;
    }
  }

  explicit ExecuteFormation_SendGoal_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stamp(_alloc, _init)
  {
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
  using _stamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _stamp_type stamp;

  // setters for named parameter idiom
  Type & set__accepted(
    const bool & _arg)
  {
    this->accepted = _arg;
    return *this;
  }
  Type & set__stamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->stamp = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ExecuteFormation_SendGoal_Response_ & other) const
  {
    if (this->accepted != other.accepted) {
      return false;
    }
    if (this->stamp != other.stamp) {
      return false;
    }
    return true;
  }
  bool operator!=(const ExecuteFormation_SendGoal_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ExecuteFormation_SendGoal_Response_

// alias to use template instance with default allocator
using ExecuteFormation_SendGoal_Response =
  omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace omnifleet_navigation_interfaces
{

namespace action
{

struct ExecuteFormation_SendGoal
{
  using Request = omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request;
  using Response = omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response;
};

}  // namespace action

}  // namespace omnifleet_navigation_interfaces


// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request __declspec(deprecated)
#endif

namespace omnifleet_navigation_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct ExecuteFormation_GetResult_Request_
{
  using Type = ExecuteFormation_GetResult_Request_<ContainerAllocator>;

  explicit ExecuteFormation_GetResult_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_init)
  {
    (void)_init;
  }

  explicit ExecuteFormation_GetResult_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _goal_id_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _goal_id_type goal_id;

  // setters for named parameter idiom
  Type & set__goal_id(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->goal_id = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ExecuteFormation_GetResult_Request_ & other) const
  {
    if (this->goal_id != other.goal_id) {
      return false;
    }
    return true;
  }
  bool operator!=(const ExecuteFormation_GetResult_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ExecuteFormation_GetResult_Request_

// alias to use template instance with default allocator
using ExecuteFormation_GetResult_Request =
  omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace omnifleet_navigation_interfaces


// Include directives for member types
// Member 'result'
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response __declspec(deprecated)
#endif

namespace omnifleet_navigation_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct ExecuteFormation_GetResult_Response_
{
  using Type = ExecuteFormation_GetResult_Response_<ContainerAllocator>;

  explicit ExecuteFormation_GetResult_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : result(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->status = 0;
    }
  }

  explicit ExecuteFormation_GetResult_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : result(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->status = 0;
    }
  }

  // field types and members
  using _status_type =
    int8_t;
  _status_type status;
  using _result_type =
    omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<ContainerAllocator>;
  _result_type result;

  // setters for named parameter idiom
  Type & set__status(
    const int8_t & _arg)
  {
    this->status = _arg;
    return *this;
  }
  Type & set__result(
    const omnifleet_navigation_interfaces::action::ExecuteFormation_Result_<ContainerAllocator> & _arg)
  {
    this->result = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ExecuteFormation_GetResult_Response_ & other) const
  {
    if (this->status != other.status) {
      return false;
    }
    if (this->result != other.result) {
      return false;
    }
    return true;
  }
  bool operator!=(const ExecuteFormation_GetResult_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ExecuteFormation_GetResult_Response_

// alias to use template instance with default allocator
using ExecuteFormation_GetResult_Response =
  omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace omnifleet_navigation_interfaces
{

namespace action
{

struct ExecuteFormation_GetResult
{
  using Request = omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request;
  using Response = omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response;
};

}  // namespace action

}  // namespace omnifleet_navigation_interfaces


// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.hpp"
// Member 'feedback'
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage __attribute__((deprecated))
#else
# define DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage __declspec(deprecated)
#endif

namespace omnifleet_navigation_interfaces
{

namespace action
{

// message struct
template<class ContainerAllocator>
struct ExecuteFormation_FeedbackMessage_
{
  using Type = ExecuteFormation_FeedbackMessage_<ContainerAllocator>;

  explicit ExecuteFormation_FeedbackMessage_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_init),
    feedback(_init)
  {
    (void)_init;
  }

  explicit ExecuteFormation_FeedbackMessage_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : goal_id(_alloc, _init),
    feedback(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _goal_id_type =
    unique_identifier_msgs::msg::UUID_<ContainerAllocator>;
  _goal_id_type goal_id;
  using _feedback_type =
    omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<ContainerAllocator>;
  _feedback_type feedback;

  // setters for named parameter idiom
  Type & set__goal_id(
    const unique_identifier_msgs::msg::UUID_<ContainerAllocator> & _arg)
  {
    this->goal_id = _arg;
    return *this;
  }
  Type & set__feedback(
    const omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback_<ContainerAllocator> & _arg)
  {
    this->feedback = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage_<ContainerAllocator> *;
  using ConstRawPtr =
    const omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage
    std::shared_ptr<omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const ExecuteFormation_FeedbackMessage_ & other) const
  {
    if (this->goal_id != other.goal_id) {
      return false;
    }
    if (this->feedback != other.feedback) {
      return false;
    }
    return true;
  }
  bool operator!=(const ExecuteFormation_FeedbackMessage_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct ExecuteFormation_FeedbackMessage_

// alias to use template instance with default allocator
using ExecuteFormation_FeedbackMessage =
  omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage_<std::allocator<void>>;

// constant definitions

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

#include "action_msgs/srv/cancel_goal.hpp"
#include "action_msgs/msg/goal_info.hpp"
#include "action_msgs/msg/goal_status_array.hpp"

namespace omnifleet_navigation_interfaces
{

namespace action
{

struct ExecuteFormation
{
  /// The goal message defined in the action definition.
  using Goal = omnifleet_navigation_interfaces::action::ExecuteFormation_Goal;
  /// The result message defined in the action definition.
  using Result = omnifleet_navigation_interfaces::action::ExecuteFormation_Result;
  /// The feedback message defined in the action definition.
  using Feedback = omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback;

  struct Impl
  {
    /// The send_goal service using a wrapped version of the goal message as a request.
    using SendGoalService = omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal;
    /// The get_result service using a wrapped version of the result message as a response.
    using GetResultService = omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult;
    /// The feedback message with generic fields which wraps the feedback message.
    using FeedbackMessage = omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage;

    /// The generic service to cancel a goal.
    using CancelGoalService = action_msgs::srv::CancelGoal;
    /// The generic message for the status of a goal.
    using GoalStatusMessage = action_msgs::msg::GoalStatusArray;
  };
};

typedef struct ExecuteFormation ExecuteFormation;

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

#endif  // OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_FORMATION__STRUCT_HPP_
