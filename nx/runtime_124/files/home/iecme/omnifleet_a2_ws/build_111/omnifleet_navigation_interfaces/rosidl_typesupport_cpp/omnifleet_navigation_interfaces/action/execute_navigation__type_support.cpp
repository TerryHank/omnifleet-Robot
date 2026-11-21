// generated from rosidl_typesupport_cpp/resource/idl__type_support.cpp.em
// with input from omnifleet_navigation_interfaces:action/ExecuteNavigation.idl
// generated code does not contain a copyright notice

#include "cstddef"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "omnifleet_navigation_interfaces/action/detail/execute_navigation__struct.hpp"
#include "rosidl_typesupport_cpp/identifier.hpp"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
#include "rosidl_typesupport_cpp/visibility_control.h"
#include "rosidl_typesupport_interface/macros.h"

namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _ExecuteNavigation_Goal_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _ExecuteNavigation_Goal_type_support_ids_t;

static const _ExecuteNavigation_Goal_type_support_ids_t _ExecuteNavigation_Goal_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _ExecuteNavigation_Goal_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _ExecuteNavigation_Goal_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _ExecuteNavigation_Goal_type_support_symbol_names_t _ExecuteNavigation_Goal_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_Goal)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_Goal)),
  }
};

typedef struct _ExecuteNavigation_Goal_type_support_data_t
{
  void * data[2];
} _ExecuteNavigation_Goal_type_support_data_t;

static _ExecuteNavigation_Goal_type_support_data_t _ExecuteNavigation_Goal_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _ExecuteNavigation_Goal_message_typesupport_map = {
  2,
  "omnifleet_navigation_interfaces",
  &_ExecuteNavigation_Goal_message_typesupport_ids.typesupport_identifier[0],
  &_ExecuteNavigation_Goal_message_typesupport_symbol_names.symbol_name[0],
  &_ExecuteNavigation_Goal_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t ExecuteNavigation_Goal_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_ExecuteNavigation_Goal_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_Goal>()
{
  return &::omnifleet_navigation_interfaces::action::rosidl_typesupport_cpp::ExecuteNavigation_Goal_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_Goal)() {
  return get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_Goal>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_navigation__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _ExecuteNavigation_Result_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _ExecuteNavigation_Result_type_support_ids_t;

static const _ExecuteNavigation_Result_type_support_ids_t _ExecuteNavigation_Result_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _ExecuteNavigation_Result_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _ExecuteNavigation_Result_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _ExecuteNavigation_Result_type_support_symbol_names_t _ExecuteNavigation_Result_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_Result)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_Result)),
  }
};

typedef struct _ExecuteNavigation_Result_type_support_data_t
{
  void * data[2];
} _ExecuteNavigation_Result_type_support_data_t;

static _ExecuteNavigation_Result_type_support_data_t _ExecuteNavigation_Result_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _ExecuteNavigation_Result_message_typesupport_map = {
  2,
  "omnifleet_navigation_interfaces",
  &_ExecuteNavigation_Result_message_typesupport_ids.typesupport_identifier[0],
  &_ExecuteNavigation_Result_message_typesupport_symbol_names.symbol_name[0],
  &_ExecuteNavigation_Result_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t ExecuteNavigation_Result_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_ExecuteNavigation_Result_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_Result>()
{
  return &::omnifleet_navigation_interfaces::action::rosidl_typesupport_cpp::ExecuteNavigation_Result_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_Result)() {
  return get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_Result>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_navigation__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _ExecuteNavigation_Feedback_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _ExecuteNavigation_Feedback_type_support_ids_t;

static const _ExecuteNavigation_Feedback_type_support_ids_t _ExecuteNavigation_Feedback_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _ExecuteNavigation_Feedback_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _ExecuteNavigation_Feedback_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _ExecuteNavigation_Feedback_type_support_symbol_names_t _ExecuteNavigation_Feedback_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_Feedback)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_Feedback)),
  }
};

typedef struct _ExecuteNavigation_Feedback_type_support_data_t
{
  void * data[2];
} _ExecuteNavigation_Feedback_type_support_data_t;

