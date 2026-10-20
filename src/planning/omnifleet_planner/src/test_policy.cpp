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
 rclcpp::shutdown();
}
