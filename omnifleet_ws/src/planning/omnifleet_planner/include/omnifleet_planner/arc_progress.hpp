#pragma once
#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>
#include <vector>
#include "nav_msgs/msg/path.hpp"

namespace omnifleet_planner {
// Progress is path arclength, not the spatially nearest occurrence on a loop.
class ArcProgress {
 public:
  void reset(const nav_msgs::msg::Path & path) {
    if (path.poses.empty()) throw std::invalid_argument("empty progress path");
    path_=path; arc_.assign(path.poses.size(),0.);
    for(size_t i=1;i<arc_.size();++i)arc_[i]=arc_[i-1]+std::hypot(
      path.poses[i].pose.position.x-path.poses[i-1].pose.position.x,
      path.poses[i].pose.position.y-path.poses[i-1].pose.position.y);
    s_=0.;stamp_=-1.;x_=path.poses.front().pose.position.x;y_=path.poses.front().pose.position.y;
    distance_=0.;travel_budget_=0.;
  }
  void update(double x,double y,double stamp,double limit=std::numeric_limits<double>::infinity()) {
    if(!std::isfinite(x)||!std::isfinite(y)||!std::isfinite(stamp))throw std::invalid_argument("nonfinite progress pose");
    if(stamp<=stamp_)return;
    const double movement=stamp_>=0?std::hypot(x-x_,y-y_):0.;
    // Keep unused physical travel instead of discarding it every frame. This
    // lets the cursor catch up after a sparse observation around a turn while
    // stationary samples still cannot open a later overlapping branch.
    travel_budget_=std::min(3.,travel_budget_+1.5*movement);
    const double lo=s_,hi=std::max(s_,std::min({arc_.back(),s_+travel_budget_+.05,limit}));
    double best_s=s_,best=std::numeric_limits<double>::infinity();
    if(path_.poses.size()==1)best=std::hypot(x-path_.poses.front().pose.position.x,y-path_.poses.front().pose.position.y);
    for(size_t i=1;i<arc_.size();++i){
      const double length=arc_[i]-arc_[i-1];
      if(length<1e-9||arc_[i]<lo||arc_[i-1]>hi)continue;
      const auto & a=path_.poses[i-1].pose.position;const auto & b=path_.poses[i].pose.position;
      const double t=std::clamp(((x-a.x)*(b.x-a.x)+(y-a.y)*(b.y-a.y))/(length*length),
        std::max(0.,(lo-arc_[i-1])/length),std::min(1.,(hi-arc_[i-1])/length));
      const double d=std::hypot(x-a.x-t*(b.x-a.x),y-a.y-t*(b.y-a.y));
      if(d<best-1e-9){best=d;best_s=arc_[i-1]+t*length;}
    }
    const double consumed=std::max(0.,best_s-s_);
    s_=std::max(s_,best_s);travel_budget_=std::max(0.,travel_budget_-consumed);
    distance_=best;x_=x;y_=y;stamp_=stamp;
  }
  double distance()const{return distance_;}
  double s()const{return s_;}
  double at(size_t index)const{return arc_.at(index);}
  size_t index()const{
    auto it=std::upper_bound(arc_.begin(),arc_.end(),s_);
    return it==arc_.begin()?0:std::min(size_t(it-arc_.begin()-1),arc_.size()-1);
  }
  const std::vector<double>& arc()const{return arc_;}
 private:
  nav_msgs::msg::Path path_;std::vector<double> arc_;
  double s_{0},stamp_{-1},x_{0},y_{0},distance_{0},travel_budget_{0};
};
}
