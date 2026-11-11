#pragma once

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <mutex>
#include <string>
#include <thread>
#include <unistd.h>

namespace mola_callback_trace
{
inline std::mutex& file_mutex()
{
  static std::mutex m;
  return m;
}

inline FILE* file()
{
  static FILE* f = [] {
    const char* path = std::getenv("MOLA_CALLBACK_TRACE_FILE");
    if (!path || !*path) return static_cast<FILE*>(nullptr);
    const std::string pid_path = std::string(path) + "." + std::to_string(getpid()) + ".csv";
    FILE* out = std::fopen(pid_path.c_str(), "w");
    if (out)
    {
      std::setvbuf(out, nullptr, _IOFBF, 64 * 1024);
      std::fputs("event,steady_ns,thread_id,callback,duration_ns\n", out);
    }
    return out;
  }();
  return f;
}

inline long long now_ns()
{
  return std::chrono::duration_cast<std::chrono::nanoseconds>(
             std::chrono::steady_clock::now().time_since_epoch())
      .count();
}

inline void emit(const char* event, const char* callback, long long at, long long duration)
{
  FILE* f = file();
  if (!f) return;
  const auto tid = std::hash<std::thread::id>{}(std::this_thread::get_id());
  std::lock_guard<std::mutex> lock(file_mutex());
  std::fprintf(f, "%s,%lld,%zu,%s,%lld\n", event, at, tid, callback, duration);
}

struct Scope
{
  const char* callback;
  long long start;
  explicit Scope(const char* name) : callback(name), start(now_ns())
  {
    emit("ENTER", callback, start, 0);
  }
  ~Scope()
  {
    const auto end = now_ns();
    emit("EXIT", callback, end, end - start);
  }
};
}  // namespace mola_callback_trace
