#include <gtest/gtest.h>
#include <mola_lidar_odometry/WorkerPipelineStats.h>
#include <mola_lidar_odometry/NavCloudPreparation.h>
#include <mola_lidar_odometry/NavigationOutputWorker.h>
#include <future>
#include <iostream>
#include <cmath>

TEST(WorkerPipeline, WindowAndDropReasons)
{
  mola::WorkerPipelineStats stats;
  for (int i=0;i<300;++i) {
    stats.input(100.+i*.1,20.);
    mola::WorkerPipelineStats::Sample sample;
    sample.total_ms=i;sample.ms[mola::WorkerPipelineStats::Gicp]=i;
    sample.queue_ms=i*.1;sample.imu_wait_ms=i*.2;
    stats.record(sample);
  }
  stats.dropped(mola::WorkerPipelineStats::ImuCapacity,3);
  stats.dropped(mola::WorkerPipelineStats::ImuCatchup,5);
  stats.dropped(mola::WorkerPipelineStats::WorkerAccounted,7);
  const auto s=stats.summary();
  EXPECT_EQ(s.window,256u);EXPECT_EQ(s.completed,300u);EXPECT_EQ(s.received,300u);
  EXPECT_EQ(s.last_total_ms,299.);EXPECT_EQ(s.p95_total_ms,286.);
  EXPECT_NEAR(s.mean_total_ms,171.5,1e-9);EXPECT_NEAR(s.input_period_ms,100.,1e-8);
  EXPECT_EQ(s.drops[mola::WorkerPipelineStats::ImuCapacity],3u);
  EXPECT_EQ(s.drops[mola::WorkerPipelineStats::ImuCatchup],5u);
  EXPECT_EQ(s.drops[mola::WorkerPipelineStats::WorkerAccounted],7u);
}

mrpt::maps::CGenericPointsMap::Ptr oldCloud(
    const mrpt::maps::CPointsMap& input,const mrpt::poses::CPose3D& sensor,
    const mrpt::poses::CPose3D& pose)
{
  auto filtered=mrpt::maps::CGenericPointsMap::Create();
  filtered->registerPointFieldsFrom(input);
  auto context=filtered->prepareForInsertPointsFrom(input);
  for (std::size_t i=0;i<input.size();++i) {
    const auto body=sensor.composePoint({input.getPointsBufferRef_x()[i],input.getPointsBufferRef_y()[i],input.getPointsBufferRef_z()[i]});
    if (std::abs(body.x)<.30 && std::abs(body.y)<.235 && body.z<.40) continue;
    filtered->insertPointFrom(i,context);
  }
  auto result=mrpt::maps::CGenericPointsMap::Create();
  result->insertAnotherMap(filtered.get(),pose);
  return result;
}

mrpt::maps::CGenericPointsMap::Ptr inputCloud(std::size_t count)
{
  auto input=mrpt::maps::CGenericPointsMap::Create();
  input->registerField_float("intensity");input->registerField_float("t");
  input->registerField_double("custom_double");input->registerField_uint16("ring");
  input->registerField_uint8("class");input->resize(count);
  for (std::size_t i=0;i<count;++i) {
    input->setPointFast(i,static_cast<float>(static_cast<int>(i%401)-200)*.01f,
        static_cast<float>(static_cast<int>(i%307)-153)*.01f,static_cast<float>(i%79)*.01f);
    input->setPointField_float(i,"intensity",static_cast<float>(i%255));
    input->setPointField_float(i,"t",static_cast<float>(i)*.000001f);
    input->setPointField_double(i,"custom_double",static_cast<double>(i)+.123456789);
    input->setPointField_uint16(i,"ring",i%32);input->setPointField_uint8(i,"class",i%5);
  }
  return input;
}

TEST(NavCloud, FieldsGeometryAndInputOwnership)
{
  const auto input=inputCloud(10000);
  const auto xBefore=input->getPointsBufferRef_x();
  for (const auto& pose: {mrpt::poses::CPose3D(),mrpt::poses::CPose3D(1.,-2.,.3,.7,-.2,.1)}) {
    const mrpt::poses::CPose3D sensor(.1,.2,.3,.1,-.1,.05);
    auto expected=oldCloud(*input,sensor,pose);
    auto actual=mola::prepareNavigationCloud(*input,sensor,pose);
    ASSERT_EQ(actual->size(),expected->size());
    for (std::size_t i=0;i<actual->size();++i) {
      EXPECT_NEAR(actual->getPointsBufferRef_x()[i],expected->getPointsBufferRef_x()[i],1e-6);
      EXPECT_NEAR(actual->getPointsBufferRef_y()[i],expected->getPointsBufferRef_y()[i],1e-6);
      EXPECT_NEAR(actual->getPointsBufferRef_z()[i],expected->getPointsBufferRef_z()[i],1e-6);
    }
    EXPECT_EQ(actual->float_fields(),expected->float_fields());
    EXPECT_EQ(actual->double_fields(),expected->double_fields());
    EXPECT_EQ(actual->uint16_fields(),expected->uint16_fields());
    EXPECT_EQ(actual->uint8_fields(),expected->uint8_fields());
  }
  EXPECT_EQ(input->getPointsBufferRef_x(),xBefore);
  mrpt::maps::CGenericPointsMap empty;
  EXPECT_EQ(mola::prepareNavigationCloud(empty,{},{})->size(),0u);
}

