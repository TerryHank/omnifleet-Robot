#include "gtest/gtest.h"
#include "omnifleet_planner/footprint_clearance_critic.hpp"
#include "pluginlib/class_loader.hpp"
#include "nav2_core/controller.hpp"
#include "tf2_ros/buffer.h"
#include <chrono>
#include <algorithm>
#include <cmath>
#include <iostream>

class BodyClearance : public ::testing::Test
{
protected:
  std::shared_ptr<rclcpp_lifecycle::LifecycleNode> parent;
  std::shared_ptr<nav2_costmap_2d::Costmap2DROS> map;
  std::unique_ptr<mppi::ParametersHandler> parameters;
  mppi::critics::FootprintClearanceCritic critic;
  mppi::models::State state;
  mppi::models::Trajectories trajectories;
  mppi::models::Path path;
  xt::xtensor<float,1> costs;
  float dt = 1.f / 15.f;
  std::unique_ptr<pluginlib::ClassLoader<nav2_core::GoalChecker>> checker_loader;
  std::shared_ptr<nav2_core::GoalChecker> checker;

  void SetUp() override {
    if (!rclcpp::ok()) {rclcpp::init(0,nullptr);}
    parent=std::make_shared<rclcpp_lifecycle::LifecycleNode>("footprint_critic_test");
    map=std::make_shared<nav2_costmap_2d::Costmap2DROS>("footprint_critic_map");
    map->set_parameters({rclcpp::Parameter("plugins",std::vector<std::string>{}),
      rclcpp::Parameter("width",4),rclcpp::Parameter("height",4),
      rclcpp::Parameter("origin_x",-2.),rclcpp::Parameter("origin_y",-2.),
      rclcpp::Parameter("resolution",.01),rclcpp::Parameter("footprint_padding",0.),
      rclcpp::Parameter("footprint","[[0.27,0.205],[0.27,-0.205],[-0.27,-0.205],[-0.27,0.205]]")});
    map->configure();
    nav2_costmap_2d::Footprint footprint;
    for (auto xy : {std::pair<double,double>{.27,.205},{.27,-.205},{-.27,-.205},{-.27,.205}}) {
      geometry_msgs::msg::Point p;p.x=xy.first;p.y=xy.second;footprint.push_back(p);
    }
    map->setRobotFootprint(footprint);
    parameters=std::make_unique<mppi::ParametersHandler>(parent);
    critic.on_configure(parent,"FollowPathMPPI","FollowPathMPPI.FootprintClearanceCritic",map,parameters.get());
    checker_loader=std::make_unique<pluginlib::ClassLoader<nav2_core::GoalChecker>>("nav2_core","nav2_core::GoalChecker");
    checker=checker_loader->createSharedInstance("nav2_controller::SimpleGoalChecker");
    checker->initialize(parent,"test_goal_checker",map);
    state.pose.pose.orientation.w=1.;
    fill(0);
  }
  void TearDown() override {map->cleanup();}
  void fill(unsigned char value) {
    auto grid=map->getCostmap();
    std::fill(grid->getCharMap(),grid->getCharMap()+grid->getSizeInCellsX()*grid->getSizeInCellsY(),value);
  }
  void wall(double at, bool vertical=true) {
    auto grid=map->getCostmap();
    for (unsigned int y=0;y<grid->getSizeInCellsY();++y) {
      for (unsigned int x=0;x<grid->getSizeInCellsX();++x) {
        double wx,wy;grid->mapToWorld(x,y,wx,wy);
        if ((vertical?wx:wy)>=at) {grid->setCost(x,y,254);}
      }
    }
  }
  mppi::CriticData data(size_t count=2,size_t steps=1) {
    trajectories.reset(count,steps);costs=xt::zeros<float>({count});
    path.reset(2);path.x(1)=2.f;
    return {state,trajectories,path,costs,dt,false,checker.get(),nullptr,std::nullopt,std::nullopt};
  }
};

