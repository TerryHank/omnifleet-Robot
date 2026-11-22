// SPDX-License-Identifier: Apache-2.0
#include "gtest/gtest.h"
#include "nav2_mppi_controller/tools/swept_footprint_collision.hpp"
#include "nav2_mppi_controller/optimizer.hpp"
#include <random>

namespace
{
nav2_costmap_2d::Footprint rectangle()
{
  nav2_costmap_2d::Footprint fp;
  for (const auto & xy : {std::pair<double,double>{.27,.205},{.27,-.205},{-.27,-.205},{-.27,.205}}) {
    geometry_msgs::msg::Point p;p.x=xy.first;p.y=xy.second;fp.push_back(p);
  }
  return fp;
}
bool cellIntersectsBody(const mppi::SweepPose & p, double x, double y, double res)
{
  const double c=std::cos(p.yaw),s=std::sin(p.yaw),dx=x-p.x,dy=y-p.y,h=res*.5;
  if (std::abs(dx)>.27*std::abs(c)+.205*std::abs(s)+h) {return false;}
  if (std::abs(dy)>.27*std::abs(s)+.205*std::abs(c)+h) {return false;}
  if (std::abs(c*dx+s*dy)>.27+h*(std::abs(c)+std::abs(s))) {return false;}
  if (std::abs(-s*dx+c*dy)>.205+h*(std::abs(c)+std::abs(s))) {return false;}
  return true;
}
}

TEST(SweptGeometry,InteriorInflationUnknownAndMapBounds)
{
  nav2_costmap_2d::Costmap2D map(200,200,.01,-1.,-1.,0);
  mppi::SweptFootprintCollision collision;const mppi::SweepPose p{0.,0.,0.};
  map.setCost(113,109,254);collision.update(&map,rectangle(),false);
  EXPECT_TRUE(collision.collides(p,p));
  map.setCost(113,109,253);collision.update(&map,rectangle(),false);
  EXPECT_FALSE(collision.collides(p,p));
  map.setCost(113,109,255);collision.update(&map,rectangle(),false);
  EXPECT_FALSE(collision.collides(p,p));
  collision.update(&map,rectangle(),true);EXPECT_TRUE(collision.collides(p,p));
  std::fill(map.getCharMap(),map.getCharMap()+40000,0);
  collision.update(&map,rectangle(),false);EXPECT_FALSE(collision.collides({.95,0.,0.},{.95,0.,0.}));
  collision.update(&map,rectangle(),true);EXPECT_TRUE(collision.collides({.95,0.,0.},{.95,0.,0.}));
}

TEST(SweptGeometry,RotationWrapUsesTheShortPhysicalTurn)
{
  nav2_costmap_2d::Costmap2D map(200,200,.01,-1.,-1.,0);
  map.setCost(100,130,254);
  mppi::SweptFootprintCollision collision;collision.update(&map,rectangle(),false);
  EXPECT_FALSE(collision.collides({0.,0.,M_PI-.01},{0.,0.,-M_PI+.01}));
}

TEST(SweptGeometry,NoMissesAgainstDenseContinuousRectangleCellIntersection)
{
  std::mt19937 rng(104);std::uniform_real_distribution<double> pos(-.5,.5),yaw(-M_PI,M_PI),delta(-.08,.08);
  nav2_costmap_2d::Costmap2D map(200,200,.01,-1.,-1.,0);
  mppi::SweptFootprintCollision collision;
  int positive=0;
  for(int scene=0;scene<200;++scene) {
    std::fill(map.getCharMap(),map.getCharMap()+40000,0);
    std::vector<std::pair<double,double>> obstacles;
    for(int k=0;k<10;++k) {
      const unsigned int x=50+rng()%100,y=50+rng()%100;map.setCost(x,y,254);
      double wx,wy;map.mapToWorld(x,y,wx,wy);obstacles.emplace_back(wx,wy);
    }
    const mppi::SweepPose a{pos(rng),pos(rng),yaw(rng)};
    const mppi::SweepPose b{a.x+delta(rng)*.4,a.y+delta(rng)*.4,a.yaw+delta(rng)};
    bool reference=false;
    for(int j=0;j<=200&&!reference;++j) {
      const double t=j/200.;const mppi::SweepPose p{a.x+t*(b.x-a.x),a.y+t*(b.y-a.y),a.yaw+t*(b.yaw-a.yaw)};
      for(const auto & xy:obstacles) {if(cellIntersectsBody(p,xy.first,xy.second,.01)) {reference=true;break;}}
    }
    collision.update(&map,rectangle(),false);
    if(reference) {++positive;EXPECT_TRUE(collision.collides(a,b))<<"scene "<<scene;}
  }
  EXPECT_GT(positive,30);
}

