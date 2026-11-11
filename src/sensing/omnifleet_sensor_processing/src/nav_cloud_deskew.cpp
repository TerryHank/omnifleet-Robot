#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sensor_msgs/msg/imu.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <std_msgs/msg/string.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <tf2_ros/buffer.h>
#include <tf2_ros/transform_listener.h>
#include <tf2_ros/transform_broadcaster.h>
#include <Eigen/Geometry>
#include <deque>
#include <unordered_set>
#include <algorithm>
#include <cstring>
#include <cstdlib>
#include <sstream>

#include "nav_motion.hpp"
class NavCloud:public rclcpp::Node{
 public:
 NavCloud():Node("nav_cloud_deskew"),buffer_(get_clock()),listener_(buffer_,this,true),broadcaster_(this){
   const char* id=std::getenv("OMNIFLEET_ROBOT_ID");if(!id)throw std::runtime_error("robot id missing");
   robot_=id;map_=robot_+"/map";sensor_=robot_+"/rslidar";
   source_=declare_parameter<std::string>("motion_source","imu");
   pub_=create_publisher<sensor_msgs::msg::PointCloud2>("/"+robot_+"/navigation/deskewed_points",rclcpp::SensorDataQoS());
   status_=create_publisher<std_msgs::msg::String>("/"+robot_+"/navigation/deskew_status",10);
   imu_=create_subscription<sensor_msgs::msg::Imu>("/"+robot_+"/omnifleet_t2/experiments/rslidar_imu_corrected",rclcpp::SensorDataQoS().keep_last(100),[this](sensor_msgs::msg::Imu::ConstSharedPtr m){on_imu(*m);});
   pose_=create_subscription<nav_msgs::msg::Odometry>("/"+robot_+"/lidar_odometry/pose",rclcpp::SensorDataQoS(),[this](nav_msgs::msg::Odometry::ConstSharedPtr m){on_pose(*m);});
   cloud_=create_subscription<sensor_msgs::msg::PointCloud2>("/"+robot_+"/rslidar_points",rclcpp::SensorDataQoS().keep_last(1),[this](sensor_msgs::msg::PointCloud2::ConstSharedPtr m){
     ++received_;if(pending_queue_.size()>=kMaxPendingMessages){pending_queue_.pop_front();++queue_overflow_drop_;}pending_queue_.push_back(std::move(m));++queued_;
   });
   timer_=create_wall_timer(std::chrono::milliseconds(5),[this]{process();});
   report_=create_wall_timer(std::chrono::seconds(2),[this]{std_msgs::msg::String m;std::ostringstream s;s<<"{\"received\":"<<received_<<",\"queued\":"<<queued_<<",\"processed\":"<<processed_<<",\"published\":"<<good_<<",\"dropped\":"<<dropped_<<",\"tf_wait_timeout_drop\":"<<tf_wait_timeout_drop_<<",\"queue_overflow_drop\":"<<queue_overflow_drop_<<",\"pending\":"<<pending_queue_.size()<<",\"processing_ms\":"<<processing_ms_<<",\"age_ms\":"<<age_ms_<<",\"anchor_age_ms\":"<<anchor_age_ms_<<",\"waiting\":\""<<waiting_<<"\"}";m.data=s.str();status_->publish(m);});
 }
 private:
 static double stamp(const builtin_interfaces::msg::Time& t){return t.sec+t.nanosec*1e-9;}
 static Quat quaternion(const geometry_msgs::msg::Quaternion& q){return Quat(q.w,q.x,q.y,q.z).normalized();}
 bool extrinsic(){
   if(extrinsic_ready_)return true;
   try{auto t=buffer_.lookupTransform(robot_+"/base_link",sensor_,tf2::TimePointZero).transform;
     sensor_p_=Vec(t.translation.x,t.translation.y,t.translation.z);sensor_q_=quaternion(t.rotation);extrinsic_ready_=true;return true;
   }catch(const tf2::TransformException&){return false;}
 }
 void on_imu(const sensor_msgs::msg::Imu& m){
   if(m.header.frame_id!=sensor_||!extrinsic())return;
   const double t=stamp(m.header.stamp);Vec w=sensor_q_*Vec(m.angular_velocity.x,m.angular_velocity.y,m.angular_velocity.z);
   if(!w.allFinite()||(!gyros_.empty()&&t<=gyros_.back().t))return;
   Quat q=Quat::Identity();
   if(!gyros_.empty()){
     const auto& prev=gyros_.back();double dt=t-prev.t;
     if(dt>.1)gyros_.clear();
     else{q=integrate_rotation(prev.q,prev.w,w,dt);}
   }
   gyros_.push_back({t,w,q});while(gyros_.size()>800)gyros_.pop_front();
 }
 void on_pose(const nav_msgs::msg::Odometry& m){
   if(m.header.frame_id!=map_||m.child_frame_id!=robot_+"/base_link")return;
   double t=stamp(m.header.stamp);if(!poses_.empty()&&t<=poses_.back().t)return;
   const auto& p=m.pose.pose.position;poses_.push_back({t,Vec(p.x,p.y,p.z),quaternion(m.pose.pose.orientation)});
   while(poses_.size()>30)poses_.pop_front();
 }
 Quat at(double t)const{
   return gyro_at(gyros_,t);
 }
 static double read(const uint8_t* data,int offset,int type){
   if(type==7){float value;std::memcpy(&value,data+offset,4);return value;}
   double value;std::memcpy(&value,data+offset,8);return value;
 }
 void process(){
   if(pending_queue_.empty()||!extrinsic())return;
   auto m=pending_queue_.front();
   if(m->header.frame_id!=sensor_||m->is_bigendian){pending_queue_.pop_front();++dropped_;++processed_;return;}
   int offsets[4]={-1,-1,-1,-1},types[4]={};const char* names[]={"x","y","z","timestamp"};
   for(const auto& f:m->fields)for(int i=0;i<4;i++)if(f.name==names[i]){offsets[i]=f.offset;types[i]=f.datatype;}
   for(int i=0;i<4;i++)if(offsets[i]<0||(types[i]!=7&&types[i]!=8)||offsets[i]+(types[i]==7?4:8)>int(m->point_step)){pending_queue_.pop_front();++dropped_;++processed_;return;}
   if(m->data.size()<size_t(m->height)*m->row_step){pending_queue_.pop_front();++dropped_;++processed_;return;}
   double lo=1e100,hi=-1e100;
   for(unsigned y=0;y<m->height;y++)for(unsigned x=0;x<m->width;x++){
     const auto* p=m->data.data()+y*m->row_step+x*m->point_step;double t=read(p,offsets[3],types[3]);
     if(std::isfinite(t)&&t>0){lo=std::min(lo,t);hi=std::max(hi,t);}
   }
   double now=get_clock()->now().seconds();
   if(hi<lo||hi-lo>.2||now-lo>.5||hi<=last_stamp_){pending_queue_.pop_front();++dropped_;++processed_;return;}
   const auto begin=std::chrono::steady_clock::now();const double ref=.5*(lo+hi);
   Quat origin_q;Vec origin_p,velocity=Vec::Zero();double ta=ref;Quat anchor_q=Quat::Identity();Vec anchor_p=Vec::Zero();
   geometry_msgs::msg::TransformStamped first,last;
   if(source_=="imu"){
     if(gyros_.size()<2||poses_.size()<2){waiting_="inputs";return;}
     auto pa=std::upper_bound(poses_.begin(),poses_.end(),hi,[](double t,const Pose& p){return t<p.t;});
     if(pa==poses_.begin()||std::prev(pa)==poses_.begin()){waiting_="anchor";return;}--pa;auto prev=std::prev(pa);ta=pa->t;
     if(hi-ta>.25||gyros_.front().t>std::min(lo,ta)||gyros_.back().t<hi){waiting_="coverage";return;}
     for(auto it=std::next(gyros_.begin());it!=gyros_.end();++it)if(it->t>=std::min(lo,ta)&&std::prev(it)->t<=hi&&it->t-std::prev(it)->t>.03){waiting_="gyro_gap";return;}
     velocity=(pa->p-prev->p)/(pa->t-prev->t);anchor_q=pa->q*at(ta).conjugate();anchor_p=pa->p;
     Quat qr=anchor_q*at(ref);origin_q=qr*sensor_q_;origin_p=anchor_p+velocity*(ref-ta)+qr*sensor_p_;anchor_age_ms_=(hi-ta)*1000;
   }else{
     try{first=buffer_.lookupTransform(map_,sensor_,rclcpp::Time(int64_t(lo*1e9)));last=buffer_.lookupTransform(map_,sensor_,rclcpp::Time(int64_t(hi*1e9)));auto t=buffer_.lookupTransform(map_,sensor_,rclcpp::Time(int64_t(ref*1e9))).transform;origin_q=quaternion(t.rotation);origin_p=Vec(t.translation.x,t.translation.y,t.translation.z);}catch(const tf2::TransformException& ex){
       std::string cloud_err,latest_err;const auto cloud_time=rclcpp::Time(int64_t(ref*1e9));
       const bool can_cloud=buffer_.canTransform(map_,sensor_,cloud_time,rclcpp::Duration::from_nanoseconds(0),&cloud_err);
       const bool can_latest=buffer_.canTransform(map_,sensor_,tf2::TimePointZero,tf2::durationFromSec(0.0),&latest_err);
       int64_t latest_ns=0;try{const auto latest=buffer_.lookupTransform(map_,sensor_,tf2::TimePointZero);latest_ns=int64_t(latest.header.stamp.sec)*1000000000LL+latest.header.stamp.nanosec;}catch(const tf2::TransformException&){}
       const double wall_now=get_clock()->now().seconds();const bool first_or_changed=waiting_!="tf";if(first_or_changed||wall_now-last_tf_diag_wall_>=1.0){
         RCLCPP_WARN(get_logger(),"historical TF wait cloud_stamp_ns=%lld cloud_header_stamp_ns=%lld now_ns=%lld cloud_age_ms=%.3f lookup_target=%s lookup_source=%s latest_tf_stamp_ns=%lld cloud_minus_latest_tf_ms=%.3f can_transform_at_cloud_stamp=%s can_transform_latest=%s tf_error=\"%s\" cloud_can_error=\"%s\" latest_can_error=\"%s\" published=%zu dropped=%zu waiting=tf",static_cast<long long>(ref*1e9),static_cast<long long>(m->header.stamp.sec)*1000000000LL+static_cast<long long>(m->header.stamp.nanosec),static_cast<long long>(wall_now*1e9),(wall_now-ref)*1000.0,map_.c_str(),sensor_.c_str(),static_cast<long long>(latest_ns),(ref*1e9-double(latest_ns))/1e6,can_cloud?"true":"false",can_latest?"true":"false",ex.what(),cloud_err.c_str(),latest_err.c_str(),good_,dropped_);last_tf_diag_wall_=wall_now;}
       if((now-ref)*1000.0>kMaxPendingAgeMs){pending_queue_.pop_front();++tf_wait_timeout_drop_;++processed_;waiting_="tf_timeout";}else waiting_="tf";return;}
   }
   sensor_msgs::msg::PointCloud2 out;out.header.frame_id=map_;out.header.stamp=rclcpp::Time(int64_t(ref*1e9));out.height=1;out.point_step=12;out.is_dense=true;
   for(int i=0;i<3;i++){sensor_msgs::msg::PointField f;f.name=names[i];f.offset=i*4;f.datatype=7;f.count=1;out.fields.push_back(f);}
   out.data.reserve(m->width*m->height*12);std::unordered_set<int64_t> voxels;voxels.reserve(30000);
   for(unsigned y=0;y<m->height;y++)for(unsigned x=0;x<m->width;x++){
     const auto* p=m->data.data()+y*m->row_step+x*m->point_step;Vec v(read(p,offsets[0],types[0]),read(p,offsets[1],types[1]),read(p,offsets[2],types[2]));double t=read(p,offsets[3],types[3]);
     if(!v.allFinite()||!std::isfinite(t)||t<lo||t>hi||v.norm()>8.)continue;
     Vec body=sensor_q_*v+sensor_p_;if(std::abs(body.x())<.30&&std::abs(body.y())<.235&&body.z()<.40)continue;
     int64_t key=int64_t(std::floor(v.x()/.05))*100000000+int64_t(std::floor(v.y()/.05))*10000+int64_t(std::floor(v.z()/.05));if(!voxels.insert(key).second)continue;
     Vec world;
     if(source_=="imu")world=project_point(anchor_q,anchor_p,velocity,ta,at(t),body,t);
     else{double a=(t-lo)/std::max(hi-lo,1e-9);const auto& p0=first.transform.translation;const auto& p1=last.transform.translation;world=quaternion(first.transform.rotation).slerp(a,quaternion(last.transform.rotation))*v+(1-a)*Vec(p0.x,p0.y,p0.z)+a*Vec(p1.x,p1.y,p1.z);}
     float xyz[]={float(world.x()),float(world.y()),float(world.z())};auto* bytes=reinterpret_cast<uint8_t*>(xyz);out.data.insert(out.data.end(),bytes,bytes+12);
   }
   out.width=out.data.size()/12;out.row_step=out.data.size();
   geometry_msgs::msg::TransformStamped tf;tf.header=out.header;tf.child_frame_id=robot_+"/navigation_lidar";
   tf.transform.translation.x=origin_p.x();tf.transform.translation.y=origin_p.y();tf.transform.translation.z=origin_p.z();
   tf.transform.rotation.x=origin_q.x();tf.transform.rotation.y=origin_q.y();tf.transform.rotation.z=origin_q.z();tf.transform.rotation.w=origin_q.w();
   broadcaster_.sendTransform(tf);pub_->publish(out);last_stamp_=hi;pending_queue_.pop_front();++good_;++processed_;waiting_="";
   processing_ms_=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-begin).count();age_ms_=(get_clock()->now().seconds()-ref)*1000;
 }
 std::string robot_,map_,sensor_,source_,waiting_;bool extrinsic_ready_=false;Vec sensor_p_;Quat sensor_q_;
 static constexpr size_t kMaxPendingMessages=3;static constexpr double kMaxPendingAgeMs=300.0;
 std::deque<Gyro> gyros_;std::deque<Pose> poses_;std::deque<sensor_msgs::msg::PointCloud2::ConstSharedPtr> pending_queue_;
 double last_stamp_=0,processing_ms_=0,age_ms_=0,anchor_age_ms_=0,last_tf_diag_wall_=-1;size_t received_=0,queued_=0,processed_=0,good_=0,dropped_=0,tf_wait_timeout_drop_=0,queue_overflow_drop_=0;
 tf2_ros::Buffer buffer_;tf2_ros::TransformListener listener_;tf2_ros::TransformBroadcaster broadcaster_;
 rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr cloud_;rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_;rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr pose_;
 rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr pub_;rclcpp::Publisher<std_msgs::msg::String>::SharedPtr status_;rclcpp::TimerBase::SharedPtr timer_,report_;
};
int main(int argc,char**argv){rclcpp::init(argc,argv);rclcpp::spin(std::make_shared<NavCloud>());rclcpp::shutdown();}
