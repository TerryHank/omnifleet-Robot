#include <gtest/gtest.h>
#include "omnifleet_dwb_hot/hot_dwb.hpp"
#include "dwb_critics/rotate_to_goal.hpp"
class RotationProbe : public omnifleet_dwb_hot::HotDWBLocalPlanner {
public:
  std::shared_ptr<dwb_critics::RotateToGoalCritic> critic;
  void setup(const nav2_util::LifecycleNode::SharedPtr & n) {
    node_=n;dwb_plugin_name_="FollowPath";
    critic=std::make_shared<dwb_critics::RotateToGoalCritic>();
    critic->initialize(n,"RotateToGoal","FollowPath",nullptr);critics_.push_back(critic);
  }
  void window(double x, nav2_core::GoalChecker * checker) {
    global_plan_.header.frame_id="map";global_plan_.poses.resize(1);
    geometry_msgs::msg::PoseStamped pose;pose.header.frame_id="map";pose.pose.position.x=x;
    updateGoalRotationWindow(pose,checker);syncCriticScales();
  }
  double score() {
    syncCriticScales();geometry_msgs::msg::Pose2D pose,goal;pose.x=.1;
    nav_2d_msgs::msg::Twist2D speed;speed.x=.2;
    critic->prepare(pose,speed,goal,nav_2d_msgs::msg::Path2D{});
    dwb_msgs::msg::Trajectory2D traj;traj.velocity.x=.1;traj.poses.push_back(goal);
    return critic->scoreTrajectory(traj);
  }
};
TEST(HotRotation, CachedSlowingAndWindowChange) {
 rclcpp::init(0,nullptr);
 auto n=std::make_shared<nav2_util::LifecycleNode>("rotation_test","");
 n->declare_parameter("FollowPath.RotateToGoal.scale",32.);
 n->declare_parameter("FollowPath.xy_goal_tolerance",.25);
 n->declare_parameter("FollowPath.trans_stopped_velocity",.05);
 n->declare_parameter("FollowPath.RotateToGoal.slowing_factor",5.);
 n->declare_parameter("FollowPath.RotateToGoal.lookahead_time",-1.);
 RotationProbe p;p.setup(n);EXPECT_NEAR(p.score(),.05,1e-6);
 n->set_parameter(rclcpp::Parameter("FollowPath.RotateToGoal.slowing_factor",10.));EXPECT_NEAR(p.score(),.1,1e-6);
 n->set_parameter(rclcpp::Parameter("FollowPath.xy_goal_tolerance",.01));EXPECT_NEAR(p.score(),0.,1e-6);
 rclcpp::shutdown();
}

class WindowGoalChecker : public nav2_core::GoalChecker {
public:
 void initialize(const rclcpp_lifecycle::LifecycleNode::WeakPtr &,const std::string &,
   const std::shared_ptr<nav2_costmap_2d::Costmap2DROS>) override {}
 void reset() override {}
 bool isGoalReached(const geometry_msgs::msg::Pose &,const geometry_msgs::msg::Pose &,
   const geometry_msgs::msg::Twist &) override {return false;}
 bool getTolerances(geometry_msgs::msg::Pose & pose,geometry_msgs::msg::Twist &) override {
   pose.position.x=.1;return true;
 }
};
TEST(HotRotation, SelectedGoalCheckerControlsRotationWindowWithoutParameterWrites) {
 rclcpp::init(0,nullptr);
 auto n=std::make_shared<nav2_util::LifecycleNode>("goal_window_test","");
 n->declare_parameter("FollowPath.RotateToGoal.scale",32.);
 n->declare_parameter("FollowPath.xy_goal_tolerance",.2);
 n->declare_parameter("FollowPath.trans_stopped_velocity",.05);
 n->declare_parameter("FollowPath.RotateToGoal.slowing_factor",5.);
 n->declare_parameter("FollowPath.RotateToGoal.lookahead_time",-1.);
 RotationProbe p;p.setup(n);WindowGoalChecker checker;
 p.window(.18,&checker);EXPECT_DOUBLE_EQ(p.critic->getScale(),0.);
 EXPECT_DOUBLE_EQ(n->get_parameter("FollowPath.xy_goal_tolerance").as_double(),.2);
 p.window(.05,&checker);EXPECT_DOUBLE_EQ(p.critic->getScale(),32.);
 p.window(.18,nullptr);EXPECT_DOUBLE_EQ(p.critic->getScale(),32.);
 rclcpp::shutdown();
}
