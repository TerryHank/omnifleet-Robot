// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from mola_msgs:srv/MolaRuntimeParamSet.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "mola_msgs/srv/detail/mola_runtime_param_set__rosidl_typesupport_introspection_c.h"
#include "mola_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "mola_msgs/srv/detail/mola_runtime_param_set__functions.h"
#include "mola_msgs/srv/detail/mola_runtime_param_set__struct.h"


// Include directives for member types
// Member `parameters`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void mola_msgs__srv__MolaRuntimeParamSet_Request__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Request_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  mola_msgs__srv__MolaRuntimeParamSet_Request__init(message_memory);
}

void mola_msgs__srv__MolaRuntimeParamSet_Request__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Request_fini_function(void * message_memory)
{
  mola_msgs__srv__MolaRuntimeParamSet_Request__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember mola_msgs__srv__MolaRuntimeParamSet_Request__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Request_message_member_array[1] = {
  {
    "parameters",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(mola_msgs__srv__MolaRuntimeParamSet_Request, parameters),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers mola_msgs__srv__MolaRuntimeParamSet_Request__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Request_message_members = {
  "mola_msgs__srv",  // message namespace
  "MolaRuntimeParamSet_Request",  // message name
  1,  // number of fields
  sizeof(mola_msgs__srv__MolaRuntimeParamSet_Request),
  mola_msgs__srv__MolaRuntimeParamSet_Request__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Request_message_member_array,  // message members
  mola_msgs__srv__MolaRuntimeParamSet_Request__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  mola_msgs__srv__MolaRuntimeParamSet_Request__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Request_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t mola_msgs__srv__MolaRuntimeParamSet_Request__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Request_message_type_support_handle = {
  0,
  &mola_msgs__srv__MolaRuntimeParamSet_Request__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Request_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_mola_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, mola_msgs, srv, MolaRuntimeParamSet_Request)() {
  if (!mola_msgs__srv__MolaRuntimeParamSet_Request__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Request_message_type_support_handle.typesupport_identifier) {
    mola_msgs__srv__MolaRuntimeParamSet_Request__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Request_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &mola_msgs__srv__MolaRuntimeParamSet_Request__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Request_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

// already included above
// #include <stddef.h>
// already included above
// #include "mola_msgs/srv/detail/mola_runtime_param_set__rosidl_typesupport_introspection_c.h"
// already included above
// #include "mola_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "rosidl_typesupport_introspection_c/field_types.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
// already included above
// #include "rosidl_typesupport_introspection_c/message_introspection.h"
// already included above
// #include "mola_msgs/srv/detail/mola_runtime_param_set__functions.h"
// already included above
// #include "mola_msgs/srv/detail/mola_runtime_param_set__struct.h"


// Include directives for member types
// Member `error_message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void mola_msgs__srv__MolaRuntimeParamSet_Response__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Response_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  mola_msgs__srv__MolaRuntimeParamSet_Response__init(message_memory);
}

void mola_msgs__srv__MolaRuntimeParamSet_Response__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Response_fini_function(void * message_memory)
{
  mola_msgs__srv__MolaRuntimeParamSet_Response__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember mola_msgs__srv__MolaRuntimeParamSet_Response__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Response_message_member_array[2] = {
  {
    "success",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(mola_msgs__srv__MolaRuntimeParamSet_Response, success),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "error_message",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(mola_msgs__srv__MolaRuntimeParamSet_Response, error_message),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers mola_msgs__srv__MolaRuntimeParamSet_Response__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Response_message_members = {
  "mola_msgs__srv",  // message namespace
  "MolaRuntimeParamSet_Response",  // message name
  2,  // number of fields
  sizeof(mola_msgs__srv__MolaRuntimeParamSet_Response),
  mola_msgs__srv__MolaRuntimeParamSet_Response__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Response_message_member_array,  // message members
  mola_msgs__srv__MolaRuntimeParamSet_Response__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  mola_msgs__srv__MolaRuntimeParamSet_Response__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Response_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t mola_msgs__srv__MolaRuntimeParamSet_Response__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Response_message_type_support_handle = {
  0,
  &mola_msgs__srv__MolaRuntimeParamSet_Response__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Response_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_mola_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, mola_msgs, srv, MolaRuntimeParamSet_Response)() {
  if (!mola_msgs__srv__MolaRuntimeParamSet_Response__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Response_message_type_support_handle.typesupport_identifier) {
    mola_msgs__srv__MolaRuntimeParamSet_Response__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Response_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &mola_msgs__srv__MolaRuntimeParamSet_Response__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Response_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "mola_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
// already included above
// #include "mola_msgs/srv/detail/mola_runtime_param_set__rosidl_typesupport_introspection_c.h"
// already included above
// #include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/service_introspection.h"

// this is intentionally not const to allow initialization later to prevent an initialization race
static rosidl_typesupport_introspection_c__ServiceMembers mola_msgs__srv__detail__mola_runtime_param_set__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_service_members = {
  "mola_msgs__srv",  // service namespace
  "MolaRuntimeParamSet",  // service name
  // these two fields are initialized below on the first access
  NULL,  // request message
  // mola_msgs__srv__detail__mola_runtime_param_set__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Request_message_type_support_handle,
  NULL  // response message
  // mola_msgs__srv__detail__mola_runtime_param_set__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_Response_message_type_support_handle
};

static rosidl_service_type_support_t mola_msgs__srv__detail__mola_runtime_param_set__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_service_type_support_handle = {
  0,
  &mola_msgs__srv__detail__mola_runtime_param_set__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_service_members,
  get_service_typesupport_handle_function,
};

// Forward declaration of request/response type support functions
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, mola_msgs, srv, MolaRuntimeParamSet_Request)();

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, mola_msgs, srv, MolaRuntimeParamSet_Response)();

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_mola_msgs
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_c, mola_msgs, srv, MolaRuntimeParamSet)() {
  if (!mola_msgs__srv__detail__mola_runtime_param_set__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_service_type_support_handle.typesupport_identifier) {
    mola_msgs__srv__detail__mola_runtime_param_set__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_service_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  rosidl_typesupport_introspection_c__ServiceMembers * service_members =
    (rosidl_typesupport_introspection_c__ServiceMembers *)mola_msgs__srv__detail__mola_runtime_param_set__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_service_type_support_handle.data;

  if (!service_members->request_members_) {
    service_members->request_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, mola_msgs, srv, MolaRuntimeParamSet_Request)()->data;
  }
  if (!service_members->response_members_) {
    service_members->response_members_ =
      (const rosidl_typesupport_introspection_c__MessageMembers *)
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, mola_msgs, srv, MolaRuntimeParamSet_Response)()->data;
  }

  return &mola_msgs__srv__detail__mola_runtime_param_set__rosidl_typesupport_introspection_c__MolaRuntimeParamSet_service_type_support_handle;
}
