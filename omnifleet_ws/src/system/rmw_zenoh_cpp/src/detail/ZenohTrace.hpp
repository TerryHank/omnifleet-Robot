// Copyright 2026 OmniFleet contributors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once

#include <unistd.h>

#include <chrono>
#include <cinttypes>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <mutex>
#include <string>
#include <string_view>
#include <thread>

namespace rmw_zenoh_cpp::trace
{
inline bool pointcloud_topic(std::string_view topic)
{
  return topic.find("rslidar_points") != std::string_view::npos;
}

inline uint64_t steady_ns()
{
  return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(
           std::chrono::steady_clock::now().time_since_epoch())
         .count());
}

inline uint64_t tid()
{
  static thread_local const uint64_t id = std::hash<std::thread::id>{}(std::this_thread::get_id());
  return id;
}

inline FILE * file()
{
  static FILE * f = []() {
      const char * path = std::getenv("RMW_ZENOH_TRACE_FILE");
      if (!path || !*path) {
        return static_cast<FILE *>(nullptr);
      }
      std::string actual(path);
      const auto marker = actual.find("%p");
      const auto process_id = std::to_string(getpid());
      if (marker != std::string::npos) {
        actual.replace(marker, 2, process_id);
      } else {
        actual += "." + process_id;
      }
      FILE * out = std::fopen(actual.c_str(), "a");
      if (out) {
        std::setvbuf(out, nullptr, _IOFBF, 65536);
      }
      return out;
    }();
  return f;
}

inline void event(
  const char * name, std::string_view topic = {}, uint64_t seq = 0,
  int64_t q_before = -1, int64_t q_after = -1, int64_t extra = -1)
{
  FILE * out = file();
  if (!out) {
    return;
  }
  static std::mutex m;
  std::lock_guard<std::mutex> lock(m);
  std::fprintf(
    out, "%s,%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRId64 ",%" PRId64 ",%" PRId64 ",%.*s\n",
    name, steady_ns(), tid(), seq, q_before, q_after, extra,
    static_cast<int>(topic.size()), topic.empty() ? "" : topic.data());
}
}  // namespace rmw_zenoh_cpp::trace
