#include "rs_driver/common/detail_trace.hpp"
/*********************************************************************************************************************
Copyright (c) 2020 RoboSense
All rights reserved

By downloading, copying, installing or using the software you agree to this license. If you do not agree to this
license, do not download, install, copy or use the software.

License Agreement
For RoboSense LiDAR SDK Library
(3-clause BSD License)

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the names of the RoboSense, nor Suteng Innovation Technology, nor the names of other contributors may be used
to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*********************************************************************************************************************/

#pragma once

#include "source/source.hpp"
#include "source/imu_kalman.hpp"

#ifdef ROS_FOUND
#include <ros/ros.h>
#include <sensor_msgs/point_cloud2_iterator.h>
#ifdef ENABLE_IMU_DATA_PARSE
  #include "sensor_msgs/Imu.h"
#endif
namespace robosense
{
namespace lidar
{

inline sensor_msgs::PointCloud2 toRosMsg(const LidarPointCloudMsg& rs_msg, const std::string& frame_id, bool send_by_rows)
{
  sensor_msgs::PointCloud2 ros_msg;

  int fields = 4;
#ifdef POINT_TYPE_XYZIF
  fields = 5;
#elif defined(POINT_TYPE_XYZIRT)
  fields = 6;
#elif defined(POINT_TYPE_XYZIRTF)
  fields = 7;
#endif
  ros_msg.fields.clear();
  ros_msg.fields.reserve(fields);

  if (send_by_rows)
  {
    ros_msg.width = rs_msg.width; 
    ros_msg.height = rs_msg.height; 
  }
  else
  {
    ros_msg.width = rs_msg.height; // exchange width and height to be compatible with pcl::PointCloud<>
    ros_msg.height = rs_msg.width; 
  }

  int offset = 0;
  offset = addPointField(ros_msg, "x", 1, sensor_msgs::PointField::FLOAT32, offset);
  offset = addPointField(ros_msg, "y", 1, sensor_msgs::PointField::FLOAT32, offset);
  offset = addPointField(ros_msg, "z", 1, sensor_msgs::PointField::FLOAT32, offset);
  offset = addPointField(ros_msg, "intensity", 1, sensor_msgs::PointField::FLOAT32, offset);
#if defined(POINT_TYPE_XYZIRT) || defined(POINT_TYPE_XYZIRTF)
  offset = addPointField(ros_msg, "ring", 1, sensor_msgs::PointField::UINT16, offset);
  offset = addPointField(ros_msg, "timestamp", 1, sensor_msgs::PointField::FLOAT64, offset);
#endif

#if defined(POINT_TYPE_XYZIF) || defined(POINT_TYPE_XYZIRTF) 
  offset = addPointField(ros_msg, "feature", 1, sensor_msgs::PointField::UINT8, offset);
#endif

#if 0
  std::cout << "off:" << offset << std::endl;
#endif

  ros_msg.point_step = offset;
  ros_msg.row_step = ros_msg.width * ros_msg.point_step;
  ros_msg.is_dense = rs_msg.is_dense;
  ros_msg.data.resize(ros_msg.point_step * ros_msg.width * ros_msg.height);

  sensor_msgs::PointCloud2Iterator<float> iter_x_(ros_msg, "x");
  sensor_msgs::PointCloud2Iterator<float> iter_y_(ros_msg, "y");
  sensor_msgs::PointCloud2Iterator<float> iter_z_(ros_msg, "z");
  sensor_msgs::PointCloud2Iterator<float> iter_intensity_(ros_msg, "intensity");

#if defined(POINT_TYPE_XYZIRT) || defined(POINT_TYPE_XYZIRTF)
  sensor_msgs::PointCloud2Iterator<uint16_t> iter_ring_(ros_msg, "ring");
  sensor_msgs::PointCloud2Iterator<double> iter_timestamp_(ros_msg, "timestamp");
#endif

#if defined(POINT_TYPE_XYZIF) || defined(POINT_TYPE_XYZIRTF) 
  sensor_msgs::PointCloud2Iterator<uint8_t> iter_feature_(ros_msg, "feature");
#endif

  if (send_by_rows)
  {
    for (size_t i = 0; i < rs_msg.height; i++)
    {
      for (size_t j = 0; j < rs_msg.width; j++)
      {
        const LidarPointCloudMsg::PointT& point = rs_msg.points[i + j * rs_msg.height];

        *iter_x_ = point.x;
        *iter_y_ = point.y;
        *iter_z_ = point.z;
        *iter_intensity_ = point.intensity;

        ++iter_x_;
        ++iter_y_;
        ++iter_z_;
        ++iter_intensity_;

#if defined(POINT_TYPE_XYZIRT) || defined(POINT_TYPE_XYZIRTF)
        *iter_ring_ = point.ring;
        *iter_timestamp_ = point.timestamp;

        ++iter_ring_;
        ++iter_timestamp_;
#endif

#if defined(POINT_TYPE_XYZIF) || defined(POINT_TYPE_XYZIRTF) 
        *iter_feature_ = point.feature;
        ++iter_feature_;
#endif
        
      }
    }
  }
  else
  {
    for (size_t i = 0; i < rs_msg.points.size(); i++)
    {
      const LidarPointCloudMsg::PointT& point = rs_msg.points[i];

      *iter_x_ = point.x;
      *iter_y_ = point.y;
      *iter_z_ = point.z;
      *iter_intensity_ = point.intensity;

      ++iter_x_;
      ++iter_y_;
      ++iter_z_;
      ++iter_intensity_;

#if defined(POINT_TYPE_XYZIRT) || defined(POINT_TYPE_XYZIRTF)
      *iter_ring_ = point.ring;
      *iter_timestamp_ = point.timestamp;

      ++iter_ring_;
      ++iter_timestamp_;
#endif

#if defined(POINT_TYPE_XYZIF) || defined(POINT_TYPE_XYZIRTF) 
        *iter_feature_ = point.feature;
        ++iter_feature_;
#endif
    }
  }

  ros_msg.header.seq = rs_msg.seq;
  ros_msg.header.stamp = ros_msg.header.stamp.fromSec(rs_msg.timestamp);
  ros_msg.header.frame_id = frame_id;

  return ros_msg;
}
#ifdef ENABLE_IMU_DATA_PARSE
sensor_msgs::Imu toRosMsg(const std::shared_ptr<ImuData>& data, const std::string& frame_id)
{
  sensor_msgs::Imu imu_msg;

  imu_msg.header.stamp = imu_msg.header.stamp.fromSec(data->timestamp);
  imu_msg.header.frame_id = frame_id;
  // Set IMU data
  imu_msg.angular_velocity.x = data->angular_velocity_x;
  imu_msg.angular_velocity.y = data->angular_velocity_y;
  imu_msg.angular_velocity.z = data->angular_velocity_z;

  imu_msg.linear_acceleration.x = data->linear_acceleration_x;
  imu_msg.linear_acceleration.y = data->linear_acceleration_y;
  imu_msg.linear_acceleration.z = data->linear_acceleration_z;
  return imu_msg;
}
#endif
class DestinationPointCloudRos : public DestinationPointCloud
{
public:

