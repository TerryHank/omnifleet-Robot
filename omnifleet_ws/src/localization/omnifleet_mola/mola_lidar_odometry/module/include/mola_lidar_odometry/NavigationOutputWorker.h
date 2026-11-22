#pragma once

#include <mola_lidar_odometry/NavCloudPreparation.h>
#include <mola_lidar_odometry/WorkerPipelineStats.h>
#include <mrpt/core/Clock.h>
#include <condition_variable>
#include <functional>
#include <optional>
#include <thread>

namespace mola
{
/** One active immutable scan and one latest pending scan, outside localization. */
class NavigationOutputWorker
{
 public:
  struct Job
  {
    mrpt::maps::CPointsMap::ConstPtr points;
    mrpt::poses::CPose3D sensor_pose, map_pose;
    mrpt::Clock::time_point stamp;
    std::string reference_frame;
    std::uint64_t epoch = 0;
    double submitted = 0;
  };
  using Cloud = mrpt::maps::CGenericPointsMap::Ptr;
  using Publisher = std::function<void(const Job&, const Cloud&)>;
  using Processor = std::function<Cloud(const Job&)>;
  struct Status
  {
    WorkerPipelineStats::Summary timing;
    std::uint64_t overwritten = 0, invalidated = 0, failed = 0;
    bool pending = false, active = false;
  };
  explicit NavigationOutputWorker(Publisher publish, Processor process = {})
      : publish_(std::move(publish)), process_(std::move(process)), thread_([this]{run();}) {}
  NavigationOutputWorker(const NavigationOutputWorker&) = delete;
  NavigationOutputWorker& operator=(const NavigationOutputWorker&) = delete;
  ~NavigationOutputWorker() { shutdown(); }
  void submit(Job job)
  {
    std::lock_guard<std::mutex> lock(mutex_);
    if (stopping_) return;
    job.epoch = epoch_;
    job.submitted = WorkerPipelineStats::now();
    if (pending_) ++overwritten_;
    pending_ = std::move(job);
    ready_.notify_one();
  }
  void invalidate()
  {
    std::lock_guard<std::mutex> lock(mutex_);
    ++epoch_;
    if (pending_) { ++invalidated_; pending_.reset(); }
  }
  Status status() const
  {
    Status result;
    result.timing=metrics_.summary();
    std::lock_guard<std::mutex> lock(mutex_);
    result.overwritten=overwritten_;result.invalidated=invalidated_;result.failed=failed_;
    result.pending=pending_.has_value();result.active=active_;
    return result;
  }
  /** After the localization producer is drained, finish the latest output and join. */
  void shutdown()
  {
    {
      std::lock_guard<std::mutex> lock(mutex_);
      stopping_=true;
      ready_.notify_one();
    }
    if (thread_.joinable()) thread_.join();
  }
 private:
  void run()
  {
    for (;;) {
      Job job;
      {
        std::unique_lock<std::mutex> lock(mutex_);
        ready_.wait(lock,[this]{return stopping_ || pending_.has_value();});
        if (!pending_) return;
        job=std::move(*pending_);pending_.reset();active_=true;
      }
      const double start=WorkerPipelineStats::now();
      WorkerPipelineStats::Sample sample;
      sample.stamp=mrpt::Clock::toDouble(job.stamp);
      sample.queue_ms=(start-job.submitted)*1000.;
      try {
        Cloud cloud;
        {
          WorkerPipelineStats::Timer timer(sample.ms[WorkerPipelineStats::NavCloud]);
          cloud=process_ ? process_(job) : prepareNavigationCloud(*job.points,job.sensor_pose,job.map_pose);
        }
        // This commit lock makes invalidate linearizable with the publisher's
        // short handoff. The publisher must not read localization state.
        std::lock_guard<std::mutex> lock(mutex_);
        if (job.epoch==epoch_) publish_(job,cloud);
        else ++invalidated_;
      } catch (...) {
        sample.faulted=true;
        std::lock_guard<std::mutex> lock(mutex_);
        ++failed_;
      }
      sample.total_ms=(WorkerPipelineStats::now()-start)*1000.;
      metrics_.record(sample);
      {
        std::lock_guard<std::mutex> lock(mutex_);
        active_=false;
      }
    }
  }
  Publisher publish_;
  Processor process_;
  mutable std::mutex mutex_;
  std::condition_variable ready_;
  std::optional<Job> pending_;
  std::uint64_t epoch_=0,overwritten_=0,invalidated_=0,failed_=0;
  bool stopping_=false,active_=false;
  WorkerPipelineStats metrics_{".navigation"};
  std::thread thread_;
};
}  // namespace mola
