// Copyright (C) 2018-2026 Jose Luis Blanco, University of Almeria,
// and individual contributors.
// SPDX-License-Identifier: GPL-3.0
#include "../src/OdometryTwist.h"

#include <iostream>
#include <stdexcept>

namespace
{
void expect(bool condition, const char* description)
{
  if (!condition)
  {
    throw std::runtime_error(description);
  }
}
void runTests()
{
  mola::LocalizationSourceBase::LocalizationUpdate update;
  nav_msgs::msg::Odometry empty;
  mola::detail::applyOdometryTwist(empty, update, nullptr, 0.0, 0.5);
  expect(empty.twist.twist.linear.x == 0.0, "default velocity must remain zero");
  expect(empty.twist.covariance[0] == 0.0, "default covariance must remain zero");

  update.twist.emplace();
  update.twist->vx = 2.0;
  update.twist->wz = 0.3;
  update.twist_cov.emplace();
  for (size_t row = 0; row < 6; row++)
  {
    for (size_t col = 0; col < 6; col++)
    {
      (*update.twist_cov)(row, col) = row * 6 + col + 0.25;
    }
  }
  nav_msgs::msg::Odometry estimated;
  mola::detail::applyOdometryTwist(estimated, update, nullptr, 0.0, 0.5);
  expect(estimated.twist.twist.linear.x == 2.0, "estimated velocity is missing");
  expect(estimated.twist.twist.angular.z == 0.3, "estimated rotation is missing");
  expect(estimated.twist.covariance[17] == 17.25, "covariance ordering is wrong");

  geometry_msgs::msg::TwistWithCovariance wheel;
  wheel.twist.linear.x = 9.0;
  wheel.covariance.fill(7.0);
  for (double age : {0.0, 0.5, -0.1})
  {
    nav_msgs::msg::Odometry msg;
    mola::detail::applyOdometryTwist(msg, update, &wheel, age, 0.5);
    expect(msg.twist.twist.linear.x == 9.0, "fresh wheel velocity is missing");
    expect(msg.twist.covariance[17] == 7.0, "wheel covariance was overwritten");
  }
  for (double age : {0.51, -0.11})
  {
    nav_msgs::msg::Odometry msg;
    mola::detail::applyOdometryTwist(msg, update, &wheel, age, 0.5);
    expect(msg.twist.twist.linear.x == 2.0, "invalid wheel age must fall back");
    expect(msg.twist.covariance[17] == 17.25, "fallback covariance is wrong");
  }
}
}  // namespace

int main()
{
  try
  {
    runTests();
    return 0;
  }
  catch (const std::exception& e)
  {
    std::cerr << e.what() << '\n';
    return 1;
  }
}