class OutputProbe : public mppi::Optimizer
{
public:
  void prepareCase()
  {
    state_.pose.pose.orientation.w=1.;path_.reset(2);path_.x(1)=2.f;
    state_.cvx.fill(.3f);state_.cvy.fill(0.f);
    for(size_t j=0;j<settings_.time_steps;++j) {state_.cwz(0,j)=1.2f;state_.cwz(1,j)=-1.2f;}
    updateStateVelocities(state_);integrateStateVelocities(generated_trajectories_,state_);
    costs_.fill(0.f);critics_data_.fail_flag=false;
    critic_manager_.evalTrajectoriesScores(critics_data_);updateControlSequence();
  }
  bool select() {return selectCollisionFreeControlSequence();}
  bool outputCollides()
  {
    const auto saved=control_sequence_;if(settings_.shift_control_sequence) {shiftControlSequence();}
    const auto trajectory=getOptimizedTrajectory();control_sequence_=saved;
    return critic_manager_.trajectoryCollides(trajectory,state_.pose.pose);
  }
  bool allFailed() const {return critics_data_.fail_flag;}
  void compareKinematics()
  {
    state_.pose.pose.orientation.w=1.;
    state_.speed.linear.x=.3;state_.speed.angular.z=.6;
    state_.vx.fill(.3f);state_.vy.fill(0.f);state_.wz.fill(.6f);
    control_sequence_.vx.fill(.3f);control_sequence_.vy.fill(0.f);control_sequence_.wz.fill(.6f);
    integrateStateVelocities(generated_trajectories_,state_);const auto optimal=getOptimizedTrajectory();
    for(size_t j=0;j<settings_.time_steps;++j) {
      EXPECT_NEAR(optimal(j,0),generated_trajectories_.x(0,j),1e-6);
      EXPECT_NEAR(optimal(j,1),generated_trajectories_.y(0,j),1e-6);
      EXPECT_NEAR(optimal(j,2),generated_trajectories_.yaws(0,j),1e-6);
    }
  }
};

class OptimizerSweptOutput : public ::testing::Test
{
protected:
  std::shared_ptr<rclcpp_lifecycle::LifecycleNode> parent;
  std::shared_ptr<nav2_costmap_2d::Costmap2DROS> map;
  std::unique_ptr<mppi::ParametersHandler> parameters;
  std::unique_ptr<OutputProbe> optimizer;
  void SetUp() override
  {
    if(!rclcpp::ok()) {rclcpp::init(0,nullptr);}
    parent=std::make_shared<rclcpp_lifecycle::LifecycleNode>("swept_output_test");
    parent->declare_parameter("controller_frequency",15.);
    parent->declare_parameter("M.model_dt",1./15.);parent->declare_parameter("M.time_steps",30);
    parent->declare_parameter("M.batch_size",2);parent->declare_parameter("M.wz_max",1.2);
    parent->declare_parameter("M.critics",std::vector<std::string>{"CostCritic"});
    parent->declare_parameter("M.CostCritic.consider_footprint",true);
    map=std::make_shared<nav2_costmap_2d::Costmap2DROS>("swept_output_map");
    map->set_parameters({rclcpp::Parameter("plugins",std::vector<std::string>{}),
      rclcpp::Parameter("width",4),rclcpp::Parameter("height",4),
      rclcpp::Parameter("origin_x",-2.),rclcpp::Parameter("origin_y",-2.),
      rclcpp::Parameter("resolution",.01),rclcpp::Parameter("footprint_padding",0.),
      rclcpp::Parameter("footprint","[[0.27,0.205],[0.27,-0.205],[-0.27,-0.205],[-0.27,0.205]]")});
    map->configure();auto * g=map->getCostmap();std::fill(g->getCharMap(),g->getCharMap()+160000,0);
    parameters=std::make_unique<mppi::ParametersHandler>(parent);
    optimizer=std::make_unique<OutputProbe>();optimizer->initialize(parent,"M",map,parameters.get());
  }
  void TearDown() override {optimizer.reset();parameters.reset();map->cleanup();rclcpp::shutdown();}
};

TEST_F(OptimizerSweptOutput,WeightedMeanCannotReintroduceCollisionAfterSafeSamples)
{
  unsigned int x,y;ASSERT_TRUE(map->getCostmap()->worldToMap(.55,0.,x,y));map->getCostmap()->setCost(x,y,254);
  optimizer->prepareCase();ASSERT_FALSE(optimizer->allFailed());ASSERT_TRUE(optimizer->outputCollides());
  ASSERT_TRUE(optimizer->select());EXPECT_FALSE(optimizer->outputCollides());
}

TEST_F(OptimizerSweptOutput,OptimizedDisplayAndSampleRolloutsUseSameKinematics)
{
  optimizer->compareKinematics();
}