  virtual void init(const YAML::Node& config);
  virtual void sendPointCloud(const LidarPointCloudMsg& msg);
  virtual ~DestinationPointCloudRos() = default;
#ifdef ENABLE_IMU_DATA_PARSE
  virtual void sendImuData(const std::shared_ptr<ImuData> & data);
#endif
private:
  std::shared_ptr<ros::NodeHandle> nh_;
  ros::Publisher pub_; 
#ifdef ENABLE_IMU_DATA_PARSE
  ros::Publisher imu_pub_; 
#endif
  std::string frame_id_;
  bool send_by_rows_;
};

inline void DestinationPointCloudRos::init(const YAML::Node& config)
{
  yamlRead<bool>(config["ros"], 
      "ros_send_by_rows", send_by_rows_, false);

  bool dense_points;
  yamlRead<bool>(config["driver"], "dense_points", dense_points, false);
  if (dense_points)
    send_by_rows_ = false;

  yamlRead<std::string>(config["ros"], 
      "ros_frame_id", frame_id_, "rslidar");

  std::string ros_send_topic;
  yamlRead<std::string>(config["ros"], 
      "ros_send_point_cloud_topic", ros_send_topic, "rslidar_points");



  nh_ = std::unique_ptr<ros::NodeHandle>(new ros::NodeHandle());
  pub_ = nh_->advertise<sensor_msgs::PointCloud2>(ros_send_topic, 10);
#ifdef ENABLE_IMU_DATA_PARSE
  std::string ros_send_imu_data_topic;
  yamlRead<std::string>(config["ros"], 
      "ros_send_imu_data_topic", ros_send_imu_data_topic, "rslidar_imu_data");
  imu_pub_ = nh_->advertise<sensor_msgs::Imu>(ros_send_imu_data_topic, 1000);
#endif
}

inline void DestinationPointCloudRos::sendPointCloud(const LidarPointCloudMsg& msg)
{
  pub_.publish(toRosMsg(msg, frame_id_, send_by_rows_));
}
#ifdef ENABLE_IMU_DATA_PARSE
inline void DestinationPointCloudRos::sendImuData(const std::shared_ptr<ImuData> & data)
{
  imu_pub_.publish(toRosMsg(data, frame_id_));
}
#endif
}  // namespace lidar
}  // namespace robosense

