#pragma once

#include "nav2_mppi_controller/critic_function.hpp"
#include "nav2_costmap_2d/footprint_collision_checker.hpp"
#include <opencv2/core.hpp>

namespace mppi::critics
{
// A soft trajectory preference. Native CostCritic keeps collision/failure ownership.
class FootprintClearanceCritic : public CriticFunction
{
public:
  void initialize() override;
  void score(CriticData & data) override;

protected:
  float clearance(float x, float y, float yaw,
    const nav2_costmap_2d::Footprint & footprint) const;
  float weight_{6.f}, desired_clearance_{.10f};
  cv::Mat free_cells_, distances_;
};
}
