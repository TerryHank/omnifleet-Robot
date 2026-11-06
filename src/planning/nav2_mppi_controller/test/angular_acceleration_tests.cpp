// SPDX-License-Identifier: Apache-2.0
#include "gtest/gtest.h"
#include "nav2_mppi_controller/optimizer.hpp"

class AngularProbe : public mppi::Optimizer
{
public:
  void sample(float measured, float target)
  {
    state_.speed.angular.z = measured;
    state_.cwz.fill(target);
    state_.cvx.fill(0.f);
    updateStateVelocities(state_);
  }
  void command(float measured, float target, bool shift)
  {
    state_.speed.angular.z = measured;
    settings_.shift_control_sequence = shift;
    control_sequence_.vx.fill(0.f);
    control_sequence_.wz.fill(target);
    applyControlSequenceConstraints();
  }
  void samplePair(float v, float w, float target_v, float target_w)
  {
    state_.speed.linear.x=v; state_.speed.angular.z=w;
    state_.cvx.fill(target_v); state_.cwz.fill(target_w);
    updateStateVelocities(state_);
  }
  void commandPair(float v, float w, float target_v, float target_w, bool shift)
  {
    state_.speed.linear.x=v; state_.speed.angular.z=w;
    settings_.shift_control_sequence=shift;
    control_sequence_.vx.fill(target_v); control_sequence_.wz.fill(target_w);
    applyControlSequenceConstraints();
  }
  geometry_msgs::msg::Twist issuedTwist()
  {return getControlFromSequenceAsTwist(builtin_interfaces::msg::Time{}).twist;}
  void warmTarget(float target, float forward=0.f)
  {control_sequence_.vx.fill(forward); control_sequence_.wz.fill(target);}
  void primeMap()
  {
    state_.pose.pose.orientation.w = 1.;
    path_.reset(2); path_.x(1) = 2.f;
    generated_trajectories_.x.fill(0.f);
    generated_trajectories_.y.fill(0.f);
    generated_trajectories_.yaws.fill(0.f);
    costs_.fill(0.f); critics_data_.fail_flag = false;
    critic_manager_.evalTrajectoriesScores(critics_data_);
  }
  bool filter()
  {
    for (auto & control : control_history_) {control.wz = -3.f;}
    return selectCollisionFreeControlSequence();
  }
  bool issuedSweepCollides()
  {
    const auto saved = control_sequence_;
    if (settings_.shift_control_sequence) {shiftControlSequence();}
    const auto trajectory = getOptimizedTrajectory();
    control_sequence_ = saved;
    return critic_manager_.trajectoryCollides(trajectory, state_.pose.pose);
  }
  float issued()
  {return getControlFromSequenceAsTwist(builtin_interfaces::msg::Time{}).twist.angular.z;}
  const auto & state() const {return state_;}
  const auto & sequence() const {return control_sequence_;}
  float history() const {return control_history_.back().wz;}
};

class AngularAcceleration : public ::testing::Test
{
protected:
  std::shared_ptr<rclcpp_lifecycle::LifecycleNode> node;
  std::shared_ptr<nav2_costmap_2d::Costmap2DROS> map;
  std::unique_ptr<mppi::ParametersHandler> parameters;
  std::unique_ptr<AngularProbe> optimizer;
  void SetUp() override
  {
    rclcpp::init(0, nullptr);
    node = std::make_shared<rclcpp_lifecycle::LifecycleNode>("angular_acceleration_test");
    node->declare_parameter("controller_frequency", 15.);
    node->declare_parameter("M.model_dt", 1./15.);
    node->declare_parameter("M.batch_size", 2);
    node->declare_parameter("M.time_steps", 30);
    node->declare_parameter("M.az_max", 1.5);
    node->declare_parameter("M.ax_max", .8);
    node->declare_parameter("M.ax_min", -.8);
    node->declare_parameter("M.wz_max", 1.2);
    node->declare_parameter("M.critics", std::vector<std::string>{"CostCritic"});
    node->declare_parameter("M.CostCritic.consider_footprint", true);
    map = std::make_shared<nav2_costmap_2d::Costmap2DROS>("angular_acceleration_map");
    map->set_parameters({rclcpp::Parameter("plugins", std::vector<std::string>{}),
      rclcpp::Parameter("width", 4), rclcpp::Parameter("height", 4),
      rclcpp::Parameter("origin_x", -2.), rclcpp::Parameter("origin_y", -2.),
      rclcpp::Parameter("resolution", .01), rclcpp::Parameter("footprint_padding", 0.),
      rclcpp::Parameter("footprint", "[[0.27,0.205],[0.27,-0.205],[-0.27,-0.205],[-0.27,0.205]]")});
    map->configure(); auto * grid = map->getCostmap();
    std::fill(grid->getCharMap(), grid->getCharMap()+160000, 0);
    parameters = std::make_unique<mppi::ParametersHandler>(node);
    optimizer = std::make_unique<AngularProbe>();
    optimizer->initialize(node, "M", map, parameters.get());
  }
  void TearDown() override
  {
    optimizer.reset(); parameters.reset();
    rclcpp::shutdown(); map.reset(); node.reset();
  }
};

