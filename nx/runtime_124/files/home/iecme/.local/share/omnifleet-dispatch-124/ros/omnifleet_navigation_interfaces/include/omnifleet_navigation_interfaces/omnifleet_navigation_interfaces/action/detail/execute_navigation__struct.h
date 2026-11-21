// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from omnifleet_navigation_interfaces:action/ExecuteNavigation.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_NAVIGATION__STRUCT_H_
#define OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_NAVIGATION__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'LOCAL'.
enum
{
  omnifleet_navigation_interfaces__action__ExecuteNavigation_Goal__LOCAL = 0
};

/// Constant 'FLEET'.
enum
{
  omnifleet_navigation_interfaces__action__ExecuteNavigation_Goal__FLEET = 1
};

// Include directives for member types
// Member 'task_id'
// Member 'command_epoch'
#include "rosidl_runtime_c/string.h"
// Member 'waypoints'
#include "omnifleet_navigation_interfaces/msg/detail/navigation_point__struct.h"

/// Struct defined in action/ExecuteNavigation in the package omnifleet_navigation_interfaces.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_Goal
{
  rosidl_runtime_c__String task_id;
  rosidl_runtime_c__String command_epoch;
  uint64_t revision;
  uint8_t source;
  bool single_point;
  bool follow_trail;
  omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence waypoints;
  float pass_radius;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_Goal;

// Struct for a sequence of omnifleet_navigation_interfaces__action__ExecuteNavigation_Goal.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_Goal__Sequence
{
  omnifleet_navigation_interfaces__action__ExecuteNavigation_Goal * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_Goal__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'code'
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in action/ExecuteNavigation in the package omnifleet_navigation_interfaces.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_Result
{
  bool success;
  rosidl_runtime_c__String code;
  rosidl_runtime_c__String message;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_Result;

// Struct for a sequence of omnifleet_navigation_interfaces__action__ExecuteNavigation_Result.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_Result__Sequence
{
  omnifleet_navigation_interfaces__action__ExecuteNavigation_Result * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_Result__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'task_id'
// Member 'phase'
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in action/ExecuteNavigation in the package omnifleet_navigation_interfaces.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_Feedback
{
  rosidl_runtime_c__String task_id;
  rosidl_runtime_c__String phase;
  rosidl_runtime_c__String message;
  uint32_t passed_points;
  float tf_age_ms;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_Feedback;

// Struct for a sequence of omnifleet_navigation_interfaces__action__ExecuteNavigation_Feedback.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_Feedback__Sequence
{
  omnifleet_navigation_interfaces__action__ExecuteNavigation_Feedback * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_Feedback__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
#include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'goal'
#include "omnifleet_navigation_interfaces/action/detail/execute_navigation__struct.h"

/// Struct defined in action/ExecuteNavigation in the package omnifleet_navigation_interfaces.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_SendGoal_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
  omnifleet_navigation_interfaces__action__ExecuteNavigation_Goal goal;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_SendGoal_Request;

// Struct for a sequence of omnifleet_navigation_interfaces__action__ExecuteNavigation_SendGoal_Request.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_SendGoal_Request__Sequence
{
  omnifleet_navigation_interfaces__action__ExecuteNavigation_SendGoal_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_SendGoal_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in action/ExecuteNavigation in the package omnifleet_navigation_interfaces.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_SendGoal_Response
{
  bool accepted;
  builtin_interfaces__msg__Time stamp;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_SendGoal_Response;

// Struct for a sequence of omnifleet_navigation_interfaces__action__ExecuteNavigation_SendGoal_Response.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_SendGoal_Response__Sequence
{
  omnifleet_navigation_interfaces__action__ExecuteNavigation_SendGoal_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_SendGoal_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"

/// Struct defined in action/ExecuteNavigation in the package omnifleet_navigation_interfaces.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_GetResult_Request
{
  unique_identifier_msgs__msg__UUID goal_id;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_GetResult_Request;

// Struct for a sequence of omnifleet_navigation_interfaces__action__ExecuteNavigation_GetResult_Request.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_GetResult_Request__Sequence
{
  omnifleet_navigation_interfaces__action__ExecuteNavigation_GetResult_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_GetResult_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'result'
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_navigation__struct.h"

/// Struct defined in action/ExecuteNavigation in the package omnifleet_navigation_interfaces.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_GetResult_Response
{
  int8_t status;
  omnifleet_navigation_interfaces__action__ExecuteNavigation_Result result;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_GetResult_Response;

// Struct for a sequence of omnifleet_navigation_interfaces__action__ExecuteNavigation_GetResult_Response.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_GetResult_Response__Sequence
{
  omnifleet_navigation_interfaces__action__ExecuteNavigation_GetResult_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_GetResult_Response__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'goal_id'
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__struct.h"
// Member 'feedback'
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_navigation__struct.h"

/// Struct defined in action/ExecuteNavigation in the package omnifleet_navigation_interfaces.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_FeedbackMessage
{
  unique_identifier_msgs__msg__UUID goal_id;
  omnifleet_navigation_interfaces__action__ExecuteNavigation_Feedback feedback;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_FeedbackMessage;

// Struct for a sequence of omnifleet_navigation_interfaces__action__ExecuteNavigation_FeedbackMessage.
typedef struct omnifleet_navigation_interfaces__action__ExecuteNavigation_FeedbackMessage__Sequence
{
  omnifleet_navigation_interfaces__action__ExecuteNavigation_FeedbackMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} omnifleet_navigation_interfaces__action__ExecuteNavigation_FeedbackMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // OMNIFLEET_NAVIGATION_INTERFACES__ACTION__DETAIL__EXECUTE_NAVIGATION__STRUCT_H_
