#include "continuous_route_plugin.cpp"
#include "ordered_mppi.cpp"
#include <cassert>
#include <fstream>
#include <iostream>

using namespace omnifleet_planner;
namespace {
nav_msgs::msg::Path path;
geometry_msgs::msg::PoseStamped current;
std::shared_ptr<OrderedMPPI> controller;
FootprintSafeGoalChecker* checker;
int plans=0,starts=0,calls=0;
class Plan : public BT::SyncActionNode {
 public:using BT::SyncActionNode::SyncActionNode;
 static BT::PortsList providedPorts(){return {BT::OutputPort<nav_msgs::msg::Path>("path")};}
 BT::NodeStatus tick()override{++plans;setOutput("path",path);return BT::NodeStatus::SUCCESS;}
};
class Follow : public BT::StatefulActionNode {
 public:using BT::StatefulActionNode::StatefulActionNode;
 static BT::PortsList providedPorts(){return {};}
 BT::NodeStatus onStart()override{++starts;return run();}
 BT::NodeStatus onRunning()override{return run();}
 void onHalted()override{}
 BT::NodeStatus run(){auto p=config().blackboard->get<nav_msgs::msg::Path>("continuous_tracking_path");controller->setPlan(p);p.header.stamp=current.header.stamp;controller->setPlan(p);auto command=controller->computeVelocityCommands(current,geometry_msgs::msg::Twist(),checker);assert(std::isfinite(command.twist.linear.x));++calls;return BT::NodeStatus::RUNNING;}
};
}
int main(int argc,char**argv){
 setenv("OMNIFLEET_ROUTE_EVIDENCE_DIR","/home/iecme/robot_backups/route_consistency_20260915/joint-failures",1);
 assert(argc==2);std::ifstream file(argv[1]);char kind;double x,y;std::vector<size_t> ends;
 path.header.frame_id="route_unit/map";
 while(file>>kind>>x>>y){if(kind=='P'){geometry_msgs::msg::PoseStamped p;p.header=path.header;p.pose.position.x=x;p.pose.position.y=y;p.pose.orientation.w=1.;path.poses.push_back(p);}else if(kind=='E')ends.push_back(size_t(x));}
 assert(path.poses.size()==207&&ends.size()==4);
 rclcpp::init(0,nullptr);
 auto node=std::make_shared<rclcpp::Node>("route_joint_bt","/route_unit");
 auto parent=std::make_shared<rclcpp_lifecycle::LifecycleNode>("controller_server","/route_unit");
 parent->declare_parameter("controller_frequency",20.);
 parent->declare_parameter("ordered_test.require_ordered_waypoints",true);
 auto map=std::make_shared<nav2_costmap_2d::Costmap2DROS>("joint_map");
 map->declare_parameter("inflation_layer.plugin",std::string("nav2_costmap_2d::InflationLayer"));
 map->set_parameters({rclcpp::Parameter("plugins",std::vector<std::string>{"inflation_layer"}),rclcpp::Parameter("width",10),rclcpp::Parameter("height",6),rclcpp::Parameter("origin_x",-4.),rclcpp::Parameter("origin_y",-3.),rclcpp::Parameter("resolution",.05),rclcpp::Parameter("global_frame","route_unit/map")});map->configure();
 auto grid=map->getCostmap();std::fill(grid->getCharMap(),grid->getCharMap()+grid->getSizeInCellsX()*grid->getSizeInCellsY(),0);
 auto tf=std::make_shared<tf2_ros::Buffer>(node->get_clock());
 controller=std::make_shared<OrderedMPPI>();controller->configure(parent,"FollowPathMPPI",tf,map);controller->activate();
 FootprintSafeGoalChecker ordered;ordered.initialize(parent,"ordered_test",map);checker=&ordered;
 nav_msgs::msg::OccupancyGrid g;g.header.frame_id=path.header.frame_id;g.info.width=200;g.info.height=120;g.info.resolution=.05;g.info.origin.position.x=-4.;g.info.origin.position.y=-3.;g.info.origin.orientation.w=1.;g.data.assign(24000,0);
 auto pub=node->create_publisher<nav_msgs::msg::OccupancyGrid>("global_costmap/costmap",rclcpp::QoS(1).reliable().transient_local());
 std::vector<nlohmann::json> states,acks;
 auto sub=node->create_subscription<std_msgs::msg::String>("omnifleet_t2/waypoints/execution_state",100,[&](std_msgs::msg::String::ConstSharedPtr m){states.push_back(nlohmann::json::parse(m->data));});
 auto ack=node->create_subscription<std_msgs::msg::String>("omnifleet_t2/waypoints/controller_progress",100,[&](std_msgs::msg::String::ConstSharedPtr m){acks.push_back(nlohmann::json::parse(m->data));});
 BT::BehaviorTreeFactory factory;factory.registerNodeType<Plan>("Plan");factory.registerNodeType<Follow>("Follow");factory.registerNodeType<ContinuousRouteControl>("ContinuousRouteControl");
 auto bb=BT::Blackboard::create();bb->set("tf_buffer",tf);bb->set<rclcpp::Node::SharedPtr>("node",node);std::vector<geometry_msgs::msg::PoseStamped> goals;for(auto i:ends)goals.push_back(path.poses[i]);bb->set("goals",goals);
 {
 auto tree=factory.createTreeFromText(R"(<root main_tree_to_execute="MainTree"><BehaviorTree ID="MainTree"><ContinuousRouteControl goals="{goals}" path="{path}" pass_radius="0.25" global_frame="route_unit/map" base_frame="route_unit/base_link" robot_prefix="route_unit" run_id="joint"><Plan path="{path}"/><Follow/></ContinuousRouteControl></BehaviorTree></root>)",bb);
 auto tick=[&](const geometry_msgs::msg::PoseStamped& pose){current=pose;current.header.stamp=node->now();geometry_msgs::msg::TransformStamped t;t.header=current.header;t.child_frame_id="route_unit/base_link";t.transform.translation.x=pose.pose.position.x;t.transform.translation.y=pose.pose.position.y;t.transform.rotation=pose.pose.orientation;tf->setTransform(t,"joint",false);g.header.stamp=node->now();pub->publish(g);std::this_thread::sleep_for(std::chrono::milliseconds(65));rclcpp::spin_some(node);auto status=tree.tickRoot();rclcpp::spin_some(node);return status;};
 for(int i=0;i<60&&starts==0;++i)assert(tick(path.poses.front())==BT::NodeStatus::RUNNING);
 assert(starts==1);
 for(const auto&p:path.poses)assert(tick(p)==BT::NodeStatus::RUNNING);
 for(int i=0;i<5;++i)tick(path.poses.back());
 assert(plans==1&&starts==1);assert(bb->get<std::vector<geometry_msgs::msg::PoseStamped>>("goals").size()==1);
 assert(acks.size()>100);
 for(const auto&a:acks){assert(a["controller_cursor"]==a["cursor"]);assert(a["controller_progress_m"]==a["progress_m"]);assert(a["path_version"]=="joint:1");}
 // A true transient lateral error pauses both layers, then resumes this task.
 auto offset=path.poses.back();for(double delta:{.1,.2,.31}){offset.pose.position.x=path.poses.back().pose.position.x+delta;offset.pose.position.y=path.poses.back().pose.position.y+delta;assert(tick(offset)==BT::NodeStatus::RUNNING);}
 std::this_thread::sleep_for(std::chrono::milliseconds(70));auto stopped=controller->computeVelocityCommands(current,geometry_msgs::msg::Twist(),checker);assert(stopped.twist.linear.x==0.&&stopped.twist.angular.z==0.);
 offset.pose.position.x=path.poses.back().pose.position.x+.2;offset.pose.position.y=path.poses.back().pose.position.y+.2;assert(tick(offset)==BT::NodeStatus::RUNNING);assert(tick(path.poses.back())==BT::NodeStatus::RUNNING);assert(starts==1);
 for(double delta:{.1,.2,.31}){offset.pose.position.x=path.poses.back().pose.position.x+delta;offset.pose.position.y=path.poses.back().pose.position.y+delta;tick(offset);}
 BT::NodeStatus result=BT::NodeStatus::RUNNING;for(int i=0;i<12&&result!=BT::NodeStatus::FAILURE;++i)result=tick(offset);assert(result==BT::NodeStatus::FAILURE);
 tree.haltTree();
 }
 FootprintSafeGoalChecker general;general.initialize(parent,"general_test",map);controller->setPlan(path);current=path.poses.front();current.header.stamp=node->now();auto ordinary=controller->computeVelocityCommands(current,geometry_msgs::msg::Twist(),&general);assert(std::isfinite(ordinary.twist.linear.x));
 controller->deactivate();controller->cleanup();controller.reset();map->cleanup();rclcpp::shutdown();
 std::cout<<"PASS real BT + MPPI on 207-point geometry; one planner/follower task, identical authoritative cursors, no velocity publisher; acknowledgements="<<acks.size()<<std::endl;
}
