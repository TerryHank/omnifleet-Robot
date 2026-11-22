#include <gtest/gtest.h>
#include <mola_kernel/MinimalModuleContainer.h>
#include <mola_lidar_odometry/LidarOdometry.h>
#include <mola_state_estimation_simple/StateEstimationSimple.h>
#include <mola_yaml/yaml_helpers.h>
#include <mrpt/maps/CGenericPointsMap.h>
#include <mrpt/obs/CObservationPointCloud.h>
#include <cstdlib>
#include <thread>

class IcpBudgetRecovery : public ::testing::Test {
protected:
  std::shared_ptr<mola::LidarOdometry> lo;
  std::shared_ptr<mola::state_estimation_simple::StateEstimationSimple> estimator;
  std::unique_ptr<mola::MinimalModuleContainer> modules;
  double stamp=0;
  void SetUp() override {
    setenv("MOLA_ICP_MAX_TIME_MS","200",1);
    setenv("MOLA_LIDAR_MAX_AGE_MS","0",1);
    setenv("MOLA_OPTIMIZE_TWIST","false",1);
    setenv("MOLA_LOCALMAP_CLASS","mola::IncrementalPointCloud",1);
    setenv("MOLA_LOCALMAP_APPROXIMATE_COV","false",1);
    setenv("MOLA_TBB_THREADS","2",1);
    setenv("MOLA_WITH_GUI","false",1);
    setenv("MOLA_SAVE_MM","",1);
    setenv("MOLA_LO_PUBLISH_DESKEWED_SCANS","false",1);
    setenv("MOLA_LO_PUBLISH_NAVIGATION_DESKEWED_SCANS","false",1);
    lo=mola::LidarOdometry::Create();estimator=mola::state_estimation_simple::StateEstimationSimple::Create();
    modules=std::make_unique<mola::MinimalModuleContainer>(std::initializer_list<mola::ExecutableBase::Ptr>{lo,estimator});
    lo->initialize(mola::load_yaml_file(BUDGET_PIPELINE));
    lo->params_.simplemap.generate=false;lo->params_.estimated_trajectory.output_file.clear();
    lo->params_.lidar_sensor_labels.assign(1,std::regex("lidar"));
    estimator->initialize(mola::load_yaml_file(BUDGET_ESTIMATOR));
    stamp=mrpt::Clock::nowDouble();
  }
  void TearDown() override {
    unsetenv("MOLA_TEST_GICP_DELAY_MS");lo.reset();estimator.reset();modules.reset();
  }
  void scan(double sensor_x) {
    auto points=mrpt::maps::CGenericPointsMap::Create();points->registerField_float("t");points->resize(3*31*21);std::size_t index=0;
    for(int plane=0;plane<3;++plane)for(int a=-15;a<=15;++a)for(int b=-10;b<=10;++b){
      float x,y,z;
      if(plane==0){x=3.;y=.13f*a;z=.09f*b;}
      else if(plane==1){x=.13f*a;y=2.5;z=.09f*b;}
      else{x=.13f*a;y=.13f*b;z=1.5;}
      points->setPointFast(index,x-sensor_x,y,z);points->setPointField_float(index,"t",0.f);++index;
    }
    auto obs=mrpt::obs::CObservationPointCloud::Create();obs->pointcloud=points;obs->sensorLabel="lidar";
    stamp+=.1;obs->timestamp=mrpt::Clock::fromDouble(stamp);lo->onNewObservation(obs);
    const auto deadline=std::chrono::steady_clock::now()+std::chrono::seconds(5);
    while(lo->isBusy()&&std::chrono::steady_clock::now()<deadline)std::this_thread::sleep_for(std::chrono::milliseconds(1));
    ASSERT_FALSE(lo->isBusy());
  }
};
TEST_F(IcpBudgetRecovery, CompletedLateResultsKeepUpdatingTrajectory) {
  scan(0.);scan(0.);const auto initial=lo->estimatedTrajectory().size();ASSERT_GT(initial,1u);
  setenv("MOLA_TEST_GICP_DELAY_MS","220",1);
  for(int i=0;i<4;++i)scan(0.);
  EXPECT_GE(lo->estimatedTrajectory().size(),initial+3);
}
TEST_F(IcpBudgetRecovery, InterruptedRegistrationResumesInsteadOfRepeatingFrozenGuess) {
  scan(0.);scan(0.);const auto initial=lo->estimatedTrajectory().size();ASSERT_GT(initial,1u);
  setenv("MOLA_TEST_GICP_DELAY_MS","220",1);
  for(int i=0;i<6;++i)scan(.05);
  const auto trajectory=lo->estimatedTrajectory();ASSERT_GT(trajectory.size(),initial);
  EXPECT_NEAR(trajectory.rbegin()->second.x,.05,.02);
}
TEST_F(IcpBudgetRecovery, LateUnmatchedResultsStillFailExistingQualityCheck) {
  scan(0.);scan(0.);const auto initial=lo->estimatedTrajectory().size();ASSERT_GT(initial,1u);
  setenv("MOLA_TEST_GICP_DELAY_MS","220",1);
  for(int i=0;i<3;++i)scan(20.);
  EXPECT_EQ(lo->estimatedTrajectory().size(),initial);
}
