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
