#include "gtest/gtest.h"
#include "omnifleet_planner/goal_footprint_cost.hpp"
#include "omnifleet_planner/footprint_safe_goal_checker.hpp"
#include "nav2_core/exceptions.hpp"
#include <thread>

class GoalCost : public ::testing::Test
{
protected:
  nav2_costmap_2d::Costmap2D map{80,80,.05,-2.,-2.,0};
  nav2_costmap_2d::Footprint footprint;
  void SetUp() override {
    for (const auto & xy : {std::pair<double,double>{-.3,-.235},{.3,-.235},{.3,.235},{-.3,.235}}) {
      geometry_msgs::msg::Point p; p.x=xy.first;p.y=xy.second;footprint.push_back(p);
    }
  }
  double cost(double yaw=0) {return omnifleet_planner::goalFootprintCost(&map,footprint,0,0,yaw);}
  void set(double x,double y,unsigned char value) {unsigned int mx,my;ASSERT_TRUE(map.worldToMap(x,y,mx,my));map.setCost(mx,my,value);}
};
TEST_F(GoalCost,FreeAndInflationAreAllowed) {
  EXPECT_EQ(cost(),0);std::fill(map.getCharMap(),map.getCharMap()+6400,253);EXPECT_EQ(cost(),253);
}
TEST_F(GoalCost,InteriorLethalAndUnknownAreRejected) {
  set(.025,.025,254);EXPECT_EQ(cost(),254);set(.025,.025,255);EXPECT_EQ(cost(),255);
}
TEST_F(GoalCost,BoundaryObstacleIsRejected) {set(.3,0,254);EXPECT_GE(cost(),254);}
TEST_F(GoalCost,RotatedFootprintChecksInterior) {set(.1,.1,254);EXPECT_EQ(cost(.8),254);}
TEST_F(GoalCost,OutsideFootprintDoesNotBlock) {set(.8,.8,254);EXPECT_EQ(cost(),0);}
TEST_F(GoalCost,OutsideMapIsRejected) {
  EXPECT_TRUE(omnifleet_planner::goalFootprintCost(&map,footprint,1.95,0,0)<0 ||
    omnifleet_planner::goalFootprintCost(&map,footprint,1.95,0,0)>=254);
}

TEST_F(GoalCost,ActualGoalCheckerAccepts253AndRejectsTrueObstacles) {
  if (!rclcpp::ok()) {rclcpp::init(0,nullptr);}
  auto parent=std::make_shared<rclcpp_lifecycle::LifecycleNode>("goal_test_parent");
  parent->declare_parameter("checker.safe_hold_time",.35);
  parent->declare_parameter("checker.stateful",false);
  auto rosmap=std::make_shared<nav2_costmap_2d::Costmap2DROS>("goal_test_map");
  rosmap->set_parameters({rclcpp::Parameter("plugins",std::vector<std::string>{}),
    rclcpp::Parameter("width",4),rclcpp::Parameter("height",4),
    rclcpp::Parameter("origin_x",-2.),rclcpp::Parameter("origin_y",-2.),
    rclcpp::Parameter("resolution",.05)});
  rosmap->configure();rosmap->setRobotFootprint(footprint);
  auto * actual=rosmap->getCostmap();
  std::fill(actual->getCharMap(),actual->getCharMap()+actual->getSizeInCellsX()*actual->getSizeInCellsY(),253);
  omnifleet_planner::FootprintSafeGoalChecker checker;
  checker.initialize(parent,"checker",rosmap);
  geometry_msgs::msg::Pose pose;pose.orientation.w=1.;geometry_msgs::msg::Twist velocity;
  EXPECT_FALSE(checker.isGoalReached(pose,pose,velocity));
  std::this_thread::sleep_for(std::chrono::milliseconds(400));
  EXPECT_TRUE(checker.isGoalReached(pose,pose,velocity));
  unsigned int mx,my;ASSERT_TRUE(actual->worldToMap(0,0,mx,my));
  actual->setCost(mx,my,254);
  EXPECT_THROW(checker.isGoalReached(pose,pose,velocity),nav2_core::PlannerException);
  actual->setCost(mx,my,255);
  EXPECT_THROW(checker.isGoalReached(pose,pose,velocity),nav2_core::PlannerException);
  auto far=pose;far.position.x=1.;
  EXPECT_FALSE(checker.isGoalReached(pose,far,velocity));
  rosmap->cleanup();
}

TEST_F(GoalCost,OrderedRouteCannotFinishAtStartNearFinalGoal) {
  if (!rclcpp::ok()) {rclcpp::init(0,nullptr);}
  auto parent=std::make_shared<rclcpp_lifecycle::LifecycleNode>("ordered_goal_parent");
  parent->declare_parameter("checker.require_ordered_waypoints",true);
  parent->declare_parameter("checker.safe_hold_time",0.0);
  auto rosmap=std::make_shared<nav2_costmap_2d::Costmap2DROS>("ordered_goal_map");
  rosmap->set_parameters({rclcpp::Parameter("plugins",std::vector<std::string>{}),
    rclcpp::Parameter("width",4),rclcpp::Parameter("height",4),
    rclcpp::Parameter("origin_x",-2.),rclcpp::Parameter("origin_y",-2.),rclcpp::Parameter("resolution",.05)});
  rosmap->configure();rosmap->setRobotFootprint(footprint);
  auto map=rosmap->getCostmap();std::fill(map->getCharMap(),map->getCharMap()+map->getSizeInCellsX()*map->getSizeInCellsY(),0);
  omnifleet_planner::FootprintSafeGoalChecker checker;checker.initialize(parent,"checker",rosmap);checker.reset();
  auto pub=parent->create_publisher<std_msgs::msg::String>("omnifleet_t2/waypoints/execution_state",10);pub->on_activate();
  rclcpp::executors::SingleThreadedExecutor exec;exec.add_node(parent->get_node_base_interface());
  geometry_msgs::msg::Pose pose;pose.orientation.w=1.;geometry_msgs::msg::Twist velocity;
  auto send=[&](int remaining,int64_t stamp,const std::string & state="tracking"){
    std_msgs::msg::String m;m.data="{\"run_id\":\"test\",\"remaining\":"+std::to_string(remaining)+",\"stamp_ns\":"+std::to_string(stamp)+",\"state\":\""+state+"\"}";
    pub->publish(m);std::this_thread::sleep_for(std::chrono::milliseconds(60));exec.spin_some();
  };
  EXPECT_FALSE(checker.isGoalReached(pose,pose,velocity));
  send(3,parent->now().nanoseconds());EXPECT_FALSE(checker.isGoalReached(pose,pose,velocity));
  send(2,parent->now().nanoseconds());EXPECT_FALSE(checker.isGoalReached(pose,pose,velocity));
  auto old=parent->now().nanoseconds();checker.reset();send(1,old);EXPECT_FALSE(checker.isGoalReached(pose,pose,velocity));
  send(1,parent->now().nanoseconds(),"replanning");EXPECT_FALSE(checker.isGoalReached(pose,pose,velocity));
  send(1,parent->now().nanoseconds());EXPECT_TRUE(checker.isGoalReached(pose,pose,velocity));
  std::this_thread::sleep_for(std::chrono::milliseconds(550));EXPECT_FALSE(checker.isGoalReached(pose,pose,velocity));
  checker.reset();EXPECT_FALSE(checker.isGoalReached(pose,pose,velocity));
  rosmap->cleanup();
}
