#pragma once

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <deque>
#include <time.h>
#include <iomanip>
#include <mutex>
#include <vector>

namespace mola
{
/** Bounded recent-window worker metrics. They never participate in estimation. */
class WorkerPipelineStats
{
 public:
  explicit WorkerPipelineStats(const char* csv_suffix = "") : csv_suffix_(csv_suffix) {}
  enum Phase : std::size_t { StateWait, ImuConsume, Preprocess, Gicp, LocalMap,
                            PosePublish, NavCloud, MapExport, Generators, Deskew, Filter1, Filter2, PhaseCount };
  enum Drop : std::size_t { ImuCapacity, ImuCatchup, WorkerAccounted, DropCount };
  static constexpr std::size_t Capacity = 256;
  static constexpr std::array<const char*, PhaseCount> Names = {
      "state_wait", "imu_consume", "preprocess", "gicp", "local_map",
      "pose_publish", "nav_cloud", "map_export", "generators", "deskew", "filter1", "filter2"};
  struct Sample
  {
    double stamp = 0, imu_wait_ms = 0, queue_ms = 0, total_ms = 0;
    double cpu_ms=0,runnable_wait_ms=0;
    double reference_stamp=0,received_steady=0,ready_steady=0,started_steady=0,completed_steady=0,quality=0;
    int iterations=0,termination=-1;
    bool icp_attempted = false;
    std::size_t pairs = 0;
    std::size_t potential_pairs = 0;
    double geometric_rms_m = 0;
    double mean_covariance_weighted_error = 0;
    std::array<double, 6> initial_pose{};
    std::array<double, 6> final_pose{};
    std::array<double, 3> matched_min{};
    std::array<double, 3> matched_max{};
    std::array<double, PhaseCount> ms{};
    bool faulted = false;
  };
  struct Summary
  {
    std::uint64_t received = 0, completed = 0;
    std::array<std::uint64_t, DropCount> drops{};
    std::size_t window = 0, queue_peak = 0;
    double input_period_ms = 0, last_input_age_ms = 0;
    double last_total_ms = 0, mean_total_ms = 0, p95_total_ms = 0, p99_total_ms = 0;
    double p95_imu_wait_ms = 0, p95_queue_ms = 0, mean_cpu_ms=0, p95_runnable_wait_ms=0;
    std::array<double, PhaseCount> last{}, p95{};
  };
  struct SchedulerSample {
    double cpu_ms=0, wait_ms=0;
    static SchedulerSample read() {
      SchedulerSample result;
#ifdef __linux__
      std::uint64_t cpu=0,wait=0,slices=0;
      std::ifstream stream("/proc/thread-self/schedstat");
      if (stream>>cpu>>wait>>slices) {
        result.cpu_ms=cpu/1e6;result.wait_ms=wait/1e6;
      }
#endif
      return result;
    }
  };
  class Timer
  {
   public:
    explicit Timer(double& output) : output_(output), start_(now()) {}
    Timer(const Timer&) = delete;
    Timer& operator=(const Timer&) = delete;
    ~Timer() { stop(); }
    void stop() { if (active_) { output_ += (now()-start_)*1000.; active_ = false; } }
   private:
    double& output_;
    double start_;
    bool active_ = true;
  };
  static double now()
  {
    return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
  }
  void input(double sensor_stamp, double age_ms)
  {
    std::lock_guard<std::mutex> lock(mutex_);
    ++received_;
    const double dt = sensor_stamp-last_input_stamp_;
    if (last_input_stamp_ > 0 && dt > 0 && dt < 1.)
      input_period_ms_ = input_period_ms_ > 0 ? .9*input_period_ms_+.1*dt*1000. : dt*1000.;
    last_input_stamp_ = sensor_stamp;
    last_input_age_ms_ = age_ms;
  }
  void dropped(Drop kind, std::size_t count = 1)
  {
    std::lock_guard<std::mutex> lock(mutex_);
    drops_[kind] += count;
  }
  void queue(std::size_t size)
  {
    std::lock_guard<std::mutex> lock(mutex_);
    queue_peak_ = std::max(queue_peak_, size);
  }
  void record(const Sample& sample)
  {
    std::lock_guard<std::mutex> lock(mutex_);
    samples_[next_] = sample;
    next_ = (next_+1)%Capacity;
    count_ = std::min(count_+1, Capacity);
    ++completed_;
    if (const char* path=std::getenv("MOLA_WORKER_METRICS_CSV");path && *path) {
      export_samples_.push_back(sample);
      if(export_samples_.size()>20000) export_samples_.pop_front();
    }
  }
  Summary summary() const
  {
    Summary result;
    std::vector<Sample> copy;
    {
      std::lock_guard<std::mutex> lock(mutex_);
      result.received=received_; result.completed=completed_; result.drops=drops_;
      result.window=count_; result.queue_peak=queue_peak_;
      result.input_period_ms=input_period_ms_; result.last_input_age_ms=last_input_age_ms_;
      if (count_) {
        const auto& last=samples_[(next_+Capacity-1)%Capacity];
        result.last=last.ms; result.last_total_ms=last.total_ms;
      }
      copy.assign(samples_.begin(), samples_.begin()+count_);
    }
    std::array<double, Capacity> values;
    const auto percentile = [&copy, &values](auto getter, double fraction) {
      if (copy.empty()) { return 0.; }
      for (std::size_t i = 0; i < copy.size(); ++i) { values[i] = getter(copy[i]); }
      const auto index = static_cast<std::size_t>(fraction * (copy.size() - 1));
      std::nth_element(values.begin(), values.begin() + index, values.begin() + copy.size());
      return values[index];
    };
    result.p95_total_ms=percentile([](const Sample& s){return s.total_ms;},.95);
    for (const auto& sample:copy) result.mean_total_ms += sample.total_ms;
    if (!copy.empty()) result.mean_total_ms /= copy.size();
    result.p99_total_ms=percentile([](const Sample& s){return s.total_ms;},.99);
    result.p95_imu_wait_ms=percentile([](const Sample& s){return s.imu_wait_ms;},.95);
    result.p95_queue_ms=percentile([](const Sample& s){return s.queue_ms;},.95);
    for (std::size_t i=0;i<PhaseCount;++i)
      result.p95[i]=percentile([i](const Sample& s){return s.ms[i];},.95);
    for (const auto& sample:copy) result.mean_cpu_ms+=sample.cpu_ms;
    if (!copy.empty()) result.mean_cpu_ms/=copy.size();
    result.p95_runnable_wait_ms=percentile([](const Sample& s){return s.runnable_wait_ms;},.95);
    return result;
  }
  /** Offline-only CSV of the bounded tail; no file I/O runs in the scan worker. */
  ~WorkerPipelineStats() { writeCSV(); }
  void writeCSV() const
  {
    const char* path=std::getenv("MOLA_WORKER_METRICS_CSV");
    if (!path || !*path) return;
    try {
      std::ofstream stream(std::string(path)+csv_suffix_);
      stream << "stamp,imu_wait_ms,queue_ms,total_ms,faulted,cpu_ms,runnable_wait_ms,reference_stamp,received_steady,ready_steady,started_steady,completed_steady,quality,iterations,termination,icp_attempted,pairs,potential_pairs,geometric_rms_m,mean_covariance_weighted_error";
      for (const auto* prefix : {"initial", "final"}) {
        for (const auto* name : {"x", "y", "z", "yaw", "pitch", "roll"}) {
          stream << ',' << prefix << '_' << name;
        }
      }
      for (const auto* prefix : {"matched_min", "matched_max"}) {
        for (const auto* name : {"x", "y", "z"}) {
          stream << ',' << prefix << '_' << name;
        }
      }
      for (const auto* name:Names) stream << ',' << name << "_ms";
      stream << '\n' << std::setprecision(17);
      std::lock_guard<std::mutex> lock(mutex_);
      const std::size_t first=count_==Capacity ? next_ : 0;
      const auto exportCount=export_samples_.empty()?count_:export_samples_.size();
      for (std::size_t i=0;i<exportCount;++i) {
        const auto& s=export_samples_.empty()?samples_[(first+i)%Capacity]:export_samples_[i];
        stream << s.stamp << ',' << s.imu_wait_ms << ',' << s.queue_ms << ',' << s.total_ms << ',' << s.faulted << ',' << s.cpu_ms << ',' << s.runnable_wait_ms << ',' << s.reference_stamp << ',' << s.received_steady << ',' << s.ready_steady << ',' << s.started_steady << ',' << s.completed_steady << ',' << s.quality << ',' << s.iterations << ',' << s.termination << ',' << s.icp_attempted << ',' << s.pairs << ',' << s.potential_pairs
               << ',' << s.geometric_rms_m << ',' << s.mean_covariance_weighted_error;
        for (const auto& pose : {s.initial_pose, s.final_pose}) {
          for (const auto value : pose) { stream << ',' << value; }
        }
        for (const auto& bounds : {s.matched_min, s.matched_max}) {
          for (const auto value : bounds) { stream << ',' << value; }
        }
        for (const auto value:s.ms) stream << ',' << value;
        stream << '\n';
      }
    } catch (...) { /* Diagnostic output cannot fail shutdown. */ }
  }
 private:
  mutable std::mutex mutex_;
  std::array<Sample, Capacity> samples_{};
  // Trial trace only: bounded to 33 minutes at 10 Hz; recent statistics stay at 256.
  std::deque<Sample> export_samples_;
  std::size_t next_=0,count_=0,queue_peak_=0;
  std::uint64_t received_=0,completed_=0;
  std::array<std::uint64_t, DropCount> drops_{};
  double last_input_stamp_=0,input_period_ms_=0,last_input_age_ms_=0;
  const char* csv_suffix_;
};
}  // namespace mola