static _ExecuteNavigation_Feedback_type_support_data_t _ExecuteNavigation_Feedback_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _ExecuteNavigation_Feedback_message_typesupport_map = {
  2,
  "omnifleet_navigation_interfaces",
  &_ExecuteNavigation_Feedback_message_typesupport_ids.typesupport_identifier[0],
  &_ExecuteNavigation_Feedback_message_typesupport_symbol_names.symbol_name[0],
  &_ExecuteNavigation_Feedback_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t ExecuteNavigation_Feedback_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_ExecuteNavigation_Feedback_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_Feedback>()
{
  return &::omnifleet_navigation_interfaces::action::rosidl_typesupport_cpp::ExecuteNavigation_Feedback_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_Feedback)() {
  return get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_Feedback>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_navigation__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _ExecuteNavigation_SendGoal_Request_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _ExecuteNavigation_SendGoal_Request_type_support_ids_t;

static const _ExecuteNavigation_SendGoal_Request_type_support_ids_t _ExecuteNavigation_SendGoal_Request_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _ExecuteNavigation_SendGoal_Request_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _ExecuteNavigation_SendGoal_Request_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _ExecuteNavigation_SendGoal_Request_type_support_symbol_names_t _ExecuteNavigation_SendGoal_Request_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_SendGoal_Request)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_SendGoal_Request)),
  }
};

typedef struct _ExecuteNavigation_SendGoal_Request_type_support_data_t
{
  void * data[2];
} _ExecuteNavigation_SendGoal_Request_type_support_data_t;

static _ExecuteNavigation_SendGoal_Request_type_support_data_t _ExecuteNavigation_SendGoal_Request_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _ExecuteNavigation_SendGoal_Request_message_typesupport_map = {
  2,
  "omnifleet_navigation_interfaces",
  &_ExecuteNavigation_SendGoal_Request_message_typesupport_ids.typesupport_identifier[0],
  &_ExecuteNavigation_SendGoal_Request_message_typesupport_symbol_names.symbol_name[0],
  &_ExecuteNavigation_SendGoal_Request_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t ExecuteNavigation_SendGoal_Request_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_ExecuteNavigation_SendGoal_Request_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_SendGoal_Request>()
{
  return &::omnifleet_navigation_interfaces::action::rosidl_typesupport_cpp::ExecuteNavigation_SendGoal_Request_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_SendGoal_Request)() {
  return get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_SendGoal_Request>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_navigation__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _ExecuteNavigation_SendGoal_Response_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _ExecuteNavigation_SendGoal_Response_type_support_ids_t;

static const _ExecuteNavigation_SendGoal_Response_type_support_ids_t _ExecuteNavigation_SendGoal_Response_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _ExecuteNavigation_SendGoal_Response_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _ExecuteNavigation_SendGoal_Response_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _ExecuteNavigation_SendGoal_Response_type_support_symbol_names_t _ExecuteNavigation_SendGoal_Response_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_SendGoal_Response)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_SendGoal_Response)),
  }
};

typedef struct _ExecuteNavigation_SendGoal_Response_type_support_data_t
{
  void * data[2];
} _ExecuteNavigation_SendGoal_Response_type_support_data_t;

static _ExecuteNavigation_SendGoal_Response_type_support_data_t _ExecuteNavigation_SendGoal_Response_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _ExecuteNavigation_SendGoal_Response_message_typesupport_map = {
  2,
  "omnifleet_navigation_interfaces",
  &_ExecuteNavigation_SendGoal_Response_message_typesupport_ids.typesupport_identifier[0],
  &_ExecuteNavigation_SendGoal_Response_message_typesupport_symbol_names.symbol_name[0],
  &_ExecuteNavigation_SendGoal_Response_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t ExecuteNavigation_SendGoal_Response_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_ExecuteNavigation_SendGoal_Response_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_SendGoal_Response>()
{
  return &::omnifleet_navigation_interfaces::action::rosidl_typesupport_cpp::ExecuteNavigation_SendGoal_Response_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_SendGoal_Response)() {
  return get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_SendGoal_Response>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
#include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_navigation__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
#include "rosidl_typesupport_cpp/service_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _ExecuteNavigation_SendGoal_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _ExecuteNavigation_SendGoal_type_support_ids_t;

static const _ExecuteNavigation_SendGoal_type_support_ids_t _ExecuteNavigation_SendGoal_service_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _ExecuteNavigation_SendGoal_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _ExecuteNavigation_SendGoal_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _ExecuteNavigation_SendGoal_type_support_symbol_names_t _ExecuteNavigation_SendGoal_service_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_SendGoal)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_SendGoal)),
  }
};

