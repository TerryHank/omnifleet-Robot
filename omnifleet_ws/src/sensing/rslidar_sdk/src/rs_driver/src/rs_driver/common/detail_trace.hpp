#pragma once
#include "causal_trace.hpp"
#include <ctime>
#include <sys/syscall.h>
namespace detail_trace {
inline int& iteration(){static thread_local int v=-1;return v;}
inline size_t& pairs(){static thread_local size_t v=0;return v;}
inline double& packet_rx_wall(){static thread_local double v=0;return v;}
inline double& packet_rx_mono(){static thread_local double v=0;return v;}
inline bool enabled(){static bool v=std::getenv("MOLA_DETAIL_TRACE")!=nullptr;return v;}
inline double cpu(){timespec t{};clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t);return t.tv_sec+t.tv_nsec*1e-9;}
struct Row{const char* stage;double raw,wall,begin,end,cpu_ms,aux,quality;int iter;size_t pair_count;long tid;unsigned long seq;};
class Recorder{
 std::mutex m_;std::deque<Row> q_;std::atomic<bool> stop_{false};std::atomic<unsigned long> seq_{0},lost_{0};std::thread writer_;
 public:
 Recorder(){
  if(!enabled())return;
  const char* p=std::getenv("MOLA_DEBUG_TRACES_FILE");if(!p)return;
  std::string file=std::string(p)+".detail."+std::to_string(getpid())+".csv";
  writer_=std::thread([this,file]{std::ofstream f(file);f<<std::setprecision(17)<<"seq,stage,raw_stamp,wall,begin_mono,end_mono,elapsed_ms,cpu_ms,iteration,pair_count,aux,quality,tid,lost\n";
    while(!stop_){drain(f);std::this_thread::sleep_for(std::chrono::milliseconds(100));}drain(f);});
 }
 void drain(std::ofstream& f){std::deque<Row> b;{std::lock_guard<std::mutex> l(m_);b.swap(q_);}
  for(auto& r:b)f<<r.seq<<','<<r.stage<<','<<r.raw<<','<<r.wall<<','<<r.begin<<','<<r.end<<','<<(r.end-r.begin)*1000<<','<<r.cpu_ms<<','<<r.iter<<','<<r.pair_count<<','<<r.aux<<','<<r.quality<<','<<r.tid<<','<<lost_<<'\n';f.flush();}
 void put(Row r){if(!enabled())return;r.seq=++seq_;std::unique_lock<std::mutex> l(m_,std::try_to_lock);if(!l.owns_lock()||q_.size()>=32768){++lost_;return;}q_.push_back(r);}
 ~Recorder(){stop_=true;if(writer_.joinable())writer_.join();}
};
inline void put(Row r){static Recorder rec;rec.put(r);}
struct Span{
 const char* stage;double begin=0,cpu_begin=0;bool on;int iter;
 explicit Span(const char* s):stage(s),on(enabled()),iter(iteration()){if(on){begin=causal_trace::mono();cpu_begin=cpu();}}
 void stop(double aux=0,double quality=0){if(!on)return;double end=causal_trace::mono();double used=(cpu()-cpu_begin)*1000;
  put(Row{stage,causal_trace::raw(),causal_trace::wall(),begin,end,used,aux,quality,iter,pairs(),syscall(SYS_gettid),0});on=false;}
 ~Span(){stop();}
};
inline void instant(const char* stage,double aux,double quality=0){if(!enabled())return;double now=causal_trace::mono();put(Row{stage,causal_trace::raw(),causal_trace::wall(),now,now,0,aux,quality,iteration(),pairs(),syscall(SYS_gettid),0});}
}
