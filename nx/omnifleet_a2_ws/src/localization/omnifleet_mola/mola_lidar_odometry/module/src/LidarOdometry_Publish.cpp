/*               _
 _ __ ___   ___ | | __ _
| '_ ` _ \ / _ \| |/ _` | Modular Optimization framework for
| | | | | | (_) | | (_| | Localization and mApping (MOLA)
|_| |_| |_|\___/|_|\__,_| https://github.com/MOLAorg/mola

 Copyright (C) 2018-2026 Jose Luis Blanco, University of Almeria,
                         and individual contributors.
 SPDX-License-Identifier: GPL-3.0
 See LICENSE for full license information.
 Closed-source licenses available upon request, for this odometry package
 alone or in combination with the complete SLAM system.
*/

/**
 * @file   LidarOdometry.cpp
 * @brief  Main C++ class exposing LIDAR odometry
 * @author Jose Luis Blanco Claraco
 * @date   Sep 16, 2023
 */

// This module:
#include <mola_lidar_odometry/LidarOdometry.h>

// MRPT:
#include <mrpt/io/CMemoryStream.h>
#include <mrpt/core/get_env.h>
#include <mrpt/maps/CSimplePointsMap.h>
#include <cmath>
#include <mrpt/serialization/CArchive.h>
#include <mrpt/system/datetime.h>

#include <iomanip>
#include <limits>
#include <sstream>

// MOLA:
#include <mola_kernel/version.h>

// SFINAE to detect for mp2p_icp map metadata:
namespace
{
// clang-format off
template <typename T, typename = void> struct has_metadata_field : std::false_type {};
template <typename T> struct has_metadata_field<T, std::void_t<decltype(T::metadata)>> : std::true_type {};

template <typename T, typename = void> struct has_map_metadata_field : std::false_type {};
template <typename T> struct has_map_metadata_field<T, std::void_t<decltype(T::map_metadata)>> : std::true_type {};
// clang-format on
}  // namespace

