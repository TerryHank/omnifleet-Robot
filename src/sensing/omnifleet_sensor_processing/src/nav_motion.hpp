#pragma once
#include <Eigen/Geometry>
#include <deque>
#include <algorithm>
#include <stdexcept>
using Vec=Eigen::Vector3d;using Quat=Eigen::Quaterniond;
struct Gyro{double t;Vec w;Quat q;};
struct Pose{double t;Vec p;Quat q;};
inline Quat integrate_rotation(const Quat& q,const Vec& before,const Vec& after,double dt){
 Vec rv=.5*(before+after)*dt;double a=rv.norm();
 return (q*(a>1e-12?Quat(Eigen::AngleAxisd(a,rv/a)):Quat::Identity())).normalized();
}
inline Quat gyro_at(const std::deque<Gyro>& history,double t){
 if(history.size()<2||t<history.front().t-1e-6||t>history.back().t+1e-6)throw std::runtime_error("gyro coverage missing");
 auto it=std::lower_bound(history.begin(),history.end(),t,[](const Gyro& g,double value){return g.t<value;});
 if(it==history.begin())return it->q;
 if(it==history.end())return history.back().q;
 auto before=std::prev(it);return before->q.slerp(std::clamp((t-before->t)/(it->t-before->t),0.,1.),it->q);
}
inline Vec project_point(const Quat& anchor_q,const Vec& anchor_p,const Vec& velocity,double anchor_t,const Quat& gyro_q,const Vec& body,double t){
 return (anchor_q*gyro_q)*body+anchor_p+velocity*(t-anchor_t);
}