TEST(NavCloud, ComparisonBenchmark)
{
  const auto input=inputCloud(120000);
  const mrpt::poses::CPose3D sensor(.1,.2,.3,.1,-.1,.05),pose(1.,-2.,.3,.7,-.2,.1);
  for (bool optimized: {false,true}) {
    std::size_t points=0;
    const double start=mola::WorkerPipelineStats::now();
    for (int i=0;i<12;++i) {
      auto output=optimized ? mola::prepareNavigationCloud(*input,sensor,pose) : oldCloud(*input,sensor,pose);
      points+=output->size();
    }
    std::cout << "NAV_BENCH " << (optimized?"inplace":"baseline") << " ms="
              << (mola::WorkerPipelineStats::now()-start)*1000./12 << " points=" << points << std::endl;
  }
}

TEST(NavigationOutput, LatestPendingAndSnapshot)
{
  std::promise<void> started, release;
  auto ready=started.get_future();
  auto gate=release.get_future().share();
  std::vector<double> published;
  mola::NavigationOutputWorker worker(
    [&](const auto& job,const auto& cloud) {
      published.push_back(mrpt::Clock::toDouble(job.stamp));
      EXPECT_EQ(job.reference_frame,"map");
      EXPECT_DOUBLE_EQ(job.map_pose.x(),published.back());
      EXPECT_EQ(cloud->size(),job.points->size());
    },
    [&](const auto& job) {
      if (job.map_pose.x()==1.) { started.set_value();gate.wait(); }
      return std::make_shared<mrpt::maps::CGenericPointsMap>(
          *std::dynamic_pointer_cast<const mrpt::maps::CGenericPointsMap>(job.points));
    });
  auto submit=[&](double value) {
    mola::NavigationOutputWorker::Job job;
    job.points=inputCloud(100);job.map_pose.x(value);
    job.stamp=mrpt::Clock::fromDouble(value);job.reference_frame="map";
    worker.submit(job);
    job.map_pose.x(999.);job.reference_frame="changed";
  };
  submit(1.);
  const bool entered=ready.wait_for(std::chrono::seconds(3))==std::future_status::ready;
  if (entered) { submit(2.);submit(3.); }
  release.set_value();worker.shutdown();
  ASSERT_TRUE(entered);
  EXPECT_EQ(published,(std::vector<double>{1.,3.}));
  EXPECT_EQ(worker.status().overwritten,1u);
  EXPECT_EQ(worker.status().timing.completed,2u);
  EXPECT_FALSE(worker.status().active);EXPECT_FALSE(worker.status().pending);
}

TEST(NavigationOutput, InvalidationAndFailure)
{
  std::promise<void> started, release;
  auto ready=started.get_future();auto gate=release.get_future().share();
  std::vector<double> published;
  mola::NavigationOutputWorker worker(
    [&](const auto& job,const auto&) { published.push_back(job.map_pose.x()); },
    [&](const auto& job) {
      if (job.map_pose.x()==1.) { started.set_value();gate.wait(); }
      if (job.map_pose.x()==3.) throw std::runtime_error("test processor failure");
      return inputCloud(10);
    });
  auto submit=[&](double value) {
    mola::NavigationOutputWorker::Job job;job.points=inputCloud(10);job.map_pose.x(value);
    worker.submit(std::move(job));
  };
  submit(1.);
  const bool entered=ready.wait_for(std::chrono::seconds(3))==std::future_status::ready;
  if (entered) { submit(2.);worker.invalidate();submit(3.); }
  release.set_value();worker.shutdown();
  ASSERT_TRUE(entered);
  EXPECT_TRUE(published.empty());
  EXPECT_EQ(worker.status().invalidated,2u);EXPECT_EQ(worker.status().failed,1u);
  EXPECT_EQ(worker.status().timing.completed,2u);
}