#endif  // ROS_FOUND

#ifdef ROS2_FOUND
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/point_cloud2_iterator.hpp>
#ifdef ENABLE_IMU_DATA_PARSE
  #include <sensor_msgs/msg/imu.hpp>
#endif
#include <sstream>

namespace robosense
{
namespace lidar
{

inline sensor_msgs::msg::PointCloud2 toRosMsg(const LidarPointCloudMsg& rs_msg, const std::string& frame_id, bool send_by_rows)
{
  sensor_msgs::msg::PointCloud2 ros_msg;

  int fields = 4;
#ifdef POINT_TYPE_XYZIF
  fields = 5;
#elif defined(POINT_TYPE_XYZIRT)
  fields = 6;
#elif defined(POINT_TYPE_XYZIRTF)
  fields = 7;
#endif
  ros_msg.fields.clear();
  ros_msg.fields.reserve(fields);

  if (send_by_rows)
  {
    ros_msg.width = rs_msg.width; 
    ros_msg.height = rs_msg.height; 
  }
  else
  {
    ros_msg.width = rs_msg.height; // exchange width and height to be compatible with pcl::PointCloud<>
    ros_msg.height = rs_msg.width; 
  }

  int offset = 0;
  offset = addPointField(ros_msg, "x", 1, sensor_msgs::msg::PointField::FLOAT32, offset);
  offset = addPointField(ros_msg, "y", 1, sensor_msgs::msg::PointField::FLOAT32, offset);
  offset = addPointField(ros_msg, "z", 1, sensor_msgs::msg::PointField::FLOAT32, offset);
  offset = addPointField(ros_msg, "intensity", 1, sensor_msgs::msg::PointField::FLOAT32, offset);

#if defined(POINT_TYPE_XYZIRT) || defined(POINT_TYPE_XYZIRTF)
  offset = addPointField(ros_msg, "ring", 1, sensor_msgs::msg::PointField::UINT16, offset);
  offset = addPointField(ros_msg, "timestamp", 1, sensor_msgs::msg::PointField::FLOAT64, offset);
#endif

#if defined(POINT_TYPE_XYZIF) || defined(POINT_TYPE_XYZIRTF) 
  offset = addPointField(ros_msg, "feature", 1, sensor_msgs::msg::PointField::UINT8, offset);
#endif

#if 0
  std::cout << "off:" << offset << std::endl;
#endif

  ros_msg.point_step = offset;
  ros_msg.row_step = ros_msg.width * ros_msg.point_step;
  ros_msg.is_dense = rs_msg.is_dense;
  ros_msg.data.resize(ros_msg.point_step * ros_msg.width * ros_msg.height);

  sensor_msgs::PointCloud2Iterator<float> iter_x_(ros_msg, "x");
  sensor_msgs::PointCloud2Iterator<float> iter_y_(ros_msg, "y");
  sensor_msgs::PointCloud2Iterator<float> iter_z_(ros_msg, "z");
  sensor_msgs::PointCloud2Iterator<float> iter_intensity_(ros_msg, "intensity");
#if defined(POINT_TYPE_XYZIRT) || defined(POINT_TYPE_XYZIRTF)
  sensor_msgs::PointCloud2Iterator<uint16_t> iter_ring_(ros_msg, "ring");
  sensor_msgs::PointCloud2Iterator<double> iter_timestamp_(ros_msg, "timestamp");
#endif

#if defined(POINT_TYPE_XYZIF) || defined(POINT_TYPE_XYZIRTF) 
  sensor_msgs::PointCloud2Iterator<uint8_t> iter_feature_(ros_msg, "feature");
#endif

  if (send_by_rows)
  {
    for (size_t i = 0; i < rs_msg.height; i++)
    {
      for (size_t j = 0; j < rs_msg.width; j++)
      {
        const LidarPointCloudMsg::PointT& point = rs_msg.points[i + j * rs_msg.height];

        *iter_x_ = point.x;
        *iter_y_ = point.y;
        *iter_z_ = point.z;
        *iter_intensity_ = point.intensity;

        ++iter_x_;
        ++iter_y_;
        ++iter_z_;
        ++iter_intensity_;

#if defined(POINT_TYPE_XYZIRT) || defined(POINT_TYPE_XYZIRTF)
      *iter_ring_ = point.ring;
      *iter_timestamp_ = point.timestamp;

      ++iter_ring_;
      ++iter_timestamp_;
#endif

#if defined(POINT_TYPE_XYZIF) || defined(POINT_TYPE_XYZIRTF) 
        *iter_feature_ = point.feature;
        ++iter_feature_;
#endif

      }
    }
  }
  else
  {
    for (size_t i = 0; i < rs_msg.points.size(); i++)
    {
      const LidarPointCloudMsg::PointT& point = rs_msg.points[i];

      *iter_x_ = point.x;
      *iter_y_ = point.y;
      *iter_z_ = point.z;
      *iter_intensity_ = point.intensity;

      ++iter_x_;
      ++iter_y_;
      ++iter_z_;
      ++iter_intensity_;

#if defined(POINT_TYPE_XYZIRT) || defined(POINT_TYPE_XYZIRTF)
      *iter_ring_ = point.ring;
      *iter_timestamp_ = point.timestamp;

      ++iter_ring_;
      ++iter_timestamp_;
#endif

#if defined(POINT_TYPE_XYZIF) || defined(POINT_TYPE_XYZIRTF) 
      *iter_feature_ = point.feature;
      ++iter_feature_;
#endif
    }
  }

  ros_msg.header.stamp.sec = (uint32_t)floor(rs_msg.timestamp);
  ros_msg.header.stamp.nanosec = (uint32_t)round((rs_msg.timestamp - ros_msg.header.stamp.sec) * 1e9);
  ros_msg.header.frame_id = frame_id;

  return ros_msg;
}
#ifdef ENABLE_IMU_DATA_PARSE
sensor_msgs::msg::Imu toRosMsg(const std::shared_ptr<ImuData>& data, const std::string& frame_id)
{
  sensor_msgs::msg::Imu imu_msg;

  imu_msg.header.stamp = rclcpp::Time(static_cast<uint64_t>(data->timestamp * 1e9));
  imu_msg.header.frame_id = frame_id;
  // Set IMU data
  imu_msg.angular_velocity.x = data->angular_velocity_x;
  imu_msg.angular_velocity.y = data->angular_velocity_y;
  imu_msg.angular_velocity.z = data->angular_velocity_z;

  imu_msg.linear_acceleration.x = data->linear_acceleration_x;
  imu_msg.linear_acceleration.y = data->linear_acceleration_y;
  imu_msg.linear_acceleration.z = data->linear_acceleration_z;
  imu_msg.orientation.w = 1.0;
  imu_msg.orientation_covariance[0] = -1.0;
  return imu_msg;
}
#endif
class DestinationPointCloudRos : virtual public DestinationPointCloud
{
public:

