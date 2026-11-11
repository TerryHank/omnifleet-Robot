#include <limits>
#include "nav2_rotation_shim_controller/nav2_rotation_shim_controller.hpp"
#include "omnifleet_planner/footprint_safe_goal_checker.hpp"
#include "omnifleet_planner/goal_footprint_cost.hpp"
#include "tf2/utils.h"
#include "pluginlib/class_list_macros.hpp"

namespace omnifleet_planner
{
// Use the pose already acquired by controller_server. Querying a new "now"
// transform for the same control cycle can extrapolate ahead of sensor TF.
class PoseRotationShim : public nav2_rotation_shim_controller::RotationShimController
{
public:
  void configure(const rclcpp_lifecycle::LifecycleNode::WeakPtr & parent,std::string name,
    std::shared_ptr<tf2_ros::Buffer> tf,std::shared_ptr<nav2_costmap_2d::Costmap2DROS> map) override {
    nav2_rotation_shim_controller::RotationShimController::configure(parent,name,tf,map);
    auto node=parent.lock();
    nav2_util::declare_parameter_if_not_declared(node,name+".rotation_center_offset_x",rclcpp::ParameterValue(0.));
    nav2_util::declare_parameter_if_not_declared(node,name+".rotation_center_offset_y",rclcpp::ParameterValue(0.));
    node->get_parameter(name+".rotation_center_offset_x",offset_x_);
    node->get_parameter(name+".rotation_center_offset_y",offset_y_);
    node->get_parameter(name+".PathAlignCritic.use_path_orientations",feasible_path_);
  }
  void setPlan(const nav_msgs::msg::Path & path) override {
    const bool point_changed=current_path_.poses.empty() || path.poses.empty() ||
       std::hypot(path.poses.back().pose.position.x-current_path_.poses.back().pose.position.x,
                  path.poses.back().pose.position.y-current_path_.poses.back().pose.position.y)>1e-6;
    if(point_changed)point_approach_direction_=0;
    const bool goal_changed=point_changed ||
       std::abs(angles::shortest_angular_distance(tf2::getYaw(current_path_.poses.back().pose.orientation),
                  tf2::getYaw(path.poses.back().pose.orientation)))>1e-6;
    if(goal_changed)goal_alignment_=false;
    const bool align_path=goal_changed||in_rotation_;
    nav2_rotation_shim_controller::RotationShimController::setPlan(path);approach_plan_=false;
    path_updated_=align_path;
  }

