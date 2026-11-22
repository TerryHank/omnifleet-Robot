#pragma once
#include <algorithm>
#include <cmath>
#include <limits>
#include "nav2_costmap_2d/footprint.hpp"
#include "nav2_costmap_2d/footprint_collision_checker.hpp"
#include "nav2_costmap_2d/cost_values.hpp"

namespace omnifleet_planner
{
// Check edges AND interior. Inflation alone is not an occupied cell.
inline double goalFootprintCost(nav2_costmap_2d::Costmap2D * map,
  const nav2_costmap_2d::Footprint & footprint, double x, double y, double yaw)
{
  if (footprint.size() < 3 || !std::isfinite(x) || !std::isfinite(y) || !std::isfinite(yaw)) {
    return nav2_costmap_2d::NO_INFORMATION;
  }
  nav2_costmap_2d::FootprintCollisionChecker<nav2_costmap_2d::Costmap2D *> checker(map);
  double cost = checker.footprintCostAtPose(x, y, yaw, footprint);
  if (cost < 0 || cost >= nav2_costmap_2d::LETHAL_OBSTACLE) {return cost;}
  nav2_costmap_2d::Footprint world;
  nav2_costmap_2d::transformFootprint(x, y, yaw, footprint, world);
  unsigned int min_x = map->getSizeInCellsX(), min_y = map->getSizeInCellsY(), max_x = 0, max_y = 0;
  for (const auto & point : world) {
    unsigned int mx, my;
    if (!map->worldToMap(point.x, point.y, mx, my)) {return nav2_costmap_2d::NO_INFORMATION;}
    min_x = std::min(min_x, mx); min_y = std::min(min_y, my);
    max_x = std::max(max_x, mx); max_y = std::max(max_y, my);
  }
  for (unsigned int my = min_y; my <= max_y; ++my) {
    for (unsigned int mx = min_x; mx <= max_x; ++mx) {
      double wx, wy; map->mapToWorld(mx, my, wx, wy);
      bool inside = false;
      for (size_t i = 0, j = world.size() - 1; i < world.size(); j = i++) {
        const auto & a = world[i]; const auto & b = world[j];
        if (((a.y > wy) != (b.y > wy)) &&
          wx < (b.x - a.x) * (wy - a.y) / (b.y - a.y) + a.x) {inside = !inside;}
      }
      if (inside) {cost = std::max(cost, static_cast<double>(map->getCost(mx, my)));}
    }
  }
  return cost;
}
}  // namespace omnifleet_planner
