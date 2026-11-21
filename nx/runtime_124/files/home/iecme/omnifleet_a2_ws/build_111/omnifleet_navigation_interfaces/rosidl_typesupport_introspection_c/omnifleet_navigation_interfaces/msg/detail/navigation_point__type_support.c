// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from omnifleet_navigation_interfaces:msg/NavigationPoint.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "omnifleet_navigation_interfaces/msg/detail/navigation_point__rosidl_typesupport_introspection_c.h"
#include "omnifleet_navigation_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "omnifleet_navigation_interfaces/msg/detail/navigation_point__functions.h"
#include "omnifleet_navigation_interfaces/msg/detail/navigation_point__struct.h"


// Include directives for member types
// Member `name`
#include "rosidl_runtime_c/string_functions.h"
// Member `pose`
#include "geometry_msgs/msg/pose_stamped.h"
// Member `pose`
#include "geometry_msgs/msg/detail/pose_stamped__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void omnifleet_navigation_interfaces__msg__NavigationPoint__rosidl_typesupport_introspection_c__NavigationPoint_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  omnifleet_navigation_interfaces__msg__NavigationPoint__init(message_memory);
}

void omnifleet_navigation_interfaces__msg__NavigationPoint__rosidl_typesupport_introspection_c__NavigationPoint_fini_function(void * message_memory)
{
  omnifleet_navigation_interfaces__msg__NavigationPoint__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember omnifleet_navigation_interfaces__msg__NavigationPoint__rosidl_typesupport_introspection_c__NavigationPoint_message_member_array[4] = {
  {
    "name",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__msg__NavigationPoint, name),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "pose",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__msg__NavigationPoint, pose),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "kind",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__msg__NavigationPoint, kind),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "dwell_seconds",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_navigation_interfaces__msg__NavigationPoint, dwell_seconds),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers omnifleet_navigation_interfaces__msg__NavigationPoint__rosidl_typesupport_introspection_c__NavigationPoint_message_members = {
  "omnifleet_navigation_interfaces__msg",  // message namespace
  "NavigationPoint",  // message name
  4,  // number of fields
  sizeof(omnifleet_navigation_interfaces__msg__NavigationPoint),
  omnifleet_navigation_interfaces__msg__NavigationPoint__rosidl_typesupport_introspection_c__NavigationPoint_message_member_array,  // message members
  omnifleet_navigation_interfaces__msg__NavigationPoint__rosidl_typesupport_introspection_c__NavigationPoint_init_function,  // function to initialize message memory (memory has to be allocated)
  omnifleet_navigation_interfaces__msg__NavigationPoint__rosidl_typesupport_introspection_c__NavigationPoint_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t omnifleet_navigation_interfaces__msg__NavigationPoint__rosidl_typesupport_introspection_c__NavigationPoint_message_type_support_handle = {
  0,
  &omnifleet_navigation_interfaces__msg__NavigationPoint__rosidl_typesupport_introspection_c__NavigationPoint_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_omnifleet_navigation_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_navigation_interfaces, msg, NavigationPoint)() {
  omnifleet_navigation_interfaces__msg__NavigationPoint__rosidl_typesupport_introspection_c__NavigationPoint_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, PoseStamped)();
  if (!omnifleet_navigation_interfaces__msg__NavigationPoint__rosidl_typesupport_introspection_c__NavigationPoint_message_type_support_handle.typesupport_identifier) {
    omnifleet_navigation_interfaces__msg__NavigationPoint__rosidl_typesupport_introspection_c__NavigationPoint_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &omnifleet_navigation_interfaces__msg__NavigationPoint__rosidl_typesupport_introspection_c__NavigationPoint_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
