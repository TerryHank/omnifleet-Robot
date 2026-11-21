// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from omnifleet_interfaces:srv/ServoCommand.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__SRV__DETAIL__SERVO_COMMAND__TRAITS_HPP_
#define OMNIFLEET_INTERFACES__SRV__DETAIL__SERVO_COMMAND__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "omnifleet_interfaces/srv/detail/servo_command__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace omnifleet_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const ServoCommand_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: operation
  {
    out << "operation: ";
    rosidl_generator_traits::value_to_yaml(msg.operation, out);
    out << ", ";
  }

  // member: id
  {
    out << "id: ";
    rosidl_generator_traits::value_to_yaml(msg.id, out);
    out << ", ";
  }

  // member: arg0
  {
    out << "arg0: ";
    rosidl_generator_traits::value_to_yaml(msg.arg0, out);
    out << ", ";
  }

  // member: arg1
  {
    out << "arg1: ";
    rosidl_generator_traits::value_to_yaml(msg.arg1, out);
    out << ", ";
  }

  // member: arg2
  {
    out << "arg2: ";
    rosidl_generator_traits::value_to_yaml(msg.arg2, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const ServoCommand_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: operation
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "operation: ";
    rosidl_generator_traits::value_to_yaml(msg.operation, out);
    out << "\n";
  }

  // member: id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "id: ";
    rosidl_generator_traits::value_to_yaml(msg.id, out);
    out << "\n";
  }

  // member: arg0
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "arg0: ";
    rosidl_generator_traits::value_to_yaml(msg.arg0, out);
    out << "\n";
  }

  // member: arg1
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "arg1: ";
    rosidl_generator_traits::value_to_yaml(msg.arg1, out);
    out << "\n";
  }

  // member: arg2
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "arg2: ";
    rosidl_generator_traits::value_to_yaml(msg.arg2, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const ServoCommand_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace omnifleet_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_interfaces::srv::ServoCommand_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_interfaces::srv::ServoCommand_Request & msg)
{
  return omnifleet_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_interfaces::srv::ServoCommand_Request>()
{
  return "omnifleet_interfaces::srv::ServoCommand_Request";
}

template<>
inline const char * name<omnifleet_interfaces::srv::ServoCommand_Request>()
{
  return "omnifleet_interfaces/srv/ServoCommand_Request";
}

template<>
struct has_fixed_size<omnifleet_interfaces::srv::ServoCommand_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<omnifleet_interfaces::srv::ServoCommand_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<omnifleet_interfaces::srv::ServoCommand_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace omnifleet_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const ServoCommand_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: value0
  {
    out << "value0: ";
    rosidl_generator_traits::value_to_yaml(msg.value0, out);
    out << ", ";
  }

  // member: value1
  {
    out << "value1: ";
    rosidl_generator_traits::value_to_yaml(msg.value1, out);
    out << ", ";
  }

  // member: value2
  {
    out << "value2: ";
    rosidl_generator_traits::value_to_yaml(msg.value2, out);
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
  const ServoCommand_Response & msg,
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

  // member: value0
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "value0: ";
    rosidl_generator_traits::value_to_yaml(msg.value0, out);
    out << "\n";
  }

  // member: value1
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "value1: ";
    rosidl_generator_traits::value_to_yaml(msg.value1, out);
    out << "\n";
  }

  // member: value2
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "value2: ";
    rosidl_generator_traits::value_to_yaml(msg.value2, out);
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

inline std::string to_yaml(const ServoCommand_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace omnifleet_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use omnifleet_interfaces::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const omnifleet_interfaces::srv::ServoCommand_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_interfaces::srv::ServoCommand_Response & msg)
{
  return omnifleet_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_interfaces::srv::ServoCommand_Response>()
{
  return "omnifleet_interfaces::srv::ServoCommand_Response";
}

template<>
inline const char * name<omnifleet_interfaces::srv::ServoCommand_Response>()
{
  return "omnifleet_interfaces/srv/ServoCommand_Response";
}

template<>
struct has_fixed_size<omnifleet_interfaces::srv::ServoCommand_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<omnifleet_interfaces::srv::ServoCommand_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<omnifleet_interfaces::srv::ServoCommand_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<omnifleet_interfaces::srv::ServoCommand>()
{
  return "omnifleet_interfaces::srv::ServoCommand";
}

template<>
inline const char * name<omnifleet_interfaces::srv::ServoCommand>()
{
  return "omnifleet_interfaces/srv/ServoCommand";
}

template<>
struct has_fixed_size<omnifleet_interfaces::srv::ServoCommand>
  : std::integral_constant<
    bool,
    has_fixed_size<omnifleet_interfaces::srv::ServoCommand_Request>::value &&
    has_fixed_size<omnifleet_interfaces::srv::ServoCommand_Response>::value
  >
{
};

template<>
struct has_bounded_size<omnifleet_interfaces::srv::ServoCommand>
  : std::integral_constant<
    bool,
    has_bounded_size<omnifleet_interfaces::srv::ServoCommand_Request>::value &&
    has_bounded_size<omnifleet_interfaces::srv::ServoCommand_Response>::value
  >
{
};

template<>
struct is_service<omnifleet_interfaces::srv::ServoCommand>
  : std::true_type
{
};

template<>
struct is_service_request<omnifleet_interfaces::srv::ServoCommand_Request>
  : std::true_type
{
};

template<>
struct is_service_response<omnifleet_interfaces::srv::ServoCommand_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // OMNIFLEET_INTERFACES__SRV__DETAIL__SERVO_COMMAND__TRAITS_HPP_
