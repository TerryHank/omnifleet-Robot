// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from omnifleet_navigation_interfaces:action/ExecuteFormation.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "omnifleet_navigation_interfaces/action/detail/execute_formation__rosidl_typesupport_introspection_c.h"
#include "omnifleet_navigation_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "omnifleet_navigation_interfaces/action/detail/execute_formation__functions.h"
#include "omnifleet_navigation_interfaces/action/detail/execute_formation__struct.h"


// Include directives for member types
// Member `task_id`
// Member `command_epoch`
#include "rosidl_runtime_c/string_functions.h"
// Member `waypoints`
#include "omnifleet_navigation_interfaces/msg/navigation_point.h"
// Member `waypoints`
#include "omnifleet_navigation_interfaces/msg/detail/navigation_point__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__ExecuteFormation_Goal_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__init(message_memory);
}

void omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__ExecuteFormation_Goal_fini_function(void * message_memory)
{
  omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__fini(message_memory);
}

size_t omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__size_function__ExecuteFormation_Goal__waypoints(
  const void * untyped_member)
{
  const omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * member =
    (const omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence *)(untyped_member);
  return member->size;
}

const void * omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__get_const_function__ExecuteFormation_Goal__waypoints(
  const void * untyped_member, size_t index)
{
  const omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * member =
    (const omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence *)(untyped_member);
  return &member->data[index];
}

void * omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__get_function__ExecuteFormation_Goal__waypoints(
  void * untyped_member, size_t index)
{
  omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * member =
    (omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence *)(untyped_member);
  return &member->data[index];
}

void omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__fetch_function__ExecuteFormation_Goal__waypoints(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const omnifleet_navigation_interfaces__msg__NavigationPoint * item =
    ((const omnifleet_navigation_interfaces__msg__NavigationPoint *)
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__get_const_function__ExecuteFormation_Goal__waypoints(untyped_member, index));
  omnifleet_navigation_interfaces__msg__NavigationPoint * value =
    (omnifleet_navigation_interfaces__msg__NavigationPoint *)(untyped_value);
  *value = *item;
}

void omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__assign_function__ExecuteFormation_Goal__waypoints(
  void * untyped_member, size_t index, const void * untyped_value)
{
  omnifleet_navigation_interfaces__msg__NavigationPoint * item =
    ((omnifleet_navigation_interfaces__msg__NavigationPoint *)
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__get_function__ExecuteFormation_Goal__waypoints(untyped_member, index));
  const omnifleet_navigation_interfaces__msg__NavigationPoint * value =
    (const omnifleet_navigation_interfaces__msg__NavigationPoint *)(untyped_value);
  *item = *value;
}

bool omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__resize_function__ExecuteFormation_Goal__waypoints(
  void * untyped_member, size_t size)
{
  omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence * member =
    (omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence *)(untyped_member);
  omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__fini(member);
  return omnifleet_navigation_interfaces__msg__NavigationPoint__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__ExecuteFormation_Goal_message_member_array[5] = {
  {
    "task_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal, task_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "command_epoch",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal, command_epoch),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "revision",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT64,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal, revision),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "waypoints",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal, waypoints),  // bytes offset in struct
    NULL,  // default value
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__size_function__ExecuteFormation_Goal__waypoints,  // size() function pointer
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__get_const_function__ExecuteFormation_Goal__waypoints,  // get_const(index) function pointer
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__get_function__ExecuteFormation_Goal__waypoints,  // get(index) function pointer
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__fetch_function__ExecuteFormation_Goal__waypoints,  // fetch(index, &value) function pointer
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__assign_function__ExecuteFormation_Goal__waypoints,  // assign(index, value) function pointer
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__resize_function__ExecuteFormation_Goal__waypoints  // resize(index) function pointer
  },
  {
    "pass_radius",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal, pass_radius),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__ExecuteFormation_Goal_message_members = {
  "omnifleet_navigation_interfaces__action",  // message namespace
  "ExecuteFormation_Goal",  // message name
  5,  // number of fields
  sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Goal),
  omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__ExecuteFormation_Goal_message_member_array,  // message members
  omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__ExecuteFormation_Goal_init_function,  // function to initialize message memory (memory has to be allocated)
  omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__ExecuteFormation_Goal_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__ExecuteFormation_Goal_message_type_support_handle = {
  0,
  &omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__ExecuteFormation_Goal_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_omnifleet_navigation_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_Goal)() {
  omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__ExecuteFormation_Goal_message_member_array[3].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, msg, NavigationPoint)();
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__ExecuteFormation_Goal_message_type_support_handle.typesupport_identifier) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__ExecuteFormation_Goal_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &omnifleet_navigation_interfaces__action__ExecuteFormation_Goal__rosidl_typesupport_introspection_c__ExecuteFormation_Goal_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__rosidl_typesupport_introspection_c.h"
// already included above
// #include "omnifleet_navigation_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__functions.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__struct.h"


// Include directives for member types
// Member `code`
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void omnifleet_navigation_interfaces__action__ExecuteFormation_Result__rosidl_typesupport_introspection_c__ExecuteFormation_Result_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  omnifleet_navigation_interfaces__action__ExecuteFormation_Result__init(message_memory);
}