TEST_F(AngularAcceleration, SampledAccelerationAndBrakingUseMeasuredVelocity)
{
  for (float sign : {-1.f, 1.f}) {
    optimizer->sample(0.f, sign*1.2f);
    const auto & acceleration = optimizer->state();
    EXPECT_NEAR(acceleration.wz(0, 1), sign*.1f, 1e-6);
    for (size_t j=1; j<30; ++j) {
      EXPECT_LE(std::abs(acceleration.wz(0,j)-acceleration.wz(0,j-1)), .100001f);
      EXPECT_NEAR(acceleration.cwz(0,j-1), acceleration.wz(0,j), 1e-6);
    }
    optimizer->sample(sign*.6f, 0.f);
    EXPECT_NEAR(optimizer->state().wz(0,1), sign*.5f, 1e-6);
    EXPECT_NEAR(optimizer->state().wz(0,6), 0.f, 1e-6);
  }
}

TEST_F(AngularAcceleration, ReversalBrakesThroughZeroBeforeTurningTheOtherWay)
{
  for (float sign : {-1.f, 1.f}) {
    optimizer->sample(sign*.6f, -sign*1.2f);
    const auto & state = optimizer->state();
    EXPECT_NEAR(state.wz(0,1), sign*.5f, 1e-6);
    EXPECT_NEAR(state.wz(0,6), 0.f, 1e-6);
    EXPECT_NEAR(state.wz(0,7), -sign*.1f, 1e-6);
  }
}

TEST_F(AngularAcceleration, FirstIssuedCommandHasOneStepBudgetWithAndWithoutShift)
{
  for (bool shift : {false, true}) {
    for (float sign : {-1.f, 1.f}) {
      optimizer->command(0.f, sign*1.2f, shift);
      EXPECT_NEAR(optimizer->issued(), sign*.1f, 1e-6);
      optimizer->command(sign*.6f, 0.f, shift);
      EXPECT_NEAR(optimizer->issued(), sign*.5f, 1e-6);
    }
  }
}

TEST_F(AngularAcceleration, FilterCannotBreakRateBoundAndHistoryTracksIssuedCommand)
{
  for (bool shift : {false, true}) {
    optimizer->command(.6f, 0.f, shift);
    optimizer->primeMap(); ASSERT_TRUE(optimizer->filter());
    EXPECT_NEAR(optimizer->issued(), .5f, 1e-6);
    EXPECT_NEAR(optimizer->history(), optimizer->issued(), 1e-6);
    const auto & sequence = optimizer->sequence().wz;
    const size_t first = shift ? 1 : 0;
    for (size_t j=first+1; j<sequence.size(); ++j) {
      EXPECT_LE(std::abs(sequence(j)-sequence(j-1)), .100001f);
    }
  }
}

TEST_F(AngularAcceleration, RepeatedCommandChangesRemainBoundedAcrossCycles)
{
  float measured = .6f;
  for (float target : {0.f, -1.2f, 1.2f, 0.f}) {
    for (int cycle=0; cycle<15; ++cycle) {
      optimizer->command(measured, target, true);
      const float issued = optimizer->issued();
      EXPECT_LE(std::abs(issued-measured), .100001f);
      EXPECT_LE(std::abs(issued), 1.200001f);
      measured = issued;
    }
  }
}

