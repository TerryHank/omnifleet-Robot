// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from omnifleet_interfaces:srv/Capability.idl
// generated code does not contain a copyright notice
#include "omnifleet_interfaces/srv/detail/capability__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "omnifleet_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "omnifleet_interfaces/srv/detail/capability__struct.h"
#include "omnifleet_interfaces/srv/detail/capability__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "rosidl_runtime_c/string.h"  // capability
#include "rosidl_runtime_c/string_functions.h"  // capability

// forward declare type support functions


using _Capability_Request__ros_msg_type = omnifleet_interfaces__srv__Capability_Request;

static bool _Capability_Request__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _Capability_Request__ros_msg_type * ros_message = static_cast<const _Capability_Request__ros_msg_type *>(untyped_ros_message);
  // Field name: capability
  {
    const rosidl_runtime_c__String * str = &ros_message->capability;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  return true;
}

static bool _Capability_Request__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _Capability_Request__ros_msg_type * ros_message = static_cast<_Capability_Request__ros_msg_type *>(untyped_ros_message);
  // Field name: capability
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->capability.data) {
      rosidl_runtime_c__String__init(&ros_message->capability);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->capability,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'capability'\n");
      return false;
    }
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_omnifleet_interfaces
size_t get_serialized_size_omnifleet_interfaces__srv__Capability_Request(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Capability_Request__ros_msg_type * ros_message = static_cast<const _Capability_Request__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name capability
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->capability.size + 1);

  return current_alignment - initial_alignment;
}

static uint32_t _Capability_Request__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_omnifleet_interfaces__srv__Capability_Request(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_omnifleet_interfaces
size_t max_serialized_size_omnifleet_interfaces__srv__Capability_Request(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // member: capability
  {
    size_t array_size = 1;

    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = omnifleet_interfaces__srv__Capability_Request;
    is_plain =
      (
      offsetof(DataType, capability) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _Capability_Request__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_omnifleet_interfaces__srv__Capability_Request(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_Capability_Request = {
  "omnifleet_interfaces::srv",
  "Capability_Request",
  _Capability_Request__cdr_serialize,
  _Capability_Request__cdr_deserialize,
  _Capability_Request__get_serialized_size,
  _Capability_Request__max_serialized_size
};

static rosidl_message_type_support_t _Capability_Request__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_Capability_Request,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, omnifleet_interfaces, srv, Capability_Request)() {
  return &_Capability_Request__type_support;
}

#if defined(__cplusplus)
}
#endif

// already included above
// #include <cassert>
// already included above
// #include <limits>
// already included above
// #include <string>
// already included above
// #include "rosidl_typesupport_fastrtps_c/identifier.h"
// already included above
// #include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
// already included above
// #include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
// already included above
// #include "omnifleet_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
// already included above
// #include "omnifleet_interfaces/srv/detail/capability__struct.h"
// already included above
// #include "omnifleet_interfaces/srv/detail/capability__functions.h"
// already included above
// #include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

// already included above
// #include "rosidl_runtime_c/string.h"  // message, transaction_id
// already included above
// #include "rosidl_runtime_c/string_functions.h"  // message, transaction_id

// forward declare type support functions


using _Capability_Response__ros_msg_type = omnifleet_interfaces__srv__Capability_Response;

static bool _Capability_Response__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _Capability_Response__ros_msg_type * ros_message = static_cast<const _Capability_Response__ros_msg_type *>(untyped_ros_message);
  // Field name: available
  {
    cdr << (ros_message->available ? true : false);
  }

  // Field name: accepted
  {
    cdr << (ros_message->accepted ? true : false);
  }

  // Field name: transaction_id
  {
    const rosidl_runtime_c__String * str = &ros_message->transaction_id;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: message
  {
    const rosidl_runtime_c__String * str = &ros_message->message;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  return true;
}

static bool _Capability_Response__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _Capability_Response__ros_msg_type * ros_message = static_cast<_Capability_Response__ros_msg_type *>(untyped_ros_message);
  // Field name: available
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->available = tmp ? true : false;
  }

  // Field name: accepted
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->accepted = tmp ? true : false;
  }

  // Field name: transaction_id
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->transaction_id.data) {
      rosidl_runtime_c__String__init(&ros_message->transaction_id);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->transaction_id,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'transaction_id'\n");
      return false;
    }
  }

  // Field name: message
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->message.data) {
      rosidl_runtime_c__String__init(&ros_message->message);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->message,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'message'\n");
      return false;
    }
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_omnifleet_interfaces
size_t get_serialized_size_omnifleet_interfaces__srv__Capability_Response(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _Capability_Response__ros_msg_type * ros_message = static_cast<const _Capability_Response__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name available
  {
    size_t item_size = sizeof(ros_message->available);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name accepted
  {
    size_t item_size = sizeof(ros_message->accepted);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name transaction_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->transaction_id.size + 1);
  // field.name message
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->message.size + 1);

  return current_alignment - initial_alignment;
}

static uint32_t _Capability_Response__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_omnifleet_interfaces__srv__Capability_Response(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_omnifleet_interfaces
size_t max_serialized_size_omnifleet_interfaces__srv__Capability_Response(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // member: available
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: accepted
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: transaction_id
  {
    size_t array_size = 1;

    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // member: message
  {
    size_t array_size = 1;

    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = omnifleet_interfaces__srv__Capability_Response;
    is_plain =
      (
      offsetof(DataType, message) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _Capability_Response__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_omnifleet_interfaces__srv__Capability_Response(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_Capability_Response = {
  "omnifleet_interfaces::srv",
  "Capability_Response",
  _Capability_Response__cdr_serialize,
  _Capability_Response__cdr_deserialize,
  _Capability_Response__get_serialized_size,
  _Capability_Response__max_serialized_size
};

static rosidl_message_type_support_t _Capability_Response__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_Capability_Response,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, omnifleet_interfaces, srv, Capability_Response)() {
  return &_Capability_Response__type_support;
}

#if defined(__cplusplus)
}
#endif

#include "rosidl_typesupport_fastrtps_cpp/service_type_support.h"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_fastrtps_c/identifier.h"
// already included above
// #include "omnifleet_interfaces/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "omnifleet_interfaces/srv/capability.h"

#if defined(__cplusplus)
extern "C"
{
#endif

static service_type_support_callbacks_t Capability__callbacks = {
  "omnifleet_interfaces::srv",
  "Capability",
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, omnifleet_interfaces, srv, Capability_Request)(),
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, omnifleet_interfaces, srv, Capability_Response)(),
};

static rosidl_service_type_support_t Capability__handle = {
  rosidl_typesupport_fastrtps_c__identifier,
  &Capability__callbacks,
  get_service_typesupport_handle_function,
};

const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, omnifleet_interfaces, srv, Capability)() {
  return &Capability__handle;
}

#if defined(__cplusplus)
}
#endif
