// SPDX-License-Identifier: Apache-2.0
#include "gtest/gtest.h"
#include "nav2_mppi_controller/critics/cost_critic.hpp"
#include <chrono>
#include <iostream>

class NativeSweptCollision : public ::testing::Test
{
protected:
  std::shared_ptr<rclcpp_lifecycle::LifecycleNode> parent;
  std::shared_ptr<nav2_costmap_2d::Costmap2DROS> map;
  std::unique_ptr<mppi::ParametersHandler> parameters;
  std::unique_ptr<mppi::critics::CostCritic> critic;
  mppi::models::State state;
  mppi::models::Trajectories trajectories;
  mppi::models::Path path;
  xt::xtensor<float,1> costs;
  float dt = 1.f/15.f;

  void SetUp() override
  {
    if (!rclcpp::ok()) {rclcpp::init(0,nullptr);}
    parent = std::make_shared<rclcpp_lifecycle::LifecycleNode>("native_sweep_test");
    map = std::make_shared<nav2_costmap_2d::Costmap2DROS>("native_sweep_map");
    map->set_parameters({rclcpp::Parameter("plugins",std::vector<std::string>{}),
      rclcpp::Parameter("width",4),rclcpp::Parameter("height",4),
      rclcpp::Parameter("origin_x",-2.),rclcpp::Parameter("origin_y",-2.),
      rclcpp::Parameter("resolution",.01),rclcpp::Parameter("footprint_padding",0.),
      rclcpp::Parameter("footprint","[[0.27,0.205],[0.27,-0.205],[-0.27,-0.205],[-0.27,0.205]]")});
    map->configure();
    parameters = std::make_unique<mppi::ParametersHandler>(parent);
    state.pose.pose.orientation.w = 1.;
    fill(0);
  }
  void TearDown() override {critic.reset();parameters.reset();map->cleanup();rclcpp::shutdown();}
  void configure(bool footprint=true, bool enabled=true)
  {
    parent->declare_parameter("FollowPathMPPI.CostCritic.consider_footprint",footprint);
    parent->declare_parameter("FollowPathMPPI.CostCritic.enabled",enabled);
    critic = std::make_unique<mppi::critics::CostCritic>();
    critic->on_configure(parent,"FollowPathMPPI","FollowPathMPPI.CostCritic",map,parameters.get());
  }
  void fill(unsigned char cost)
  {
    auto * g = map->getCostmap();
    std::fill(g->getCharMap(),g->getCharMap()+g->getSizeInCellsX()*g->getSizeInCellsY(),cost);
  }
  void obstacle(double x,double y)
  {
    unsigned int mx,my;ASSERT_TRUE(map->getCostmap()->worldToMap(x,y,mx,my));
    map->getCostmap()->setCost(mx,my,254);
  }
  void wall(double x)
  {
    auto * g = map->getCostmap();
    for(unsigned int iy=0;iy<g->getSizeInCellsY();++iy) {
      for(unsigned int ix=0;ix<g->getSizeInCellsX();++ix) {
        double wx,wy;g->mapToWorld(ix,iy,wx,wy);if(wx>=x) {g->setCost(ix,iy,254);}
      }
    }
  }
  mppi::CriticData data(size_t count=2,size_t steps=1)
  {
    trajectories.reset(count,steps);costs=xt::zeros<float>({count});
    path.reset(2);path.x(1)=2.f;
    return {state,trajectories,path,costs,dt,false,nullptr,nullptr,std::nullopt,std::nullopt};
  }
};

TEST_F(NativeSweptCollision,ZeroCenterStillChecksRotatedCorner)
{
  wall(.32);configure();auto d=data();trajectories.yaws(1,0)=-.65f;
  critic->score(d);
  EXPECT_FLOAT_EQ(costs(0),0.f);EXPECT_GT(costs(1),1000.f);EXPECT_FALSE(d.fail_flag);
}

TEST_F(NativeSweptCollision,WholeBodyDetectsObstacleInsideOutline)
{
  obstacle(.13,.09);configure();auto d=data(1);
  critic->score(d);EXPECT_TRUE(d.fail_flag);EXPECT_GT(costs(0),1000.f);
}

TEST_F(NativeSweptCollision,ContinuousRotationDetectsWallBetweenFreeEndpoints)
{
  wall(.32);configure();state.pose.pose.orientation.z=1.;state.pose.pose.orientation.w=0.;
  auto d=data(1);trajectories.yaws(0,0)=static_cast<float>(M_PI/2.);
  critic->score(d);EXPECT_TRUE(d.fail_flag);EXPECT_GT(costs(0),1000.f);
}

TEST_F(NativeSweptCollision,InflatedCellsRemainSoftAndDoNotBecomeNewCollisionGate)
{
  fill(253);configure();auto d=data(1);critic->score(d);
  EXPECT_FALSE(d.fail_flag);EXPECT_LT(costs(0),1000.f);
}

TEST_F(NativeSweptCollision,ExplicitlyDisabledCriticRemainsDisabled)
{
  obstacle(0.,0.);configure(true,false);auto d=data(1);critic->score(d);
  EXPECT_FALSE(d.fail_flag);EXPECT_FLOAT_EQ(costs(0),0.f);
}

TEST_F(NativeSweptCollision,SelectedPointModeRetainsExistingBehavior)
{
  obstacle(.13,.09);configure(false);auto d=data(1);critic->score(d);
  EXPECT_FALSE(d.fail_flag);EXPECT_FLOAT_EQ(costs(0),0.f);
}

TEST_F(NativeSweptCollision,ProductionBatchTimingNearObstacleOutsideOrientedBody)
{
  obstacle(.30,.30);configure();state.pose.pose.orientation.z=std::sin(M_PI/8.);
  state.pose.pose.orientation.w=std::cos(M_PI/8.);auto d=data(1000,56);
  trajectories.yaws.fill(static_cast<float>(M_PI/4.));critic->score(d);EXPECT_FALSE(d.fail_flag);
  const auto start=std::chrono::steady_clock::now();
  for(int i=0;i<5;++i) {costs.fill(0.f);critic->score(d);}
  const double ms=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count()/5.;
  std::cout<<"full_rectangle_sweep_1000x56_ms="<<ms<<std::endl;
  EXPECT_LT(ms,1000./15.);EXPECT_FALSE(d.fail_flag);
}
