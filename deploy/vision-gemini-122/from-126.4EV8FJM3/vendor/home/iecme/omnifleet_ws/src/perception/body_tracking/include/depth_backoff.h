#ifndef OMNIFLEET_DEPTH_BACKOFF_H_
#define OMNIFLEET_DEPTH_BACKOFF_H_
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <limits>

class DepthBackoff {
 public:
  void ConfigureReverse(double p, double maximum) { reverse_p_=p;reverse_maximum_=maximum; }
  double ReverseP() const { return reverse_p_; }
  double ReverseMaximum() const { return reverse_maximum_; }
  void SetTarget(double target) { target_ = target; }
  double Target() const { return target_; }
  void Observe(int64_t track_id, bool valid, double range) {
    if (track_id != track_id_) {
      reversing_ = advancing_ = hold_forward_ = false;
      track_id_ = track_id;
    }
    valid_ = track_id >= 0 && valid && std::isfinite(range) && range > 0.;
    range_ = valid_ ? range : std::numeric_limits<double>::quiet_NaN();
    if (!valid_) return;
    if (range_ < target_-.10) { reversing_ = true; advancing_ = false; }
    if (range_ > target_+.10) { advancing_ = true; reversing_ = false; }
    if (reversing_ && range_ >= target_-.001) reversing_ = false;
    if (advancing_ && range_ <= target_+.001) advancing_ = false;
    hold_forward_ = !advancing_;
  }

  bool Reversing() const { return reversing_; }
  bool HoldForward() const { return hold_forward_; }
  double Range() const { return range_; }
  double Velocity(double forward_max = .2) const {
    if (!valid_) return 0.;
    if (reversing_) return -std::min(reverse_maximum_, std::max(.03, reverse_p_*(target_-range_)));
    return advancing_ ? std::min(forward_max,std::max(.03,.6*(range_-target_))) : 0.;
  }
  const char *Mode() const {
    if (!valid_) return reversing_ || hold_forward_ ? "WAIT_DEPTH" : "APPROACH_FOR_DEPTH";
    if (reversing_) return "BACKOFF";
    return advancing_ ? "FOLLOW" : "HOLD";
  }

 private:
  double reverse_p_=1.,reverse_maximum_=.25;
  double target_ = 1.;
  int64_t track_id_ = -1;
  bool reversing_ = false, advancing_ = false, hold_forward_ = false, valid_ = false;
  double range_ = std::numeric_limits<double>::quiet_NaN();
};
#endif
