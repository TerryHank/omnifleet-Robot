// SPDX-License-Identifier: Apache-2.0
#pragma once

#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>
#include <opencv2/imgproc.hpp>
#include "nav2_costmap_2d/cost_values.hpp"
#include "nav2_costmap_2d/footprint_collision_checker.hpp"

namespace mppi
{
struct SweepPose
{
  double x, y, yaw;
};

// Whole occupied-cell / swept polygon intersection. One summed-area table per
// batch avoids scanning obstacle points or all cells inside every robot pose.
class SweptFootprintCollision
{
public:
  void update(nav2_costmap_2d::Costmap2D * map,
    const nav2_costmap_2d::Footprint & footprint, bool unknown_collision)
  {
    width_ = map->getSizeInCellsX(); height_ = map->getSizeInCellsY();
    resolution_ = map->getResolution(); ox_ = map->getOriginX(); oy_ = map->getOriginY();
    footprint_ = footprint; unknown_collision_ = unknown_collision; radius_ = 0.;
    for (const auto & p : footprint_) {radius_ = std::max(radius_, std::hypot(p.x, p.y));}
    cv::Mat raw(height_, width_, CV_8UC1, map->getCharMap());
    if (unknown_collision_) {
      cv::compare(raw, nav2_costmap_2d::INSCRIBED_INFLATED_OBSTACLE, mask_, cv::CMP_GT);
    } else {
      cv::compare(raw, nav2_costmap_2d::LETHAL_OBSTACLE, mask_, cv::CMP_EQ);
    }
    mask_ /= 255;
    cv::integral(mask_, integral_, CV_32S);
    points_.reserve(footprint_.size() * 2); hull_.reserve(footprint_.size() * 4);
  }

  bool collides(const SweepPose & a, const SweepPose & b)
  {
    points_.clear();
    double minx = std::numeric_limits<double>::infinity(), maxx = -minx;
    double miny = minx, maxy = maxx;
    for (const auto & pose : {a, b}) {
      const double c = std::cos(pose.yaw), s = std::sin(pose.yaw);
      for (const auto & p : footprint_) {
        const double x = (pose.x + c*p.x - s*p.y - ox_)/resolution_;
        const double y = (pose.y + s*p.x + c*p.y - oy_)/resolution_;
        points_.emplace_back(x, y);
        minx = std::min(minx, x); maxx = std::max(maxx, x);
        miny = std::min(miny, y); maxy = std::max(maxy, y);
      }
    }
    // A rotating corner follows an arc outside its endpoint chord. Its maximum
    // chord deviation is r*(1-cos(delta_yaw/2)); expand the hull by this amount.
    // This is a geometric sweep bound, not an extra navigation clearance.
    const double turn = std::atan2(std::sin(b.yaw-a.yaw), std::cos(b.yaw-a.yaw));
    const double error = 2.*radius_*std::pow(std::sin(turn*.25), 2)/resolution_;
    int x0 = std::floor(minx-error), x1 = std::floor(maxx+error);
    int y0 = std::floor(miny-error), y1 = std::floor(maxy+error);
    if (unknown_collision_ && (x0 < 0 || y0 < 0 || x1 >= width_ || y1 >= height_)) {
      return true;  // Preserve the configured unknown/out-of-map collision policy.
    }
    x0 = std::max(0,x0); x1 = std::min(width_-1,x1);
    y0 = std::max(0,y0); y1 = std::min(height_-1,y1);
    if (x0 > x1 || y0 > y1 || sum(x0,y0,x1,y1) == 0) {return false;}
    // The hull and its input vertices have identical coordinate extrema.
    // Only build the hull when the same bounding box contains an occupied cell.
    std::sort(points_.begin(), points_.end(), [](const auto & p, const auto & q) {
        return p.x < q.x || (p.x == q.x && p.y < q.y);
      });
    hull_.resize(points_.size() * 2);
    size_t k = 0;
    for (const auto & p : points_) {
      while (k >= 2 && cross(hull_[k-2], hull_[k-1], p) <= 0.) {--k;}
      hull_[k++] = p;
    }
    const size_t lower = k + 1;
    for (size_t i = points_.size()-1; i > 0; --i) {
      const auto & p = points_[i-1];
      while (k >= lower && cross(hull_[k-2], hull_[k-1], p) <= 0.) {--k;}
      hull_[k++] = p;
    }
    hull_.resize(k-1);

    for (int y = y0; y <= y1; ++y) {
      if (sum(x0,y,x1,y) == 0) {continue;}
      const double lo = y-error, hi = y+1.+error;
      double left = std::numeric_limits<double>::infinity(), right = -left;
      const auto add = [&](double x) {left = std::min(left,x); right = std::max(right,x);};
      for (size_t i = 0; i < hull_.size(); ++i) {
        const auto & p = hull_[i]; const auto & q = hull_[(i+1)%hull_.size()];
        if (p.y >= lo && p.y <= hi) {add(p.x);}
        if ((p.y < lo) != (q.y < lo)) {add(p.x+(lo-p.y)*(q.x-p.x)/(q.y-p.y));}
        if ((p.y > hi) != (q.y > hi)) {add(p.x+(hi-p.y)*(q.x-p.x)/(q.y-p.y));}
      }
      if (left > right) {continue;}
      const int first = std::max(x0, static_cast<int>(std::floor(left-error)));
      const int last = std::min(x1, static_cast<int>(std::floor(right+error)));
      if (first <= last && sum(first,y,last,y) != 0) {return true;}
    }
    return false;
  }

private:
  static double cross(const cv::Point2d & o, const cv::Point2d & a, const cv::Point2d & b)
  {return (a.x-o.x)*(b.y-o.y)-(a.y-o.y)*(b.x-o.x);}
  int sum(int x0, int y0, int x1, int y1) const
  {
    return integral_.at<int>(y1+1,x1+1)-integral_.at<int>(y0,x1+1)-
           integral_.at<int>(y1+1,x0)+integral_.at<int>(y0,x0);
  }
  int width_{0}, height_{0};
  double resolution_{0.}, ox_{0.}, oy_{0.}, radius_{0.};
  bool unknown_collision_{false};
  nav2_costmap_2d::Footprint footprint_;
  cv::Mat mask_, integral_;
  std::vector<cv::Point2d> points_, hull_;
};
}  // namespace mppi
