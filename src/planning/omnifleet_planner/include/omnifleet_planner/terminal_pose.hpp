#pragma once
#include <algorithm>
#include <cmath>

namespace omnifleet_planner {
// Keep terminal heading alignment across small localization-point translations.
// Position is corrected afterwards; the goal checker's tolerances stay unchanged.
class TerminalPose {
public:
  void setGoal(double x,double y,double yaw) {
    if(!have_goal_||std::hypot(x-goal_x_,y-goal_y_)>1e-6||
      std::abs(std::atan2(std::sin(yaw-goal_yaw_),std::cos(yaw-goal_yaw_)))>1e-6){active_=false;adjusting_=false;}
    have_goal_=true;goal_x_=x;goal_y_=y;goal_yaw_=yaw;
  }
  void reset(){active_=false;have_goal_=false;adjusting_=false;}
  bool command(double x,double y,double yaw_error,double xy_tolerance,double yaw_tolerance,
    double max_linear,double max_angular,double & linear,double & angular) {
    const double distance=std::hypot(x,y);
    if(!active_&&distance>xy_tolerance*1.25)return false;
    if(distance>.3){active_=false;adjusting_=false;return false;}
    active_=true;linear=0.;angular=0.;
    if(distance<=xy_tolerance*.75)adjusting_=false;
    if(!adjusting_&&std::abs(yaw_error)>yaw_tolerance*.5) {
      angular=std::clamp(1.5*yaw_error,-max_angular,max_angular);return true;
    }
    if(distance<=xy_tolerance*.75)return true;
    adjusting_=true;
    const double direction=x>=0.?1.:-1.;
    const double heading=std::atan2(direction*y,direction*x);
    if(std::abs(heading)>.3) {
      angular=std::clamp(1.5*heading,-max_angular,max_angular);return true;
    }
    linear=direction*std::min(max_linear,.8*distance)*std::cos(heading);
    angular=std::clamp(2.*linear*y/(distance*distance),-max_angular,max_angular);return true;
  }
private:
  bool active_{false},have_goal_{false},adjusting_{false};
  double goal_x_{0.},goal_y_{0.},goal_yaw_{0.};
};
}