void omnifleet_navigation_interfaces__action__ExecuteFormation_Result__rosidl_typesupport_introspection_c__ExecuteFormation_Result_fini_function(void * message_memory)
{
  omnifleet_navigation_interfaces__action__ExecuteFormation_Result__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember omnifleet_navigation_interfaces__action__ExecuteFormation_Result__rosidl_typesupport_introspection_c__ExecuteFormation_Result_message_member_array[3] = {
  {
    "success",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_Result, success),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "code",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_Result, code),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "message",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_Result, message),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers omnifleet_navigation_interfaces__action__ExecuteFormation_Result__rosidl_typesupport_introspection_c__ExecuteFormation_Result_message_members = {
  "omnifleet_navigation_interfaces__action",  // message namespace
  "ExecuteFormation_Result",  // message name
  3,  // number of fields
  sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Result),
  omnifleet_navigation_interfaces__action__ExecuteFormation_Result__rosidl_typesupport_introspection_c__ExecuteFormation_Result_message_member_array,  // message members
  omnifleet_navigation_interfaces__action__ExecuteFormation_Result__rosidl_typesupport_introspection_c__ExecuteFormation_Result_init_function,  // function to initialize message memory (memory has to be allocated)
  omnifleet_navigation_interfaces__action__ExecuteFormation_Result__rosidl_typesupport_introspection_c__ExecuteFormation_Result_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t omnifleet_navigation_interfaces__action__ExecuteFormation_Result__rosidl_typesupport_introspection_c__ExecuteFormation_Result_message_type_support_handle = {
  0,
  &omnifleet_navigation_interfaces__action__ExecuteFormation_Result__rosidl_typesupport_introspection_c__ExecuteFormation_Result_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_omnifleet_navigation_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_Result)() {
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Result__rosidl_typesupport_introspection_c__ExecuteFormation_Result_message_type_support_handle.typesupport_identifier) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Result__rosidl_typesupport_introspection_c__ExecuteFormation_Result_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &omnifleet_navigation_interfaces__action__ExecuteFormation_Result__rosidl_typesupport_introspection_c__ExecuteFormation_Result_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__rosidl_typesupport_introspection_c.h"
// already included above
// #include "omnifleet_navigation_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__functions.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__struct.h"


// Include directives for member types
// Member `task_id`
// Member `phase`
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__rosidl_typesupport_introspection_c__ExecuteFormation_Feedback_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__init(message_memory);
}

void omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__rosidl_typesupport_introspection_c__ExecuteFormation_Feedback_fini_function(void * message_memory)
{
  omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__rosidl_typesupport_introspection_c__ExecuteFormation_Feedback_message_member_array[5] = {
  {
    "task_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback, task_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "phase",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback, phase),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "message",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback, message),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "passed_points",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback, passed_points),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "tf_age_ms",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback, tf_age_ms),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__rosidl_typesupport_introspection_c__ExecuteFormation_Feedback_message_members = {
  "omnifleet_navigation_interfaces__action",  // message namespace
  "ExecuteFormation_Feedback",  // message name
  5,  // number of fields
  sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback),
  omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__rosidl_typesupport_introspection_c__ExecuteFormation_Feedback_message_member_array,  // message members
  omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__rosidl_typesupport_introspection_c__ExecuteFormation_Feedback_init_function,  // function to initialize message memory (memory has to be allocated)
  omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__rosidl_typesupport_introspection_c__ExecuteFormation_Feedback_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__rosidl_typesupport_introspection_c__ExecuteFormation_Feedback_message_type_support_handle = {
  0,
  &omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__rosidl_typesupport_introspection_c__ExecuteFormation_Feedback_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_omnifleet_navigation_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_Feedback)() {
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__rosidl_typesupport_introspection_c__ExecuteFormation_Feedback_message_type_support_handle.typesupport_identifier) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__rosidl_typesupport_introspection_c__ExecuteFormation_Feedback_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &omnifleet_navigation_interfaces__action__ExecuteFormation_Feedback__rosidl_typesupport_introspection_c__ExecuteFormation_Feedback_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__rosidl_typesupport_introspection_c.h"
// already included above
// #include "omnifleet_navigation_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__functions.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__struct.h"


// Include directives for member types
// Member `goal_id`
#include "unique_identifier_msgs/msg/uuid.h"
// Member `goal_id`
#include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"
// Member `goal`
#include "omnifleet_navigation_interfaces/action/execute_formation.h"
// Member `goal`
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__init(message_memory);
}

void omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_fini_function(void * message_memory)
{
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_message_member_array[2] = {
  {
    "goal_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request, goal_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "goal",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request, goal),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_message_members = {
  "omnifleet_navigation_interfaces__action",  // message namespace
  "ExecuteFormation_SendGoal_Request",  // message name
  2,  // number of fields
  sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request),
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_message_member_array,  // message members
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_message_type_support_handle = {
  0,
  &omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_omnifleet_navigation_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_SendGoal_Request)() {
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_Goal)();
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_message_type_support_handle.typesupport_identifier) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Request__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__rosidl_typesupport_introspection_c.h"
// already included above
// #include "omnifleet_navigation_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__functions.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__struct.h"


// Include directives for member types
// Member `stamp`
#include "builtin_interfaces/msg/time.h"
// Member `stamp`
#include "builtin_interfaces/msg/detail/time__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__init(message_memory);
}

void omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Response_fini_function(void * message_memory)
{
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Response_message_member_array[2] = {
  {
    "accepted",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response, accepted),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "stamp",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response, stamp),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Response_message_members = {
  "omnifleet_navigation_interfaces__action",  // message namespace
  "ExecuteFormation_SendGoal_Response",  // message name
  2,  // number of fields
  sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response),
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Response_message_member_array,  // message members
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Response_message_type_support_handle = {
  0,
  &omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_omnifleet_navigation_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_SendGoal_Response)() {
  omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Response_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Time)();
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Response_message_type_support_handle.typesupport_identifier) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &omnifleet_navigation_interfaces__action__ExecuteFormation_SendGoal_Response__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "omnifleet_navigation_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_service_members = {
  "omnifleet_navigation_interfaces__action",  // service namespace
  "ExecuteFormation_SendGoal",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Request_message_type_support_handle,
  NULL  // response message
  // omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_Response_message_type_support_handle
};

static rosidl_service_type_support_t omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_service_type_support_handle = {
  0,
  &omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_SendGoal_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_SendGoal_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_omnifleet_navigation_interfaces
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_SendGoal)() {
  if (!omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_service_type_support_handle.typesupport_identifier) {
    omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_SendGoal_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_SendGoal_Response)()->data;
  }

  return &omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_SendGoal_service_type_support_handle;
}

// already included above
// #include <stddef.h>
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__rosidl_typesupport_introspection_c.h"
// already included above
// #include "omnifleet_navigation_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__functions.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__struct.h"


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/uuid.h"
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__init(message_memory);
}

void omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Request_fini_function(void * message_memory)
{
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Request_message_member_array[1] = {
  {
    "goal_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request, goal_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Request_message_members = {
  "omnifleet_navigation_interfaces__action",  // message namespace
  "ExecuteFormation_GetResult_Request",  // message name
  1,  // number of fields
  sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request),
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Request_message_member_array,  // message members
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Request_message_type_support_handle = {
  0,
  &omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_omnifleet_navigation_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_GetResult_Request)() {
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Request_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Request_message_type_support_handle.typesupport_identifier) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Request__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__rosidl_typesupport_introspection_c.h"
// already included above
// #include "omnifleet_navigation_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__functions.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__struct.h"


// Include directives for member types
// Member `result`
// already included above
// #include "omnifleet_navigation_interfaces/action/execute_formation.h"
// Member `result`
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__init(message_memory);
}

void omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Response_fini_function(void * message_memory)
{
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Response_message_member_array[2] = {
  {
    "status",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response, status),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "result",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response, result),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Response_message_members = {
  "omnifleet_navigation_interfaces__action",  // message namespace
  "ExecuteFormation_GetResult_Response",  // message name
  2,  // number of fields
  sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response),
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Response_message_member_array,  // message members
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Response_message_type_support_handle = {
  0,
  &omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_omnifleet_navigation_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_GetResult_Response)() {
  omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Response_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_Result)();
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Response_message_type_support_handle.typesupport_identifier) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &omnifleet_navigation_interfaces__action__ExecuteFormation_GetResult_Response__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "omnifleet_navigation_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_service_members = {
  "omnifleet_navigation_interfaces__action",  // service namespace
  "ExecuteFormation_GetResult",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Request_message_type_support_handle,
  NULL  // response message
  // omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_Response_message_type_support_handle
};

static rosidl_service_type_support_t omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_service_type_support_handle = {
  0,
  &omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_GetResult_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_GetResult_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_omnifleet_navigation_interfaces
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_GetResult)() {
  if (!omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_service_type_support_handle.typesupport_identifier) {
    omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_GetResult_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_GetResult_Response)()->data;
  }

  return &omnifleet_navigation_interfaces__action__detail__execute_formation__rosidl_typesupport_introspection_c__ExecuteFormation_GetResult_service_type_support_handle;
}

// already included above
// #include <stddef.h>
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__rosidl_typesupport_introspection_c.h"
// already included above
// #include "omnifleet_navigation_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__functions.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__struct.h"


// Include directives for member types
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/uuid.h"
// Member `goal_id`
// already included above
// #include "unique_identifier_msgs/msg/detail/uuid__rosidl_typesupport_introspection_c.h"
// Member `feedback`
// already included above
// #include "omnifleet_navigation_interfaces/action/execute_formation.h"
// Member `feedback`
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_formation__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__rosidl_typesupport_introspection_c__ExecuteFormation_FeedbackMessage_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__init(message_memory);
}

void omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__rosidl_typesupport_introspection_c__ExecuteFormation_FeedbackMessage_fini_function(void * message_memory)
{
  omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__rosidl_typesupport_introspection_c__ExecuteFormation_FeedbackMessage_message_member_array[2] = {
  {
    "goal_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage, goal_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "feedback",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage, feedback),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__rosidl_typesupport_introspection_c__ExecuteFormation_FeedbackMessage_message_members = {
  "omnifleet_navigation_interfaces__action",  // message namespace
  "ExecuteFormation_FeedbackMessage",  // message name
  2,  // number of fields
  sizeof(omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage),
  omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__rosidl_typesupport_introspection_c__ExecuteFormation_FeedbackMessage_message_member_array,  // message members
  omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__rosidl_typesupport_introspection_c__ExecuteFormation_FeedbackMessage_init_function,  // function to initialize message memory (memory has to be allocated)
  omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__rosidl_typesupport_introspection_c__ExecuteFormation_FeedbackMessage_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__rosidl_typesupport_introspection_c__ExecuteFormation_FeedbackMessage_message_type_support_handle = {
  0,
  &omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__rosidl_typesupport_introspection_c__ExecuteFormation_FeedbackMessage_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_omnifleet_navigation_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_FeedbackMessage)() {
  omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__rosidl_typesupport_introspection_c__ExecuteFormation_FeedbackMessage_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, unique_identifier_msgs, msg, UUID)();
  omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__rosidl_typesupport_introspection_c__ExecuteFormation_FeedbackMessage_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, action, ExecuteFormation_Feedback)();
  if (!omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__rosidl_typesupport_introspection_c__ExecuteFormation_FeedbackMessage_message_type_support_handle.typesupport_identifier) {
    omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__rosidl_typesupport_introspection_c__ExecuteFormation_FeedbackMessage_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &omnifleet_navigation_interfaces__action__ExecuteFormation_FeedbackMessage__rosidl_typesupport_introspection_c__ExecuteFormation_FeedbackMessage_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