typedef struct _ExecuteNavigation_SendGoal_type_support_data_t
{
  void * data[2];
} _ExecuteNavigation_SendGoal_type_support_data_t;

static _ExecuteNavigation_SendGoal_type_support_data_t _ExecuteNavigation_SendGoal_service_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _ExecuteNavigation_SendGoal_service_typesupport_map = {
  2,
  "omnifleet_navigation_interfaces",
  &_ExecuteNavigation_SendGoal_service_typesupport_ids.typesupport_identifier[0],
  &_ExecuteNavigation_SendGoal_service_typesupport_symbol_names.symbol_name[0],
  &_ExecuteNavigation_SendGoal_service_typesupport_data.data[0],
};

static const rosidl_service_type_support_t ExecuteNavigation_SendGoal_service_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_ExecuteNavigation_SendGoal_service_typesupport_map),
  ::rosidl_typesupport_cpp::get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_service_type_support_t *
get_service_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_SendGoal>()
{
  return &::omnifleet_navigation_interfaces::action::rosidl_typesupport_cpp::ExecuteNavigation_SendGoal_service_type_support_handle;
}

}  // namespace rosidl_typesupport_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_SendGoal)() {
  return ::rosidl_typesupport_cpp::get_service_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_SendGoal>();
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_navigation__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _ExecuteNavigation_GetResult_Request_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _ExecuteNavigation_GetResult_Request_type_support_ids_t;

static const _ExecuteNavigation_GetResult_Request_type_support_ids_t _ExecuteNavigation_GetResult_Request_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _ExecuteNavigation_GetResult_Request_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _ExecuteNavigation_GetResult_Request_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _ExecuteNavigation_GetResult_Request_type_support_symbol_names_t _ExecuteNavigation_GetResult_Request_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_GetResult_Request)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_GetResult_Request)),
  }
};

typedef struct _ExecuteNavigation_GetResult_Request_type_support_data_t
{
  void * data[2];
} _ExecuteNavigation_GetResult_Request_type_support_data_t;

static _ExecuteNavigation_GetResult_Request_type_support_data_t _ExecuteNavigation_GetResult_Request_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _ExecuteNavigation_GetResult_Request_message_typesupport_map = {
  2,
  "omnifleet_navigation_interfaces",
  &_ExecuteNavigation_GetResult_Request_message_typesupport_ids.typesupport_identifier[0],
  &_ExecuteNavigation_GetResult_Request_message_typesupport_symbol_names.symbol_name[0],
  &_ExecuteNavigation_GetResult_Request_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t ExecuteNavigation_GetResult_Request_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_ExecuteNavigation_GetResult_Request_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_GetResult_Request>()
{
  return &::omnifleet_navigation_interfaces::action::rosidl_typesupport_cpp::ExecuteNavigation_GetResult_Request_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_GetResult_Request)() {
  return get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_GetResult_Request>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_navigation__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _ExecuteNavigation_GetResult_Response_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _ExecuteNavigation_GetResult_Response_type_support_ids_t;

static const _ExecuteNavigation_GetResult_Response_type_support_ids_t _ExecuteNavigation_GetResult_Response_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _ExecuteNavigation_GetResult_Response_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _ExecuteNavigation_GetResult_Response_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _ExecuteNavigation_GetResult_Response_type_support_symbol_names_t _ExecuteNavigation_GetResult_Response_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_GetResult_Response)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_GetResult_Response)),
  }
};

typedef struct _ExecuteNavigation_GetResult_Response_type_support_data_t
{
  void * data[2];
} _ExecuteNavigation_GetResult_Response_type_support_data_t;

