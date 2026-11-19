#include "navigation_policy.cpp"
#include <stdexcept>
#include <iostream>
int recovery_ticks=0, recovery_halts=0, plans=0;
class RecoveryProbe : public BT::StatefulActionNode {
public:
  using BT::StatefulActionNode::StatefulActionNode;
  static BT::PortsList providedPorts(){return {};}
  BT::NodeStatus onStart() override {++recovery_ticks;return BT::NodeStatus::RUNNING;}
  BT::NodeStatus onRunning() override {++recovery_ticks;return BT::NodeStatus::RUNNING;}
  void onHalted() override {++recovery_halts;}
};
void check(bool value, const char * label) {if(!value)throw std::runtime_error(label);std::cout<<"PASS "<<label<<std::endl;}
int main(int argc,char **argv){
 rclcpp::init(argc,argv);
 auto seed=std::make_shared<rclcpp::Node>("policy_test_seed");
 auto bb=BT::Blackboard::create();bb->set("node",seed);
 BT::NodeConfiguration config;config.blackboard=bb;
 auto policy=omnifleet_planner::policy(config);
 auto set=[&](const rclcpp::Parameter &p){check(policy->node->set_parameters_atomically({p}).successful,"parameter accepted");};
 BT::BehaviorTreeFactory f;
 f.registerNodeType<omnifleet_planner::RecoveryAllowed>("RecoveryAllowed");
 f.registerNodeType<omnifleet_planner::ReplanningControl>("ReplanningControl");
 f.registerNodeType<RecoveryProbe>("RecoveryProbe");
 f.registerSimpleAction("PlanProbe",[](BT::TreeNode&){++plans;return BT::NodeStatus::SUCCESS;});
 auto recovery=f.createTreeFromText("<root main_tree_to_execute='T'><BehaviorTree ID='T'><RecoveryAllowed><RecoveryProbe/></RecoveryAllowed></BehaviorTree></root>",bb);
 check(recovery.tickRoot()==BT::NodeStatus::RUNNING,"enabled recovery starts");
 set(rclcpp::Parameter("automatic_recovery",false));
 check(recovery.tickRoot()==BT::NodeStatus::FAILURE && recovery_halts==1,"disable cancels running recovery");
 recovery.haltTree();int prior=recovery_ticks;recovery.tickRoot();check(recovery_ticks==prior,"disabled recovery never starts");
 set(rclcpp::Parameter("automatic_recovery",true));check(recovery.tickRoot()==BT::NodeStatus::RUNNING,"reenable recovery");recovery.haltTree();
 geometry_msgs::msg::PoseStamped goal;bb->set("goal",goal);bb->set("planner",std::string("one"));
 auto plan=f.createTreeFromText("<root main_tree_to_execute='T'><BehaviorTree ID='T'><ReplanningControl goal='{goal}' planner_id='{planner}'><PlanProbe/></ReplanningControl></BehaviorTree></root>",bb);
 set(rclcpp::Parameter("automatic_replanning",false));
 plan.tickRoot();for(int i=0;i<10;++i)plan.tickRoot();check(plans==1,"disabled replan still makes initial plan only");
 goal.pose.position.x=1;bb->set("goal",goal);plan.tickRoot();check(plans==2,"new goal replans while disabled");
 bb->set("planner",std::string("two"));plan.tickRoot();check(plans==3,"new algorithm replans while disabled");
 set(rclcpp::Parameter("automatic_replanning",true));set(rclcpp::Parameter("replanning_interval",0.2));
 std::this_thread::sleep_for(std::chrono::milliseconds(230));plan.tickRoot();check(plans==4,"interval controls repeated planning");
 set(rclcpp::Parameter("replanning_interval",60.0));std::this_thread::sleep_for(std::chrono::milliseconds(230));plan.tickRoot();check(plans==4,"new interval takes effect without restart");
 check(!policy->node->set_parameters_atomically({rclcpp::Parameter("replanning_interval",0.0)}).successful,"reject zero interval");
 plan.haltTree();plan.tickRoot();check(plans==5,"new navigation always plans");
 std::vector<geometry_msgs::msg::PoseStamped> goals(3);
 bb->set("goals",goals);
 auto through=f.createTreeFromText("<root main_tree_to_execute='T'><BehaviorTree ID='T'><ReplanningControl goals='{goals}' planner_id='{planner}'><PlanProbe/></ReplanningControl></BehaviorTree></root>",bb);
 set(rclcpp::Parameter("automatic_replanning",false));
 int before=plans;through.tickRoot();through.tickRoot();check(plans==before+1,"continuous initial plan respects disabled periodic replanning");
 goals.erase(goals.begin());bb->set("goals",goals);through.tickRoot();check(plans==before+2,"passing a waypoint replans remaining goals while periodic replanning is disabled");
 through.tickRoot();check(plans==before+2,"unchanged remaining goals do not cause retry loop");
 set(rclcpp::Parameter("automatic_replanning",true));set(rclcpp::Parameter("replanning_interval",0.2));
 std::this_thread::sleep_for(std::chrono::milliseconds(230));through.tickRoot();check(plans==before+3,"continuous replanning uses the shared interval");
 through.haltTree();
 auto tf=std::make_shared<tf2_ros::Buffer>(seed->get_clock());bb->set("tf_buffer",tf);
 geometry_msgs::msg::TransformStamped transform;transform.header.frame_id="map";
 transform.child_frame_id="base_link";transform.transform.rotation.w=1.;
 tf->setTransform(transform,"formation-test",true);
 f.registerNodeType<omnifleet_planner::FormationPoseReached>("FormationPoseReached");
 auto hold=f.createTreeFromText("<root main_tree_to_execute='T'><BehaviorTree ID='T'><KeepRunningUntilFailure><ReactiveFallback><FormationPoseReached goal='{goal}'/><RecoveryProbe/></ReactiveFallback></KeepRunningUntilFailure></BehaviorTree></root>",bb);
 goal.header.frame_id="map";goal.pose.position.x=.05;goal.pose.orientation.w=1.;bb->set("goal",goal);
 prior=recovery_ticks;hold.tickRoot();check(recovery_ticks==prior,"arrived formation holds without motion controller");
 transform.transform.translation.x=-.05;tf->setTransform(transform,"formation-test",true);
 prior=recovery_ticks;hold.tickRoot();check(recovery_ticks==prior,"arrived slot stays parked across localization noise");
 transform.transform.translation.x=0.;tf->setTransform(transform,"formation-test",true);
 goal.pose.position.x=1.;bb->set("goal",goal);hold.tickRoot();check(recovery_ticks>prior,"moving slot resumes motion controller");
 goal.pose.position.x=.05;goal.pose.orientation.z=std::sin(.5/2);goal.pose.orientation.w=std::cos(.5/2);bb->set("goal",goal);
 prior=recovery_ticks;hold.tickRoot();check(recovery_ticks>prior,"heading error still requires correction");
 goal.pose.orientation.z=0.;goal.pose.orientation.w=1.;bb->set("goal",goal);
 prior=recovery_halts;hold.tickRoot();check(recovery_halts>prior,"arriving slot halts running controller");hold.haltTree();

 auto moving_hold=f.createTreeFromText("<root main_tree_to_execute='T'><BehaviorTree ID='T'><FormationPoseReached goal='{goal}' respect_target_motion='true'/></BehaviorTree></root>",bb);
 auto context_pub=seed->create_publisher<std_msgs::msg::String>("navigation/fleet/follow_context",1);
 auto context_tick=[&](double speed,BT::NodeStatus expected){
   std_msgs::msg::String m;m.data=nlohmann::json{{"speed",speed}}.dump();
   for(int i=0;i<100;++i){context_pub->publish(m);std::this_thread::sleep_for(std::chrono::milliseconds(10));
     if(moving_hold.tickRoot()==expected)return true;}
   return false;
 };
 check(context_tick(.3,BT::NodeStatus::FAILURE),"moving leader keeps motion controller active inside pose tolerance");
 prior=recovery_ticks;hold.tickRoot();check(recovery_ticks==prior,"formation hold behavior stays unchanged");
 check(context_tick(0.,BT::NodeStatus::SUCCESS),"stopped leader allows pose hold");
 moving_hold.haltTree();
 int blocked_plans=0;
 f.registerSimpleAction("BlockedPlan",[&](BT::TreeNode&){++blocked_plans;return BT::NodeStatus::FAILURE;});
 auto waiting=f.createTreeFromText("<root main_tree_to_execute='T'><BehaviorTree ID='T'><KeepRunningUntilFailure><ForceSuccess><Sequence><BlockedPlan/><RecoveryProbe/></Sequence></ForceSuccess></KeepRunningUntilFailure></BehaviorTree></root>",bb);
 prior=recovery_ticks;check(waiting.tickRoot()==BT::NodeStatus::RUNNING,"blocked dynamic plan holds session alive");
 check(recovery_ticks==prior,"blocked plan never starts motion controller");waiting.tickRoot();
 check(blocked_plans==2,"blocked session can evaluate the next target update");waiting.haltTree();
 rclcpp::shutdown();
}
