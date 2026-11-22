// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from omnifleet_interfaces:srv/StoreMission.idl
// generated code does not contain a copyright notice

#ifndef OMNIFLEET_INTERFACES__SRV__DETAIL__STORE_MISSION__TRAITS_HPP_
#define OMNIFLEET_INTERFACES__SRV__DETAIL__STORE_MISSION__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "omnifleet_interfaces/srv/detail/store_mission__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'poses'
#include "geometry_msgs/msg/detail/pose__traits.hpp"

namespace omnifleet_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const StoreMission_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: mission_id
  {
    out << "mission_id: ";
    rosidl_generator_traits::value_to_yaml(msg.mission_id, out);
    out << ", ";
  }

  // member: poses
  {
    if (msg.poses.size() == 0) {
      out << "poses: []";
    } else {
      out << "poses: [";
      size_t pending_items = msg.poses.size();
      for (auto item : msg.poses) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: loop
  {
    out << "loop: ";
    rosidl_generator_traits::value_to_yaml(msg.loop, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const StoreMission_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: mission_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mission_id: ";
    rosidl_generator_traits::value_to_yaml(msg.mission_id, out);
    out << "\n";
  }

  // member: poses
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.poses.size() == 0) {
      out << "poses: []\n";
    } else {
      out << "poses:\n";
      for (auto item : msg.poses) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: loop
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "loop: ";
    rosidl_generator_traits::value_to_yaml(msg.loop, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const StoreMission_Request & msg, bool use_flow_style = false)
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
  const omnifleet_interfaces::srv::StoreMission_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_interfaces::srv::StoreMission_Request & msg)
{
  return omnifleet_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_interfaces::srv::StoreMission_Request>()
{
  return "omnifleet_interfaces::srv::StoreMission_Request";
}

template<>
inline const char * name<omnifleet_interfaces::srv::StoreMission_Request>()
{
  return "omnifleet_interfaces/srv/StoreMission_Request";
}

template<>
struct has_fixed_size<omnifleet_interfaces::srv::StoreMission_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<omnifleet_interfaces::srv::StoreMission_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<omnifleet_interfaces::srv::StoreMission_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace omnifleet_interfaces
{

namespace srv
{

inline void to_flow_style_yaml(
  const StoreMission_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: accepted
  {
    out << "accepted: ";
    rosidl_generator_traits::value_to_yaml(msg.accepted, out);
    out << ", ";
  }

  // member: revision
  {
    out << "revision: ";
    rosidl_generator_traits::value_to_yaml(msg.revision, out);
    out << ", ";
  }

  // member: map_id
  {
    out << "map_id: ";
    rosidl_generator_traits::value_to_yaml(msg.map_id, out);
    out << ", ";
  }

  // member: map_sha256
  {
    out << "map_sha256: ";
    rosidl_generator_traits::value_to_yaml(msg.map_sha256, out);
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
  const StoreMission_Response & msg,
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

  // member: revision
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "revision: ";
    rosidl_generator_traits::value_to_yaml(msg.revision, out);
    out << "\n";
  }

  // member: map_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "map_id: ";
    rosidl_generator_traits::value_to_yaml(msg.map_id, out);
    out << "\n";
  }

  // member: map_sha256
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "map_sha256: ";
    rosidl_generator_traits::value_to_yaml(msg.map_sha256, out);
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

inline std::string to_yaml(const StoreMission_Response & msg, bool use_flow_style = false)
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
  const omnifleet_interfaces::srv::StoreMission_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  omnifleet_interfaces::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use omnifleet_interfaces::srv::to_yaml() instead")]]
inline std::string to_yaml(const omnifleet_interfaces::srv::StoreMission_Response & msg)
{
  return omnifleet_interfaces::srv::to_yaml(msg);
}

template<>
inline const char * data_type<omnifleet_interfaces::srv::StoreMission_Response>()
{
  return "omnifleet_interfaces::srv::StoreMission_Response";
}

template<>
inline const char * name<omnifleet_interfaces::srv::StoreMission_Response>()
{
  return "omnifleet_interfaces/srv/StoreMission_Response";
}

template<>
struct has_fixed_size<omnifleet_interfaces::srv::StoreMission_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<omnifleet_interfaces::srv::StoreMission_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<omnifleet_interfaces::srv::StoreMission_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<omnifleet_interfaces::srv::StoreMission>()
{
  return "omnifleet_interfaces::srv::StoreMission";
}

template<>
inline const char * name<omnifleet_interfaces::srv::StoreMission>()
{
  return "omnifleet_interfaces/srv/StoreMission";
}

template<>
struct has_fixed_size<omnifleet_interfaces::srv::StoreMission>
  : std::integral_constant<
    bool,
    has_fixed_size<omnifleet_interfaces::srv::StoreMission_Request>::value &&
    has_fixed_size<omnifleet_interfaces::srv::StoreMission_Response>::value
  >
{
};

template<>
struct has_bounded_size<omnifleet_interfaces::srv::StoreMission>
  : std::integral_constant<
    bool,
    has_bounded_size<omnifleet_interfaces::srv::StoreMission_Request>::value &&
    has_bounded_size<omnifleet_interfaces::srv::StoreMission_Response>::value
  >
{
};

template<>
struct is_service<omnifleet_interfaces::srv::StoreMission>
  : std::true_type
{
};

template<>
struct is_service_request<omnifleet_interfaces::srv::StoreMission_Request>
  : std::true_type
{
};

template<>
struct is_service_response<omnifleet_interfaces::srv::StoreMission_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // OMNIFLEET_INTERFACES__SRV__DETAIL__STORE_MISSION__TRAITS_HPP_
