#include <ompl/base/StateSpace.h>
#include <ompl/base/ScopedState.h>
#include <ompl/base/PlannerTerminationCondition.h>
#include <ompl/base/spaces/ReedsSheppStateSpace.h>
#include <ompl/base/spaces/DubinsStateSpace.h>
#include <ompl/geometric/planners/rrt/RRTConnect.h>
#include <ompl/geometric/PathSimplifier.h>
#include <ompl/util/Console.h>
#include <ompl/util/RandomNumbers.h>
#include <nlohmann/json.hpp>
#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <memory>
#include <type_traits>
#include <vector>

namespace ob=ompl::base;
namespace og=ompl::geometric;
using J=nlohmann::json;
using Point=std::array<double,2>;
using Pose=std::array<double,3>;
using Poly=std::vector<Point>;
using Poses=std::vector<Pose>;

double wrap(double a){return std::atan2(std::sin(a),std::cos(a));}
template<class Path> int segmentType(const Path &path,int index){
  if constexpr(std::is_enum_v<std::decay_t<decltype(path.type_[0])>>)return path.type_[index];
  else return (*path.type_)[index];
}
Poly transformed(const Poly &body,const Pose &p){
  Poly out;double c=std::cos(p[2]),s=std::sin(p[2]);
  for(auto v:body)out.push_back({p[0]+c*v[0]-s*v[1],p[1]+s*v[0]+c*v[1]});
  return out;
}
// Input footprints are convex hulls of the configured padded vehicle polygons.
bool overlaps(const Poly &a,const Poly &b){
  for(const auto *poly:{&a,&b})for(size_t i=0;i<poly->size();++i){
    const auto &p=(*poly)[i],&q=(*poly)[(i+1)%poly->size()];
    Point n{p[1]-q[1],q[0]-p[0]};
    double al=1e100,ah=-1e100,bl=1e100,bh=-1e100;
    for(auto v:a){double x=n[0]*v[0]+n[1]*v[1];al=std::min(al,x);ah=std::max(ah,x);}
    for(auto v:b){double x=n[0]*v[0]+n[1]*v[1];bl=std::min(bl,x);bh=std::max(bh,x);}
    if(ah<bl-1e-9||bh<al-1e-9)return false;
  }
  return true;
}
struct Scene {
  int width,height;double resolution;Pose origin;bool allow_unknown;
  std::vector<int> cells;std::vector<Poly> bodies;std::vector<double> radii;std::vector<bool> reversible;
  explicit Scene(const J &j){
    auto m=j.at("map");width=m.at("width");height=m.at("height");resolution=m.at("resolution");
    origin=m.at("origin").get<Pose>();allow_unknown=m.value("allow_unknown",false);
    cells=m.at("data").get<std::vector<int>>();
    if(width<=0||height<=0||resolution<=0||cells.size()!=size_t(width*height))throw std::runtime_error("invalid_map");
    for(const auto &r:j.at("robots")){
      bodies.push_back(r.at("footprint").get<Poly>());radii.push_back(r.at("turn_radius"));
      reversible.push_back(r.value("reversible",true));
      if(bodies.back().size()<3||radii.back()<=0)throw std::runtime_error("invalid_robot_geometry");
    }
  }
  Poly gridPoly(const Poly &world)const{
    Poly out;double c=std::cos(origin[2]),s=std::sin(origin[2]);
    for(auto p:world){double x=p[0]-origin[0],y=p[1]-origin[1];out.push_back({(c*x+s*y)/resolution,(-s*x+c*y)/resolution});}
    return out;
  }
  bool terrain(const Poly &world)const{
    auto p=gridPoly(world);double xl=1e100,xh=-1e100,yl=1e100,yh=-1e100;
    for(auto v:p){xl=std::min(xl,v[0]);xh=std::max(xh,v[0]);yl=std::min(yl,v[1]);yh=std::max(yh,v[1]);}
    if(xl<0||yl<0||xh>=width||yh>=height)return true;
    for(int y=std::floor(yl);y<=std::floor(yh);++y)for(int x=std::floor(xl);x<=std::floor(xh);++x){
      int value=cells[y*width+x];
      if(value<65 && (value>=0||allow_unknown))continue;
      Poly cell{{double(x),double(y)},{double(x+1),double(y)},{double(x+1),double(y+1)},{double(x),double(y+1)}};
      if(overlaps(p,cell))return true;
    }
    return false;
  }
  bool valid(const Poses &poses)const{
    if(poses.size()!=bodies.size())return false;
    std::vector<Poly> polygons;
    for(size_t i=0;i<poses.size();++i){
      auto poly=transformed(bodies[i],poses[i]);if(terrain(poly))return false;
      for(const auto &other:polygons)if(overlaps(poly,other))return false;
      polygons.push_back(std::move(poly));
    }
    return true;
  }
  Poses decode(const ob::State *state)const{
    Poses out;auto all=state->as<ob::CompoundState>();
    for(size_t i=0;i<bodies.size();++i){auto p=all->as<ob::SE2StateSpace::StateType>(i);out.push_back({p->getX(),p->getY(),p->getYaw()});}
    return out;
  }
  bool sampled(const std::vector<Poses> &path)const{
    if(path.empty())return false;
    for(size_t k=0;k<path.size();++k){
      if(!valid(path[k]))return false;
      if(!k)continue;
      double extent=0;
      for(size_t i=0;i<bodies.size();++i){double radius=0;for(auto p:bodies[i])radius=std::max(radius,std::hypot(p[0],p[1]));
        extent=std::max(extent,std::hypot(path[k][i][0]-path[k-1][i][0],path[k][i][1]-path[k-1][i][1])+radius*std::abs(wrap(path[k][i][2]-path[k-1][i][2])));}
      int steps=std::max(1,int(std::ceil(extent/std::min(.01,resolution*.2))));
      for(int n=1;n<steps;++n){Poses between=path[k-1];double f=double(n)/steps;
        for(size_t i=0;i<bodies.size();++i){for(int d=0;d<2;++d)between[i][d]+=f*(path[k][i][d]-between[i][d]);between[i][2]+=f*wrap(path[k][i][2]-between[i][2]);}
        if(!valid(between))return false;
      }
    }
    return true;
  }
};

