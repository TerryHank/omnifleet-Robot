// Copyright (c) 2024，D-Robotics.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#ifndef ROBOT_CTRL_NODE_H_
#define ROBOT_CTRL_NODE_H_
#include <string>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sys/stat.h>
#include <mutex>
#include <utility>
#include "std_msgs/msg/string.hpp"

#include "include/common.h"
#include "include/depth_backoff.h"
#include "include/bearing_centering.h"
#include "rcl_interfaces/msg/set_parameters_result.hpp"

class RobotCmdVelNode : public rclcpp::Node {
 public:
  explicit RobotCmdVelNode(const std::string &node_name) : Node(node_name) {
    RCLCPP_INFO(rclcpp::get_logger("RobotCmdVelNode"),
                "RobotCmdVelNode construct");
    twist_publisher_ = this->create_publisher<Twist>(twist_pub_topic_name_, 10);
    preview_publisher_ = this->create_publisher<Twist>("body_tracking_cmd", 10);
    state_publisher_ = this->create_publisher<std_msgs::msg::String>("body_tracking_state", 1);
    enable_motion_ = this->declare_parameter<bool>("enable_motion", true);
    gesture_control_ = this->declare_parameter<std::string>("operator_mode", "follow") == "gesture";
    this->declare_parameter<double>("follow_distance", LoadDistance());
    this->declare_parameter<double>("reverse_max_speed", .25);
    this->declare_parameter<double>("reverse_p", 1.0);
    this->declare_parameter<double>("steering_p", 1.8);
    this->declare_parameter<double>("steering_d", .35);
    this->declare_parameter<double>("steering_max_speed", .8);
    this->declare_parameter<double>("derivative_weight", .7);
    parameter_callback_ = this->add_on_set_parameters_callback([this](const std::vector<rclcpp::Parameter> &parameters) {
      rcl_interfaces::msg::SetParametersResult result; result.successful = true;
      for (const auto &parameter : parameters) {
        const auto name=parameter.get_name();
        if (name=="enable_motion" && parameter.get_type()!=rclcpp::ParameterType::PARAMETER_BOOL) {
          result.successful=false;result.reason="enable_motion must be bool";
        }
        if (name == "operator_mode" &&
            (parameter.get_type() != rclcpp::ParameterType::PARAMETER_STRING ||
             (parameter.as_string() != "follow" && parameter.as_string() != "gesture"))) {
          result.successful = false; result.reason = "operator_mode must be follow or gesture";
        }
        const bool tuning=name=="reverse_max_speed" || name=="reverse_p" || name=="steering_p" ||
                          name=="steering_d" || name=="steering_max_speed" || name=="derivative_weight";
        if (tuning && (parameter.get_type()!=rclcpp::ParameterType::PARAMETER_DOUBLE ||
                       !std::isfinite(parameter.as_double()) || parameter.as_double()<0. ||
                       (name=="derivative_weight" && parameter.as_double()>1.))) {
          result.successful=false;result.reason="gain/speed must be finite and nonnegative; derivative_weight must be in [0,1]";
        }
        if (parameter.get_name() == "follow_distance" &&
            (parameter.get_type() != rclcpp::ParameterType::PARAMETER_DOUBLE ||
             !std::isfinite(parameter.as_double()) || parameter.as_double() <= .1)) {
          result.successful = false; result.reason = "follow_distance must be a finite double greater than 0.1m";
        }
      }
      if (result.successful) {
        for (const auto &parameter : parameters) {
          if (parameter.get_name() == "follow_distance" && !SaveDistance(parameter.as_double())) {
            result.successful = false;
            result.reason = "Unable to save follow distance";
          }
        }
      }
      if (result.successful) {
        for (const auto &parameter : parameters) {
          if (parameter.get_name()=="enable_motion") {
            std::lock_guard<std::mutex> lock(motion_mutex_);
            if (enable_motion_ && !parameter.as_bool()) twist_publisher_->publish(Twist{});
            enable_motion_=parameter.as_bool();
          } else if (parameter.get_name() == "operator_mode") {
            std::lock_guard<std::mutex> lock(motion_mutex_);
            const bool next = parameter.as_string() == "gesture";
            if (gesture_control_ != next) {
              if (enable_motion_) twist_publisher_->publish(Twist{});
              preview_publisher_->publish(Twist{});
              gesture_control_ = next;
              ++mode_revision_;
            }
          }
        }
      }
      return result;
    });
  }

  double TargetDistance() const { return this->get_parameter("follow_distance").as_double(); }

  std::pair<bool, uint64_t> OperatorMode() const {
    std::lock_guard<std::mutex> lock(motion_mutex_);
    return {gesture_control_, mode_revision_};
  }

  void ApplyTuning(DepthBackoff &backoff, BearingCentering &centering) const {
    backoff.ConfigureReverse(get_parameter("reverse_p").as_double(),get_parameter("reverse_max_speed").as_double());
    centering.Configure(get_parameter("steering_p").as_double(),get_parameter("steering_d").as_double(),
                        get_parameter("steering_max_speed").as_double(),get_parameter("derivative_weight").as_double());
  }

