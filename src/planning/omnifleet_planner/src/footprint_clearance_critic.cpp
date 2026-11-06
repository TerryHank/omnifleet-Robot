#include "omnifleet_planner/footprint_clearance_critic.hpp"
#include "pluginlib/class_list_macros.hpp"
#include <opencv2/imgproc.hpp>
#include <algorithm>
#include <cmath>
#include <limits>

namespace mppi::critics
{
void FootprintClearanceCritic::initialize()
{
  auto get = parameters_handler_->getParamGetter(name_);
  get(weight_, "cost_weight", 6.0);
  get(desired_clearance_, "desired_clearance", .10);
  RCLCPP_INFO(logger_, "FootprintClearanceCritic: soft body clearance %.2f m, weight %.1f",
    desired_clearance_, weight_);
}

float FootprintClearanceCritic::clearance(float x, float y, float yaw,
  const nav2_costmap_2d::Footprint & footprint) const
{
  const float c = std::cos(yaw), s = std::sin(yaw);
  float nearest = std::numeric_limits<float>::infinity();
  for (size_t k = 0; k < footprint.size(); ++k) {
    const auto & a = footprint[k];
    const auto & b = footprint[(k + 1) % footprint.size()];
    // Corners and edge midpoints expose rotation-dependent wall clearance.
    for (float t : {0.f, .5f}) {
      const float px = a.x + t * (b.x - a.x), py = a.y + t * (b.y - a.y);
      unsigned int mx, my;
      if (costmap_->worldToMap(x + c * px - s * py, y + s * px + c * py, mx, my)) {
        nearest = std::min(nearest, distances_.at<float>(my, mx));
      }
    }
  }
  return std::max(0.f, nearest - static_cast<float>(costmap_->getResolution() * .71));
}

void FootprintClearanceCritic::score(CriticData & data)
{
  if (!enabled_) {return;}
  const auto & footprint = costmap_ros_->getRobotFootprint();
  if (footprint.empty()) {return;}
  const auto & tr = data.trajectories;
  const size_t steps = tr.x.shape(1);
  if (steps == 0) {return;}

  // Build one distance field per batch, not an obstacle search for every pose.
  cv::Mat costs(costmap_->getSizeInCellsY(), costmap_->getSizeInCellsX(), CV_8UC1,
    costmap_->getCharMap());
  cv::compare(costs, nav2_costmap_2d::LETHAL_OBSTACLE, free_cells_, cv::CMP_NE);
  cv::distanceTransform(free_cells_, distances_, cv::DIST_L2, cv::DIST_MASK_5);
  distances_ *= costmap_->getResolution();

  const float resolution = costmap_->getResolution();
  for (size_t i = 0; i < tr.x.shape(0); ++i) {
    float total = 0.f, peak = 0.f;
    float px = data.state.pose.pose.position.x, py = data.state.pose.pose.position.y;
    const auto & q = data.state.pose.pose.orientation;
    float yaw = std::atan2(2. * (q.w * q.z + q.x * q.y), 1. - 2. * (q.y * q.y + q.z * q.z));
    // Alternate rollout endpoints plus their midpoints retain the temporal density
    // without doubling the 1000 x 56 trajectory batch's footprint lookups.
    for (size_t j = (steps - 1) % 2; j < steps; j += 2) {
      const float turn = std::atan2(std::sin(tr.yaws(i,j) - yaw), std::cos(tr.yaws(i,j) - yaw));
      // Also score between rollout poses so a turning corner is seen earlier.
      const float gap = std::min(clearance(tr.x(i,j), tr.y(i,j), tr.yaws(i,j), footprint),
        clearance((px + tr.x(i,j)) * .5f, (py + tr.y(i,j)) * .5f, yaw + turn * .5f, footprint));
      // Normalize the soft preference by the requested clearance, not by
      // the shrinking measured gap. Hard collisions remain owned by CostCritic.
      const float penalty = std::max(0.f, desired_clearance_ - gap) /
        std::max(resolution, desired_clearance_);
      const float squared = penalty * penalty;
      total += squared; peak = std::max(peak, squared);
      px = tr.x(i,j); py = tr.y(i,j); yaw = tr.yaws(i,j);
    }
    // Preserve short close-wall events instead of averaging them into a long clear tail.
    data.costs(i) += weight_ * (total / ((steps + 1) / 2) + peak);
  }
}
}

PLUGINLIB_EXPORT_CLASS(mppi::critics::FootprintClearanceCritic, mppi::critics::CriticFunction)
