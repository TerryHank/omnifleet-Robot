// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from omnifleet_navigation_interfaces:action/ExecuteFormation.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_FORMATION__TRAITS_HPP_
#define OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_FORMATION__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "omnifleet_navigation_interfaces/action/detail/execute_formation__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'waypoints'
#include "omnifleet_navigation_interfaces/msg/detail/navigation_point__traits.hpp"

namespace omnifleet_navigation_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const ExecuteFormation_Goal & msg,
  std::ostream & out)
{
  out << "{";
  // member: task_id
  {
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
    out << ", ";
  }

  // member: command_epoch
  {
    out << "command_epoch: ";
    rosidl_generator_traits::value_to_yaml(msg.command_epoch, out);
    out << ", ";
  }

  // member: revision
  {
    out << "revision: ";
    rosidl_generator_traits::value_to_yaml(msg.revision, out);
    out << ", ";
  }

  // member: waypoints
  {
    if (msg.waypoints.size() == 0) {
      out << "waypoints: []";
    } else {
      out << "waypoints: [";
      size_t pending_items = msg.waypoints.size();
      for (auto item : msg.waypoints) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: pass_radius
  {
    out << "pass_radius: ";
    rosidl_generator_traits::value_to_yaml(msg.pass_radius, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ExecuteFormation_Goal & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: task_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
    out << "\n";
  }

  // member: command_epoch
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "command_epoch: ";
    rosidl_generator_traits::value_to_yaml(msg.command_epoch, out);
    out << "\n";
  }

  // member: revision
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "revision: ";
    rosidl_generator_traits::value_to_yaml(msg.revision, out);
    out << "\n";
  }

  // member: waypoints
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.waypoints.size() == 0) {
      out << "waypoints: []\n";
    } else {
      out << "waypoints:\n";
      for (auto item : msg.waypoints) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: pass_radius
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pass_radius: ";
    rosidl_generator_traits::value_to_yaml(msg.pass_radius, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ExecuteFormation_Goal & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_navigation_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_navigation_interfaces::action::ExecuteFormation_Goal & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_navigation_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_navigation_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_navigation_interfaces::action::ExecuteFormation_Goal & msg)
{
  return omnifleet_navigation_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal>()
{
  return "omnifleet_navigation_interfaces::action::ExecuteFormation_Goal";
}

template<>
inline const char * name<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal>()
{
  return "omnifleet_navigation_interfaces/action/ExecuteFormation_Goal";
}

template<>
struct has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace omnifleet_navigation_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const ExecuteFormation_Result & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: code
  {
    out << "code: ";
    rosidl_generator_traits::value_to_yaml(msg.code, out);
    out << ", ";
  }

  // member: message
  {
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ExecuteFormation_Result & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }

  // member: code
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "code: ";
    rosidl_generator_traits::value_to_yaml(msg.code, out);
    out << "\n";
  }

  // member: message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ExecuteFormation_Result & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_navigation_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_navigation_interfaces::action::ExecuteFormation_Result & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_navigation_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_navigation_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_navigation_interfaces::action::ExecuteFormation_Result & msg)
{
  return omnifleet_navigation_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_navigation_interfaces::action::ExecuteFormation_Result>()
{
  return "omnifleet_navigation_interfaces::action::ExecuteFormation_Result";
}

template<>
inline const char * name<omnifleet_navigation_interfaces::action::ExecuteFormation_Result>()
{
  return "omnifleet_navigation_interfaces/action/ExecuteFormation_Result";
}

template<>
struct has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_Result>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_Result>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<omnifleet_navigation_interfaces::action::ExecuteFormation_Result>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace omnifleet_navigation_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const ExecuteFormation_Feedback & msg,
  std::ostream & out)
{
  out << "{";
  // member: task_id
  {
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
    out << ", ";
  }

  // member: phase
  {
    out << "phase: ";
    rosidl_generator_traits::value_to_yaml(msg.phase, out);
    out << ", ";
  }

  // member: message
  {
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << ", ";
  }

  // member: passed_points
  {
    out << "passed_points: ";
    rosidl_generator_traits::value_to_yaml(msg.passed_points, out);
    out << ", ";
  }

  // member: tf_age_ms
  {
    out << "tf_age_ms: ";
    rosidl_generator_traits::value_to_yaml(msg.tf_age_ms, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ExecuteFormation_Feedback & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: task_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "task_id: ";
    rosidl_generator_traits::value_to_yaml(msg.task_id, out);
    out << "\n";
  }

  // member: phase
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "phase: ";
    rosidl_generator_traits::value_to_yaml(msg.phase, out);
    out << "\n";
  }

  // member: message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << "\n";
  }

  // member: passed_points
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "passed_points: ";
    rosidl_generator_traits::value_to_yaml(msg.passed_points, out);
    out << "\n";
  }

  // member: tf_age_ms
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "tf_age_ms: ";
    rosidl_generator_traits::value_to_yaml(msg.tf_age_ms, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ExecuteFormation_Feedback & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_navigation_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_navigation_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_navigation_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback & msg)
{
  return omnifleet_navigation_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback>()
{
  return "omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback";
}

template<>
inline const char * name<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback>()
{
  return "omnifleet_navigation_interfaces/action/ExecuteFormation_Feedback";
}

template<>
struct has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"
// Member 'goal'
#include "omnifleet_navigation_interfaces/action/detail/execute_formation__traits.hpp"

namespace omnifleet_navigation_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const ExecuteFormation_SendGoal_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: goal_id
  {
    out << "goal_id: ";
    to_flow_style_yaml(msg.goal_id, out);
    out << ", ";
  }

  // member: goal
  {
    out << "goal: ";
    to_flow_style_yaml(msg.goal, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ExecuteFormation_SendGoal_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: goal_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal_id:\n";
    to_block_style_yaml(msg.goal_id, out, indentation + 2);
  }

  // member: goal
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal:\n";
    to_block_style_yaml(msg.goal, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ExecuteFormation_SendGoal_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_navigation_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_navigation_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_navigation_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request & msg)
{
  return omnifleet_navigation_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request>()
{
  return "omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request";
}

template<>
inline const char * name<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request>()
{
  return "omnifleet_navigation_interfaces/action/ExecuteFormation_SendGoal_Request";
}

template<>
struct has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request>
  : std::integral_constant<bool, has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal>::value && has_fixed_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request>
  : std::integral_constant<bool, has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal>::value && has_bounded_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct is_message<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace omnifleet_navigation_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const ExecuteFormation_SendGoal_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: accepted
  {
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
    out << ", ";
  }

  // member: stamp
  {
    out << "stamp: ";
    to_flow_style_yaml(msg.stamp, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ExecuteFormation_SendGoal_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: accepted
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
    out << "\n";
  }

  // member: stamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stamp:\n";
    to_block_style_yaml(msg.stamp, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ExecuteFormation_SendGoal_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_navigation_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_navigation_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_navigation_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response & msg)
{
  return omnifleet_navigation_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response>()
{
  return "omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response";
}

template<>
inline const char * name<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response>()
{
  return "omnifleet_navigation_interfaces/action/ExecuteFormation_SendGoal_Response";
}

template<>
struct has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response>
  : std::integral_constant<bool, has_fixed_size<builtin_interfaces::msg::Time>::value> {};

template<>
struct has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response>
  : std::integral_constant<bool, has_bounded_size<builtin_interfaces::msg::Time>::value> {};

template<>
struct is_message<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal>()
{
  return "omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal";
}

template<>
inline const char * name<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal>()
{
  return "omnifleet_navigation_interfaces/action/ExecuteFormation_SendGoal";
}

template<>
struct has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal>
  : std::integral_constant<
    bool,
    has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request>::value &&
    has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response>::value
  >
{
};

template<>
struct has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal>
  : std::integral_constant<
    bool,
    has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request>::value &&
    has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response>::value
  >
{
};

template<>
struct is_service<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal>
  : std::true_type
{
};

template<>
struct is_service_request<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Request>
  : std::true_type
{
};

template<>
struct is_service_response<omnifleet_navigation_interfaces::action::ExecuteFormation_SendGoal_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"

namespace omnifleet_navigation_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const ExecuteFormation_GetResult_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: goal_id
  {
    out << "goal_id: ";
    to_flow_style_yaml(msg.goal_id, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ExecuteFormation_GetResult_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: goal_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal_id:\n";
    to_block_style_yaml(msg.goal_id, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ExecuteFormation_GetResult_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_navigation_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_navigation_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_navigation_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request & msg)
{
  return omnifleet_navigation_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request>()
{
  return "omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request";
}

template<>
inline const char * name<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request>()
{
  return "omnifleet_navigation_interfaces/action/ExecuteFormation_GetResult_Request";
}

template<>
struct has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request>
  : std::integral_constant<bool, has_fixed_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request>
  : std::integral_constant<bool, has_bounded_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct is_message<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'result'
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__traits.hpp"

namespace omnifleet_navigation_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const ExecuteFormation_GetResult_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: status
  {
    out << "status: ";
    rosidl_generator_traits::value_to_yaml(msg.status, out);
    out << ", ";
  }

  // member: result
  {
    out << "result: ";
    to_flow_style_yaml(msg.result, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ExecuteFormation_GetResult_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: status
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "status: ";
    rosidl_generator_traits::value_to_yaml(msg.status, out);
    out << "\n";
  }

  // member: result
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "result:\n";
    to_block_style_yaml(msg.result, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ExecuteFormation_GetResult_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_navigation_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_navigation_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_navigation_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response & msg)
{
  return omnifleet_navigation_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response>()
{
  return "omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response";
}

template<>
inline const char * name<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response>()
{
  return "omnifleet_navigation_interfaces/action/ExecuteFormation_GetResult_Response";
}

template<>
struct has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response>
  : std::integral_constant<bool, has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_Result>::value> {};

template<>
struct has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response>
  : std::integral_constant<bool, has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_Result>::value> {};

template<>
struct is_message<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult>()
{
  return "omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult";
}

template<>
inline const char * name<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult>()
{
  return "omnifleet_navigation_interfaces/action/ExecuteFormation_GetResult";
}

template<>
struct has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult>
  : std::integral_constant<
    bool,
    has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request>::value &&
    has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response>::value
  >
{
};

template<>
struct has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult>
  : std::integral_constant<
    bool,
    has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request>::value &&
    has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response>::value
  >
{
};

template<>
struct is_service<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult>
  : std::true_type
{
};

template<>
struct is_service_request<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Request>
  : std::true_type
{
};

template<>
struct is_service_response<omnifleet_navigation_interfaces::action::ExecuteFormation_GetResult_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__traits.hpp"
// Member 'feedback'
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__traits.hpp"

namespace omnifleet_navigation_interfaces
{

namespace action
{

inline void to_flow_style_yaml(
  const ExecuteFormation_FeedbackMessage & msg,
  std::ostream & out)
{
  out << "{";
  // member: goal_id
  {
    out << "goal_id: ";
    to_flow_style_yaml(msg.goal_id, out);
    out << ", ";
  }

  // member: feedback
  {
    out << "feedback: ";
    to_flow_style_yaml(msg.feedback, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ExecuteFormation_FeedbackMessage & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: goal_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "goal_id:\n";
    to_block_style_yaml(msg.goal_id, out, indentation + 2);
  }

  // member: feedback
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "feedback:\n";
    to_block_style_yaml(msg.feedback, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ExecuteFormation_FeedbackMessage & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_navigation_interfaces::action::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_navigation_interfaces::action::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_navigation_interfaces::action::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage & msg)
{
  return omnifleet_navigation_interfaces::action::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage>()
{
  return "omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage";
}

template<>
inline const char * name<omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage>()
{
  return "omnifleet_navigation_interfaces/action/ExecuteFormation_FeedbackMessage";
}

template<>
struct has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage>
  : std::integral_constant<bool, has_fixed_size<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback>::value && has_fixed_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage>
  : std::integral_constant<bool, has_bounded_size<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback>::value && has_bounded_size<unique_identifier_msgs::msg::UUID>::value> {};

template<>
struct is_message<omnifleet_navigation_interfaces::action::ExecuteFormation_FeedbackMessage>
  : std::true_type {};

}  // namespace rosidl_generator_traits


namespace rosidl_generator_traits
{

template<>
struct is_action<omnifleet_navigation_interfaces::action::ExecuteFormation>
  : std::true_type
{
};

template<>
struct is_action_goal<omnifleet_navigation_interfaces::action::ExecuteFormation_Goal>
  : std::true_type
{
};

template<>
struct is_action_result<omnifleet_navigation_interfaces::action::ExecuteFormation_Result>
  : std::true_type
{
};

template<>
struct is_action_feedback<omnifleet_navigation_interfaces::action::ExecuteFormation_Feedback>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits


#endif  // OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_FORMATION__TRAITS_HPP_