J plan(const J &request){
  Scene scene(request);
  if(request.value("operation",std::string("plan"))=="validate")return {{"valid",scene.sampled(request.at("path").get<std::vector<Poses>>())}};
  Poses starts,goals;
  for(auto &r:request.at("robots")){starts.push_back(r.at("start").get<Pose>());goals.push_back(r.at("goal").get<Pose>());}
  if(!scene.valid(starts))return {{"success",false},{"reason","start_collision"}};
  if(!scene.valid(goals))return {{"success",false},{"reason","goal_collision"}};
  auto space=std::make_shared<ob::CompoundStateSpace>();
  std::vector<ob::StateSpacePtr> parts;
  // Search in the bounding box of observed terrain and the supplied start/goals.
  double xl=1e100,xh=-1e100,yl=1e100,yh=-1e100;
  for(int y=0;y<scene.height;++y)for(int x=0;x<scene.width;++x)if(scene.cells[y*scene.width+x]>=0){
    double gx=(x+.5)*scene.resolution,gy=(y+.5)*scene.resolution,c=std::cos(scene.origin[2]),s=std::sin(scene.origin[2]);
    double wx=scene.origin[0]+c*gx-s*gy,wy=scene.origin[1]+s*gx+c*gy;
    xl=std::min(xl,wx);xh=std::max(xh,wx);yl=std::min(yl,wy);yh=std::max(yh,wy);
  }
  for(const auto &set:{starts,goals})for(auto p:set){xl=std::min(xl,p[0]-1.);xh=std::max(xh,p[0]+1.);yl=std::min(yl,p[1]-1.);yh=std::max(yh,p[1]+1.);}
  for(size_t i=0;i<starts.size();++i){
    ob::StateSpacePtr part=scene.reversible[i]?ob::StateSpacePtr(std::make_shared<ob::ReedsSheppStateSpace>(scene.radii[i])):ob::StateSpacePtr(std::make_shared<ob::DubinsStateSpace>(scene.radii[i]));ob::RealVectorBounds bounds(2);
    bounds.setLow(0,xl);bounds.setHigh(0,xh);bounds.setLow(1,yl);bounds.setHigh(1,yh);part->as<ob::SE2StateSpace>()->setBounds(bounds);
    parts.push_back(part);space->addSubspace(part,1.);
  }
  space->lock();auto si=std::make_shared<ob::SpaceInformation>(space);
  si->setStateValidityChecker([&](const ob::State *s){return scene.valid(scene.decode(s));});
  double radius=*std::min_element(scene.radii.begin(),scene.radii.end());
  si->setStateValidityCheckingResolution(std::min(.005,.005*radius)/space->getMaximumExtent());si->setup();
  ob::ScopedState<> start(space),goal(space);
  for(size_t i=0;i<starts.size();++i)for(auto pair:{std::make_pair(start.get(),starts[i]),std::make_pair(goal.get(),goals[i])}){
    auto p=pair.first->as<ob::CompoundState>()->as<ob::SE2StateSpace::StateType>(i);p->setXY(pair.second[0],pair.second[1]);p->setYaw(wrap(pair.second[2]));
  }
  auto problem=std::make_shared<ob::ProblemDefinition>(si);problem->setStartAndGoalStates(start,goal);
  auto planner=std::make_shared<og::RRTConnect>(si);planner->setRange(.6);planner->setProblemDefinition(problem);planner->setup();
  auto status=planner->solve(ob::timedPlannerTerminationCondition(request.value("seconds",3.)));
  if(status!=ob::PlannerStatus::EXACT_SOLUTION)return {{"success",false},{"reason","joint_path_not_found"},{"detail",status.asString()}};
  auto path=std::dynamic_pointer_cast<og::PathGeometric>(problem->getSolutionPath());
  og::PathSimplifier simplifier(si);simplifier.simplify(*path,.15);
  J phases=J::array();
  for(size_t edge=1;edge<path->getStateCount();++edge){
    auto a=path->getState(edge-1),b=path->getState(edge);
    struct Segments {std::array<double,5> lengths{};std::array<int,5> curves{};double total=0.;};
    std::vector<Segments> rs;
    std::vector<double> cuts{0.,1.};
    for(size_t i=0;i<parts.size();++i){
      auto sa=a->as<ob::CompoundState>()->components[i],sb=b->as<ob::CompoundState>()->components[i];Segments segments;
      if(scene.reversible[i]){
        auto path=parts[i]->as<ob::ReedsSheppStateSpace>()->reedsShepp(sa,sb);
        for(int k=0;k<5;++k){segments.lengths[k]=path.length_[k];segments.curves[k]=path.type_[k]==ob::ReedsSheppStateSpace::RS_LEFT?1:path.type_[k]==ob::ReedsSheppStateSpace::RS_RIGHT?-1:0;}
      }else{
        auto path=parts[i]->as<ob::DubinsStateSpace>()->dubins(sa,sb);
        for(int k=0;k<3;++k){segments.lengths[k]=path.length_[k];segments.curves[k]=segmentType(path,k)==ob::DubinsStateSpace::DUBINS_LEFT?1:segmentType(path,k)==ob::DubinsStateSpace::DUBINS_RIGHT?-1:0;}
      }
      for(double length:segments.lengths)segments.total+=std::abs(length);rs.push_back(segments);
      double sum=0.;for(double length:segments.lengths){sum+=std::abs(length);if(segments.total>1e-9)cuts.push_back(std::clamp(sum/segments.total,0.,1.));}
    }
    std::sort(cuts.begin(),cuts.end());cuts.erase(std::unique(cuts.begin(),cuts.end(),[](double a,double b){return std::abs(a-b)<1e-8;}),cuts.end());
    auto work=space->allocState();
    for(size_t cut=1;cut<cuts.size();++cut){
      double f0=cuts[cut-1],f1=cuts[cut],mid=(f0+f1)*.5;space->interpolate(a,b,f0,work);
      J phase={{"kind","twist"},{"start",scene.decode(work)},{"delta",J::array()}};
      for(size_t i=0;i<parts.size();++i){
        auto &r=rs[i];double total=r.total,at=0.;int segment=0;
        for(;segment<4;++segment){if(at+std::abs(r.lengths[segment])>mid*total+1e-10)break;at+=std::abs(r.lengths[segment]);}
        double distance=std::copysign(total*(f1-f0)*scene.radii[i],r.lengths[segment]);int curve=r.curves[segment];
        phase["delta"].push_back({distance,curve*distance/scene.radii[i]});
      }
      phases.push_back(phase);
    }
    space->freeState(work);
  }
  return {{"success",true},{"planner","OMPL joint Reeds-Shepp RRTConnect"},{"phases",phases}};
}
int main(){
  ompl::msg::setLogLevel(ompl::msg::LOG_NONE);ompl::RNG::setSeed(17);
  try{J request;std::cin>>request;std::cout<<plan(request).dump()<<std::endl;}
  catch(const std::exception &e){std::cout<<J{{"success",false},{"reason",e.what()}}.dump()<<std::endl;return 1;}
}
