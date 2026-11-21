// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from mola_msgs:srv/RelocalizeNearPose.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "mola_msgs/srv/detail/relocalize_near_pose__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace mola_msgs
{

namespace srv
{

namespace rosidl_typesupport_introspection_cpp
{

void RelocalizeNearPose_Request_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) mola_msgs::srv::RelocalizeNearPose_Request(_init);
}

void RelocalizeNearPose_Request_fini_function(void * message_memory)
{
  auto typed_message = static_cast<mola_msgs::srv::RelocalizeNearPose_Request *>(message_memory);
  typed_message->~RelocalizeNearPose_Request();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember RelocalizeNearPose_Request_message_member_array[1] = {
  {
    "pose",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<geometry_msgs::msg::PoseWithCovarianceStamped>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(mola_msgs::srv::RelocalizeNearPose_Request, pose),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers RelocalizeNearPose_Request_message_members = {
  "mola_msgs::srv",  // message namespace
  "RelocalizeNearPose_Request",  // message name
  1,  // number of fields
  sizeof(mola_msgs::srv::RelocalizeNearPose_Request),
  RelocalizeNearPose_Request_message_member_array,  // message members
  RelocalizeNearPose_Request_init_function,  // function to initialize message memory (memory has to be allocated)
  RelocalizeNearPose_Request_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t RelocalizeNearPose_Request_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &RelocalizeNearPose_Request_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace srv

}  // namespace mola_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<mola_msgs::srv::RelocalizeNearPose_Request>()
{
  return &::mola_msgs::srv::rosidl_typesupport_introspection_cpp::RelocalizeNearPose_Request_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, mola_msgs, srv, RelocalizeNearPose_Request)() {
  return &::mola_msgs::srv::rosidl_typesupport_introspection_cpp::RelocalizeNearPose_Request_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "array"
// already included above
// #include "cstddef"
// already included above
// #include "string"
// already included above
// #include "vector"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "mola_msgs/srv/detail/relocalize_near_pose__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/field_types.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace mola_msgs
{

namespace srv
{

namespace rosidl_typesupport_introspection_cpp
{

void RelocalizeNearPose_Response_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) mola_msgs::srv::RelocalizeNearPose_Response(_init);
}

void RelocalizeNearPose_Response_fini_function(void * message_memory)
{
  auto typed_message = static_cast<mola_msgs::srv::RelocalizeNearPose_Response *>(message_memory);
  typed_message->~RelocalizeNearPose_Response();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember RelocalizeNearPose_Response_message_member_array[1] = {
  {
    "accepted",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(mola_msgs::srv::RelocalizeNearPose_Response, accepted),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers RelocalizeNearPose_Response_message_members = {
  "mola_msgs::srv",  // message namespace
  "RelocalizeNearPose_Response",  // message name
  1,  // number of fields
  sizeof(mola_msgs::srv::RelocalizeNearPose_Response),
  RelocalizeNearPose_Response_message_member_array,  // message members
  RelocalizeNearPose_Response_init_function,  // function to initialize message memory (memory has to be allocated)
  RelocalizeNearPose_Response_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t RelocalizeNearPose_Response_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &RelocalizeNearPose_Response_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace srv

}  // namespace mola_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<mola_msgs::srv::RelocalizeNearPose_Response>()
{
  return &::mola_msgs::srv::rosidl_typesupport_introspection_cpp::RelocalizeNearPose_Response_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, mola_msgs, srv, RelocalizeNearPose_Response)() {
  return &::mola_msgs::srv::rosidl_typesupport_introspection_cpp::RelocalizeNearPose_Response_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_interface/macros.h"
// already included above
// #include "rosidl_typesupport_introspection_cpp/visibility_control.h"
// already included above
// #include "mola_msgs/srv/detail/relocalize_near_pose__struct.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/service_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/service_type_support_decl.hpp"

namespace mola_msgs
{

namespace srv
{

namespace rosidl_typesupport_introspection_cpp
{

// this is intentionally not const to allow initialization later to prevent an initialization race
static ::rosidl_typesupport_introspection_cpp::ServiceMembers RelocalizeNearPose_service_members = {
  "mola_msgs::srv",  // service namespace
  "RelocalizeNearPose",  // service name
  // these two fields are initialized below on the first access
  // see get_service_type_support_handle<mola_msgs::srv::RelocalizeNearPose>()
  nullptr,  // request message
  nullptr  // response message
};

static const rosidl_service_type_support_t RelocalizeNearPose_service_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &RelocalizeNearPose_service_members,
  get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace srv

}  // namespace mola_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_service_type_support_t *
get_service_type_support_handle<mola_msgs::srv::RelocalizeNearPose>()
{
  // get a handle to the value to be returned
  auto service_type_support =
    &::mola_msgs::srv::rosidl_typesupport_introspection_cpp::RelocalizeNearPose_service_type_support_handle;
  // get a non-const and properly typed version of the data void *
  auto service_members = const_cast<::rosidl_typesupport_introspection_cpp::ServiceMembers *>(
    static_cast<const ::rosidl_typesupport_introspection_cpp::ServiceMembers *>(
      service_type_support->data));
  // make sure that both the request_members_ and the response_members_ are initialized
  // if they are not, initialize them
  if (
    service_members->request_members_ == nullptr ||
    service_members->response_members_ == nullptr)
  {
    // initialize the request_members_ with the static function from the external library
    service_members->request_members_ = static_cast<
      const ::rosidl_typesupport_introspection_cpp::MessageMembers *
      >(
      ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<
        ::mola_msgs::srv::RelocalizeNearPose_Request
      >()->data
      );
    // initialize the response_members_ with the static function from the external library
    service_members->response_members_ = static_cast<
      const ::rosidl_typesupport_introspection_cpp::MessageMembers *
      >(
      ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<
        ::mola_msgs::srv::RelocalizeNearPose_Response
      >()->data
      );
  }
  // finally return the properly initialized service_type_support handle
  return service_type_support;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, mola_msgs, srv, RelocalizeNearPose)() {
  return ::rosidl_typesupport_introspection_cpp::get_service_type_support_handle<mola_msgs::srv::RelocalizeNearPose>();
}

#ifdef __cplusplus
}
#endif
