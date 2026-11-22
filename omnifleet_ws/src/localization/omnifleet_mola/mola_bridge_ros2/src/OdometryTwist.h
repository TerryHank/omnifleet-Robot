// Copyright (C) 2018-2026 Jose Luis Blanco, University of Almeria,
// and individual contributors.
// SPDX-License-Identifier: GPL-3.0
#pragma once

#include <mola_kernel/interfaces/LocalizationSourceBase.h>
#include <geometry_msgs/msg/twist_with_covariance.hpp>
#include <nav_msgs/msg/odometry.hpp>

namespace mola::detail
{
/** Select velocity and covariance together; stale external data falls back to
 * the localization estimate. No input preserves the bridge's zero output. */
inline void applyOdometryTwist(
    nav_msgs::msg::Odometry& msg,
    const LocalizationSourceBase::LocalizationUpdate& update,
    const geometry_msgs::msg::TwistWithCovariance* latest,
    double age, double maximumAge)
{
  if (latest && age >= -0.1 && age <= maximumAge)
  {
    msg.twist = *latest;
    return;
  }
  if (!update.twist)
  {
    return;
  }
  msg.twist.twist.linear.x = update.twist->vx;
  msg.twist.twist.linear.y = update.twist->vy;
  msg.twist.twist.linear.z = update.twist->vz;
  msg.twist.twist.angular.x = update.twist->wx;
  msg.twist.twist.angular.y = update.twist->wy;
  msg.twist.twist.angular.z = update.twist->wz;
  if (update.twist_cov)
  {
    for (size_t row = 0; row < 6; row++)
    {
      for (size_t col = 0; col < 6; col++)
      {
        msg.twist.covariance[row * 6 + col] = (*update.twist_cov)(row, col);
      }
    }
  }
}
}  // namespace mola::detail