  virtual void init(const YAML::Node& config);
  virtual void sendPointCloud(const LidarPointCloudMsg& msg);
#ifdef ENABLE_IMU_DATA_PARSE
  virtual void sendImuData(const std::shared_ptr<ImuData> & data);
#endif
  virtual ~DestinationPointCloudRos() = default;

private:
  std::shared_ptr<rclcpp::Node> node_ptr_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr pub_;
#ifdef ENABLE_IMU_DATA_PARSE
  rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr imu_pub_;
  rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr imu_raw_pub_;
  bool imu_kalman_enabled_ = false;
  ImuKalman imu_kalman_;

#endif
  std::string frame_id_;
  bool send_by_rows_;
};

inline void DestinationPointCloudRos::init(const YAML::Node& config)
{
  yamlRead<bool>(config["ros"], 
      "ros_send_by_rows", send_by_rows_, false);

  bool dense_points;
  yamlRead<bool>(config["driver"], "dense_points", dense_points, false);
  if (dense_points)
    send_by_rows_ = false;

  yamlRead<std::string>(config["ros"], 
      "ros_frame_id", frame_id_, "rslidar");

  std::string ros_send_topic;
  yamlRead<std::string>(config["ros"], 
      "ros_send_point_cloud_topic", ros_send_topic, "rslidar_points");

  size_t ros_queue_length;
  yamlRead<size_t>(config["ros"], "ros_queue_length", ros_queue_length, 100);

  static int node_index = 0;
  std::stringstream node_name;
  node_name << "rslidar_points_destination_" << node_index++;

  node_ptr_.reset(new rclcpp::Node(node_name.str()));

  pub_ = node_ptr_->create_publisher<sensor_msgs::msg::PointCloud2>(ros_send_topic, rclcpp::QoS(ros_queue_length).best_effort());

#ifdef ENABLE_IMU_DATA_PARSE
  std::string ros_send_imu_data_topic;
  yamlRead<std::string>(config["ros"], 
      "ros_send_imu_data_topic", ros_send_imu_data_topic, "rslidar_imu_data");
  imu_pub_ = node_ptr_->create_publisher<sensor_msgs::msg::Imu>(ros_send_imu_data_topic, 1000);
  std::string raw_topic;
  yamlRead<std::string>(config["ros"], "ros_send_imu_raw_topic", raw_topic, "rslidar_imu_data_raw");
  imu_raw_pub_ = node_ptr_->create_publisher<sensor_msgs::msg::Imu>(raw_topic, rclcpp::SensorDataQoS());
  yamlRead<bool>(config["ros"], "imu_kalman_enabled", imu_kalman_enabled_, false);
  if (imu_kalman_enabled_)
  {
    const auto r = config["ros"]["imu_kalman_measurement_variance"].as<std::vector<double>>();
    const auto q = config["ros"]["imu_kalman_process_variance_rate"].as<std::vector<double>>();
    if (r.size() != 6 || q.size() != 6)
      throw std::invalid_argument("IMU Kalman R and Q must each contain gyro xyz, accel xyz");
    std::array<double, 6> measurement_variance, process_variance_rate;
    std::copy(r.begin(), r.end(), measurement_variance.begin());
    std::copy(q.begin(), q.end(), process_variance_rate.begin());
    imu_kalman_.configure(measurement_variance, process_variance_rate);
  }
  RCLCPP_INFO(node_ptr_->get_logger(), "Airy IMU six-axis Kalman: %s; raw topic=%s",
              imu_kalman_enabled_ ? "enabled" : "disabled", raw_topic.c_str());

#endif

}

inline void DestinationPointCloudRos::sendPointCloud(const LidarPointCloudMsg& msg)
{
  causal_trace::emit("pc2_convert_begin",msg.timestamp);
  auto cloud = toRosMsg(msg, frame_id_, send_by_rows_);
  causal_trace::emit("pc2_publish_begin",msg.timestamp);
  pub_->publish(cloud);
  causal_trace::emit("pc2_publish_end",msg.timestamp);
}
#ifdef ENABLE_IMU_DATA_PARSE
inline void DestinationPointCloudRos::sendImuData(const std::shared_ptr<ImuData> & data)
{

  auto msg = toRosMsg(data, frame_id_);
  imu_raw_pub_->publish(msg);
  if (imu_kalman_enabled_)
  {
    const std::array<double, 6> measurement = {
      msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z,
      msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z};
    std::array<double, 6> filtered;
    if (!imu_kalman_.update(data->timestamp, measurement, filtered)) return;
    msg.angular_velocity.x = filtered[0];
    msg.angular_velocity.y = filtered[1];
    msg.angular_velocity.z = filtered[2];
    msg.linear_acceleration.x = filtered[3];
    msg.linear_acceleration.y = filtered[4];
    msg.linear_acceleration.z = filtered[5];
    const auto& variance = imu_kalman_.variance();
    for (size_t i = 0; i < 3; ++i)
    {
      msg.angular_velocity_covariance[4 * i] = variance[i];
      msg.linear_acceleration_covariance[4 * i] = variance[i + 3];
    }
  }
  imu_pub_->publish(msg);
}
#endif
}  // namespace lidar
}  // namespace robosense

#endif
