#include <gtest/gtest.h>
#include "omnifleet_dwb_hot/hot_dwb.hpp"
class ConstantCritic : public dwb_core::TrajectoryCritic {
public:
  double scoreTrajectory(const dwb_msgs::msg::Trajectory2D &) override {return 10.0;}
};
class TestPlanner : public omnifleet_dwb_hot::HotDWBLocalPlanner {
public:
  void setup(const nav2_util::LifecycleNode::SharedPtr & node) {
    node_ = node; dwb_plugin_name_ = "FollowPath";
    short_circuit_trajectory_evaluation_ = false;
    auto critic = std::make_shared<ConstantCritic>();
    critic->initialize(node, "BaseObstacle", "FollowPath", nullptr);
    critics_.push_back(critic);
  }
  double score() {
    syncCriticScales();
    return scoreTrajectory(dwb_msgs::msg::Trajectory2D{}).total;
  }
};
TEST(HotScoring, ChangesCachedWeightWithoutReconfigure) {
  rclcpp::init(0, nullptr);
  auto node = std::make_shared<nav2_util::LifecycleNode>("hot_scoring_test", "");
  node->declare_parameter("FollowPath.BaseObstacle.scale", 0.02);
  {
    TestPlanner planner; planner.setup(node);
    EXPECT_NEAR(planner.score(), 0.2, 1e-6);  // DWB scores are float32.
    ASSERT_TRUE(node->set_parameter(rclcpp::Parameter("FollowPath.BaseObstacle.scale", 0.8)).successful);
    EXPECT_NEAR(planner.score(), 8.0, 1e-6);
    node->set_parameter(rclcpp::Parameter("FollowPath.BaseObstacle.scale", -1.0));
    EXPECT_THROW(planner.score(), std::runtime_error);
  }
  node.reset(); rclcpp::shutdown();
}
