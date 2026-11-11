#include "omnifleet_planner/footprint_safe_goal_checker.hpp"
#include "nav2_core/controller.hpp"
#include "nav2_core/exceptions.hpp"
#include "pluginlib/class_loader.hpp"
#include "tf2_ros/buffer.h"
#include <cassert>
#include <cmath>
#include <iostream>
#include <thread>
int main(int argc,char**argv){
 rclcpp::init(0,nullptr);
 auto parent=std::make_shared<rclcpp_lifecycle::LifecycleNode>("controller_server",rclcpp::NodeOptions().arguments({"--ros-args","--params-file",argv[1]}));
 parent->declare_parameter("ordered_test.require_ordered_waypoints",true);
 auto map=std::make_shared<nav2_costmap_2d::Costmap2DROS>("arc_free_map");
 map->declare_parameter("inflation_layer.plugin",std::string("nav2_costmap_2d::InflationLayer"));
 map->set_parameters({rclcpp::Parameter("plugins",std::vector<std::string>{"inflation_layer"}),rclcpp::Parameter("footprint","[[0.25,0.185],[0.25,-0.185],[-0.25,-0.185],[-0.25,0.185]]"),rclcpp::Parameter("width",10),rclcpp::Parameter("height",6),rclcpp::Parameter("origin_x",-2.),rclcpp::Parameter("origin_y",-3.),rclcpp::Parameter("resolution",.05),rclcpp::Parameter("global_frame","map")});map->configure();
 nav2_costmap_2d::Footprint footprint;for(const auto & xy: {std::pair<double,double>{.25,.185},{.25,-.185},{-.25,-.185},{-.25,.185}}){geometry_msgs::msg::Point v;v.x=xy.first;v.y=xy.second;footprint.push_back(v);}map->setRobotFootprint(footprint);
 auto grid=map->getCostmap();std::fill(grid->getCharMap(),grid->getCharMap()+grid->getSizeInCellsX()*grid->getSizeInCellsY(),0);
 auto tf=std::make_shared<tf2_ros::Buffer>(parent->get_clock());
 pluginlib::ClassLoader<nav2_core::Controller> loader("nav2_core","nav2_core::Controller");
 auto controller=loader.createSharedInstance("omnifleet_planner::OrderedMPPI");controller->configure(parent,"FollowPathMPPI",tf,map);controller->activate();
 omnifleet_planner::FootprintSafeGoalChecker ordered,general;ordered.initialize(parent,"ordered_test",map);general.initialize(parent,"general_test",map);assert(ordered.requiresOrderedWaypoints());assert(!general.requiresOrderedWaypoints());
 nav_msgs::msg::Path route;route.header.frame_id="map";route.header.stamp=parent->now();std::vector<double> xs{2.2,0.,3.,0.,2.6};
 for(size_t i=1;i<xs.size();++i){int n=std::ceil(std::abs(xs[i]-xs[i-1])/.05);for(int j=0;j<n;++j){geometry_msgs::msg::PoseStamped p;p.header=route.header;p.pose.position.x=xs[i-1]+(xs[i]-xs[i-1])*j/n;p.pose.orientation.z=1.;route.poses.push_back(p);}}
 auto goal=route.poses.back();goal.pose.position.x=2.6;route.poses.push_back(goal);
 geometry_msgs::msg::PoseStamped pose=route.poses.front();geometry_msgs::msg::Twist speed;geometry_msgs::msg::TwistStamped cmd;
 controller->setPlan(route);
 for(int i=0;i<3;++i){pose.header.stamp=parent->now();cmd=controller->computeVelocityCommands(pose,speed,&ordered);assert(std::isfinite(cmd.twist.linear.x)&&std::isfinite(cmd.twist.angular.z));}
 controller->setPlan(route);pose=route.poses.front();pose.pose.position.y=.31;pose.header.stamp=parent->now();cmd=controller->computeVelocityCommands(pose,speed,&ordered);assert(cmd.twist.linear.x==0.&&cmd.twist.angular.z==0.);
 pose.pose.position.y=0.;pose.header.stamp=parent->now();cmd=controller->computeVelocityCommands(pose,speed,&ordered);assert(std::isfinite(cmd.twist.linear.x));
 controller->setPlan(route);pose=route.poses.front();pose.pose.position.y=.31;pose.header.stamp=parent->now();cmd=controller->computeVelocityCommands(pose,speed,&ordered);assert(cmd.twist.linear.x==0.&&cmd.twist.angular.z==0.);
 std::this_thread::sleep_for(std::chrono::milliseconds(550));pose.header.stamp=parent->now();bool persistent=false;try{controller->computeVelocityCommands(pose,speed,&ordered);}catch(const nav2_core::PlannerException&){persistent=true;}assert(persistent);
 controller->setPlan(route);pose.header.stamp=parent->now();cmd=controller->computeVelocityCommands(pose,speed,&general);assert(std::isfinite(cmd.twist.linear.x));
 controller->deactivate();controller->cleanup();controller.reset();map->cleanup();rclcpp::shutdown();std::cout<<"PASS pluginlib load, configured production MPPI parameters, ordered and unchanged single-point branches; no command publisher or navigation goal\n";
}
