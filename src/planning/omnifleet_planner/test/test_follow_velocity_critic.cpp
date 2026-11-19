#include "gtest/gtest.h"
#include "omnifleet_planner/follow_velocity_critic.hpp"
#include "nav2_core/controller.hpp"
#include "pluginlib/class_loader.hpp"
#include "tf2_ros/buffer.h"
#include <thread>

class FollowVelocity : public ::testing::Test
{
protected:
  std::shared_ptr<rclcpp_lifecycle::LifecycleNode> parent;
  std::shared_ptr<nav2_costmap_2d::Costmap2DROS> map;
  rclcpp::Node::SharedPtr sender;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher;
  std::unique_ptr<mppi::ParametersHandler> parameters;
  void SetUp() override {
    if(!rclcpp::ok())rclcpp::init(0,nullptr);
    parent=std::make_shared<rclcpp_lifecycle::LifecycleNode>("controller_server",
      rclcpp::NodeOptions().arguments({"--ros-args","--params-file",TEST_YAML}));
    map=std::make_shared<nav2_costmap_2d::Costmap2DROS>("follow_test_map");
    map->set_parameters({rclcpp::Parameter("plugins",std::vector<std::string>{}),
      rclcpp::Parameter("width",6),rclcpp::Parameter("height",6),
      rclcpp::Parameter("origin_x",-3.),rclcpp::Parameter("origin_y",-3.),
      rclcpp::Parameter("resolution",.05),rclcpp::Parameter("footprint",
        "[[0.25,0.185],[0.25,-0.185],[-0.25,-0.185],[-0.25,0.185]]")});
    map->configure();fill(0);
    sender=std::make_shared<rclcpp::Node>("follow_test_sender");
    publisher=sender->create_publisher<std_msgs::msg::String>("navigation/fleet/follow_context",10);
    parameters=std::make_unique<mppi::ParametersHandler>(parent);
  }
  void TearDown() override {map->cleanup();}
  void fill(unsigned char value) {
    auto grid=map->getCostmap();
    std::fill(grid->getCharMap(),grid->getCharMap()+grid->getSizeInCellsX()*grid->getSizeInCellsY(),value);
  }
  void context(bool active,float speed) {
    for(int i=0;i<100 && !publisher->get_subscription_count();++i)
      std::this_thread::sleep_for(std::chrono::milliseconds(10));
    ASSERT_GT(publisher->get_subscription_count(),0u);
    std_msgs::msg::String msg;msg.data=std::string("{\"active\":")+(active?"true":"false")+
      ",\"tracking_speed\":"+std::to_string(speed)+"}";
    publisher->publish(msg);std::this_thread::sleep_for(std::chrono::milliseconds(30));
  }
};

TEST_F(FollowVelocity,MovingReferenceInactiveAndExpiry) {
  mppi::critics::FollowVelocityCritic critic;
  critic.on_configure(parent,"FollowPathMPPI","FollowPathMPPI.FollowVelocityCritic",map,parameters.get());
  mppi::models::State state;state.reset(2,56);
  for(size_t j=0;j<56;++j)state.vx(1,j)=.3;
  mppi::models::Trajectories trajectories;trajectories.reset(2,56);
  mppi::models::Path path;path.reset(2);
  xt::xtensor<float,1> costs=xt::zeros<float>({2});float dt=1.f/15.f;
  mppi::CriticData data{state,trajectories,path,costs,dt,false,nullptr,nullptr,std::nullopt,std::nullopt};
  critic.score(data);EXPECT_FLOAT_EQ(costs(0),0.f);
  context(true,.3);critic.score(data);EXPECT_GT(costs(0),costs(1)+8.f);EXPECT_FALSE(data.fail_flag);
  costs.fill(0);context(false,.3);critic.score(data);EXPECT_FLOAT_EQ(costs(0),0.f);
  context(true,.3);critic.score(data);costs.fill(0);
  std::this_thread::sleep_for(std::chrono::milliseconds(820));
  critic.score(data);EXPECT_FLOAT_EQ(costs(0),0.f);EXPECT_FALSE(data.fail_flag);
}

