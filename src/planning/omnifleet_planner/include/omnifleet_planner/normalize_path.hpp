#pragma once

#include <nav_msgs/msg/path.hpp>
#include <cmath>

namespace omnifleet_planner {

// Segment concatenation can repeat a junction position with a new heading.
// A zero-length segment hides the cusp from MPPI's adjacent-vector test.
// Keep the outgoing heading, including the exact final goal orientation.
inline nav_msgs::msg::Path normalizePathJunctions(const nav_msgs::msg::Path & input)
{
  nav_msgs::msg::Path output;
  output.header = input.header;
  output.poses.reserve(input.poses.size());
  for (const auto & pose : input.poses) {
    if (!output.poses.empty()) {
      const auto & a = output.poses.back().pose.position;
      const auto & b = pose.pose.position;
      if (std::abs(a.x-b.x) < 1e-6 && std::abs(a.y-b.y) < 1e-6 &&
          std::abs(a.z-b.z) < 1e-6)
      {
        output.poses.back() = pose;
        continue;
      }
    }
    output.poses.push_back(pose);
  }
  return output;
}

}  // namespace omnifleet_planner
