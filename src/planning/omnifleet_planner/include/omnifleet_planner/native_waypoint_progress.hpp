#pragma once
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <string>

namespace omnifleet_planner {
struct NativeWaypointProgressState {
  int64_t reset_ns{0}, stamp_ns{0};
  double goal_x{0.}, goal_y{0.};
  bool ready{false};
  void reset(int64_t now) {reset_ns=now;stamp_ns=0;ready=false;}
  void observe(int64_t stamp, size_t remaining, double x, double y, const std::string & run) {
    if (stamp<=reset_ns || stamp<=stamp_ns) {return;}
    stamp_ns=stamp;goal_x=x;goal_y=y;
    ready=remaining==1 && !run.empty() && std::isfinite(x) && std::isfinite(y);
  }
  bool canFinish(double x, double y, int64_t now) const {
    const auto age=now-stamp_ns;
    return ready && stamp_ns>reset_ns && age>=0 && age<=500000000 &&
      std::isfinite(x) && std::isfinite(y) && std::abs(x-goal_x)<1e-4 && std::abs(y-goal_y)<1e-4;
  }
};
}  // namespace omnifleet_planner
