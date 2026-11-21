#include <cmath>
#include <cstdint>

#include "gtest/gtest.h"
#include "nav_msgs/msg/occupancy_grid.hpp"
#include "nav_msgs/msg/path.hpp"

#include "omnifleet_a2_planner/path_map_policy.hpp"

namespace
{

nav_msgs::msg::OccupancyGrid makeMap()
{
  nav_msgs::msg::OccupancyGrid map;
  map.header.frame_id = "map";
  map.info.resolution = 1.0;
  map.info.width = 5;
  map.info.height = 5;
  map.info.origin.orientation.w = 1.0;
  map.data.assign(25, 0);
  return map;
}

nav_msgs::msg::Path makePath(
  std::initializer_list<std::pair<double, double>> points)
{
  nav_msgs::msg::Path path;
  path.header.frame_id = "map";
  for (const auto & [x, y] : points) {
    geometry_msgs::msg::PoseStamped pose;
    pose.header.frame_id = "map";
    pose.pose.position.x = x;
    pose.pose.position.y = y;
    pose.pose.orientation.w = 1.0;
    path.poses.push_back(pose);
  }
  return path;
}

}  // namespace

TEST(PathMapPolicy, AcceptsKnownPathInsideBounds)
{
  const auto result = omnifleet_a2_planner::checkPathAgainstMap(
    makePath({{0.5, 0.5}, {2.5, 2.5}, {4.5, 4.5}}), makeMap());
  EXPECT_TRUE(result.accepted());
  EXPECT_FALSE(result.exploration_mode);
}

TEST(PathMapPolicy, RejectsAnyPoseOutsideBounds)
{
  const auto result = omnifleet_a2_planner::checkPathAgainstMap(
    makePath({{0.5, 0.5}, {-0.01, 2.0}, {4.5, 4.5}}), makeMap());
  EXPECT_EQ(result.code, omnifleet_a2_planner::PathMapResultCode::OUT_OF_BOUNDS);
  EXPECT_EQ(result.pose_index, 1u);
}

TEST(PathMapPolicy, RejectsUnknownShortcutForKnownGoal)
{
  auto map = makeMap();
  map.data[2 * map.info.width + 2] = -1;
  const auto result = omnifleet_a2_planner::checkPathAgainstMap(
    makePath({{0.5, 0.5}, {2.5, 2.5}, {4.5, 4.5}}), map);
  EXPECT_EQ(result.code, omnifleet_a2_planner::PathMapResultCode::UNKNOWN_NOT_ALLOWED);
  EXPECT_EQ(result.pose_index, 1u);
}

TEST(PathMapPolicy, AllowsUnknownCellsWhenGoalIsUnknown)
{
  auto map = makeMap();
  map.data[2 * map.info.width + 2] = -1;
  map.data[4 * map.info.width + 4] = -1;
  const auto result = omnifleet_a2_planner::checkPathAgainstMap(
    makePath({{0.5, 0.5}, {2.5, 2.5}, {4.5, 4.5}}), map);
  EXPECT_TRUE(result.accepted());
  EXPECT_TRUE(result.exploration_mode);
}

TEST(PathMapPolicy, RejectsLethalObstacleCells)
{
  auto map = makeMap();
  map.data[2 * map.info.width + 2] = 100;
  const auto result = omnifleet_a2_planner::checkPathAgainstMap(
    makePath({{0.5, 0.5}, {2.5, 2.5}, {4.5, 4.5}}), map);
  EXPECT_EQ(result.code, omnifleet_a2_planner::PathMapResultCode::LETHAL_CELL);
  EXPECT_EQ(result.pose_index, 1u);
}

TEST(PathMapPolicy, HandlesRotatedMapOrigin)
{
  auto map = makeMap();
  const double yaw = std::acos(-1.0) / 2.0;
  map.info.origin.position.x = 10.0;
  map.info.origin.position.y = 20.0;
  map.info.origin.orientation.z = std::sin(yaw / 2.0);
  map.info.origin.orientation.w = std::cos(yaw / 2.0);
  const auto result = omnifleet_a2_planner::checkPathAgainstMap(
    makePath({{9.5, 20.5}, {8.5, 22.5}, {6.5, 24.5}}), map);
  EXPECT_TRUE(result.accepted());
}

TEST(PathMapPolicy, RejectsFrameMismatch)
{
  auto path = makePath({{0.5, 0.5}, {1.5, 1.5}});
  path.header.frame_id = "odom";
  const auto result = omnifleet_a2_planner::checkPathAgainstMap(path, makeMap());
  EXPECT_EQ(result.code, omnifleet_a2_planner::PathMapResultCode::FRAME_MISMATCH);
}

TEST(PathMapPolicy, RejectsEmptyPath)
{
  nav_msgs::msg::Path path;
  path.header.frame_id = "map";
  const auto result = omnifleet_a2_planner::checkPathAgainstMap(path, makeMap());
  EXPECT_EQ(result.code, omnifleet_a2_planner::PathMapResultCode::EMPTY_PATH);
}
