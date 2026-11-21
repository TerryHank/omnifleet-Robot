#include "omnifleet_planner/native_waypoint_progress.hpp"
#include <iostream>
#include <limits>
#include <stdexcept>
void check(bool value,const char * label) {if(!value)throw std::runtime_error(label);std::cout<<"PASS "<<label<<std::endl;}
int main() {
  omnifleet_planner::NativeWaypointProgressState p;p.reset(1000000000);
  check(!p.canFinish(2.,3.,1000000001),"no progress cannot finish");
  p.observe(1100000000,4,2.,3.,"closed-loop");
  check(!p.canFinish(2.,3.,1200000000),"starting at terminal goal cannot skip three mandatory points");
  p.observe(1200000000,2,2.,3.,"closed-loop");
  check(!p.canFinish(2.,3.,1200000001),"one unpassed intermediate point still blocks completion");
  p.observe(1300000000,1,2.,3.,"closed-loop");
  check(p.canFinish(2.,3.,1400000000),"only final goal remaining allows ordinary goal checks");
  check(!p.canFinish(2.01,3.,1400000000),"another path endpoint cannot authorize completion");
  check(!p.canFinish(2.,3.,1900000000),"stale progress cannot finish");
  check(!p.canFinish(2.,3.,1250000000),"future progress cannot finish");
  p.reset(2000000000);p.observe(1300000000,1,2.,3.,"closed-loop");
  check(!p.canFinish(2.,3.,2000000001),"old task progress rejected after reset");
  p.observe(2100000000,1,2.,3.,"");check(!p.canFinish(2.,3.,2100000001),"missing run marker cannot finish");
  p.observe(2200000000,1,std::numeric_limits<double>::quiet_NaN(),3.,"run");
  check(!p.canFinish(2.,3.,2200000001),"invalid endpoint cannot finish");
}
