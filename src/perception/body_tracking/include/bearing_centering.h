#ifndef OMNIFLEET_BEARING_CENTERING_H_
#define OMNIFLEET_BEARING_CENTERING_H_
#include <algorithm>
#include <cmath>
#include <cstdint>

class BearingCentering {
 public:
  void Configure(double p, double d, double maximum, double weight) {
    p_=p;d_=d;maximum_=maximum;weight_=weight;
  }
  double P() const { return p_; }
  double D() const { return d_; }
  double Maximum() const { return maximum_; }
  double Weight() const { return weight_; }
  double Update(int64_t id, double error, double source_time) {
    const double dt = source_time-last_time_;
    if (id != id_ || dt <= .001 || dt > .5) rate_ = 0.;
    else rate_ = (1.-weight_)*rate_ + weight_*std::max(-3.,std::min(3.,(error-last_error_)/dt));
    id_ = id;last_error_ = error;last_time_ = source_time;
    if (!std::isfinite(error) || std::abs(error) <= .025) return 0.;
    const double command = p_*error + d_*rate_;
    // D damps arrival at centre; it must not reverse away from the observed target.
    return command*error < 0. ? 0. : std::max(-maximum_,std::min(maximum_,command));
  }
  double Error() const { return last_error_; }

 private:
  double p_=1.8,d_=.35,maximum_=.8,weight_=.7;
  int64_t id_ = -1;
  double last_time_ = 0., last_error_ = 0., rate_ = 0.;
};
#endif
