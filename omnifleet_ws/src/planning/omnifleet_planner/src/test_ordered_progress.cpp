#include "omnifleet_planner/ordered_progress.hpp"
#include "omnifleet_planner/arc_progress.hpp"
#include <iostream>
#include <fstream>
#include <cassert>
using namespace omnifleet_planner;
nav_msgs::msg::Path make(std::initializer_list<std::pair<double,double>> points){nav_msgs::msg::Path p;p.header.frame_id="map";for(auto xy:points){geometry_msgs::msg::PoseStamped q;q.pose.position.x=xy.first;q.pose.position.y=xy.second;q.pose.orientation.w=1.;p.poses.push_back(q);}return p;}
int main(int argc,char**argv){
  const auto short_turn=make({{0,0},{1,0},{.9,0},{2,0}});
  ArcProgress old;old.reset(short_turn);OrderedProgress progress;progress.reset(short_turn);progress.set_checkpoints({1,2,3},.05);
  double stamp=1.;for(double x:{0.,.1,.2,.3,.4,.5,.6,.7,.8,.9,.96,1.01}){old.update(x,0,stamp);progress.update(x,0,stamp);stamp+=.1;}
  std::cout<<"old short-turn s="<<old.s()<<" new="<<progress.s()<<" checkpoint="<<progress.completed()<<std::endl;
  assert(old.s()>1.1);assert(progress.completed()==1);assert(progress.s()<=1.05);
  const auto overlap=make({{0,0},{2,0},{0,0},{2,0}});progress.reset(overlap);progress.set_checkpoints({1,2,3},.10);
  progress.update(0,0,stamp++);const double initial_budget=progress.budget();
  for(int i=0;i<10000;++i)progress.update((i%2?.002:-.002),0,stamp+=.01);
  assert(progress.completed()==0);assert(progress.budget()<=initial_budget+.01);assert(progress.s()<.01);
  for(int i=0;i<=40;++i)progress.update(i*.05,0,stamp+=.1);
  assert(progress.completed()==1);
  for(int i=40;i>=0;--i)progress.update(i*.05,0,stamp+=.1);
  assert(progress.completed()==2);
  const auto s=progress.s();progress.update(2,0,stamp);assert(progress.s()==s);
  // A line segment crosses a pass circle even with both ends outside it.
  const auto line=make({{0,0},{.3,0},{.8,0},{1,0}});progress.reset(line);progress.set_checkpoints({1,2,3},.15);
  progress.update(0,0,stamp++);progress.update(.1,0,stamp++);progress.update(.46,0,stamp++);assert(progress.completed()==1);
  progress.reset(line);progress.set_checkpoints({1,2,3},.10);progress.update(0,0,stamp++);progress.update(0,.4,stamp++);assert(progress.distance()>.30);
  // Window lag must not be presented as lateral deviation.
  progress.reset(line);progress.set_checkpoints({3},.10);progress.update(.8,0,stamp++);assert(progress.distance()<1e-8);assert(progress.mismatch()>.30);
  auto repeat=line;repeat.header.stamp.sec=123;assert(routeFingerprint(line)==routeFingerprint(repeat));repeat.poses.back().pose.position.x+=.01;assert(routeFingerprint(line)!=routeFingerprint(repeat));
  if(argc>1){
    std::ifstream in(argv[1]);nav_msgs::msg::Path path;path.header.frame_id="map";std::vector<size_t> ends;char kind;double x,y;
    while(in>>kind>>x>>y){if(kind=='P'){geometry_msgs::msg::PoseStamped q;q.pose.position.x=x;q.pose.position.y=y;q.pose.orientation.w=1.;path.poses.push_back(q);}else if(kind=='E')ends.push_back(size_t(x));}
    assert(path.poses.size()==207);progress.reset(path);progress.set_checkpoints(ends,.25);
    for(size_t i=0;i<path.poses.size();++i){const auto&p=path.poses[i].pose.position;progress.update(p.x,p.y,stamp+=.1);assert(progress.distance()<=.30);assert(progress.mismatch()<=.30);}
    assert(progress.completed()==ends.size()-1);std::cout<<"207-point planned-geometry replay passed, not recorded vehicle trajectory"<<std::endl;
  }
  std::cout<<"PASS old-version counterexample, short turn, overlapping legs, jitter, duplicate timestamps, swept circle, lateral/matching distinction, final checkpoint retained"<<std::endl;
}
