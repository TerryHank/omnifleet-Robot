#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <vector>
#include "nav_msgs/msg/path.hpp"

namespace omnifleet_planner {
// Republishing timestamps do not change route identity.
inline std::string routeFingerprint(const nav_msgs::msg::Path& path) {
  uint64_t hash=1469598103934665603ULL;
  auto add=[&](const void* data,size_t size){auto p=static_cast<const unsigned char*>(data);while(size--){hash^=*p++;hash*=1099511628211ULL;}};
  add(path.header.frame_id.data(),path.header.frame_id.size());
  for(const auto& p:path.poses){const auto&a=p.pose.position;const auto&q=p.pose.orientation;for(double value:{a.x,a.y,a.z,q.x,q.y,q.z,q.w})add(&value,sizeof(value));}
  return std::to_string(hash);
}
class OrderedProgress {
 public:
  struct Projection {double s{0},distance{std::numeric_limits<double>::infinity()};};
  void reset(const nav_msgs::msg::Path& path) {
    if(path.poses.empty())throw std::invalid_argument("empty progress path");
    path_=path;arc_.assign(path.poses.size(),0.);
    for(size_t i=1;i<arc_.size();++i)arc_[i]=arc_[i-1]+std::hypot(path.poses[i].pose.position.x-path.poses[i-1].pose.position.x,path.poses[i].pose.position.y-path.poses[i-1].pose.position.y);
    s_=0.;stamp_=-1.;credit_=.30;distance_=mismatch_=0.;lo_=hi_=0.;checkpoint_=cusp_=0;ends_.clear();radius_=.25;
    x_=anchor_x_=path.poses.front().pose.position.x;y_=anchor_y_=path.poses.front().pose.position.y;
    cusps_.clear();
    for(size_t i=1;i+1<arc_.size();++i){const auto&a=path_.poses[i-1].pose.position;const auto&b=path_.poses[i].pose.position;const auto&c=path_.poses[i+1].pose.position;
      if((b.x-a.x)*(c.x-b.x)+(b.y-a.y)*(c.y-b.y)<0.)cusps_.push_back(i);}
    ends_=cusps_;if(ends_.empty()||ends_.back()!=arc_.size()-1)ends_.push_back(arc_.size()-1);
  }
  void set_checkpoints(const std::vector<size_t>& ends,double radius) {
    if(ends.empty()||ends.back()>=arc_.size()||!std::is_sorted(ends.begin(),ends.end())||!std::isfinite(radius)||radius<.05||radius>.5)throw std::invalid_argument("invalid route checkpoints");
    ends_=ends;radius_=radius;checkpoint_=0;
  }
  static Projection project(const nav_msgs::msg::Path& path,const std::vector<double>& arc,double x,double y,double lo,double hi) {
    Projection best;
    if(path.poses.size()==1){const auto&p=path.poses[0].pose.position;return {0.,std::hypot(x-p.x,y-p.y)};}
    for(size_t i=1;i<arc.size();++i){
      const double length=arc[i]-arc[i-1];if(length<1e-9||arc[i]<lo||arc[i-1]>hi)continue;
      const auto&a=path.poses[i-1].pose.position;const auto&b=path.poses[i].pose.position;
      const double lower=std::max(0.,(lo-arc[i-1])/length),upper=std::min(1.,(hi-arc[i-1])/length);if(lower>upper)continue;
      const double t=std::clamp(((x-a.x)*(b.x-a.x)+(y-a.y)*(b.y-a.y))/(length*length),lower,upper);
      const double d=std::hypot(x-a.x-t*(b.x-a.x),y-a.y-t*(b.y-a.y));if(d<best.distance-1e-9)best={arc[i-1]+t*length,d};
    }return best;
  }
  static double circle_entry(double gx,double gy,double ax,double ay,double bx,double by,double radius) {
    const double dx=bx-ax,dy=by-ay,px=ax-gx,py=ay-gy,a=dx*dx+dy*dy,c=px*px+py*py-radius*radius;
    if(c<=0.)return 0.;if(a<1e-12)return 2.;
    const double b=2.*(px*dx+py*dy),disc=b*b-4.*a*c;if(disc<0.)return 2.;
    const double t=(-b-std::sqrt(disc))/(2.*a);return t>=0.&&t<=1.?t:2.;
  }
  void update(double x,double y,double stamp) {
    if(!std::isfinite(x)||!std::isfinite(y)||!std::isfinite(stamp))throw std::invalid_argument("nonfinite progress pose");
    if(stamp<=stamp_)return;const bool previous=stamp_>=0;
    if(previous){const double movement=std::hypot(x-anchor_x_,y-anchor_y_);if(movement>=.01){credit_+=movement;anchor_x_=x;anchor_y_=y;}}
    else {anchor_x_=x;anchor_y_=y;}
    double last_entry=-1.;
    for(;;){
      const double begin=this->begin(),end=this->end();
      lo_=std::max(begin,s_-.10);hi_=std::max(lo_,std::min(end,credit_));
      const auto bounded=project(path_,arc_,x,y,lo_,hi_);const auto branch=project(path_,arc_,x,y,begin,end);
      distance_=branch.distance;mismatch_=std::abs(branch.s-bounded.s);if(std::isfinite(bounded.distance))s_=std::max(s_,bounded.s);
      if(distance_>.30||mismatch_>.30)break;
      if(cusp_<cusps_.size()&&arc_[cusps_[cusp_]]<=arc_[ends_[checkpoint_]]&&s_+.10>=end){
        const auto&turn=path_.poses[cusps_[cusp_]].pose.position;
        const auto&before=path_.poses[cusps_[cusp_]-1].pose.position;
        const bool approaching=previous?((x-x_)*(turn.x-before.x)+(y-y_)*(turn.y-before.y)>1e-10):std::hypot(x-turn.x,y-turn.y)<.01;
        if(approaching&&(std::hypot(x-turn.x,y-turn.y)<=.10||(previous&&circle_entry(turn.x,turn.y,x_,y_,x,y,.10)<=1.))){
          s_=end;credit_=std::max(credit_,end);++cusp_;
          // A cusp at the mission checkpoint is also processed below.
          if(end<arc_[ends_[checkpoint_]]-1e-9)continue;
        }else break;
      }
      if(checkpoint_+1>=ends_.size()||end<arc_[ends_[checkpoint_]]-1e-9)break;
      const auto&g=path_.poses[ends_[checkpoint_]].pose.position;
      const double entry=previous?circle_entry(g.x,g.y,x_,y_,x,y,radius_):(std::hypot(x-g.x,y-g.y)<=radius_?0.:2.);
      // Both arc occurrence and increasing segment intersection are required.
      if(entry>1.||entry<=last_entry+1e-9||s_+radius_<end)break;
      last_entry=entry;s_=end;credit_=std::max(credit_,end);++checkpoint_;
    }x_=x;y_=y;stamp_=stamp;
  }
  double distance()const{return distance_;} double mismatch()const{return mismatch_;}
  double s()const{return s_;} double at(size_t i)const{return arc_.at(i);}
  size_t completed()const{return checkpoint_;}
  double begin()const{return std::max(checkpoint_?arc_[ends_[checkpoint_-1]]:0.,cusp_?arc_[cusps_[cusp_-1]]:0.);}
  double end()const{return std::min(arc_[ends_[checkpoint_]],cusp_<cusps_.size()?arc_[cusps_[cusp_]]:arc_.back());}
  double control_end()const{return cusp_<cusps_.size()?arc_[cusps_[cusp_]]:arc_.back();}
  double budget()const{return std::max(0.,credit_-s_);} double lo()const{return lo_;} double hi()const{return hi_;}
  size_t index()const{auto i=std::upper_bound(arc_.begin(),arc_.end(),s_);return i==arc_.begin()?0:std::min(size_t(i-arc_.begin()-1),arc_.size()-1);}
  const std::vector<double>& arc()const{return arc_;}
 private:
  nav_msgs::msg::Path path_;std::vector<double> arc_;std::vector<size_t> ends_,cusps_;size_t checkpoint_{0},cusp_{0};
  double s_{0},stamp_{-1},x_{0},y_{0},anchor_x_{0},anchor_y_{0},credit_{.30},distance_{0},mismatch_{0},radius_{.25},lo_{0},hi_{0};
};
}
