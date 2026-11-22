#include <chrono>
#include <cmath>
#include <memory>
#include <thread>
#include "behaviortree_cpp_v3/bt_factory.h"
#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "continuous_route_control.hpp"

BT_REGISTER_NODES(factory)
{
  factory.registerNodeType<omnifleet_planner::ContinuousRouteControl>("ContinuousRouteControl");
}
