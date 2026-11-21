#include "omnifleet_planner/publish_native_progress.hpp"
#include "omnifleet_planner/native_waypoint_progress.hpp"
#include <iostream>
#include <stdexcept>
#include <thread>
void check(bool value,const char * label) {if(!value)throw std::runtime_error(label);std::cout<<"PASS "<<label<<std::endl;}
int main(int argc,char ** argv) {
  rclcpp::init(argc,argv);auto node=std::make_shared<rclcpp::Node>("native_progress_integration");
  omnifleet_planner::NativeWaypointProgressState gate;gate.reset(node->get_clock()->now().nanoseconds());
  int received=0;
  auto sub=node->create_subscription<std_msgs::msg::String>("omnifleet_t2/waypoints/native_progress",1,[&](std_msgs::msg::String::ConstSharedPtr m) {
    auto j=nlohmann::json::parse(m->data);gate.observe(j["stamp_ns"],j["remaining"],j["goal_x"],j["goal_y"],j["run_id"]);++received;
  });
  auto bb=BT::Blackboard::create();bb->set("node",node);
  std::vector<geometry_msgs::msg::PoseStamped> goals(4);nav_msgs::msg::Path path;
  geometry_msgs::msg::PoseStamped end;end.pose.position.x=2.;end.pose.position.y=3.;path.poses.push_back(end);
  bb->set("goals",goals);bb->set("path",path);
  BT::BehaviorTreeFactory f;f.registerNodeType<omnifleet_planner::PublishNativeWaypointProgress>("PublishNativeWaypointProgress");
  auto tree=f.createTreeFromText("<root main_tree_to_execute='T'><BehaviorTree ID='T'><PublishNativeWaypointProgress goals='{goals}' path='{path}'/></BehaviorTree></root>",bb);
  auto publish=[&]() {
    int before=received;
    for (int i=0;i<30 && received==before;++i) {check(tree.tickRoot()==BT::NodeStatus::SUCCESS,"publisher tick succeeds");rclcpp::spin_some(node);std::this_thread::sleep_for(std::chrono::milliseconds(20));}
    check(received>before,"progress reaches subscriber");
  };
  publish();check(!gate.canFinish(2.,3.,node->get_clock()->now().nanoseconds()),"closed-loop start at endpoint cannot complete four goals");
  goals.erase(goals.begin());bb->set("goals",goals);publish();check(!gate.canFinish(2.,3.,node->get_clock()->now().nanoseconds()),"two intermediate goals still required");
  goals.erase(goals.begin(),goals.begin()+2);bb->set("goals",goals);publish();check(gate.canFinish(2.,3.,node->get_clock()->now().nanoseconds()),"last goal reached only after intermediate goals removed");
  gate.reset(node->get_clock()->now().nanoseconds());check(!gate.canFinish(2.,3.,node->get_clock()->now().nanoseconds()),"new goal checker reset clears old completion");
  tree.haltTree();sub.reset();node.reset();rclcpp::shutdown();
}