TEST_F(AngularAcceleration, ExistingAzMaxParameterUpdateChangesActualConstraint)
{
  parameters->start();
  ASSERT_TRUE(node->set_parameter(rclcpp::Parameter("M.az_max", .6)).successful);
  optimizer->command(0.f, 1.2f, true);
  EXPECT_NEAR(optimizer->issued(), .04f, 1e-6);
  optimizer->sample(.6f, 0.f);
  EXPECT_NEAR(optimizer->state().wz(0,1), .56f, 1e-6);
}

TEST_F(AngularAcceleration, BrakingSweepDetectsWallThatInstantStopWouldMiss)
{
  unsigned int x,y;
  ASSERT_TRUE(map->getCostmap()->worldToMap(.245, .225, x, y));
  map->getCostmap()->setCost(x,y,254);
  optimizer->command(.6f, 0.f, true); optimizer->primeMap();
  EXPECT_TRUE(optimizer->issuedSweepCollides());
}

TEST_F(AngularAcceleration, FullOptimizerOutputAndDisplayedSweepAgree)
{
  geometry_msgs::msg::PoseStamped pose; pose.header.frame_id="odom"; pose.pose.orientation.w=1.;
  geometry_msgs::msg::Twist speed; speed.angular.z=.8;
  nav_msgs::msg::Path plan; plan.header=pose.header;
  plan.poses.push_back(pose); auto goal=pose; goal.pose.position.x=2.; plan.poses.push_back(goal);
  for (int cycle=0; cycle<8; ++cycle) {
    const auto command=optimizer->evalControl(pose,speed,plan,nullptr);
    EXPECT_LE(std::abs(command.twist.angular.z-speed.angular.z), .100001);
    EXPECT_LE(std::abs(command.twist.linear.x-speed.linear.x), .8/15.+1e-6);
    const auto displayed=optimizer->getOptimizedTrajectory();
    EXPECT_NEAR(displayed(0,2), speed.angular.z/15., 1e-6);
    EXPECT_NEAR(displayed(0,0), speed.linear.x/15., 1e-6);
    speed=command.twist;
  }
}

TEST_F(AngularAcceleration, DelayedFeedbackDoesNotRestartTheIssuedCommandRamp)
{
  parameters->start();
  node->set_parameters({rclcpp::Parameter("M.gamma",0.),rclcpp::Parameter("M.wz_std",.001)});
  geometry_msgs::msg::PoseStamped pose;pose.header.frame_id="odom";pose.pose.orientation.w=1.;
  geometry_msgs::msg::Twist measured;
  nav_msgs::msg::Path plan;plan.header=pose.header;plan.poses.push_back(pose);
  auto goal=pose;goal.pose.position.x=2.;plan.poses.push_back(goal);
  double last=0.;
  for(int cycle=0;cycle<4;++cycle) {
    optimizer->warmTarget(1.2f);
    last=optimizer->evalControl(pose,measured,plan,nullptr).twist.angular.z;
    const auto predicted=optimizer->getOptimizedTrajectory();
    EXPECT_NEAR(predicted(0,2),0.,1e-6);
    EXPECT_LE(std::abs(predicted(1,2)),.1/15.+1e-6);
    std::cout<<"delayed_feedback_ramp_cycle="<<cycle<<" command="<<last<<std::endl;
  }
  EXPECT_GT(last,.2);
}