namespace mola
{

void LidarOdometry::doPublishUpdatedLocalization(const mrpt::Clock::time_point & scan_ref_time)
{
  const ProfilerEntry tle(profiler_, "advertiseUpdatedLocalization");

  LocalizationUpdate lu;
  lu.method = "lidar_odometry";
  lu.reference_frame = params_.publish_reference_frame;
  lu.child_frame = params_.publish_vehicle_frame;
  lu.timestamp = scan_ref_time;
  lu.pose = state_.last_lidar_pose.mean.asTPose();
  lu.cov = state_.last_lidar_pose.cov;
  lu.quality = state_.last_icp_quality;

  corrected_stamp_=mrpt::Clock::toDouble(scan_ref_time);
  advertiseUpdatedLocalization(lu);
}

void LidarOdometry::doPublishUpdatedLocalMap(const mrpt::Clock::time_point & scan_ref_time)
{
  // Publish geo-referenced data for the map, if applicable.
  publishMetricMapGeoreferencingData();

  if (!state_.local_map_needs_publish) {
    return;
  }

  if (
    state_.localmap_advertise_updates_counter++ <
    params_.local_map_updates.publish_map_updates_every_n) {
    return;
  }

  // === This was ===
  // Don't publish if nobody is listening, OR, if it is still
  // pending to subscribe to us:
  //if (!anyUpdateMapSubscriber()) { return; }
  // ================
  // However, DON'T do this, since if publishing to ROS, latched messages
  // from a once-at-start-up publication would be expected.

  state_.local_map_needs_publish = false;

  const ProfilerEntry tleCleanup(profiler_, "doPublishUpdatedLocalMap");
  state_.localmap_advertise_updates_counter = 0;

  MapUpdate mu;
  mu.method = "lidar_odometry";
  mu.reference_frame = params_.publish_reference_frame;
  mu.timestamp = scan_ref_time;

  // publish all local map layers:
  // make map *copies* to make this multithread safe.
  // This is costly for large maps (!). That's why we decimate sending
  // map notifications and check for anyUpdateMapSubscriber() above.
  for (const auto & [layerName, layerMap] : state_.local_map->layers) {
    mu.map_name = layerName;

    // Bound the visualization copy independently of the full ICP reference.
    if (auto pts = std::dynamic_pointer_cast<mrpt::maps::CPointsMap>(layerMap);
        pts && std::string(pts->GetRuntimeClass()->className) == "mola::IncrementalPointCloud") {
      const auto limit = std::max<size_t>(1, mrpt::get_env<size_t>("MOLA_LOCALMAP_VIZ_MAX_POINTS_OVERALL", 500000));
      const auto stride = std::max<size_t>(1, (pts->size() + limit - 1) / limit);
      auto copy = mrpt::maps::CSimplePointsMap::Create();
      copy->reserve(std::min(pts->size(), limit));
      for (size_t i = 0; i < pts->size(); i += stride) {
        float x, y, z;
        pts->getPointFast(i, x, y, z);
        if (std::isfinite(x) && std::isfinite(y) && std::isfinite(z)) copy->insertPointFast(x, y, z);
      }
      mu.map = copy;
    }
    // Make a copy of the maps:
    else if (auto mapPts = std::dynamic_pointer_cast<mrpt::maps::CPointsMap>(layerMap);
        mapPts) {  // point cloud maps:
      auto mapCopy = std::dynamic_pointer_cast<mrpt::maps::CPointsMap>(
        mrpt::rtti::classFactory(layerMap->GetRuntimeClass()->className));
      ASSERT_(mapCopy);
      mapCopy->insertAnotherMap(mapPts.get(), mrpt::poses::CPose3D::Identity());

      mu.map = mapCopy;
    }
    // classes implementing getAsSimplePointsMap()
    else if (auto * auxPts = layerMap->getAsSimplePointsMap(); auxPts) {
      auto mapCopy = mrpt::maps::CSimplePointsMap::Create();
      mapCopy->insertAnotherMap(auxPts, mrpt::poses::CPose3D::Identity());

      mu.map = mapCopy;
    } else {
      // Any other class: make a deep copy.
      mrpt::io::CMemoryStream buf;
      auto ar = mrpt::serialization::archiveFrom(buf);
      ar << *layerMap;
      buf.Seek(0);
      auto out = ar.ReadObject();

      mu.map = std::dynamic_pointer_cast<mrpt::maps::CMetricMap>(out);
      ASSERT_(mu.map);
    }

    // send it out:
    advertiseUpdatedMap(mu);

    MRPT_LOG_DEBUG_STREAM("Published map layer: '" << layerName << "'");
  }

  // And publish the map metadata (added in mp2p_icp>=1.7.0)
  {
    std::stringstream ss;
    state_.local_map->metadata.printAsYAML(
      ss, mrpt::containers::YamlEmitOptions{.emitHeader = false});
    mu.map_name = "metadata";
    mu.map_metadata = ss.str();
    mu.map.reset();  // no map, just metadata
    advertiseUpdatedMap(mu);
  }
}

void LidarOdometry::doPublishDeskewedScan(const mrpt::Clock::time_point & scan_ref_time)
{
  const auto deskewedScan =
    params_.publish_navigation_deskewed_scans
      ? state_.last_navigation_deskewed_scan_for_publishing
      : state_.last_deskewed_scan_for_publishing;
  if (!deskewedScan) {
    return;
  }

  state_.last_deskewed_scan_for_publishing.reset();
  state_.last_navigation_deskewed_scan_for_publishing.reset();

  // Don't publish if nobody is listening, OR, if it is still
  // pending to subscribe to us:
  if (!anyUpdateMapSubscriber()) {
    MRPT_LOG_DEBUG("doPublishDeskewedScan: Skipping, since we have no subscriber.");
    return;
  }

  const ProfilerEntry tleCleanup(profiler_, "doPublishDeskewedScan");

  MapUpdate mu;
  mu.method = "lidar_odometry";
  mu.reference_frame = params_.publish_reference_frame;
  mu.timestamp = scan_ref_time;
  mu.map_name = "deskewed_scan";
  mu.map = deskewedScan;
  mu.keep_last_one_only = false;  // Aggregate all scans

  // send it out:
  advertiseUpdatedMap(mu);

  MRPT_LOG_DEBUG("Published deskewed map");
}

void LidarOdometry::publishMetricMapGeoreferencingData()
{
  if (!state_.local_map) {
    return;
  }

  if (!state_.local_map->georeferencing.has_value()) {
    // no geo-ref data
    return;
  }
  const auto & g = state_.local_map->georeferencing.value();

  if (!state_.local_map_georef_needs_publish) {
    return;
  }

  // === This was ===
  // Don't publish if nobody is listening, OR, if it is still
  // pending to subscribe to us:
  //if (!anyUpdateMapSubscriber()) { return; }
  // ================
  // However, DON'T do this, since if publishing to ROS, latched messages
  // from a once-at-start-up publication would be expected.

  state_.local_map_georef_needs_publish = false;

  // Hand the map geo-reference to the state estimator so it can convert GNSS
  // fixes into map-frame constraints. This is a no-op for estimators that do
  // not support GNSS/geo-referencing (default NavStateFilter implementation).
  // Note: the map stores an mp2p_icp georef; copy it into the mola_kernel type.
  if (state_.navstate_fuse) {
    mola::Georeferencing georef;
    georef.geo_coord = g.geo_coord;
    georef.T_enu_to_map = g.T_enu_to_map;
#if defined(MOLA_KERNEL_NAVSTATE_FILTER_HAS_GEO_REFERENCE)
    state_.navstate_fuse->set_geo_reference(georef);
#endif
  }

  // This will publish geo-ref data via mola_kernel API as mrpt_nav_interfaces::msg::GeoreferencingMetadata

  MRPT_LOG_DEBUG_STREAM(
    "Publishing map georeferencing metadata: T_enu_to_map="
    << g.T_enu_to_map.asString()                           //
    << " geo_coord.lat=" << g.geo_coord.lat.getAsString()  //
    << " geo_coord.lon=" << g.geo_coord.lon.getAsString()  //
    << " geo_coord.height=" << g.geo_coord.height          //
  );

  MapUpdate mu;
  mu.method = "lidar_odometry";
  mu.reference_frame = params_.publish_reference_frame;
  mu.timestamp = mrpt::Clock::now();
  mu.map_name = "georef";

  auto & georef = mu.georeferencing.emplace();
  georef.T_enu_to_map = g.T_enu_to_map;
  georef.geo_coord = g.geo_coord;

  // send it out:
  advertiseUpdatedMap(mu);
}

void LidarOdometry::onPublishDiagnostics()
{
  std::unique_lock<std::recursive_mutex> scanOwner(scan_owner_mtx_);
  auto lckState = mrpt::lockHelper(state_mtx_);

  const auto curStamp = state_.last_obs_timestamp ? *state_.last_obs_timestamp : mrpt::Clock::now();

  mrpt::containers::yaml diagValues = mrpt::containers::yaml::Map();

  const double dtAvr = profiler_.getMeanTime("onLidar");

  diagValues["icp_quality"] = state_.last_icp_quality;
  diagValues["average_process_time"] = dtAvr;
  diagValues["dropped_frames_ratio"] = getDropStats();
  diagValues["parameters"] = getModuleParameters();

  DiagnosticsOutput diag;
  diag.timestamp = curStamp;
  diag.label = "status";
  diag.value = diagValues;

  module_publish_diagnostics(diag);
}

#if MOLA_HAS_DIAGNOSTICS_PROVIDER
namespace
{
mola::DiagnosticKeyValue kv_d(const std::string & key, double value, int precision = 3)
{
  std::ostringstream ss;
  ss.precision(precision);
  ss << std::fixed << value;
  return {key, ss.str()};
}
mola::DiagnosticKeyValue kv_u(const std::string & key, std::size_t value)
{
  return {key, std::to_string(value)};
}
mola::DiagnosticLevel worst(mola::DiagnosticLevel a, mola::DiagnosticLevel b)
{
  using L = mola::DiagnosticLevel;
  auto rank = [](L x) {
    switch (x) {
      case L::OK:
        return 0;
      case L::WARN:
        return 1;
      case L::STALE:
        return 2;
      case L::ERROR:
        return 3;
    }
    return 0;
  };
  return rank(a) >= rank(b) ? a : b;
}
}  // namespace

void LidarOdometry::refreshDiagnosticsSnapshot()
{
  std::vector<mola::DiagnosticStatusMsg> status;
  const auto worker = worker_pipeline_stats_.summary();
  const auto nav = navigation_output_.status();
  using L = mola::DiagnosticLevel;

  std::unique_lock<std::recursive_mutex> scanOwner(scan_owner_mtx_);

  auto lckState = mrpt::lockHelper(state_mtx_);

  const auto & th = params_.diagnostics;
  const auto now = mrpt::Clock::now();
  // Use wall-clock reception time to avoid false positives when sensor
  // hardware clocks are not synchronized to system time.
  const double lastObsAgeSec =
    state_.last_obs_reception_time
      ? mrpt::system::timeDifference(*state_.last_obs_reception_time, now)
      : std::numeric_limits<double>::infinity();

  const double icpQ = state_.last_icp_quality;
  const double lifetimeMean = profiler_.getMeanTime("onLidar");
  const double dtAvr = worker.window ? worker.mean_total_ms/1000. : lifetimeMean;
  const double droppedRatio = getDropStats();
  const std::size_t startIndex = status.size();
  const double processedPeriod = state_.last_observed_scan_period_sec;
  const double sensorPeriod = worker.input_period_ms > 0 ? worker.input_period_ms/1000. : processedPeriod;

  // 1) Input Data
  {
    mola::DiagnosticStatusMsg s;
    s.name = "LidarOdometry: Input Data";
    if (!state_.last_obs_reception_time) {
      s.level = L::STALE;
      s.message = "No observations received yet";
    } else if (lastObsAgeSec > th.input_error_sec) {
      s.level = L::ERROR;
      s.message = "No observations for >" + std::to_string(th.input_error_sec) + "s";
    } else if (lastObsAgeSec > th.input_stale_sec) {
      s.level = L::STALE;
      s.message = "Input appears stale";
    } else if (droppedRatio > th.dropped_ratio_error) {
      s.level = L::ERROR;
      s.message = "Very high frame drop rate";
    } else if (droppedRatio > th.dropped_ratio_warn) {
      s.level = L::WARN;
      s.message = "High frame drop rate";
    } else {
      s.level = L::OK;
      s.message = "Nominal";
    }
    s.values.push_back(kv_d("last_obs_age_sec", lastObsAgeSec));
    s.values.push_back(kv_d("dropped_ratio", droppedRatio));
    status.push_back(std::move(s));
  }

  // 2) ICP Quality
  {
    mola::DiagnosticStatusMsg s;
    s.name = "LidarOdometry: ICP Quality";
    if (!state_.last_icp_timestamp) {
      s.level = L::STALE;
      s.message = "No ICP result yet";
    } else if (state_.last_icp_budget_interrupted) {
      s.level = L::WARN;
      s.message = "ICP budget interrupted; retaining internal progress for retry";
    } else if (icpQ < th.icp_quality_error) {
      s.level = L::ERROR;
      s.message = "ICP quality critically low";
    } else if (icpQ < th.icp_quality_warn) {
      s.level = L::WARN;
      s.message = "ICP quality degraded";
    } else {
      s.level = L::OK;
      s.message = "Nominal";
    }
    s.values.push_back(kv_d("quality", icpQ));
    s.values.push_back(kv_u("last_icp_iterations", state_.last_icp_iterations));
    s.values.push_back({"last_icp_was_good", state_.last_icp_was_good ? "true" : "false"});
    s.values.push_back({"budget_interrupted", state_.last_icp_budget_interrupted ? "true" : "false"});
    s.values.push_back(kv_u("budget_overruns", state_.registration_icp_budget_overruns));
    s.values.push_back(kv_u("budget_resumes", state_.registration_icp_budget_resumes));
    status.push_back(std::move(s));
  }

  // 3) Timing
  {
    mola::DiagnosticStatusMsg s;
    s.name = "LidarOdometry: Timing";
    const double util = (sensorPeriod > 0) ? (dtAvr / sensorPeriod) : 0.0;
    if (sensorPeriod > 0 && util > th.timing_utilization_warn) {
      s.level = L::WARN;
      s.message = "Process time close to sensor period";
    } else {
      s.level = L::OK;
      s.message = "Nominal";
    }
    s.values.push_back(kv_d("avg_ms", dtAvr * 1000.0));
    s.values.push_back(kv_d("sensor_period_ms", sensorPeriod * 1000.0));
    s.values.push_back(kv_d("processed_scan_period_ms", processedPeriod * 1000.0));
    s.values.push_back(kv_d("profiler_lifetime_mean_ms", lifetimeMean * 1000.0));
    s.values.push_back(kv_d("utilization_pct", util * 100.0));
    status.push_back(std::move(s));
  }

  // Recent timings are independent of cumulative profiler means.
  {
    mola::DiagnosticStatusMsg s;
    s.name = "LidarOdometry: Worker Pipeline";
    s.level = L::OK;
    s.message = "Recent 256 worker samples; steady-clock durations";
    s.values.push_back(kv_u("window_samples", worker.window));
    s.values.push_back(kv_u("input_received", worker.received));
    s.values.push_back(kv_u("worker_completed", worker.completed));
    s.values.push_back(kv_u("queue_peak", worker.queue_peak));
    s.values.push_back(kv_d("input_period_ms", worker.input_period_ms));
    s.values.push_back(kv_d("last_input_age_ms", worker.last_input_age_ms));
    s.values.push_back(kv_d("last_total_ms", worker.last_total_ms));
    s.values.push_back(kv_d("recent_mean_total_ms", worker.mean_total_ms));
    s.values.push_back(kv_d("p95_total_ms", worker.p95_total_ms));
    s.values.push_back(kv_d("p99_total_ms", worker.p99_total_ms));
    s.values.push_back(kv_d("p95_imu_wait_ms", worker.p95_imu_wait_ms));
    s.values.push_back(kv_d("p95_queue_ms", worker.p95_queue_ms));
    s.values.push_back(kv_u("drop_imu_capacity", worker.drops[WorkerPipelineStats::ImuCapacity]));
    s.values.push_back(kv_u("drop_imu_catchup", worker.drops[WorkerPipelineStats::ImuCatchup]));
    s.values.push_back(kv_u("drop_worker_accounted", worker.drops[WorkerPipelineStats::WorkerAccounted]));
    for (std::size_t i=0; i<WorkerPipelineStats::PhaseCount; ++i) {
      s.values.push_back(kv_d(std::string("last_")+WorkerPipelineStats::Names[i]+"_ms", worker.last[i]));
      s.values.push_back(kv_d(std::string("p95_")+WorkerPipelineStats::Names[i]+"_ms", worker.p95[i]));
    }
    status.push_back(std::move(s));
  }

  {
    mola::DiagnosticStatusMsg s;
    s.name = "LidarOdometry: Navigation Output";
    s.level = nav.failed ? L::ERROR : L::OK;
    s.message = "One active and one latest pending immutable scan; nav_cloud is worker handoff time";
    s.values.push_back(kv_u("completed", nav.timing.completed));
    s.values.push_back(kv_u("overwritten_pending", nav.overwritten));
    s.values.push_back(kv_u("invalidated", nav.invalidated));
    s.values.push_back(kv_u("failed", nav.failed));
    s.values.push_back(kv_u("pending", nav.pending));
    s.values.push_back(kv_u("active", nav.active));
    s.values.push_back(kv_d("mean_ms", nav.timing.mean_total_ms));
    s.values.push_back(kv_d("p95_ms", nav.timing.p95_total_ms));
    s.values.push_back(kv_d("p95_queue_ms", nav.timing.p95_queue_ms));
    status.push_back(std::move(s));
  }

  // 4) Local Map (informational)
  {
    mola::DiagnosticStatusMsg s;
    s.name = "LidarOdometry: Local Map";
    s.level = L::OK;
    s.message = "Informational";
    std::size_t numLayers = 0;
    std::size_t totalPts = 0;
    if (state_.local_map) {
      numLayers = state_.local_map->layers.size();
      for (const auto & [layerName, layerMap] : state_.local_map->layers) {
        if (!layerMap) continue;
        if (auto pts = std::dynamic_pointer_cast<mrpt::maps::CPointsMap>(layerMap); pts)
          totalPts += pts->size();
      }
    }
    s.values.push_back(kv_u("num_layers", numLayers));
    s.values.push_back(kv_u("total_points", totalPts));
    status.push_back(std::move(s));
  }

  // 5) Overall status: worst-of the entries added by this provider
  {
    mola::DiagnosticStatusMsg s;
    s.name = "LidarOdometry: Overall Status";
    s.level = L::OK;
    for (std::size_t i = startIndex; i < status.size(); ++i) {
      s.level = worst(s.level, status[i].level);
    }
    switch (s.level) {
      case L::OK:
        s.message = "Nominal";
        break;
      case L::WARN:
        s.message = "Degraded";
        break;
      case L::STALE:
        s.message = "Stale input";
        break;
      case L::ERROR:
        s.message = "Non-functional";
        break;
    }
    s.values.push_back(kv_d("icp_quality", icpQ));
    s.values.push_back(kv_d("process_time_avg_ms", dtAvr * 1000.0));
    s.values.push_back(kv_d("dropped_frames_ratio", droppedRatio));
    status.push_back(std::move(s));
  }
  {
    mola::DiagnosticStatusMsg d;
    d.name="LidarOdometry: Causal Frame";
    d.level=L::OK; d.message="Completed scan snapshot";
    d.values.push_back(kv_d("scan_stamp",state_.last_obs_timestamp ? mrpt::Clock::toDouble(*state_.last_obs_timestamp):0,6));
    d.values.push_back(kv_u("completed_sequence",worker.completed));
    d.values.push_back(kv_u("pipeline_epoch",scan_epoch_.load()));
    d.values.push_back(kv_u("requested_tbb_threads",requested_tbb_threads_));
    d.values.push_back(kv_u("effective_tbb_threads",effective_tbb_threads_));
    d.values.push_back(kv_d("mean_cpu_ms",worker.mean_cpu_ms));
    d.values.push_back(kv_d("p95_runnable_wait_ms",worker.p95_runnable_wait_ms));
    d.values.push_back(kv_d("lidar_correction_stamp",corrected_stamp_,6));
    status.push_back(std::move(d));
  }
  std::scoped_lock cacheLock(diagnostics_snapshot_mtx_);
  diagnostics_snapshot_=std::move(status);
}
void LidarOdometry::getDiagnostics(std::vector<mola::DiagnosticStatusMsg>& status) {
  std::scoped_lock lock(diagnostics_snapshot_mtx_);
  auto copy=diagnostics_snapshot_;
  const auto now=mrpt::Clock::nowDouble();
  for(auto& d:copy) if(d.name=="LidarOdometry: Causal Frame") {
    const double imu=latest_imu_time_.load();
    d.values.push_back(kv_d("imu_input_age_ms",imu>0?(now-imu)*1000.:-1));
    for(const auto& kv:d.values) if(kv.key=="lidar_correction_stamp") {
      const auto t=std::stod(kv.value);
      d.values.push_back(kv_d("lidar_correction_age_ms",t>0?(now-t)*1000.:-1));break;
    }
  }
  status.insert(status.end(),copy.begin(),copy.end());
}
#endif  // MOLA_HAS_DIAGNOSTICS_PROVIDER

}  // namespace mola