  geometry_msgs::msg::TwistStamped computeVelocityCommands(
    const geometry_msgs::msg::PoseStamped & pose,const geometry_msgs::msg::Twist & velocity,
    nav2_core::GoalChecker * checker) override
  {
    auto owned=dynamic_cast<FootprintSafeGoalChecker *>(checker);
    const bool point_goal=owned && owned->isPointGoalChecker();
    if(owned && (owned->isFleetGoalChecker() || owned->requiresOrderedWaypoints())) {
      in_rotation_=false;
      if(approach_plan_){primary_controller_->setPlan(current_path_);approach_plan_=false;}
      return primary_controller_->computeVelocityCommands(pose,velocity,checker);
    }
    auto in_frame=[&](geometry_msgs::msg::PoseStamped p) {
      p.header.frame_id=current_path_.header.frame_id;p.header.stamp=pose.header.stamp;
      if(p.header.frame_id!=pose.header.frame_id)
        p=tf_->transform(p,pose.header.frame_id,tf2::durationFromSec(.3));
      return p;
    };
    bool detour=false;
    double point_linear_limit=std::numeric_limits<double>::infinity();
    auto slow_point_approach=[&point_linear_limit](geometry_msgs::msg::TwistStamped & command) {
      const double speed=std::abs(command.twist.linear.x);
      if(speed>point_linear_limit) {
        const double scale=point_linear_limit/speed;
        command.twist.linear.x*=scale;
        command.twist.angular.z*=scale;
      }
    };
    try {
      std::lock_guard<std::mutex> lock(mutex_);
      if((point_goal || rotate_to_goal_heading_) && !current_path_.poses.empty()) {
        const auto goal=in_frame(current_path_.poses.back());
        geometry_msgs::msg::Pose tolerance;geometry_msgs::msg::Twist speed;
        checker->getTolerances(tolerance,speed);
        const auto target=center(goal.pose),current=center(pose.pose);
        const double distance=std::hypot(target.x-current.x,target.y-current.y);
        const double position_error=std::hypot(goal.pose.position.x-pose.pose.position.x,
          goal.pose.position.y-pose.pose.position.y);
        const bool position_reached=position_error<=tolerance.position.x;
        if(point_goal) {
          // Leave room for feedback delay and the tracks' travel after a stop.
          point_linear_limit=.10 + .50 * std::max(0., position_error-tolerance.position.x);
        }
        const double angle=angles::shortest_angular_distance(tf2::getYaw(pose.pose.orientation),tf2::getYaw(goal.pose.orientation));
        // Once the requested pose is in tolerance, hold zero while the native
        // goal checker completes its existing checks. Replanning must not push it away.
        if((position_reached || (!point_goal && goal_alignment_)) &&
           (point_goal || std::abs(angle)<=std::abs(tf2::getYaw(tolerance.orientation)))) {
          in_rotation_=false;goal_alignment_=true;phase("hold_goal");
          geometry_msgs::msg::TwistStamped hold;hold.header=pose.header;return hold;
        }
        if(point_goal) {
          if(position_error<=.45) {
            auto command=approach_point(pose,goal,velocity,point_linear_limit);
            last_angular_vel_=command.twist.angular.z;
            return command;
          }
          point_approach_direction_=0;
        }
        if(!point_goal && (position_reached || goal_alignment_)) {
          // Inside the existing XY tolerance, finish yaw with the same bounded
          // in-place turn used for path alignment instead of translating away.
          in_rotation_=false;goal_alignment_=true;phase("align_goal");
          auto command=rotate(angle,pose,velocity);
          last_angular_vel_=command.twist.angular.z;return command;
        }
        // Use the same configured tolerance to hand the final pose to MPPI.
        // Keep that final reference through replans rather than switching back
        // to an approach tangent when the tracked pivot slips.
        if(!point_goal && distance<=tolerance.position.x)goal_alignment_=true;
        if(!point_goal && goal_alignment_) {
          in_rotation_=false;phase("align_goal");
          if(approach_plan_){primary_controller_->setPlan(current_path_);approach_plan_=false;}
          auto command=primary_controller_->computeVelocityCommands(pose,velocity,checker);
          last_angular_vel_=command.twist.angular.z;return command;
        }
      }
      if(path_updated_ && current_path_.poses.size()>1) {
        // A short feasible path can translate before its final in-place turn.
        // Preserve that travel heading when no sample reaches the lookahead.
        auto sampled=current_path_.poses.back();
        bool travel_sample=false;
        const auto & start=current_path_.poses.front().pose.position;
        for(const auto & p:current_path_.poses) {
          const double distance=std::hypot(p.pose.position.x-start.x,p.pose.position.y-start.y);
          if(feasible_path_ && !travel_sample && distance>0.){sampled=p;travel_sample=true;}
          if(distance>=forward_sampling_distance_) {
            sampled=p;break;
          }
        }
        const auto point=in_frame(sampled);
        const auto target=center(point.pose),current=center(pose.pose);
        const double heading=feasible_path_ ? tf2::getYaw(point.pose.orientation) :
          std::atan2(target.y-current.y,target.x-current.x);
        const double angle=angles::shortest_angular_distance(tf2::getYaw(pose.pose.orientation),heading);
        const double threshold=in_rotation_?angular_disengage_threshold_:angular_dist_threshold_;
        if(std::abs(angle)>threshold) {
          phase("align_path");in_rotation_=true;
          auto command=rotate(angle,pose,velocity,point_goal);
          last_angular_vel_=command.twist.angular.z;return command;
        }
        path_updated_=false;
      }
      if(feasible_path_) {
        // A kinematically feasible plan already specifies body heading,
        // including reverse segments. Keep those headings for native MPPI.
        if(approach_plan_){primary_controller_->setPlan(current_path_);approach_plan_=false;}
        in_rotation_=false;phase("track_feasible_path");
        auto command=primary_controller_->computeVelocityCommands(pose,velocity,checker);
        slow_point_approach(command);
        last_angular_vel_=command.twist.angular.z;return command;
      }
    }catch(const std::runtime_error & error) {
      // Keep native obstacle avoidance available when an in-place rotation
      // is obstructed. No collision result is converted into a motion command.
      detour=true;
      if(phase_!="native_detour")RCLCPP_INFO(logger_,"Rotation deferred to native controller: %s",error.what());
      path_updated_=false;
    }
    in_rotation_=false;phase(detour?"native_detour":"track_path");
    if(!approach_plan_ && current_path_.poses.size()>1) {
      auto approach=current_path_;const auto & goal=approach.poses.back().pose.position;
      auto from=approach.poses.front().pose.position;
      for(auto i=approach.poses.rbegin();i!=approach.poses.rend();++i) {
        from=i->pose.position;
        if(std::hypot(goal.x-from.x,goal.y-from.y)>=forward_sampling_distance_)break;
      }
      if(std::hypot(goal.x-from.x,goal.y-from.y)>1e-6) {
        double yaw=std::atan2(goal.y-from.y,goal.x-from.x);
        const auto original=approach.poses.back().pose;
        if(approach.header.frame_id==pose.header.frame_id &&
           std::hypot(original.position.x-pose.pose.position.x,original.position.y-pose.pose.position.y)<.3) {
          const auto a=center(original),b=center(pose.pose);yaw=std::atan2(a.y-b.y,a.x-b.x);
        }
        const double goal_yaw=tf2::getYaw(original.orientation);
        auto & endpoint=approach.poses.back().pose;
        endpoint.position.x+=std::cos(yaw)*offset_x_-std::sin(yaw)*offset_y_-std::cos(goal_yaw)*offset_x_+std::sin(goal_yaw)*offset_y_;
        endpoint.position.y+=std::sin(yaw)*offset_x_+std::cos(yaw)*offset_y_-std::sin(goal_yaw)*offset_x_-std::cos(goal_yaw)*offset_y_;
        auto & q=endpoint.orientation;q.x=q.y=0.;q.z=std::sin(yaw/2);q.w=std::cos(yaw/2);
      }
      // Position tracking uses the approach tangent. Only the dedicated final
      // rotation uses the requested goal yaw, avoiding competing objectives.
      primary_controller_->setPlan(approach);approach_plan_=true;
    }
    auto command=primary_controller_->computeVelocityCommands(pose,velocity,checker);
    slow_point_approach(command);
    last_angular_vel_=command.twist.angular.z;return command;
  }
private:
  geometry_msgs::msg::Point center(const geometry_msgs::msg::Pose & pose) const {
    auto p=pose.position;const double yaw=tf2::getYaw(pose.orientation);
    p.x-=std::cos(yaw)*offset_x_-std::sin(yaw)*offset_y_;
    p.y-=std::sin(yaw)*offset_x_+std::cos(yaw)*offset_y_;return p;
  }
  geometry_msgs::msg::TwistStamped approach_point(
    const geometry_msgs::msg::PoseStamped & pose, const geometry_msgs::msg::PoseStamped & goal,
    const geometry_msgs::msg::Twist & velocity,double linear_limit) {
    const double yaw=tf2::getYaw(pose.pose.orientation);
    const double bearing=std::atan2(goal.pose.position.y-pose.pose.position.y,
                                    goal.pose.position.x-pose.pose.position.x);
    const double forward_error=angles::shortest_angular_distance(yaw,bearing);
    if(point_approach_direction_==0)
      point_approach_direction_=std::abs(forward_error)<=M_PI/2 ? 1 : -1;
    const double heading=point_approach_direction_>0 ? bearing : bearing+M_PI;
    const double error=angles::shortest_angular_distance(yaw,heading);
    const double threshold=in_rotation_ ? angular_disengage_threshold_ : angular_dist_threshold_;
    if(std::abs(error)>threshold) {
      in_rotation_=true;phase("align_point_approach");
      return rotate(error,pose,velocity,true);
    }
    geometry_msgs::msg::TwistStamped command;
    command.header=pose.header;
    command.twist.linear.x=point_approach_direction_*linear_limit*std::cos(error);
    command.twist.angular.z=std::clamp(1.4*error-.2*velocity.angular.z,-.6,.6);
    check_sweep(pose,command.twist);
    in_rotation_=false;phase("approach_point");
    return command;
  }

