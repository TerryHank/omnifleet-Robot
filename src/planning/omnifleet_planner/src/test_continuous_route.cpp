#include "continuous_route_plugin.cpp"
#include <cassert>
#include <filesystem>
#include <fstream>
#include <iostream>

namespace {
nav_msgs::msg::Path planned_path;
int plans=0,starts=0,halts=0;
bool pending=false;
class Plan : public BT::StatefulActionNode {
 public:
 using BT::StatefulActionNode::StatefulActionNode;
 static BT::PortsList providedPorts(){return {BT::OutputPort<nav_msgs::msg::Path>("path")};}
 BT::NodeStatus value(){if(pending)return BT::NodeStatus::RUNNING;setOutput("path",planned_path);return BT::NodeStatus::SUCCESS;}
 BT::NodeStatus onStart()override{++plans;return value();}
 BT::NodeStatus onRunning()override{return value();}
 void onHalted()override{}
};
class Follow : public BT::StatefulActionNode {
 public:
 using BT::StatefulActionNode::StatefulActionNode;
 static BT::PortsList providedPorts(){return {};}
 BT::NodeStatus onStart()override{++starts;return BT::NodeStatus::RUNNING;}
 BT::NodeStatus onRunning()override{return BT::NodeStatus::RUNNING;}
 void onHalted()override{++halts;}
};
geometry_msgs::msg::PoseStamped pose(double x,double y=0){geometry_msgs::msg::PoseStamped p;p.header.frame_id="route_unit/map";p.pose.position.x=x;p.pose.position.y=y;p.pose.orientation.w=1;return p;}
}