TEST_F(BodyClearance,SameCenterDifferentYawExposesCornerPreferenceMissingFromNativeCost) {
  wall(.40);auto d=data();trajectories.yaws(1,0)=-.65;
  pluginlib::ClassLoader<mppi::critics::CriticFunction> native_loader(
    "nav2_mppi_controller","mppi::critics::CriticFunction");
  auto native=native_loader.createSharedInstance("mppi::critics::CostCritic");
  parent->declare_parameter("FollowPathMPPI.CostCritic.consider_footprint",true);
  native->on_configure(parent,"FollowPathMPPI","FollowPathMPPI.CostCritic",map,parameters.get());
  native->score(d);EXPECT_FLOAT_EQ(costs(0),costs(1));EXPECT_FLOAT_EQ(costs(0),0.f);
  critic.score(d);EXPECT_FLOAT_EQ(costs(0),0.f);EXPECT_GT(costs(1),costs(0));
  EXPECT_FALSE(d.fail_flag);
}

TEST_F(BodyClearance,PrefersUnrotatedBodyInNarrowCorridor) {
  wall(.35,false);auto grid=map->getCostmap();
  for(unsigned int y=0;y<grid->getSizeInCellsY();++y) {
    double wx,wy;grid->mapToWorld(0,y,wx,wy);
    if(wy<=-.35) {for(unsigned int x=0;x<grid->getSizeInCellsX();++x) {grid->setCost(x,y,254);}}
  }
  auto d=data();trajectories.yaws(1,0)=.5;
  critic.score(d);EXPECT_FLOAT_EQ(costs(0),0.f);EXPECT_GT(costs(1),costs(0));
}

TEST_F(BodyClearance,PrefersBodyAwayFromWallWithoutRejectingAnyTrajectory) {
  wall(.30,false);auto d=data(2,8);
  for(size_t j=0;j<8;++j) {trajectories.y(1,j)=-.15;}
  critic.score(d);EXPECT_GT(costs(0),costs(1));EXPECT_FALSE(d.fail_flag);
  d.fail_flag=true;critic.score(d);EXPECT_TRUE(d.fail_flag);
}

TEST_F(BodyClearance,ScoresCornerSweepBetweenSafeEndpoints) {
  wall(.32);auto d=data();
  state.pose.pose.orientation.z=1.;state.pose.pose.orientation.w=0.;
  trajectories.yaws(0,0)=static_cast<float>(M_PI);
  trajectories.yaws(1,0)=static_cast<float>(M_PI/2.);
  critic.score(d);
  // The second endpoint fits, but its intermediate corner sweeps through the wall.
  EXPECT_GT(costs(1),costs(0));EXPECT_FALSE(d.fail_flag);
}

TEST_F(BodyClearance,EmptyAndUnknownMapsDoNotAddNewFailureConditions) {
  for(auto value:{0,255}) {
    fill(value);auto d=data();critic.score(d);
    EXPECT_FLOAT_EQ(costs(0),0.f);EXPECT_FALSE(d.fail_flag);
  }
}

TEST_F(BodyClearance,RebuildsFieldWhenCurrentMapChanges) {
  auto d=data();critic.score(d);EXPECT_FLOAT_EQ(costs(0),0.f);
  wall(.30);critic.score(d);EXPECT_GT(costs(0),0.f);
}

TEST_F(BodyClearance,BriefCloseTurnIsNotDilutedByLongClearTail) {
  wall(.40);auto d=data(2,56);
  // First trajectory is clear until a close corner turn in its last rollout.
  trajectories.yaws(0,55)=-.65f;
  // Second trajectory maintains a modest, consistent gap without the close turn.
  for(size_t j=0;j<56;++j) {trajectories.x(1,j)=.04f;}
  critic.score(d);
  EXPECT_GT(costs(0),costs(1));
  EXPECT_FALSE(d.fail_flag);
}