TEST_F(AngularAcceleration, DelayedPositiveFeedbackDoesNotHoldTheReverseCorrectionPositive)
{
  parameters->start();
  node->set_parameters({rclcpp::Parameter("M.gamma",0.),rclcpp::Parameter("M.wz_std",.001)});
  geometry_msgs::msg::PoseStamped pose;pose.header.frame_id="odom";pose.pose.orientation.w=1.;
  geometry_msgs::msg::Twist measured;measured.angular.z=.6;
  nav_msgs::msg::Path plan;plan.header=pose.header;plan.poses.push_back(pose);
  auto goal=pose;goal.pose.position.x=2.;plan.poses.push_back(goal);
  double last=.6;
  for(int cycle=0;cycle<6;++cycle) {
    optimizer->warmTarget(-1.2f);
    last=optimizer->evalControl(pose,measured,plan,nullptr).twist.angular.z;
    std::cout<<"delayed_feedback_reverse_cycle="<<cycle<<" command="<<last<<std::endl;
  }
  EXPECT_LT(last,.3);
}

TEST_F(AngularAcceleration, SteeringLimitedCommandDoesNotSendFullForwardVelocity)
{
  for(bool shift : {false,true}) {
    optimizer->commandPair(0.f,0.f,.5f,1.f,shift);
    const auto cmd=optimizer->issuedTwist();
    EXPECT_NEAR(cmd.linear.x,.05,1e-6);
    EXPECT_NEAR(cmd.angular.z,.1,1e-6);
    EXPECT_NEAR(cmd.angular.z,2*cmd.linear.x,1e-6);
  }
}

TEST_F(AngularAcceleration, ExistingLinearAccelerationAndBrakingParametersAreApplied)
{
  optimizer->commandPair(0.f,0.f,.5f,0.f,true);
  EXPECT_NEAR(optimizer->issuedTwist().linear.x,.8/15.,1e-6);
  optimizer->commandPair(.4f,0.f,0.f,0.f,true);
  EXPECT_NEAR(optimizer->issuedTwist().linear.x,.4-.8/15.,1e-6);
  optimizer->commandPair(-.4f,0.f,0.f,0.f,true);
  EXPECT_NEAR(optimizer->issuedTwist().linear.x,-.4+.8/15.,1e-6);
}

TEST_F(AngularAcceleration, SampledForwardAndTurnIncrementsKeepTheSameRatio)
{
  optimizer->samplePair(0.f,0.f,.5f,1.f);
  const auto & s=optimizer->state();
  EXPECT_NEAR(s.vx(0,1),.05f,1e-6); EXPECT_NEAR(s.wz(0,1),.1f,1e-6);
  for(size_t j=1;j<30;++j) {
    EXPECT_NEAR(s.wz(0,j),2*s.vx(0,j),1e-6);
    EXPECT_LE(std::abs(s.vx(0,j)-s.vx(0,j-1)),.8f/15.f+1e-6f);
    EXPECT_LE(std::abs(s.wz(0,j)-s.wz(0,j-1)),.100001f);
  }
}

TEST_F(AngularAcceleration, MovingForwardCannotJumpToTargetBeforeSteeringAccelerates)
{
  optimizer->commandPair(.3f,0.f,.5f,1.f,true);
  const auto cmd=optimizer->issuedTwist();
  EXPECT_NEAR(cmd.linear.x,.32,1e-6); EXPECT_NEAR(cmd.angular.z,.1,1e-6);
}

TEST_F(AngularAcceleration, FullOptimizerStartsTheRequestedArcWithCoupledVelocities)
{
  parameters->start();
  node->set_parameters({rclcpp::Parameter("M.gamma",0.),
    rclcpp::Parameter("M.vx_std",.001),rclcpp::Parameter("M.wz_std",.001)});
  geometry_msgs::msg::PoseStamped pose;pose.header.frame_id="odom";pose.pose.orientation.w=1.;
  geometry_msgs::msg::Twist measured;
  nav_msgs::msg::Path plan;plan.header=pose.header;plan.poses.push_back(pose);
  auto goal=pose;goal.pose.position.x=2.;plan.poses.push_back(goal);
  optimizer->warmTarget(1.f,.5f);
  const auto command=optimizer->evalControl(pose,measured,plan,nullptr).twist;
  EXPECT_LT(command.linear.x,.06); EXPECT_GT(command.linear.x,.035);
  EXPECT_GT(command.angular.z,.08); EXPECT_LE(command.angular.z,.100001);
  EXPECT_NEAR(command.angular.z,2*command.linear.x,.003);
  EXPECT_FALSE(optimizer->issuedSweepCollides());
}
