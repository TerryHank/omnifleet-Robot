#include <gtest/gtest.h>
#include "omnifleet_planner/hot_rpp.hpp"
#include "nav2_controller/plugins/simple_goal_checker.hpp"
#include "omnifleet_planner/footprint_safe_goal_checker.hpp"

class FollowProbe : public omnifleet_planner::HotRegulatedPurePursuitController {
public:
  int64_t stamp() const {return rclcpp::Time(global_plan_.header.stamp).nanoseconds();}
  geometry_msgs::msg::TwistStamped run(const nlohmann::json & context) {
    geometry_msgs::msg::PoseStamped pose;pose.header.frame_id="map";pose.header.stamp=node_.lock()->now();pose.pose.orientation.w=1.;
    return followVelocity(pose,geometry_msgs::msg::Twist(),context);
  }
};
class FollowControl : public ::testing::Test {
protected:
  rclcpp_lifecycle::LifecycleNode::SharedPtr node;
  std::shared_ptr<nav2_costmap_2d::Costmap2DROS> map;
  FollowProbe controller;
  nlohmann::json context{{"head_x",1.},{"head_y",0.},{"distance",1.},{"speed",.3},{"limit_controller","MPPI"}};
  void SetUp() override {
    if(!rclcpp::ok())rclcpp::init(0,nullptr);
    node=std::make_shared<rclcpp_lifecycle::LifecycleNode>("follow_control_test");
    node->declare_parameter("MPPI.vx_max",.5);node->declare_parameter("MPPI.wz_max",1.2);
    node->declare_parameter("RPP.desired_linear_vel",.4);node->declare_parameter("RPP.approach_velocity_scaling_dist",1.);
    map=std::make_shared<nav2_costmap_2d::Costmap2DROS>("follow_test_map");
    map->set_parameters({rclcpp::Parameter("plugins",std::vector<std::string>{}),rclcpp::Parameter("global_frame","map"),rclcpp::Parameter("robot_base_frame","map"),
      rclcpp::Parameter("width",4),rclcpp::Parameter("height",4),rclcpp::Parameter("origin_x",-2.),rclcpp::Parameter("origin_y",-2.),rclcpp::Parameter("resolution",.05)});
    map->configure();auto grid=map->getCostmap();
    std::fill(grid->getCharMap(),grid->getCharMap()+grid->getSizeInCellsX()*grid->getSizeInCellsY(),0);
    nav2_costmap_2d::Footprint footprint;for(auto xy:{std::pair<double,double>{-.01,-.01},{.01,-.01},{.01,.01},{-.01,.01}}){geometry_msgs::msg::Point p;p.x=xy.first;p.y=xy.second;footprint.push_back(p);}map->setRobotFootprint(footprint);
    auto tf=std::make_shared<tf2_ros::Buffer>(node->get_clock());controller.configure(node,"RPP",tf,map);controller.activate();path(.6);
  }
  void path(double end,double lateral=0.) {
    nav_msgs::msg::Path plan;plan.header.frame_id="map";plan.header.stamp=node->now();
    for(int i=0;i<=20;++i){geometry_msgs::msg::PoseStamped p;p.header=plan.header;p.pose.position.x=end*i/20.;p.pose.position.y=lateral*i/20.;p.pose.orientation.w=1.;plan.poses.push_back(p);}controller.setPlan(plan);
  }
  void TearDown() override {controller.deactivate();controller.cleanup();rclcpp::shutdown();map->cleanup();}
};
TEST_F(FollowControl,AtRequestedGapMatchesMovingPredecessorInsteadOfBrakingToGoal) {
  path(.2);EXPECT_NEAR(controller.run(context).twist.linear.x,.3,1e-5);
  EXPECT_DOUBLE_EQ(node->get_parameter("RPP.approach_velocity_scaling_dist").as_double(),1.);
}
TEST_F(FollowControl,ExtraGapCatchesUpAndPermanentMaximumCanBeChanged) {
  context["head_x"]=1.6;EXPECT_NEAR(controller.run(context).twist.linear.x,.5,1e-5);
  node->set_parameter(rclcpp::Parameter("MPPI.vx_max",.2));EXPECT_NEAR(controller.run(context).twist.linear.x,.2,1e-5);
}
TEST_F(FollowControl,TooCloseAndStoppedDoesNotReverseOrSwing) {
  context["head_x"]=.85;context["speed"]=0.;path(.1,.05);
  auto command=controller.run(context);EXPECT_DOUBLE_EQ(command.twist.linear.x,0.);EXPECT_DOUBLE_EQ(command.twist.angular.z,0.);
}
TEST_F(FollowControl,SmallHeadingErrorKeepsMovingAndLimitsAngularAcceleration) {
  path(.6,.08);auto command=controller.run(context);
  EXPECT_GT(command.twist.linear.x,.25);EXPECT_LE(std::abs(command.twist.angular.z),.161);
}
TEST_F(FollowControl,Nav2CollisionCheckStillRejectsAnOccupiedArc) {
  auto grid=map->getCostmap();unsigned x,y;ASSERT_TRUE(grid->worldToMap(.1,0.,x,y));
  for(unsigned i=x;i<x+4;++i)for(unsigned j=y-2;j<=y+2;++j)grid->setCost(i,j,254);
  EXPECT_THROW(controller.run(context),nav2_core::PlannerException);
}
TEST_F(FollowControl,TemporarySpeedLimitIsHonoredAndCanBeCleared) {
  context["head_x"]=1.6;controller.setSpeedLimit(.18,false);EXPECT_LE(controller.run(context).twist.linear.x,.18);
  controller.setSpeedLimit(0.,false);EXPECT_NEAR(controller.run(context).twist.linear.x,.5,1e-5);
}
TEST_F(FollowControl,OrdinaryRppStillUsesItsPermanentApproachProfile) {
  path(.5);nav2_controller::SimpleGoalChecker checker;checker.initialize(node,"checker",map);
  geometry_msgs::msg::PoseStamped pose;pose.header.frame_id="map";pose.header.stamp=node->now();pose.pose.orientation.w=1.;
  EXPECT_NEAR(controller.computeVelocityCommands(pose,geometry_msgs::msg::Twist(),&checker).twist.linear.x,.2,1e-5);
}
TEST_F(FollowControl,PassedMovingEndpointDoesNotCommandATurnAround) {
  path(-.1,.01);auto command=controller.run(context);
  EXPECT_GT(command.twist.linear.x,.29);EXPECT_LT(std::abs(command.twist.angular.z),.05);
}
TEST_F(FollowControl,VeryShortPathDoesNotAmplifySmallLateralError) {
  path(.1,.02);auto command=controller.run(context);
  EXPECT_GT(command.twist.linear.x,.28);EXPECT_LT(std::abs(command.twist.angular.z),.05);
}
TEST_F(FollowControl,ClosingVelocityBrakesBeforeTheGapUndershoots) {
  context["head_x"]=1.1;context["speed"]=.1;context["range_rate"]=-.5;
  EXPECT_DOUBLE_EQ(controller.run(context).twist.linear.x,0.);
  context["range_rate"]=0.;EXPECT_GT(controller.run(context).twist.linear.x,.15);
}
TEST_F(FollowControl,FollowTuningReadsTheSameEditableControllerParameters) {
  context["head_x"]=1.2;context["speed"]=.1;context["range_rate"]=-.2;
  EXPECT_NEAR(controller.run(context).twist.linear.x,.2,1e-5);
  node->set_parameter(rclcpp::Parameter("RPP.follow_gap_gain",2.));EXPECT_NEAR(controller.run(context).twist.linear.x,.4,1e-5);
  node->set_parameter(rclcpp::Parameter("RPP.follow_speed_damping",1.));EXPECT_NEAR(controller.run(context).twist.linear.x,.3,1e-5);
}
TEST_F(FollowControl,FollowingCannotFinishAtAMovingIntermediateGoal) {
  node->declare_parameter("fleet_goal_checker.safe_hold_time",0.);
  node->declare_parameter("general_checker.safe_hold_time",0.);
  omnifleet_planner::FootprintSafeGoalChecker follow,ordinary;
  follow.initialize(node,"fleet_goal_checker",map);ordinary.initialize(node,"general_checker",map);
  geometry_msgs::msg::Pose pose;pose.orientation.w=1.;geometry_msgs::msg::Twist velocity;velocity.linear.x=.2;
  EXPECT_FALSE(follow.isGoalReached(pose,pose,velocity));
  EXPECT_TRUE(ordinary.isGoalReached(pose,pose,velocity));
  auto pub=node->create_publisher<std_msgs::msg::String>("navigation/fleet/follow_context",10);pub->on_activate();
  rclcpp::executors::SingleThreadedExecutor executor;executor.add_node(node->get_node_base_interface());
  auto send=[&](double speed){for(int i=0;i<4;++i){std_msgs::msg::String msg;msg.data=nlohmann::json{{"speed",speed}}.dump();pub->publish(msg);std::this_thread::sleep_for(std::chrono::milliseconds(40));executor.spin_some();}};
  send(.3);velocity.linear.x=0.;EXPECT_FALSE(follow.isGoalReached(pose,pose,velocity));
  send(0.);EXPECT_TRUE(follow.isGoalReached(pose,pose,velocity));
}
TEST_F(FollowControl,ConcurrentMaximumSpeedEditsDoNotDeadlockControl) {
  std::thread editor([&]{for(int i=0;i<30;++i){node->set_parameter(rclcpp::Parameter("MPPI.vx_max",i%2?.5:.4));std::this_thread::yield();}});
  for(int i=0;i<40;++i){EXPECT_LE(controller.run(context).twist.linear.x,.5);std::this_thread::yield();}
  editor.join();
}
TEST_F(FollowControl,ContextAppliesOnlyToMatchingNavigationPath) {
  path(.5);context["path_stamps"]=nlohmann::json::array({controller.stamp()});
  auto publisher=node->create_publisher<std_msgs::msg::String>("navigation/fleet/follow_context",10);publisher->on_activate();
  rclcpp::executors::SingleThreadedExecutor executor;executor.add_node(node->get_node_base_interface());
  for(int i=0;i<6;++i){std_msgs::msg::String message;message.data=context.dump();publisher->publish(message);std::this_thread::sleep_for(std::chrono::milliseconds(50));executor.spin_some();}
  nav2_controller::SimpleGoalChecker checker;checker.initialize(node,"checker",map);
  geometry_msgs::msg::PoseStamped pose;pose.header.frame_id="map";pose.header.stamp=node->now();pose.pose.orientation.w=1.;
  EXPECT_NEAR(controller.computeVelocityCommands(pose,geometry_msgs::msg::Twist(),&checker).twist.linear.x,.3,1e-5);
  path(.5);
  EXPECT_NEAR(controller.computeVelocityCommands(pose,geometry_msgs::msg::Twist(),&checker).twist.linear.x,.2,1e-5);
}