  void RobotCtl(const Twist &msg, uint64_t mode_revision) const {
    std::stringstream ss;
    ss << "RobotCtl"
       << ", angular: " << msg.angular.x << " " << msg.angular.y << " "
       << msg.angular.z << ", linear: " << msg.linear.x << " " << msg.linear.y
       << " " << msg.linear.z
       << ", pub twist ts: " << TimeHelper::GetCurrentTimestampMicroSec();
    RCLCPP_WARN(rclcpp::get_logger("RobotCmdVelNode"), "%s", ss.str().data());

    std::lock_guard<std::mutex> lock(motion_mutex_);
    const bool stop = msg.linear.x == 0 && msg.linear.y == 0 && msg.linear.z == 0 &&
                      msg.angular.x == 0 && msg.angular.y == 0 && msg.angular.z == 0;
    if (!stop && mode_revision != mode_revision_) return;
    if (enable_motion_) twist_publisher_->publish(msg);
    preview_publisher_->publish(msg);
  }

  void PublishTrackingState(const TrackInfo &info, const builtin_interfaces::msg::Time &stamp, const DepthBackoff &backoff, const BearingCentering &centering, const char *gesture_motion = "NONE", bool follow_active = false) const {
    const char *state = info.tracking_sta == TrackingStatus::TRACKING ? "TRACKING" :
                        info.tracking_sta == TrackingStatus::LOST ? "LOST" : "INITING";
    std::ostringstream out;
    out << "{\"state\":\"" << state << "\",\"track_id\":" << info.track_id
        << ",\"serial_lost_num\":" << info.serial_lost_num
        << ",\"has_face_head\":" << (info.has_face_head ? "true" : "false")
        << ",\"source_stamp\":[" << stamp.sec << "," << stamp.nanosec << "]}";
    std::string payload = out.str();
    payload.pop_back();
    std::ostringstream distance;
    distance << ",\"range_base_m\":";
    if (std::isfinite(backoff.Range())) distance << backoff.Range(); else distance << "null";
    const std::string range_mode = backoff.Mode();
    const char *control_mode = ((range_mode == "FOLLOW" || range_mode == "APPROACH_FOR_DEPTH") &&
                                std::abs(centering.Error()) > .15) ? "CENTER" : backoff.Mode();
    if (std::string(gesture_motion) != "NONE") control_mode = info.serial_lost_num > 0 ? "WAIT_PERSON" : gesture_motion;
    bool motion;
    { std::lock_guard<std::mutex> lock(motion_mutex_); motion=enable_motion_; }
    distance << ",\"motion_enabled\":" << (motion?"true":"false")
             << ",\"operator_mode\":\"unified\""
             << ",\"follow_active\":" << (follow_active ? "true" : "false")
             << ",\"distance_mode\":\"" << backoff.Mode() << "\",\"control_mode\":\"" << control_mode
             << "\",\"target_distance_m\":" << backoff.Target()
             << ",\"heading_error_rad\":" << centering.Error()
             << ",\"gesture_motion\":\"" << gesture_motion << "\""
             << ",\"rotation_degrees\":0,\"rotation_active\":false,\"rotation_done\":false"
             << ",\"tuning\":{\"reverse_max_speed\":" << backoff.ReverseMaximum()
             << ",\"reverse_p\":" << backoff.ReverseP()
             << ",\"steering_p\":" << centering.P()
             << ",\"steering_d\":" << centering.D()
             << ",\"steering_max_speed\":" << centering.Maximum()
             << ",\"derivative_weight\":" << centering.Weight() << "}}";
    std_msgs::msg::String message; message.data = payload + distance.str(); state_publisher_->publish(message);
  }

 private:
  mutable std::mutex motion_mutex_;
  bool enable_motion_=false;
  bool gesture_control_ = false;
  uint64_t mode_revision_ = 0;
  static std::string DistanceDirectory() {
    const char *home = std::getenv("HOME");
    return std::string(home ? home : ".") + "/.config/omnifleet";
  }

  static double LoadDistance() {
    std::ifstream input(DistanceDirectory() + "/body_tracking_distance");
    double distance = 1.0;
    if (input >> distance && std::isfinite(distance) && distance > .1) return distance;
    return 1.0;
  }

  static bool SaveDistance(double distance) {
    const std::string directory = DistanceDirectory();
    ::mkdir(directory.substr(0, directory.find_last_of('/')).c_str(), 0700);
    ::mkdir(directory.c_str(), 0700);
    const std::string filename = directory + "/body_tracking_distance";
    const std::string temporary = filename + ".tmp";
    std::ofstream output(temporary);
    output.precision(17);
    output << distance << '\n';
    output.close();
    return output && std::rename(temporary.c_str(), filename.c_str()) == 0;
  }

  rclcpp::node_interfaces::OnSetParametersCallbackHandle::SharedPtr parameter_callback_;
  rclcpp::Publisher<Twist>::SharedPtr preview_publisher_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr state_publisher_;
  rclcpp::Publisher<Twist>::SharedPtr twist_publisher_ = nullptr;
  // topic name for turtle sim is "turtle1/cmd_vel" and for robot is "/cmd_vel"
  const std::string twist_pub_topic_name_ = "/cmd_vel";
};

#endif
