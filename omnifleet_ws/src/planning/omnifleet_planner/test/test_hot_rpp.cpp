#include <gtest/gtest.h>
#include "omnifleet_planner/hot_rpp.hpp"
#include "omnifleet_planner/exact_goal_endpoint.hpp"
class RppProbe : public omnifleet_planner::HotRegulatedPurePursuitController {
public:
  void setup(const rclcpp_lifecycle::LifecycleNode::SharedPtr & node) {
    node_=node;plugin_name_="RPP";min_approach_linear_velocity_=.05;
  }
  double point(const nav_msgs::msg::Path & p) {
    syncAdditionalParameters();return getLookAheadPoint(1.,p).pose.position.x;
  }
  double approach(const nav_msgs::msg::Path & p) {
    syncAdditionalParameters();double v=.4;applyApproachVelocityScaling(p,v);return v;
  }
  void setupTerminal(const nav_msgs::msg::Path & path) {
    use_rotate_to_heading_=true;desired_linear_vel_=.15;rotate_to_heading_angular_vel_=.35;
    use_collision_detection_=false;costmap_=&probe_map_;setPlan(path);
  }
  void enableReverseTracking() {use_rotate_to_heading_=false;allow_reversing_=true;}
  bool rotatesToPath(double x,double y) {
    geometry_msgs::msg::PoseStamped carrot;carrot.pose.position.x=x;carrot.pose.position.y=y;
    double angle;return shouldRotateToPath(carrot,angle);
  }
  bool terminal(const geometry_msgs::msg::PoseStamped & pose,nav2_core::GoalChecker * checker,
    geometry_msgs::msg::TwistStamped & command) {return terminalVelocity(pose,checker,command);}
private:
  nav2_costmap_2d::Costmap2D probe_map_{20,20,.1,-1.,-1.};
};
class TerminalChecker : public nav2_core::GoalChecker {
public:
  void initialize(const rclcpp_lifecycle::LifecycleNode::WeakPtr &,const std::string &,
    const std::shared_ptr<nav2_costmap_2d::Costmap2DROS>) override {}
  void reset() override {}
  bool isGoalReached(const geometry_msgs::msg::Pose &,const geometry_msgs::msg::Pose &,
    const geometry_msgs::msg::Twist &) override {return false;}
  bool getTolerances(geometry_msgs::msg::Pose & pose,geometry_msgs::msg::Twist &) override {
    pose.position.x=.08;pose.orientation.z=std::sin(.125);pose.orientation.w=std::cos(.125);return true;
  }
};
TEST(HotRpp, ReverseTrackingSkipsPathAlignmentButKeepsFinalHeading) {
  nav_msgs::msg::Path path;path.header.frame_id="map";path.poses.resize(1);
  path.poses[0].pose.orientation.z=1.;path.poses[0].pose.orientation.w=0.;
  RppProbe controller;controller.setupTerminal(path);controller.enableReverseTracking();
  EXPECT_FALSE(controller.rotatesToPath(1.,1.));
  EXPECT_FALSE(controller.rotatesToPath(-1.,0.));
  EXPECT_FALSE(controller.rotatesToPath(-1.,-1.));
  TerminalChecker checker;geometry_msgs::msg::PoseStamped pose;
  pose.header.frame_id="map";pose.pose.position.x=-.05;pose.pose.orientation.w=1.;
  geometry_msgs::msg::TwistStamped command;
  ASSERT_TRUE(controller.terminal(pose,&checker,command));
  EXPECT_DOUBLE_EQ(command.twist.linear.x,0.);EXPECT_GT(command.twist.angular.z,0.);
}
TEST(HotRpp, ActualWrapperRetainsHeadingAndReversesToStrictGoalPosition) {
  nav_msgs::msg::Path path;path.header.frame_id="map";path.poses.resize(1);
  path.poses[0].pose.orientation.z=1.;path.poses[0].pose.orientation.w=0.;
  RppProbe controller;controller.setupTerminal(path);TerminalChecker checker;
  geometry_msgs::msg::PoseStamped pose;pose.header.frame_id="map";pose.pose.position.x=-.095;pose.pose.orientation.w=1.;
  geometry_msgs::msg::TwistStamped command;
  ASSERT_TRUE(controller.terminal(pose,&checker,command));EXPECT_GT(command.twist.angular.z,0.);
  pose.pose.position.x=-.16;pose.pose.orientation.z=std::sin(.7);pose.pose.orientation.w=std::cos(.7);
  ASSERT_TRUE(controller.terminal(pose,&checker,command));EXPECT_DOUBLE_EQ(command.twist.linear.x,0.);EXPECT_GT(command.twist.angular.z,0.);
  pose.pose.orientation.z=1.;pose.pose.orientation.w=0.;
  ASSERT_TRUE(controller.terminal(pose,&checker,command));EXPECT_LT(command.twist.linear.x,0.);
  pose.pose.position.x=-.03;
  ASSERT_TRUE(controller.terminal(pose,&checker,command));EXPECT_DOUBLE_EQ(command.twist.linear.x,0.);EXPECT_DOUBLE_EQ(command.twist.angular.z,0.);
}
TEST(HotRpp, TerminalHeadingSurvivesPositionDriftThenCorrectsPosition) {
  omnifleet_planner::TerminalPose terminal;terminal.setGoal(2.49,-.087,3.091);
  double v=9.,w=9.;
  EXPECT_TRUE(terminal.command(.07,0.,2.2,.08,.25,.05,.35,v,w));
  EXPECT_DOUBLE_EQ(v,0.);EXPECT_GT(w,0.);
  // A path replan with the same endpoint must not reset final alignment.
  terminal.setGoal(2.49,-.087,3.091);
  EXPECT_TRUE(terminal.command(-.18,.03,1.,.08,.25,.05,.35,v,w));
  EXPECT_DOUBLE_EQ(v,0.);EXPECT_GT(w,0.);
  EXPECT_TRUE(terminal.command(-.18,.03,.03,.08,.25,.05,.35,v,w));
  EXPECT_LT(v,0.);EXPECT_LE(std::abs(v),.05);
  EXPECT_TRUE(terminal.command(-.035,.02,.03,.08,.25,.05,.35,v,w));
  EXPECT_DOUBLE_EQ(v,0.);EXPECT_DOUBLE_EQ(w,0.);
}
TEST(HotRpp, NewGoalResetsTerminalButLateralCorrectionKeepsItsPhase) {
  omnifleet_planner::TerminalPose terminal;terminal.setGoal(1.,0.,0.);
  double v,w;
  EXPECT_TRUE(terminal.command(.07,0.,1.,.08,.25,.05,.35,v,w));
  terminal.setGoal(2.,0.,0.);
  EXPECT_FALSE(terminal.command(1.,0.,1.,.08,.25,.05,.35,v,w));
  EXPECT_TRUE(terminal.command(.07,0.,1.,.08,.25,.05,.35,v,w));
  EXPECT_TRUE(terminal.command(-.16,-.08,.01,.08,.25,.05,.35,v,w));
  EXPECT_DOUBLE_EQ(v,0.);EXPECT_GT(w,0.);
  // While correcting position, a heading away from the final orientation is
  // intentional and must not send the controller back to final alignment.
  EXPECT_TRUE(terminal.command(-.18,-.01,-.4,.08,.25,.05,.35,v,w));
  EXPECT_LT(v,0.);EXPECT_GT(w,0.);
  EXPECT_TRUE(terminal.command(-.035,.01,-.4,.08,.25,.05,.35,v,w));
  EXPECT_DOUBLE_EQ(v,0.);EXPECT_LT(w,0.);
}
TEST(HotRpp, LateralPositionAndSensorPivotConvergeWithoutRelaxingGoal) {
  omnifleet_planner::TerminalPose terminal;terminal.setGoal(0.,0.,0.);
  double x=.07,y=.065,yaw=-3.131592653589793;bool stopped=false;
  for(int i=0;i<6000;++i) {
    const double local_x=-std::cos(yaw)*x-std::sin(yaw)*y;
    const double local_y=std::sin(yaw)*x-std::cos(yaw)*y;
    const double error=std::atan2(std::sin(-yaw),std::cos(-yaw));
    double v,w;
    ASSERT_TRUE(terminal.command(local_x,local_y,error,.08,.25,.05,.35,v,w));
    if(std::abs(v)+std::abs(w)<1e-8){stopped=true;break;}
    v*=1.3;const double lateral=-.06*v+.05*w;
    x+=.02*(v*std::cos(yaw)-lateral*std::sin(yaw));
    y+=.02*(v*std::sin(yaw)+lateral*std::cos(yaw));yaw+=.02*w;
  }
  EXPECT_TRUE(stopped);EXPECT_LT(std::hypot(x,y),.08);
  EXPECT_LT(std::abs(std::atan2(std::sin(yaw),std::cos(yaw))),.25);
}
TEST(ExactGoal, AppendsRequestedPoseWithinTheSameFreeCell) {
  nav2_costmap_2d::Costmap2D map(20,20,.1,0.,0.);
  nav_msgs::msg::Path path;path.header.frame_id="map";path.poses.resize(1);
  path.poses.back().pose.position.x=.15;path.poses.back().pose.position.y=.15;
  path.poses.back().pose.orientation.w=1.;
  geometry_msgs::msg::PoseStamped goal;goal.header.frame_id="map";
  goal.pose.position.x=.19;goal.pose.position.y=.11;goal.pose.orientation.z=1.;
  ASSERT_TRUE(omnifleet_planner::appendExactGoal(path,goal,map,false));
  ASSERT_EQ(path.poses.size(),2u);EXPECT_DOUBLE_EQ(path.poses.back().pose.position.x,.19);
  EXPECT_DOUBLE_EQ(path.poses.back().pose.position.y,.11);EXPECT_DOUBLE_EQ(path.poses.back().pose.orientation.z,1.);
  EXPECT_EQ(path.poses.back().header.frame_id,"map");
}
TEST(ExactGoal, NeverConnectsAcrossCellsOrIntoAnOccupiedCell) {
  nav2_costmap_2d::Costmap2D map(20,20,.1,0.,0.);
  nav_msgs::msg::Path path;path.header.frame_id="map";path.poses.resize(1);
  path.poses.back().pose.position.x=.15;path.poses.back().pose.position.y=.15;
  geometry_msgs::msg::PoseStamped goal;goal.header.frame_id="map";goal.pose.position.x=.25;goal.pose.position.y=.15;
  EXPECT_FALSE(omnifleet_planner::appendExactGoal(path,goal,map,false));
  goal.pose.position.x=.19;map.setCost(1,1,nav2_costmap_2d::LETHAL_OBSTACLE);
  EXPECT_FALSE(omnifleet_planner::appendExactGoal(path,goal,map,false));
  map.setCost(1,1,nav2_costmap_2d::NO_INFORMATION);
  EXPECT_FALSE(omnifleet_planner::appendExactGoal(path,goal,map,false));EXPECT_EQ(path.poses.size(),1u);
}
TEST(HotRpp, ActualInterpolationAndApproachChange) {
  rclcpp::init(0,nullptr);
  auto node=std::make_shared<rclcpp_lifecycle::LifecycleNode>("rpp_probe");
  node->declare_parameter("RPP.use_interpolation",false);
  node->declare_parameter("RPP.approach_velocity_scaling_dist",1.);
  RppProbe p;p.setup(node);
  nav_msgs::msg::Path path;path.poses.resize(2);path.poses.back().pose.position.x=2.;
  EXPECT_DOUBLE_EQ(p.point(path),2.);
  node->set_parameter(rclcpp::Parameter("RPP.use_interpolation",true));
  EXPECT_NEAR(p.point(path),1.,1e-6);
  path.poses.back().pose.position.x=.5;
  EXPECT_NEAR(p.approach(path),.2,1e-6);
  node->set_parameter(rclcpp::Parameter("RPP.approach_velocity_scaling_dist",2.));
  EXPECT_NEAR(p.approach(path),.1,1e-6);
  rclcpp::shutdown();
}

TEST(ExactGoal,UnknownAllowedRetainsExactPositionAndOrientation) {
  nav2_costmap_2d::Costmap2D map(20,20,.1,-1.,-1.,255);
  nav_msgs::msg::Path path;path.header.frame_id="map";
  geometry_msgs::msg::PoseStamped point;point.header=path.header;
  point.pose.position.x=.25;point.pose.position.y=.05;point.pose.orientation.w=1.;
  path.poses={point};auto goal=point;goal.pose.position.x=.28;
  goal.pose.orientation=nav2_util::geometry_utils::orientationAroundZAxis(.7);
  EXPECT_FALSE(omnifleet_planner::appendExactGoal(path,goal,map,false));
  ASSERT_TRUE(omnifleet_planner::appendExactGoal(path,goal,map,false,true));
  EXPECT_DOUBLE_EQ(path.poses.back().pose.position.x,.28);
  EXPECT_DOUBLE_EQ(path.poses.back().pose.orientation.z,goal.pose.orientation.z);
  unsigned int mx,my;ASSERT_TRUE(map.worldToMap(.28,.05,mx,my));map.setCost(mx,my,254);
  EXPECT_FALSE(omnifleet_planner::appendExactGoal(path,goal,map,false,true));
}
