// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from omnifleet_interfaces:srv/StoreMission.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "omnifleet_interfaces/srv/detail/store_mission__rosidl_typesupport_introspection_c.h"
#include "omnifleet_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "omnifleet_interfaces/srv/detail/store_mission__functions.h"
#include "omnifleet_interfaces/srv/detail/store_mission__struct.h"


// Include directives for member types
// Member `mission_id`
#include "rosidl_runtime_c/string_functions.h"
// Member `poses`
#include "geometry_msgs/msg/pose.h"
// Member `poses`
#include "geometry_msgs/msg/detail/pose__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__StoreMission_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  omnifleet_interfaces__srv__StoreMission_Request__init(message_memory);
}

void omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__StoreMission_Request_fini_function(void * message_memory)
{
  omnifleet_interfaces__srv__StoreMission_Request__fini(message_memory);
}

size_t omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__size_function__StoreMission_Request__poses(
  const void * untyped_member)
{
  const geometry_msgs__msg__Pose__Sequence * member =
    (const geometry_msgs__msg__Pose__Sequence *)(untyped_member);
  return member->size;
}

const void * omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__get_const_function__StoreMission_Request__poses(
  const void * untyped_member, size_t index)
{
  const geometry_msgs__msg__Pose__Sequence * member =
    (const geometry_msgs__msg__Pose__Sequence *)(untyped_member);
  return &member->data[index];
}

void * omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__get_function__StoreMission_Request__poses(
  void * untyped_member, size_t index)
{
  geometry_msgs__msg__Pose__Sequence * member =
    (geometry_msgs__msg__Pose__Sequence *)(untyped_member);
  return &member->data[index];
}

void omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__fetch_function__StoreMission_Request__poses(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const geometry_msgs__msg__Pose * item =
    ((const geometry_msgs__msg__Pose *)
    omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__get_const_function__StoreMission_Request__poses(untyped_member, index));
  geometry_msgs__msg__Pose * value =
    (geometry_msgs__msg__Pose *)(untyped_value);
  *value = *item;
}

void omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__assign_function__StoreMission_Request__poses(
  void * untyped_member, size_t index, const void * untyped_value)
{
  geometry_msgs__msg__Pose * item =
    ((geometry_msgs__msg__Pose *)
    omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__get_function__StoreMission_Request__poses(untyped_member, index));
  const geometry_msgs__msg__Pose * value =
    (const geometry_msgs__msg__Pose *)(untyped_value);
  *item = *value;
}

