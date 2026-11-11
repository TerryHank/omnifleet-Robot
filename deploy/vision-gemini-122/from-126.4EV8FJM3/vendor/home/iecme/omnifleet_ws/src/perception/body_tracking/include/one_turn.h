#ifndef OMNIFLEET_ONE_TURN_H_
#define OMNIFLEET_ONE_TURN_H_
#include <algorithm>
#include <cmath>

class OneTurn {
 public:
  void Observe(double yaw) {
    if (!std::isfinite(yaw)) return;
    if (ready_ && active_) progress_ += direction_*std::remainder(yaw-yaw_,Goal());
    yaw_=yaw;ready_=true;
    if (active_ && progress_ >= Goal()-1e-9) { active_=false;done_=true; }
  }
  void Start(int direction,double speed) {
    direction_=direction;speed_=std::abs(speed);progress_=0.;active_=true;done_=false;
  }
  void Stop() { active_=done_=false;progress_=0.; }
  bool Ready() const { return ready_; }
  bool Active() const { return active_; }
  bool Done() const { return done_; }
  double Degrees() const { return progress_*180./std::acos(-1.); }
  double Velocity() const {
    if (!ready_ || !active_) return 0.;
    return direction_*std::min(speed_,std::max(.15,.8*(Goal()-progress_)));
  }
 private:
  static double Goal() { return 2.*std::acos(-1.); }
  bool ready_=false,active_=false,done_=false;
  int direction_=1;
  double yaw_=0.,progress_=0.,speed_=.4;
};
#endif
