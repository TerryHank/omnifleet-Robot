#pragma once

#include <array>
#include <cmath>
#include <stdexcept>

namespace robosense { namespace lidar {

// Six independent random-walk Kalman filters, in the driver's native IMU axes/units.
class ImuKalman
{
public:
  void configure(const std::array<double, 6>& measurement_variance,
                 const std::array<double, 6>& process_variance_rate)
  {
    for (size_t i = 0; i < 6; ++i)
      if (!std::isfinite(measurement_variance[i]) || measurement_variance[i] <= 0 ||
          !std::isfinite(process_variance_rate[i]) || process_variance_rate[i] < 0)
        throw std::invalid_argument("IMU Kalman variances must be finite, R>0 and Q>=0");
    r_ = measurement_variance;
    q_rate_ = process_variance_rate;
    initialized_ = false;
  }

  bool update(double stamp, const std::array<double, 6>& measurement,
              std::array<double, 6>& filtered)
  {
    if (!std::isfinite(stamp) || stamp <= 0) return false;
    for (double value : measurement) if (!std::isfinite(value)) return false;
    const double dt = stamp - stamp_;
    if (initialized_ && dt <= 0) return false;
    if (!initialized_ || dt > 0.1)
    {
      x_ = measurement;
      p_ = r_;
      initialized_ = true;
    }
    else
    {
      for (size_t i = 0; i < 6; ++i)
      {
        const double predicted_p = p_[i] + q_rate_[i] * dt;
        const double gain = predicted_p / (predicted_p + r_[i]);
        x_[i] += gain * (measurement[i] - x_[i]);
        p_[i] = (1.0 - gain) * predicted_p;
      }
    }
    stamp_ = stamp;
    filtered = x_;
    return true;
  }

  const std::array<double, 6>& variance() const { return p_; }

private:
  std::array<double, 6> r_{}, q_rate_{}, x_{}, p_{};
  double stamp_ = 0;
  bool initialized_ = false;
};

}}  // namespace robosense::lidar