static _ExecuteNavigation_GetResult_Response_type_support_data_t _ExecuteNavigation_GetResult_Response_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _ExecuteNavigation_GetResult_Response_message_typesupport_map = {
  2,
  "omnifleet_navigation_interfaces",
  &_ExecuteNavigation_GetResult_Response_message_typesupport_ids.typesupport_identifier[0],
  &_ExecuteNavigation_GetResult_Response_message_typesupport_symbol_names.symbol_name[0],
  &_ExecuteNavigation_GetResult_Response_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t ExecuteNavigation_GetResult_Response_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_ExecuteNavigation_GetResult_Response_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_GetResult_Response>()
{
  return &::omnifleet_navigation_interfaces::action::rosidl_typesupport_cpp::ExecuteNavigation_GetResult_Response_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_GetResult_Response)() {
  return get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_GetResult_Response>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/service_type_support_struct.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_navigation__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/service_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _ExecuteNavigation_GetResult_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _ExecuteNavigation_GetResult_type_support_ids_t;

static const _ExecuteNavigation_GetResult_type_support_ids_t _ExecuteNavigation_GetResult_service_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _ExecuteNavigation_GetResult_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _ExecuteNavigation_GetResult_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _ExecuteNavigation_GetResult_type_support_symbol_names_t _ExecuteNavigation_GetResult_service_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_GetResult)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_GetResult)),
  }
};

typedef struct _ExecuteNavigation_GetResult_type_support_data_t
{
  void * data[2];
} _ExecuteNavigation_GetResult_type_support_data_t;

static _ExecuteNavigation_GetResult_type_support_data_t _ExecuteNavigation_GetResult_service_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _ExecuteNavigation_GetResult_service_typesupport_map = {
  2,
  "omnifleet_navigation_interfaces",
  &_ExecuteNavigation_GetResult_service_typesupport_ids.typesupport_identifier[0],
  &_ExecuteNavigation_GetResult_service_typesupport_symbol_names.symbol_name[0],
  &_ExecuteNavigation_GetResult_service_typesupport_data.data[0],
};

static const rosidl_service_type_support_t ExecuteNavigation_GetResult_service_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_ExecuteNavigation_GetResult_service_typesupport_map),
  ::rosidl_typesupport_cpp::get_service_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_service_type_support_t *
get_service_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_GetResult>()
{
  return &::omnifleet_navigation_interfaces::action::rosidl_typesupport_cpp::ExecuteNavigation_GetResult_service_type_support_handle;
}

}  // namespace rosidl_typesupport_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_GetResult)() {
  return ::rosidl_typesupport_cpp::get_service_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_GetResult>();
}

#ifdef __cplusplus
}
#endif

// already included above
// #include "cstddef"
// already included above
// #include "rosidl_runtime_c/message_type_support_struct.h"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_navigation__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/identifier.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_c/type_support_map.h"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support_dispatch.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
// already included above
// #include "rosidl_typesupport_interface/macros.h"

namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace rosidl_typesupport_cpp
{

typedef struct _ExecuteNavigation_FeedbackMessage_type_support_ids_t
{
  const char * typesupport_identifier[2];
} _ExecuteNavigation_FeedbackMessage_type_support_ids_t;

static const _ExecuteNavigation_FeedbackMessage_type_support_ids_t _ExecuteNavigation_FeedbackMessage_message_typesupport_ids = {
  {
    "rosidl_typesupport_fastrtps_cpp",  // ::rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
    "rosidl_typesupport_introspection_cpp",  // ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  }
};

typedef struct _ExecuteNavigation_FeedbackMessage_type_support_symbol_names_t
{
  const char * symbol_name[2];
} _ExecuteNavigation_FeedbackMessage_type_support_symbol_names_t;

#define STRINGIFY_(s) #s
#define STRINGIFY(s) STRINGIFY_(s)

static const _ExecuteNavigation_FeedbackMessage_type_support_symbol_names_t _ExecuteNavigation_FeedbackMessage_message_typesupport_symbol_names = {
  {
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_FeedbackMessage)),
    STRINGIFY(ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_FeedbackMessage)),
  }
};

typedef struct _ExecuteNavigation_FeedbackMessage_type_support_data_t
{
  void * data[2];
} _ExecuteNavigation_FeedbackMessage_type_support_data_t;

static _ExecuteNavigation_FeedbackMessage_type_support_data_t _ExecuteNavigation_FeedbackMessage_message_typesupport_data = {
  {
    0,  // will store the shared library later
    0,  // will store the shared library later
  }
};