  geometry_msgs::msg::TwistStamped rotate(double angle,const geometry_msgs::msg::PoseStamped & pose,
    const geometry_msgs::msg::Twist & velocity,bool point_start=false) {
    geometry_msgs::msg::TwistStamped command;
    command.header = pose.header;
    // Predict the remaining turn at the current time, then damp measured spin.
    auto node = node_.lock();
    const double age = std::max(0., (node->now() - rclcpp::Time(pose.header.stamp)).seconds());
    const double remaining = angle - velocity.angular.z * age;
    // Offset the loaded tracks' low-speed breakaway resistance during path alignment.
    const double breakaway = point_start ?
      std::copysign(std::min(.45, 2.5 * std::abs(remaining)), remaining) : 0.;
    const double requested = std::clamp(.8 * remaining + breakaway - .35 * velocity.angular.z,
      -rotate_to_heading_angular_vel_, rotate_to_heading_angular_vel_);
    const double previous = std::isfinite(last_angular_vel_) &&
      std::abs(last_angular_vel_) <= rotate_to_heading_angular_vel_ ? last_angular_vel_ : 0.;
    const double accel = point_start ? 2.0 * max_angular_accel_ : max_angular_accel_;
    const double step = accel * control_duration_;
    command.twist.angular.z = std::clamp(requested, previous - step, previous + step);
    check_sweep(pose,command.twist);
    return command;
  }

