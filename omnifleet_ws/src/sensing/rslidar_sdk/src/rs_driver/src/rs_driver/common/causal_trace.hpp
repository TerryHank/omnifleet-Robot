#pragma once
#include <atomic>
#include <chrono>
#include <cstdlib>
#include <deque>
#include <fstream>
#include <iomanip>
#include <mutex>
#include <thread>
#include <limits>
#include <unistd.h>
#include <cstring>
#include <ctime>
#include <sys/syscall.h>
namespace causal_trace {
inline double wall() {return std::chrono::duration<double>(std::chrono::system_clock::now().time_since_epoch()).count();}
inline double mono() {return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();}
inline double& raw() {static thread_local double value=std::numeric_limits<double>::quiet_NaN();return value;}
struct Row {const char* event; double stamp,raw_stamp,wall,mono,a,b; unsigned long seq; double thread_cpu; long tid;};
class Recorder {
 std::mutex mutex_;std::deque<Row> q_;std::atomic<bool> stop_{false};
 std::atomic<unsigned long> seq_{0},lost_{0};std::thread writer_;bool enabled_=false;
 public:
 Recorder() {
  const char* flag=std::getenv("MOLA_SAVE_DEBUG_TRACES");const char* path=std::getenv("MOLA_DEBUG_TRACES_FILE");
  enabled_=flag&&std::string(flag)=="true"&&path;
  if (!enabled_)return;
  const std::string file=std::string(path)+".causal."+std::to_string(getpid())+".csv";
  writer_=std::thread([this,file] {
   std::ofstream f(file);f<<std::setprecision(17)<<"seq,event,stamp,raw_stamp,wall,mono,a,b,lost,thread_cpu,tid\n";
   while (!stop_) {drain(f);std::this_thread::sleep_for(std::chrono::milliseconds(100));}
   drain(f);
  });
 }
 void drain(std::ofstream& f) {
  std::deque<Row> batch;
  {std::lock_guard<std::mutex> lock(mutex_);batch.swap(q_);}
  for(const auto& r:batch)f<<r.seq<<','<<r.event<<','<<r.stamp<<','<<r.raw_stamp<<','<<r.wall<<','<<r.mono<<','<<r.a<<','<<r.b<<','<<lost_.load()<<','<<r.thread_cpu<<','<<r.tid<<'\n';
  f.flush();
 }
 ~Recorder(){stop_=true;if(writer_.joinable())writer_.join();}
 void put(const char* event,double stamp,double a,double b) {
  if(!enabled_)return;
  Row r{event,stamp,raw(),wall(),mono(),a,b,++seq_,
        std::numeric_limits<double>::quiet_NaN(),0};
  if(std::strcmp(event,"icp_begin")==0||std::strcmp(event,"icp_end")==0) {
   timespec ts{};
   if(clock_gettime(CLOCK_THREAD_CPUTIME_ID,&ts)==0)r.thread_cpu=ts.tv_sec+ts.tv_nsec*1e-9;
   r.tid=syscall(SYS_gettid);
  }
  std::unique_lock<std::mutex> lock(mutex_,std::try_to_lock);
  if(!lock.owns_lock()||q_.size()>=8192){++lost_;return;}
  q_.push_back(r);
 }
};
inline void emit(const char* event,double stamp,double a=0,double b=0) {
 static Recorder recorder;recorder.put(event,stamp,a,b);
}
struct WorkerScope {
 double stamp;
 explicit WorkerScope(double s):stamp(s){raw()=s;emit("worker_begin",s);}
 ~WorkerScope(){emit("worker_end",stamp);raw()=std::numeric_limits<double>::quiet_NaN();}
};
}