TEST_F(BodyClearance,ProductionBatchTiming) {
  wall(.40);auto d=data(1000,56);
  for(size_t i=0;i<1000;++i) {
    for(size_t j=0;j<56;++j) {
      trajectories.x(i,j)=.1f*std::sin(i*.01f);
      trajectories.y(i,j)=-.5f+j*.02f;
      trajectories.yaws(i,j)=.6f*std::sin(i*.01f+j*.02f);
    }
  }
  critic.score(d);
  auto start=std::chrono::steady_clock::now();
  for(int k=0;k<10;++k) {critic.score(d);}
  double ms=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count()/10.;
  std::cout<<"footprint_clearance_batch_1000x56_ms="<<ms<<std::endl;
  EXPECT_LT(ms,1000./15.);EXPECT_FALSE(d.fail_flag);
}

TEST_F(BodyClearance,NativeMPPIComputesWithSameGlobalPathAndBodyCritic) {
  wall(.28,false);
  parent->declare_parameter("controller_frequency",15.);
  parent->declare_parameter("FollowPathMPPI.model_dt",1./15.);
  parent->declare_parameter("FollowPathMPPI.visualize",false);
  parent->declare_parameter("FollowPathMPPI.CostCritic.consider_footprint",true);
  parent->declare_parameter("FollowPathMPPI.critics",std::vector<std::string>{
    "ConstraintCritic","CostCritic","FootprintClearanceCritic",
    "GoalCritic","PathAlignCritic","PathFollowCritic"});
  pluginlib::ClassLoader<nav2_core::Controller> controllers("nav2_core","nav2_core::Controller");
  pluginlib::ClassLoader<nav2_core::GoalChecker> checkers("nav2_core","nav2_core::GoalChecker");
  auto controller=controllers.createSharedInstance("nav2_mppi_controller::MPPIController");
  auto checker=checkers.createSharedInstance("nav2_controller::SimpleGoalChecker");
  checker->initialize(parent,"smoke_goal_checker",map);
  auto tf=std::make_shared<tf2_ros::Buffer>(parent->get_clock());
  controller->configure(parent,"FollowPathMPPI",tf,map);controller->activate();
  nav_msgs::msg::Path route;route.header.frame_id="map";route.header.stamp=parent->now();
  for(int j=0;j<=40;++j) {
    geometry_msgs::msg::PoseStamped p;p.header=route.header;
    p.pose.position.x=j*.025;p.pose.orientation.w=1.;route.poses.push_back(p);
  }
  controller->setPlan(route);
  auto pose=route.poses.front();geometry_msgs::msg::Twist speed;
  for(int j=0;j<5;++j) {
    pose.header.stamp=parent->now();
    auto command=controller->computeVelocityCommands(pose,speed,checker.get());
    EXPECT_TRUE(std::isfinite(command.twist.linear.x));
    EXPECT_TRUE(std::isfinite(command.twist.angular.z));
  }
  EXPECT_EQ(route.poses.size(),41u);
  controller->deactivate();controller->cleanup();
}

TEST(BodyClearancePlugin,PluginlibCanLoadCritic) {
  pluginlib::ClassLoader<mppi::critics::CriticFunction> loader(
    "nav2_mppi_controller","mppi::critics::CriticFunction");
  EXPECT_NE(loader.createSharedInstance("mppi::critics::FootprintClearanceCritic"),nullptr);
}

TEST_F(BodyClearance,CloseSafeTrajectoryHasBoundedSoftPreference) {
  wall(.28,false);auto d=data(2,56);
  for(size_t j=0;j<56;++j)trajectories.y(1,j)=.05f;
  critic.score(d);
  EXPECT_GT(costs(0),0.f);
  EXPECT_LE(costs(0),12.f);
  EXPECT_LE(costs(1),12.f);
  EXPECT_FALSE(d.fail_flag);
}