  void check_sweep(const geometry_msgs::msg::PoseStamped & pose,const geometry_msgs::msg::Twist & twist) {
    auto grid=costmap_ros_->getCostmap();std::unique_lock<nav2_costmap_2d::Costmap2D::mutex_t> lock(*grid->getMutex());
    const auto pivot=center(pose.pose);const double yaw=tf2::getYaw(pose.pose.orientation);
    const double c=std::cos(yaw),s=std::sin(yaw),v=twist.linear.x,w=twist.angular.z;
    for(double t=0.;t<=simulate_ahead_time_;t+=control_duration_) {
      const double delta=w*t,next=yaw+delta;
      const double x=std::abs(w)<1e-6 ? v*t : v/w*std::sin(delta);
      const double y=std::abs(w)<1e-6 ? 0. : v/w*(1.-std::cos(delta));
      const double cost=goalFootprintCost(grid,costmap_ros_->getRobotFootprint(),
        pivot.x+c*x-s*y+std::cos(next)*offset_x_-std::sin(next)*offset_y_,
        pivot.y+s*x+c*y+std::sin(next)*offset_x_+std::cos(next)*offset_y_,next);
      if(cost<0. || cost>=nav2_costmap_2d::LETHAL_OBSTACLE)
        throw nav2_core::PlannerException("Goal alignment or approach sweep intersects obstacle");
    }
  }
  void phase(const std::string & value) {
    if(value==phase_)return;
    phase_=value;RCLCPP_INFO(logger_,"Single-point MPPI phase: %s",value.c_str());
  }
  std::string phase_;
  bool goal_alignment_{false},approach_plan_{false},feasible_path_{false};
  int point_approach_direction_{0};
  double offset_x_{0.},offset_y_{0.};
};
}
PLUGINLIB_EXPORT_CLASS(omnifleet_planner::PoseRotationShim,nav2_core::Controller)
