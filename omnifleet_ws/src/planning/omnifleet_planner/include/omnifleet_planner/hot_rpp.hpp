#pragma once
#include "nav2_regulated_pure_pursuit_controller/regulated_pure_pursuit_controller.hpp"
#include "nav2_core/exceptions.hpp"
#include "nav2_util/node_utils.hpp"
#include "std_msgs/msg/string.hpp"
#include "omnifleet_planner/terminal_pose.hpp"
#include "tf2/utils.h"
#include <nlohmann/json.hpp>
#include <cmath>
namespace omnifleet_planner {
class HotRegulatedPurePursuitController : public nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController {
public:
  void configure(const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent, std::string name,
    std::shared_ptr<tf2_ros::Buffer> tf, std::shared_ptr<nav2_costmap_2d::Costmap2DROS> map) override {
    RegulatedPurePursuitController::configure(parent,name,tf,map);
    auto node=parent.lock();
    nav2_util::declare_parameter_if_not_declared(node,name+".follow_gap_gain",rclcpp::ParameterValue(1.));
    nav2_util::declare_parameter_if_not_declared(node,name+".follow_speed_damping",rclcpp::ParameterValue(.5));
    follow_sub_=parent.lock()->create_subscription<std_msgs::msg::String>("navigation/fleet/follow_context",10,
      [this](std_msgs::msg::String::ConstSharedPtr message){
        try {
          auto value=nlohmann::json::parse(message->data);
          for(const auto key:{"head_x","head_y","distance","speed"})
            if(!value.at(key).is_number()||!std::isfinite(value.at(key).get<double>()))return;
          if(value.contains("range_rate")&&(!value["range_rate"].is_number()||!std::isfinite(value["range_rate"].get<double>())))return;
          if(value.at("distance").get<double>()<0||!value.at("path_stamps").is_array()||!value.at("limit_controller").is_string())return;
          std::lock_guard<std::mutex> lock(follow_mutex_);follow_=std::move(value);
        }catch(const nlohmann::json::exception&){}
      });
  }
  void cleanup() override {terminal_pose_.reset();follow_sub_.reset();RegulatedPurePursuitController::cleanup();}
  void setPlan(const nav_msgs::msg::Path & path) override {
    {
      std::lock_guard<std::mutex> lock(mutex_);
      if(path.poses.empty())terminal_pose_.reset();
      else {const auto & goal=path.poses.back().pose;terminal_pose_.setGoal(goal.position.x,goal.position.y,tf2::getYaw(goal.orientation));}
    }
    RegulatedPurePursuitController::setPlan(path);
  }
  void setSpeedLimit(const double & limit,const bool & percentage) override {
    std::lock_guard<std::mutex> lock(mutex_);follow_speed_limit_=limit;follow_limit_percentage_=percentage;
    RegulatedPurePursuitController::setSpeedLimit(limit,percentage);
  }
  geometry_msgs::msg::TwistStamped computeVelocityCommands(
    const geometry_msgs::msg::PoseStamped & pose, const geometry_msgs::msg::Twist & speed,
    nav2_core::GoalChecker * checker) override {
    syncAdditionalParameters();
    nlohmann::json follow;
    {std::lock_guard<std::mutex> lock(follow_mutex_);follow=follow_;}
    const auto stamp=rclcpp::Time(global_plan_.header.stamp).nanoseconds();
    if(follow.is_object()&&std::find(follow["path_stamps"].begin(),follow["path_stamps"].end(),stamp)!=follow["path_stamps"].end()) {
      terminal_pose_.reset();return followVelocity(pose,speed,follow);
    }
    last_follow_time_=0.;
    geometry_msgs::msg::TwistStamped terminal;
    if(terminalVelocity(pose,checker,terminal))return terminal;
    return RegulatedPurePursuitController::computeVelocityCommands(pose, speed, checker);
  }
protected:
  bool terminalVelocity(const geometry_msgs::msg::PoseStamped & pose,nav2_core::GoalChecker * checker,
    geometry_msgs::msg::TwistStamped & command) {
    if(!checker)return false;
    geometry_msgs::msg::Pose tolerance;geometry_msgs::msg::Twist velocity_tolerance;
    if(!checker->getTolerances(tolerance,velocity_tolerance))return false;
    const double xy=tolerance.position.x,yaw_tolerance=std::abs(tf2::getYaw(tolerance.orientation));
    std::lock_guard<std::mutex> lock(mutex_);
    // Final goal alignment is independent of en-route path-heading rotation.
    if(global_plan_.poses.empty()||xy<=0.||xy>.1||yaw_tolerance<=0.)return false;
    geometry_msgs::msg::PoseStamped global;
    if(!transformPose(global_plan_.header.frame_id,pose,global))throw nav2_core::PlannerException("Terminal pose transform failed");
    const auto & goal=global_plan_.poses.back().pose;
    const double heading=tf2::getYaw(global.pose.orientation),dx=goal.position.x-global.pose.position.x,dy=goal.position.y-global.pose.position.y;
    const double x=std::cos(heading)*dx+std::sin(heading)*dy,y=-std::sin(heading)*dx+std::cos(heading)*dy;
    const double error=std::atan2(std::sin(tf2::getYaw(goal.orientation)-heading),std::cos(tf2::getYaw(goal.orientation)-heading));
    double linear,angular;
    if(!terminal_pose_.command(x,y,error,xy,yaw_tolerance,std::min(.05,desired_linear_vel_),rotate_to_heading_angular_vel_,linear,angular))return false;
    std::unique_lock<nav2_costmap_2d::Costmap2D::mutex_t> map_lock(*costmap_->getMutex());
    if(use_collision_detection_&&isCollisionImminent(pose,linear,angular,std::hypot(x,y)))
      throw nav2_core::PlannerException("Terminal pose detected collision ahead");
    command.header=pose.header;command.twist.linear.x=linear;command.twist.angular.z=angular;return true;
  }
  void syncAdditionalParameters() {
    auto node = node_.lock();
    if (!node) {throw std::runtime_error("RPP parameter node expired");}
    const auto interpolation=node->get_parameter(plugin_name_ + ".use_interpolation").as_bool();
    const auto approach=node->get_parameter(plugin_name_ + ".approach_velocity_scaling_dist").as_double();
    std::lock_guard<std::mutex> lock(mutex_);
    use_interpolation_=interpolation;approach_velocity_scaling_dist_=approach;
  }
  geometry_msgs::msg::TwistStamped followVelocity(const geometry_msgs::msg::PoseStamped & pose,
    const geometry_msgs::msg::Twist & speed,const nlohmann::json & follow) {
    auto node=node_.lock();const auto selected=follow.at("limit_controller").get<std::string>();
    // Parameter callbacks acquire the node parameter lock before mutex_.
    // Read parameters first to keep that same lock order while editing live.
    double vmax=0.,wmax=0.;
    if(!node->get_parameter(selected+".vx_max",vmax)&&!node->get_parameter(selected+".max_vel_x",vmax))
      node->get_parameter(selected+".desired_linear_vel",vmax);
    if(!node->get_parameter(selected+".wz_max",wmax))node->get_parameter(selected+".max_vel_theta",wmax);
    const double gap_gain=node->get_parameter(plugin_name_+".follow_gap_gain").as_double();
    const double damping=node->get_parameter(plugin_name_+".follow_speed_damping").as_double();
    std::lock_guard<std::mutex> lock(mutex_);
    if(vmax<=0.)vmax=desired_linear_vel_;
    if(wmax<=0.)wmax=rotate_to_heading_angular_vel_;
    std::unique_lock<nav2_costmap_2d::Costmap2D::mutex_t> map_lock(*costmap_->getMutex());
    geometry_msgs::msg::PoseStamped global;
    if(!transformPose(global_plan_.header.frame_id,pose,global))throw nav2_core::PlannerException("Follow pose transform failed");
    const double gap=std::hypot(follow.at("head_x").get<double>()-global.pose.position.x,
      follow.at("head_y").get<double>()-global.pose.position.y);
    if(follow_speed_limit_>0.)vmax=std::min(vmax,follow_limit_percentage_?vmax*follow_speed_limit_/100.:follow_speed_limit_);
    const double requested=std::clamp(follow.at("speed").get<double>()+
      gap_gain*(gap-follow.at("distance").get<double>())+damping*follow.value("range_rate",0.),0.,vmax);
    auto path=transformGlobalPlan(pose);
    const double lookahead=getLookAheadDistance(speed);
    auto carrot=getLookAheadPoint(lookahead,path);
    // A moving destination can pass behind the robot before the next path
    // update. Do not turn back towards that expired short endpoint.
    const auto & end=path.poses.back().pose.position;
    if(carrot.pose.position.x<0.&&std::hypot(end.x,end.y)<min_lookahead_dist_) {
      auto head=global;head.pose.position.x=follow.at("head_x").get<double>();head.pose.position.y=follow.at("head_y").get<double>();
      geometry_msgs::msg::PoseStamped local_head;
      if(transformPose(costmap_ros_->getBaseFrameID(),head,local_head)&&local_head.pose.position.x>0.)carrot=local_head;
    }
    carrot_pub_->publish(createCarrotMsg(carrot));
    const double x=carrot.pose.position.x,y=carrot.pose.position.y,r2=x*x+y*y;
    const double curvature=2.*y/std::max(r2,lookahead*lookahead);
    double linear=requested,sign=1.;
    // Keep curvature/obstacle regulation. A moving predecessor is not a
    // stationary terminal goal; range feedback supplies its stopping profile.
    const double cost=costAtPose(pose.pose.position.x,pose.pose.position.y);
    const double approach=approach_velocity_scaling_dist_,desired=desired_linear_vel_;
    approach_velocity_scaling_dist_=0.;desired_linear_vel_=vmax;
    applyConstraints(curvature,speed,cost,path,linear,sign);
    approach_velocity_scaling_dist_=approach;desired_linear_vel_=desired;
    linear=std::min(requested,linear);
    const double angle=std::atan2(y,x);
    linear*=std::max(0.,std::cos(angle));
    double angular=linear*curvature;
    if(x<0.&&requested>0.)angular=2.*angle/lookahead_time_;
    const double now=clock_->now().seconds();
    if(last_follow_time_==0.||now-last_follow_time_>1.)last_follow_angular_=std::clamp(speed.angular.z,-wmax,wmax);
    const double dt=last_follow_time_>0.?std::clamp(now-last_follow_time_,0.,2.*control_duration_):control_duration_;
    angular=std::clamp(angular,last_follow_angular_-max_angular_accel_*dt,last_follow_angular_+max_angular_accel_*dt);
    angular=std::clamp(angular,-wmax,wmax);
    if(requested==0.)angular=0.;
    if(use_collision_detection_&&isCollisionImminent(pose,linear,angular,std::sqrt(r2)))
      throw nav2_core::PlannerException("Real-time follow detected collision ahead");
    last_follow_time_=now;last_follow_angular_=angular;
    geometry_msgs::msg::TwistStamped command;command.header=pose.header;
    command.twist.linear.x=linear;command.twist.angular.z=angular;return command;
  }
private:
  TerminalPose terminal_pose_;
  std::mutex follow_mutex_;
  nlohmann::json follow_;
  double follow_speed_limit_{0.};bool follow_limit_percentage_{false};
  double last_follow_time_{0.},last_follow_angular_{0.};
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr follow_sub_;
};
}
