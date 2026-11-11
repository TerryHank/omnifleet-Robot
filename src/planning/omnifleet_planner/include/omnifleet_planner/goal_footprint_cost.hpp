#pragma once
#include <algorithm>
#include <cmath>
#include <limits>
#include "nav2_costmap_2d/footprint.hpp"
#include "nav2_costmap_2d/footprint_collision_checker.hpp"
#include "nav2_costmap_2d/cost_values.hpp"
#include "nav2_util/line_iterator.hpp"

namespace omnifleet_planner
{
// Check edges AND interior. Inflation alone is not an occupied cell.
inline double goalFootprintCost(nav2_costmap_2d::Costmap2D * map,
  const nav2_costmap_2d::Footprint & footprint, double x, double y, double yaw,
  bool allow_unknown = false)
{
  if (footprint.size() < 3 || !std::isfinite(x) || !std::isfinite(y) || !std::isfinite(yaw)) {
    return nav2_costmap_2d::NO_INFORMATION;
  }
  nav2_costmap_2d::FootprintCollisionChecker<nav2_costmap_2d::Costmap2D *> checker(map);
  double cost = allow_unknown ? 0. : checker.footprintCostAtPose(x, y, yaw, footprint);
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
  if (allow_unknown) {
    // Unknown cells may be traversed, but must not mask a lethal edge/interior cell.
    for (size_t i = 0, j = world.size() - 1; i < world.size(); j = i++) {
      unsigned int ax, ay, bx, by;
      map->worldToMap(world[j].x, world[j].y, ax, ay);
      map->worldToMap(world[i].x, world[i].y, bx, by);
      for (nav2_util::LineIterator line(ax, ay, bx, by); line.isValid(); line.advance()) {
        const auto value = map->getCost(line.getX(), line.getY());
        if (value == nav2_costmap_2d::LETHAL_OBSTACLE) {return value;}
        if (value != nav2_costmap_2d::NO_INFORMATION) {cost = std::max(cost, double(value));}
      }
    }
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
      if (inside) {
        const auto value = map->getCost(mx, my);
        if (!allow_unknown || value != nav2_costmap_2d::NO_INFORMATION) {
          cost = std::max(cost, static_cast<double>(value));
        }
      }
    }
  }
  return cost;
}
}  // namespace omnifleet_planner