TEST_F(FollowVelocity,ProductionMPPIStartsInsideSlotToleranceAndRetainsCollisionFailure) {
  pluginlib::ClassLoader<nav2_core::Controller> controllers("nav2_core","nav2_core::Controller");
  pluginlib::ClassLoader<nav2_core::GoalChecker> checkers("nav2_core","nav2_core::GoalChecker");
  auto controller=controllers.createSharedInstance("nav2_mppi_controller::MPPIController");
  auto checker=checkers.createSharedInstance("nav2_controller::SimpleGoalChecker");
  checker->initialize(parent,"test_goal_checker",map);
  auto tf=std::make_shared<tf2_ros::Buffer>(parent->get_clock());
  controller->configure(parent,"FollowPathMPPI",tf,map);controller->activate();
  nav_msgs::msg::Path route;route.header.frame_id="map";route.header.stamp=parent->now();
  for(int j=0;j<=2;++j) {
    geometry_msgs::msg::PoseStamped p;p.header=route.header;
    p.pose.position.x=j*.025;p.pose.orientation.w=1.;route.poses.push_back(p);
  }
  controller->setPlan(route);auto pose=route.poses.front();geometry_msgs::msg::Twist speed;
  context(true,.3);double peak=0.;
  for(int j=0;j<10;++j) {
    context(true,.3);pose.header.stamp=parent->now();
    auto command=controller->computeVelocityCommands(pose,speed,checker.get());
    peak=std::max(peak,command.twist.linear.x);
    EXPECT_TRUE(std::isfinite(command.twist.angular.z));
  }
  std::cout<<"near_slot_reference_0.3_command_peak="<<peak<<std::endl;
  EXPECT_GT(peak,.08);
  fill(nav2_costmap_2d::LETHAL_OBSTACLE);controller->setPlan(route);context(true,.3);
  try {
    controller->computeVelocityCommands(pose,speed,checker.get());FAIL()<<"All colliding trajectories must fail";
  }catch(const std::runtime_error & error) {
    EXPECT_STREQ(error.what(),"Optimizer fail to compute path");
  }
  controller->deactivate();controller->cleanup();
}

TEST_F(FollowVelocity,FormationTracksAngularReferenceWithoutChangingTrailMode) {
  mppi::critics::FollowVelocityCritic critic;
  critic.on_configure(parent,"FollowPathMPPI","FollowPathMPPI.FollowVelocityCritic",map,parameters.get());
  mppi::models::State state;state.reset(3,56);
  for(size_t j=0;j<56;++j){state.wz(0,j)=-.5;state.wz(2,j)=.5;}
  mppi::models::Trajectories trajectories;trajectories.reset(3,56);
  mppi::models::Path path;path.reset(2);
  xt::xtensor<float,1> costs=xt::zeros<float>({3});float dt=1.f/15.f;
  mppi::CriticData data{state,trajectories,path,costs,dt,false,nullptr,nullptr,std::nullopt,std::nullopt};
  context(true,0.);critic.score(data);
  EXPECT_FLOAT_EQ(costs(0),costs(2));costs.fill(0);
  std_msgs::msg::String msg;msg.data=R"({"active":true,"formation":true,"tracking_speed":0,"tracking_angular":0.5})";
  publisher->publish(msg);std::this_thread::sleep_for(std::chrono::milliseconds(50));
  critic.score(data);EXPECT_GT(costs(0),costs(1));EXPECT_GT(costs(1),costs(2));EXPECT_FALSE(data.fail_flag);
}

TEST_F(FollowVelocity,SingleGoalRecoversLateralErrorBeforeFinalHeading) {
  pluginlib::ClassLoader<nav2_core::Controller> controllers("nav2_core","nav2_core::Controller");
  pluginlib::ClassLoader<nav2_core::GoalChecker> checkers("nav2_core","nav2_core::GoalChecker");
  auto controller=controllers.createSharedInstance("nav2_mppi_controller::MPPIController");
  auto checker=checkers.createSharedInstance("nav2_controller::SimpleGoalChecker");
  checker->initialize(parent,"test_goal_checker",map);
  auto tf=std::make_shared<tf2_ros::Buffer>(parent->get_clock());
  controller->configure(parent,"FollowPathMPPI",tf,map);controller->activate();
  nav_msgs::msg::Path route;route.header.frame_id="map";route.header.stamp=parent->now();
  for(int j=0;j<=10;++j) {
    geometry_msgs::msg::PoseStamped p;p.header=route.header;p.pose.position.y=.25*(1.-j/10.);
    const double yaw=j==10?0.:-M_PI/2;p.pose.orientation.z=std::sin(yaw/2);p.pose.orientation.w=std::cos(yaw/2);route.poses.push_back(p);
  }
  controller->setPlan(route);auto pose=route.poses.front();pose.pose.orientation.z=0.;pose.pose.orientation.w=1.;
  geometry_msgs::msg::Twist speed;double yaw=0.,peak=0.,distance=.25;
  context(false,0.);
  for(int j=0;j<160 && distance>.08;++j) {
    pose.header.stamp=parent->now();const auto command=controller->computeVelocityCommands(pose,speed,checker.get()).twist;
    speed=command;const double dt=1./15.;peak=std::max(peak,std::abs(command.angular.z));
    yaw+=command.angular.z*dt;pose.pose.position.x+=command.linear.x*std::cos(yaw)*dt;
    pose.pose.position.y+=command.linear.x*std::sin(yaw)*dt;
    pose.pose.orientation.z=std::sin(yaw/2);pose.pose.orientation.w=std::cos(yaw/2);
    distance=std::hypot(pose.pose.position.x,pose.pose.position.y);
  }
  std::cout<<"lateral_goal_error="<<distance<<" peak_turn="<<peak<<std::endl;
  EXPECT_LT(distance,.08);EXPECT_GT(peak,.1);
  controller->deactivate();controller->cleanup();
}