int main(int argc,char**argv){
 setenv("OMNIFLEET_ROUTE_EVIDENCE_DIR","/tmp/omnifleet_route_unit_evidence",1);
 nav_msgs::msg::Path overlapping;
 overlapping.poses={pose(2.6),pose(1.),pose(0.),pose(1.),pose(3.),pose(1.),pose(.02),pose(1.),pose(2.63)};
 auto ends=omnifleet_planner::ContinuousRouteControl::waypoint_ends(overlapping,{pose(0.),pose(3.),pose(.02),pose(2.63)});
 assert((ends==std::vector<size_t>{2,4,6,8}));
 assert(omnifleet_planner::ContinuousRouteControl::segment_reaches(pose(.3),.1,0.,.5,0.,.15));
 assert(!omnifleet_planner::ContinuousRouteControl::segment_reaches(pose(.3),.1,.2,.5,.2,.15));
 rclcpp::init(argc,argv);
 auto node=std::make_shared<rclcpp::Node>("continuous_route_unit");
 auto tf=std::make_shared<tf2_ros::Buffer>(node->get_clock());
 auto grid=nav_msgs::msg::OccupancyGrid();grid.header.frame_id="route_unit/map";grid.info.resolution=.05;grid.info.width=grid.info.height=100;grid.info.origin.position.x=grid.info.origin.position.y=-2.;grid.info.origin.orientation.w=1;grid.data.resize(10000,0);
 auto pub=node->create_publisher<nav_msgs::msg::OccupancyGrid>("/route_unit/global_costmap/costmap",rclcpp::QoS(1).reliable().transient_local());
 auto static_pub=node->create_publisher<nav_msgs::msg::OccupancyGrid>("/route_unit/map",rclcpp::QoS(1).reliable().transient_local());
 auto cloud_pub=node->create_publisher<sensor_msgs::msg::PointCloud2>("/route_unit/navigation/deskewed_points",rclcpp::SensorDataQoS());
 auto deskew_pub=node->create_publisher<std_msgs::msg::String>("/route_unit/navigation/deskew_status",10);
 planned_path.header.frame_id="route_unit/map";for(int i=0;i<=20;++i)planned_path.poses.push_back(pose(i*.05));
 assert(omnifleet_planner::ContinuousRouteControl::path_clear(grid,planned_path,0,0,0));
 const size_t cell=size_t(std::floor(2./grid.info.resolution))*100+size_t(std::floor(2.5/grid.info.resolution));
 grid.data[cell]=100;
 assert(!omnifleet_planner::ContinuousRouteControl::path_clear(grid,planned_path,0,0,0));
 grid.data[cell]=-1;
 assert(!omnifleet_planner::ContinuousRouteControl::path_clear(grid,planned_path,0,0,0));
 assert(omnifleet_planner::ContinuousRouteControl::path_clear(grid,planned_path,0,0,0,true));grid.data[cell]=0;
 // A distant future obstacle is outside the current safety corridor.
 auto long_grid=grid;long_grid.info.width=200;long_grid.data.assign(size_t(long_grid.info.width)*long_grid.info.height,0);
 nav_msgs::msg::Path long_path;long_path.header.frame_id="route_unit/map";for(int i=0;i<=80;++i)long_path.poses.push_back(pose(i*.05));
 const int far_x=std::floor((3.-long_grid.info.origin.position.x)/long_grid.info.resolution),far_y=std::floor((0.-long_grid.info.origin.position.y)/long_grid.info.resolution);
 long_grid.data[size_t(far_y)*long_grid.info.width+far_x]=100;
 assert(omnifleet_planner::ContinuousRouteControl::path_clear(long_grid,long_path,0,0,0,false,2.0));
 assert(!omnifleet_planner::ContinuousRouteControl::path_clear(long_grid,long_path,0,0,0,false,4.0));
 BT::BehaviorTreeFactory factory;factory.registerNodeType<Plan>("Plan");factory.registerNodeType<Follow>("Follow");factory.registerNodeType<omnifleet_planner::ContinuousRouteControl>("ContinuousRouteControl");
 auto bb=BT::Blackboard::create();bb->set("tf_buffer",tf);bb->set<rclcpp::Node::SharedPtr>("node",node);bb->set("goals",std::vector<geometry_msgs::msg::PoseStamped>{pose(.3),pose(.8),pose(1.)});
 {
 auto tree=factory.createTreeFromText(R"(<root main_tree_to_execute="MainTree"><BehaviorTree ID="MainTree"><ContinuousRouteControl goals="{goals}" path="{path}" pass_radius="0.15" allow_unknown="false" global_frame="route_unit/map" base_frame="route_unit/base_link" robot_prefix="route_unit" run_id="unit"><Plan path="{path}"/><Follow/></ContinuousRouteControl></BehaviorTree></root>)",bb);
 auto tick=[&](double x,double y=0){geometry_msgs::msg::TransformStamped t;t.header.frame_id="route_unit/map";t.child_frame_id="route_unit/base_link";t.header.stamp=node->now();t.transform.translation.x=x;t.transform.translation.y=y;t.transform.rotation.w=1.;tf->setTransform(t,"unit",false);grid.header.stamp=node->now();pub->publish(grid);static_pub->publish(grid);sensor_msgs::msg::PointCloud2 cloud;cloud.header.stamp=node->now();cloud.header.frame_id="route_unit/map";cloud.width=2;cloud.height=1;cloud_pub->publish(cloud);std_msgs::msg::String status;status.data="{\"published\":1}";deskew_pub->publish(status);std::this_thread::sleep_for(std::chrono::milliseconds(60));return tree.tickRoot();};
 geometry_msgs::msg::TransformStamped old;old.header.frame_id="route_unit/map";old.child_frame_id="route_unit/base_link";old.header.stamp=node->now()-rclcpp::Duration::from_seconds(.7);old.transform.rotation.w=1.;tf->setTransform(old,"unit",false);
 assert(tree.tickRoot()==BT::NodeStatus::RUNNING);assert(plans==0 && starts==0);
 tick(0);
 assert(tick(1.5)==BT::NodeStatus::FAILURE);assert(plans==0 && starts==0);
 tree.haltTree();
 for(int i=0;i<60 && plans==0;++i)tick(0);
 assert(plans==1 && starts==1);
 assert(std::abs(bb->get<nav_msgs::msg::Path>("continuous_tracking_path").poses.back().pose.position.x-1.)<1e-6);
 tick(.1);std::this_thread::sleep_for(std::chrono::milliseconds(320));tick(.46);
 assert(bb->get<std::vector<geometry_msgs::msg::PoseStamped>>("goals").size()==2);
 assert(bb->get<std::vector<geometry_msgs::msg::PoseStamped>>("continuous_plan_goals").size()==3);
 assert(plans==1 && starts==1 && halts==0);
 assert(std::abs(bb->get<nav_msgs::msg::Path>("continuous_tracking_path").poses.back().pose.position.x-1.)<1e-6);
 // Obstacle invalidates the remaining path: stop follower while replanning.
 grid.data[size_t(std::floor(2./grid.info.resolution))*100+size_t(std::floor(2.8/grid.info.resolution))]=100;pending=true;
 for(int i=0;i<15 && plans<2;++i)tick(.3);
 assert(plans==2 && halts==1);
 // The planner result is authoritative for its current internal costmap. The
 // old published grid remains blocked here and must not immediately veto it.
 planned_path.poses.clear();for(int i=0;i<=20;++i)planned_path.poses.push_back(pose(i*.05));pending=false;assert(tick(.3)==BT::NodeStatus::RUNNING);
 assert(starts==2 && plans==2);
 grid.data[size_t(std::floor(2./grid.info.resolution))*100+size_t(std::floor(2.8/grid.info.resolution))]=0;
 bool evidence=false;for(const auto& file:std::filesystem::directory_iterator("/tmp/omnifleet_route_unit_evidence")){std::ifstream in(file.path());std::string text((std::istreambuf_iterator<char>(in)),{});if(text.find("forward_corridor_blocked")!=std::string::npos&&text.find("\"global_costmap\":{")!=std::string::npos&&text.find("\"static_map\":{")!=std::string::npos&&text.find("\"cloud_points\":2")!=std::string::npos&&text.find("\\\"published\\\":1")!=std::string::npos)evidence=true;}assert(evidence);
 // Deviation stops, never replans a shortcut across the remaining route.
 tick(.3,.1);tick(.3,.2);tick(.3,.3);tick(.3,.4);
 BT::NodeStatus result=BT::NodeStatus::RUNNING;
 for(int i=0;i<22 && result!=BT::NodeStatus::FAILURE;++i)result=tick(.3,.4);
 assert(result==BT::NodeStatus::FAILURE && plans==2);
 tree.haltTree();const int after_deviation=starts;
 for(int i=0;i<60 && starts==after_deviation;++i)tick(.3);
 assert(starts>after_deviation);
 // External cancellation while tracking must also preserve the progress trace.
 tree.haltTree();bool external=false;
 for(const auto& file:std::filesystem::directory_iterator("/tmp/omnifleet_route_unit_evidence")){std::ifstream in(file.path());std::string text((std::istreambuf_iterator<char>(in)),{});if(text.find("external_cancel_or_halt")!=std::string::npos&&text.find("progress_trace")!=std::string::npos)external=true;}
 assert(external);const int after_cancel=starts;for(int i=0;i<60&&starts==after_cancel;++i)tick(.3);assert(starts>after_cancel);
 // Once following started, stale TF remains an immediate failure.
 tf->clear();old.header.stamp=node->now()-rclcpp::Duration::from_seconds(.7);tf->setTransform(old,"unit",false);
 assert(tree.tickRoot()==BT::NodeStatus::FAILURE);
 tree.haltTree();const int prior_starts=starts;
 for(int i=0;i<60 && starts==prior_starts;++i)tick(.3);
 assert(starts>prior_starts);
 // A fresh but implausible localization jump must fail the route.
 assert(tick(1.5)==BT::NodeStatus::FAILURE);
 tree.haltTree();
 }
 rclcpp::shutdown();std::cout<<"PASS: collision interpolation, unknown policy, ordered pass without replan, obstacle stop/replan/resume, deviation stops without shortcut replanning, localization jump stop\n";
}