static const type_support_map_t _ExecuteNavigation_FeedbackMessage_message_typesupport_map = {
  2,
  "omnifleet_navigation_interfaces",
  &_ExecuteNavigation_FeedbackMessage_message_typesupport_ids.typesupport_identifier[0],
  &_ExecuteNavigation_FeedbackMessage_message_typesupport_symbol_names.symbol_name[0],
  &_ExecuteNavigation_FeedbackMessage_message_typesupport_data.data[0],
};

static const rosidl_message_type_support_t ExecuteNavigation_FeedbackMessage_message_type_support_handle = {
  ::rosidl_typesupport_cpp::typesupport_identifier,
  reinterpret_cast<const type_support_map_t *>(&_ExecuteNavigation_FeedbackMessage_message_typesupport_map),
  ::rosidl_typesupport_cpp::get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_FeedbackMessage>()
{
  return &::omnifleet_navigation_interfaces::action::rosidl_typesupport_cpp::ExecuteNavigation_FeedbackMessage_message_type_support_handle;
}

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation_FeedbackMessage)() {
  return get_message_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation_FeedbackMessage>();
}

#ifdef __cplusplus
}
#endif
}  // namespace rosidl_typesupport_cpp

#include "action_msgs/msg/goal_status_array.hpp"
#include "action_msgs/srv/cancel_goal.hpp"
// already included above
// #include "omnifleet_navigation_interfaces/action/detail/execute_navigation__struct.hpp"
// already included above
// #include "rosidl_typesupport_cpp/visibility_control.h"
#include "rosidl_runtime_c/action_type_support_struct.h"
#include "rosidl_typesupport_cpp/action_type_support.hpp"
// already included above
// #include "rosidl_typesupport_cpp/message_type_support.hpp"
// already included above
// #include "rosidl_typesupport_cpp/service_type_support.hpp"

namespace omnifleet_navigation_interfaces
{

namespace action
{

namespace rosidl_typesupport_cpp
{

static rosidl_action_type_support_t ExecuteNavigation_action_type_support_handle = {
  NULL, NULL, NULL, NULL, NULL};

}  // namespace rosidl_typesupport_cpp

}  // namespace action

}  // namespace omnifleet_navigation_interfaces

namespace rosidl_typesupport_cpp
{

template<>
ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_action_type_support_t *
get_action_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation>()
{
  using ::omnifleet_navigation_interfaces::action::rosidl_typesupport_cpp::ExecuteNavigation_action_type_support_handle;
  // Thread-safe by always writing the same values to the static struct
  ExecuteNavigation_action_type_support_handle.goal_service_type_support = get_service_type_support_handle<::omnifleet_navigation_interfaces::action::ExecuteNavigation::Impl::SendGoalService>();
  ExecuteNavigation_action_type_support_handle.result_service_type_support = get_service_type_support_handle<::omnifleet_navigation_interfaces::action::ExecuteNavigation::Impl::GetResultService>();
  ExecuteNavigation_action_type_support_handle.cancel_service_type_support = get_service_type_support_handle<::omnifleet_navigation_interfaces::action::ExecuteNavigation::Impl::CancelGoalService>();
  ExecuteNavigation_action_type_support_handle.feedback_message_type_support = get_message_type_support_handle<::omnifleet_navigation_interfaces::action::ExecuteNavigation::Impl::FeedbackMessage>();
  ExecuteNavigation_action_type_support_handle.status_message_type_support = get_message_type_support_handle<::omnifleet_navigation_interfaces::action::ExecuteNavigation::Impl::GoalStatusMessage>();
  return &ExecuteNavigation_action_type_support_handle;
}

}  // namespace rosidl_typesupport_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_CPP_PUBLIC
const rosidl_action_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__ACTION_SYMBOL_NAME(rosidl_typesupport_cpp, omnifleet_navigation_interfaces, action, ExecuteNavigation)() {
  return ::rosidl_typesupport_cpp::get_action_type_support_handle<omnifleet_navigation_interfaces::action::ExecuteNavigation>();
}

#ifdef __cplusplus
}
#endif
