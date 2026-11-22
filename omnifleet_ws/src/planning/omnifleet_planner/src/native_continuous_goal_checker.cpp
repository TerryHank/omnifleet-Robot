#include "omnifleet_planner/footprint_safe_goal_checker.hpp"
#include "omnifleet_planner/native_waypoint_progress.hpp"
#include "pluginlib/class_list_macros.hpp"
#include <nlohmann/json.hpp>

namespace omnifleet_planner {
class NativeContinuousGoalChecker : public FootprintSafeGoalChecker {
public:
  void initialize(const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent,
    const std::string &, const std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap) override
  {
    auto node=parent.lock();clock_=node->get_clock();
    // Share the actual single-goal tolerance, dynamic updates and footprint hold.
    FootprintSafeGoalChecker::initialize(parent,"general_goal_checker",costmap);
    sub_=node->create_subscription<std_msgs::msg::String>(
      "omnifleet_t2/waypoints/native_progress",rclcpp::QoS(1),
      [this](std_msgs::msg::String::ConstSharedPtr message) {
        std::lock_guard<std::mutex> lock(mutex_);
        try {
          const auto data=nlohmann::json::parse(message->data);
          progress_.observe(data.at("stamp_ns").get<int64_t>(),data.at("remaining").get<size_t>(),
            data.at("goal_x").get<double>(),data.at("goal_y").get<double>(),data.at("run_id").get<std::string>());
        } catch (const nlohmann::json::exception &) {progress_.ready=false;}
      });
  }
  void reset() override {
    FootprintSafeGoalChecker::reset();
    std::lock_guard<std::mutex> lock(mutex_);progress_.reset(clock_->now().nanoseconds());
  }
  bool isGoalReached(const geometry_msgs::msg::Pose & pose,
    const geometry_msgs::msg::Pose & goal,const geometry_msgs::msg::Twist & velocity) override
  {
    bool ready;
    {std::lock_guard<std::mutex> lock(mutex_);ready=progress_.canFinish(goal.position.x,goal.position.y,clock_->now().nanoseconds());}
    if (!ready) {FootprintSafeGoalChecker::reset();return false;}
    return FootprintSafeGoalChecker::isGoalReached(pose,goal,velocity);
  }
private:
  rclcpp::Clock::SharedPtr clock_;
  NativeWaypointProgressState progress_;
  std::mutex mutex_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr sub_;
};
}  // namespace omnifleet_planner
PLUGINLIB_EXPORT_CLASS(omnifleet_planner::NativeContinuousGoalChecker,nav2_core::GoalChecker)