bool omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__resize_function__StoreMission_Request__poses(
  void * untyped_member, size_t size)
{
  geometry_msgs__msg__Pose__Sequence * member =
    (geometry_msgs__msg__Pose__Sequence *)(untyped_member);
  geometry_msgs__msg__Pose__Sequence__fini(member);
  return geometry_msgs__msg__Pose__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__StoreMission_Request_message_member_array[3] = {
  {
    "mission_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_interfaces__srv__StoreMission_Request, mission_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "poses",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_interfaces__srv__StoreMission_Request, poses),  // bytes offset in struct
    NULL,  // default value
    omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__size_function__StoreMission_Request__poses,  // size() function pointer
    omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__get_const_function__StoreMission_Request__poses,  // get_const(index) function pointer
    omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__get_function__StoreMission_Request__poses,  // get(index) function pointer
    omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__fetch_function__StoreMission_Request__poses,  // fetch(index, &value) function pointer
    omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__assign_function__StoreMission_Request__poses,  // assign(index, value) function pointer
    omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__resize_function__StoreMission_Request__poses  // resize(index) function pointer
  },
  {
    "loop",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_interfaces__srv__StoreMission_Request, loop),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__StoreMission_Request_message_members = {
  "omnifleet_interfaces__srv",  // message namespace
  "StoreMission_Request",  // message name
  3,  // number of fields
  sizeof(omnifleet_interfaces__srv__StoreMission_Request),
  omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__StoreMission_Request_message_member_array,  // message members
  omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__StoreMission_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__StoreMission_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__StoreMission_Request_message_type_support_handle = {
  0,
  &omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__StoreMission_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_omnifleet_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_interfaces, srv, StoreMission_Request)() {
  omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__StoreMission_Request_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Pose)();
  if (!omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__StoreMission_Request_message_type_support_handle.typesupport_identifier) {
    omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__StoreMission_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &omnifleet_interfaces__srv__StoreMission_Request__rosidl_typesupport_introspection_c__StoreMission_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "omnifleet_interfaces/srv/detail/store_mission__rosidl_typesupport_introspection_c.h"
// already included above
// #include "omnifleet_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "omnifleet_interfaces/srv/detail/store_mission__functions.h"
// already included above
// #include "omnifleet_interfaces/srv/detail/store_mission__struct.h"


// Include directives for member types
// Member `map_id`
// Member `map_sha256`
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void omnifleet_interfaces__srv__StoreMission_Response__rosidl_typesupport_introspection_c__StoreMission_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  omnifleet_interfaces__srv__StoreMission_Response__init(message_memory);
}

void omnifleet_interfaces__srv__StoreMission_Response__rosidl_typesupport_introspection_c__StoreMission_Response_fini_function(void * message_memory)
{
  omnifleet_interfaces__srv__StoreMission_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember omnifleet_interfaces__srv__StoreMission_Response__rosidl_typesupport_introspection_c__StoreMission_Response_message_member_array[5] = {
  {
    "accepted",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_interfaces__srv__StoreMission_Response, accepted),  // bytes offset in struct
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
    offsetof(omnifleet_interfaces__srv__StoreMission_Response, revision),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "map_id",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_interfaces__srv__StoreMission_Response, map_id),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "map_sha256",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(omnifleet_interfaces__srv__StoreMission_Response, map_sha256),  // bytes offset in struct
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
    offsetof(omnifleet_interfaces__srv__StoreMission_Response, message),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers omnifleet_interfaces__srv__StoreMission_Response__rosidl_typesupport_introspection_c__StoreMission_Response_message_members = {
  "omnifleet_interfaces__srv",  // message namespace
  "StoreMission_Response",  // message name
  5,  // number of fields
  sizeof(omnifleet_interfaces__srv__StoreMission_Response),
  omnifleet_interfaces__srv__StoreMission_Response__rosidl_typesupport_introspection_c__StoreMission_Response_message_member_array,  // message members
  omnifleet_interfaces__srv__StoreMission_Response__rosidl_typesupport_introspection_c__StoreMission_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  omnifleet_interfaces__srv__StoreMission_Response__rosidl_typesupport_introspection_c__StoreMission_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t omnifleet_interfaces__srv__StoreMission_Response__rosidl_typesupport_introspection_c__StoreMission_Response_message_type_support_handle = {
  0,
  &omnifleet_interfaces__srv__StoreMission_Response__rosidl_typesupport_introspection_c__StoreMission_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_omnifleet_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_interfaces, srv, StoreMission_Response)() {
  if (!omnifleet_interfaces__srv__StoreMission_Response__rosidl_typesupport_introspection_c__StoreMission_Response_message_type_support_handle.typesupport_identifier) {
    omnifleet_interfaces__srv__StoreMission_Response__rosidl_typesupport_introspection_c__StoreMission_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &omnifleet_interfaces__srv__StoreMission_Response__rosidl_typesupport_introspection_c__StoreMission_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "omnifleet_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "omnifleet_interfaces/srv/detail/store_mission__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers omnifleet_interfaces__srv__detail__store_mission__rosidl_typesupport_introspection_c__StoreMission_service_members = {
  "omnifleet_interfaces__srv",  // service namespace
  "StoreMission",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // omnifleet_interfaces__srv__detail__store_mission__rosidl_typesupport_introspection_c__StoreMission_Request_message_type_support_handle,
  NULL  // response message
  // omnifleet_interfaces__srv__detail__store_mission__rosidl_typesupport_introspection_c__StoreMission_Response_message_type_support_handle
};

static rosidl_service_type_support_t omnifleet_interfaces__srv__detail__store_mission__rosidl_typesupport_introspection_c__StoreMission_service_type_support_handle = {
  0,
  &omnifleet_interfaces__srv__detail__store_mission__rosidl_typesupport_introspection_c__StoreMission_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_interfaces, srv, StoreMission_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_interfaces, srv, StoreMission_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_omnifleet_interfaces
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_interfaces, srv, StoreMission)() {
  if (!omnifleet_interfaces__srv__detail__store_mission__rosidl_typesupport_introspection_c__StoreMission_service_type_support_handle.typesupport_identifier) {
    omnifleet_interfaces__srv__detail__store_mission__rosidl_typesupport_introspection_c__StoreMission_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)omnifleet_interfaces__srv__detail__store_mission__rosidl_typesupport_introspection_c__StoreMission_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_interfaces, srv, StoreMission_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, omnifleet_interfaces, srv, StoreMission_Response)()->data;
  }

  return &omnifleet_interfaces__srv__detail__store_mission__rosidl_typesupport_introspection_c__StoreMission_service_type_support_handle;
}
