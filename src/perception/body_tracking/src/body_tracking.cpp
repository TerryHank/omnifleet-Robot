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

#include "include/body_tracking.h"

#include <algorithm>
#include <fstream>
#include <memory>
#include <new>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include "include/time_helper.h"
#include "include/util.h"

std::shared_ptr<TrackingManager> TrackingManager::Instance() {
  static std::shared_ptr<TrackingManager> inst = nullptr;
  if (!inst) {
    inst = std::shared_ptr<TrackingManager>(new TrackingManager());
  }
  return inst;
}

TrackingManager::TrackingManager() {
  start_ = true;

  track_info_.is_movectrl_running = false;

  param_node_ = std::make_shared<ParametersClass>(&track_cfg_);

  robot_cmdvel_node_ =
      std::make_shared<RobotCmdVelNode>("horizon_tracking_RobotCmdVel");

  last_frame_done_ = true;

  if (!smart_process_task_) {
    smart_process_task_ = std::make_shared<std::thread>([this]() {
      while (start_ && rclcpp::ok()) {
        std::unique_lock<std::mutex> lg(smart_queue_mtx_);
        smart_queue_condition_.wait_for(lg, std::chrono::seconds(1), [&]() {
          return !smart_queue_.empty() || !rclcpp::ok() || !start_;
        });
        if (smart_queue_.empty() || !rclcpp::ok() || !start_) {
          continue;
        }
        auto smart_frame = std::move(smart_queue_.front());
        smart_queue_.pop();
        lg.unlock();
        RunTrackingStrategy(smart_frame);
      }
    });
  }
}

TrackingManager::~TrackingManager() {}

void TrackingManager::Release() {
  RCLCPP_WARN(rclcpp::get_logger("TrackingManager"), "TrackingManager release");
  start_ = false;

  if (smart_process_task_ && smart_process_task_->joinable()) {
    smart_process_task_->join();
    smart_process_task_ = nullptr;
  }

  CancelMove();
  std::this_thread::sleep_for(std::chrono::milliseconds(50));
  param_node_ = nullptr;
  robot_cmdvel_node_ = nullptr;
}

void TrackingManager::UpdateTrackAngle() {
  if (track_info_.present_rect.empty()) return;

  cv::Point2f fit_center(track_cfg_.img_width / 2, track_cfg_.img_height);
  cv::Point2f start_pt(track_cfg_.img_width, track_cfg_.img_height);
  cv::Point2f end_pt(
      (track_info_.present_rect[0] + track_info_.present_rect[2]) / 2,
      (track_info_.present_rect[1] + track_info_.present_rect[3]) / 2);

  track_info_.angel_with_robot_ =
      CalAngelOfTwoVector(fit_center, start_pt, end_pt);

  {
    std::stringstream ss;
    ss << "frame_ts: " << track_info_.frame_ts
       << ", track_id: " << track_info_.track_id << ", angel_with_robot: "
       << std::abs(track_info_.angel_with_robot_ - 90)
       // << ", img_width_: " << img_width_ << ", img_height_: " << img_height_
       // << ", rect: " << track_info_.present_rect[0] << " " <<
       // track_info_.present_rect[1]
       // << " " << track_info_.present_rect[2]  << " " <<
       // track_info_.present_rect[3]
       << std::endl;
    RCLCPP_INFO(rclcpp::get_logger("TrackingManager"),
                "UpdateTrackAngle: %s",
                ss.str().data());
  }

  auto transform_y_angle_to_x_radian =
      [this](float robot_y_negtive_angel) -> float {
    float robot_x_positive_angel = robot_y_negtive_angel;
    bool kps_is_clock_wise = true;
    if (robot_y_negtive_angel < 90) {
      kps_is_clock_wise = true;
      robot_x_positive_angel = 90 - robot_x_positive_angel;
    } else if (robot_y_negtive_angel > 90) {
      kps_is_clock_wise = false;
      robot_x_positive_angel = robot_x_positive_angel - 90;
    }
    float robot_x_positive_radian = robot_x_positive_angel * PI / 180.0;
    if (kps_is_clock_wise) {
      robot_x_positive_radian = (-1.0) * robot_x_positive_radian;
    }

    std::stringstream ss;
    ss << "robot robot_y_negtive_angel: " << robot_y_negtive_angel
       << ", robot_x_positive_angel: " << robot_x_positive_angel
       << ", robot_x_positive_radian: " << robot_x_positive_radian
       << ", kps_is_clock_wise: " << kps_is_clock_wise;
    RCLCPP_INFO(rclcpp::get_logger("TrackingManager"), "%s", ss.str().c_str());
    return robot_x_positive_radian;
  };

  track_info_.robot_x_positive_radian_with_track_ =
      transform_y_angle_to_x_radian(track_info_.angel_with_robot_);
  track_info_.robot_y_negtive_radian_with_track_ =
      track_info_.angel_with_robot_ * PI / 180.0;
}

void TrackingManager::DoRotateMove() {
  if (!robot_cmdvel_node_) return;

  auto twist = std::make_shared<Twist>();
  twist->linear.x = 0;
  twist->linear.y = 0;
  twist->linear.z = 0;
  twist->angular.x = 0;
  twist->angular.y = 0;
  twist->angular.z = 0;

  bool do_move = false;
  bool do_rotate = false;
  const double bearing = bearing_valid_ ? bearing_error_ : (track_info_.angel_with_robot_-90.)*PI/180.;
  const double source_time = track_info_.frame_ts_sec + track_info_.frame_ts_nanosec*1e-9;
  twist->angular.z = centering_.Update(track_info_.track_id, bearing, source_time);
  do_rotate = std::abs(twist->angular.z) > 1e-6;

  twist->linear.x = depth_backoff_.Velocity(track_cfg_.move_step);
  if (std::string(depth_backoff_.Mode()) == "APPROACH_FOR_DEPTH") twist->linear.x = .08;
  if (twist->linear.x > 0. && std::abs(bearing) > .15) twist->linear.x = 0.;
  do_move = std::abs(twist->linear.x) > 1e-6;

  if (do_move || do_rotate) {
    last_cmdvel_is_cancel_ = false;
    last_cmdvel_type_ = 2;
    RCLCPP_WARN(rclcpp::get_logger("TrackingManager"),
                "Do rotate move, ts sec: %llu, nanosec: %llu",
                track_info_.frame_ts_sec,
                track_info_.frame_ts_nanosec);
    robot_cmdvel_node_->RobotCtl(*twist);

    // if (do_rotate) {
    //   // 避免由于智能结果输出时间间隔不均匀导致的小车过度运动
    //   static int cmd_ms = 30;
    //   std::this_thread::sleep_for(std::chrono::milliseconds(cmd_ms));
    //   CancelMove();
    // }
  } else {
    CancelMove();
  }
}

void TrackingManager::CancelMove() {
  if (last_cmdvel_is_cancel_) return;
  if (robot_cmdvel_node_) {
    RCLCPP_WARN(rclcpp::get_logger("TrackingManager"), "cancel move");
    auto twist = std::make_shared<Twist>();
    twist->linear.x = 0;
    twist->linear.y = 0;
    twist->linear.z = 0;
    twist->angular.x = 0;
    twist->angular.y = 0;
    twist->angular.z = 0;
    robot_cmdvel_node_->RobotCtl(*twist);
  }

  last_cmdvel_is_cancel_ = true;
  last_cmdvel_type_ = -1;
  last_move_step_ratio_ = 1.0;
}

void TrackingManager::ProcessSmart(
    const ai_msgs::msg::PerceptionTargets::ConstSharedPtr &msg) {
  if (!msg || !rclcpp::ok()) {
    return;
  }

  uint64_t frame_ts = (msg->header.stamp.sec % 1000) * 1000 +
                      msg->header.stamp.nanosec / 1000 / 1000;

  track_info_.frame_ts_sec = msg->header.stamp.sec;
  track_info_.frame_ts_nanosec = msg->header.stamp.nanosec;

  RCLCPP_INFO(rclcpp::get_logger("TrackingManager"),
              "process smart frame_ts %llu",
              frame_ts);

  // update track info
  // if the track is lost, reset track info
  if (TrackingStatus::TRACKING == track_info_.tracking_sta) {
    // update status
    // find track
    bool find_track = false;
    std::vector<int> present_rect;
    int body_kps_5_y = -1;
    int body_kps_6_y = -1;
    int gesture = 0;
    for (const auto &target : msg->targets) {
      if (track_cfg_.track_body) {
        // tracking body
        bool tar_has_body = false;
        std::vector<int> body_rect;
        for (const auto &roi : target.rois) {
          if ("body" == roi.type) {
            tar_has_body = true;
            body_rect.push_back(roi.rect.x_offset);
            body_rect.push_back(roi.rect.y_offset);
            body_rect.push_back(roi.rect.x_offset + roi.rect.width);
            body_rect.push_back(roi.rect.y_offset + roi.rect.height);
            break;
          }
        }

        if (!tar_has_body) continue;
        if (target.track_id == track_info_.track_id) {
          find_track = true;
          present_rect = body_rect;
          // 获取target对应的kps，用于误触发策略
          for (const auto &point : target.points) {
            if ("body_kps" == point.type) {
              body_kps_5_y = point.point.at(5).y;
              body_kps_6_y = point.point.at(6).y;
              break;
            }
          }
          break;
        }
      } else {
        // tracking hand
        bool tar_has_hand = false;
        std::vector<int> hand_rect;
        for (const auto &roi : target.rois) {
          if ("hand" == roi.type) {
            tar_has_hand = true;
            hand_rect.push_back(roi.rect.x_offset);
            hand_rect.push_back(roi.rect.y_offset);
            hand_rect.push_back(roi.rect.x_offset + roi.rect.width);
            hand_rect.push_back(roi.rect.y_offset + roi.rect.height);
            break;
          }
        }

        if (!tar_has_hand) continue;

        int tar_gesture = -1;
        for (const auto &attr : target.attributes) {
          RCLCPP_INFO(rclcpp::get_logger("TrackingManager"),
                      "track_id: %d, attr type: %s, val: %d",
                      target.track_id,
                      attr.type.c_str(),
                      attr.value);
          if ("gesture" == attr.type) {
            tar_gesture = attr.value;
          }
        }

        gesture = tar_gesture;
        if (target.track_id == track_info_.track_id) {
          find_track = true;
          present_rect = hand_rect;
          break;
        }
      }
    }

    if (find_track) {
      if (1 == track_cfg_.activate_wakeup_gesture) {
        if (track_cfg_.track_body) {
          // tracking body
          // check if has cancel gesture
          for (const auto &target : msg->targets) {
            bool owned_hand = true;
            for (const auto &attr : target.attributes) {
              if (attr.type == "body_track_id" &&
                  static_cast<uint64_t>(attr.value) != track_info_.track_id) owned_hand = false;
            }
            if (!owned_hand) continue;
            bool tar_has_hand = false;
            std::vector<int> hand_rect;
            for (const auto &roi : target.rois) {
              if ("hand" == roi.type) {
                tar_has_hand = true;
                hand_rect.push_back(roi.rect.x_offset);
                hand_rect.push_back(roi.rect.y_offset);
                hand_rect.push_back(roi.rect.x_offset + roi.rect.width);
                hand_rect.push_back(roi.rect.y_offset + roi.rect.height);
                break;
              }
            }

            if (!tar_has_hand) continue;

            int tar_gesture = -1;
            for (const auto &attr : target.attributes) {
              RCLCPP_INFO(rclcpp::get_logger("TrackingManager"),
                          "track_id: %d, attr type: %s, val: %d",
                          target.track_id,
                          attr.type.c_str(),
                          attr.value);
              if ("gesture" == attr.type) {
                tar_gesture = attr.value;
              }
            }

            if (tar_gesture != track_cfg_.cancel_tracking_gesture_ ||
                present_rect.empty())
              continue;
            const auto &present_hand_rect = hand_rect;
            if (present_hand_rect[0] >= present_rect[0] &&
                present_hand_rect[0] <= present_rect[2] &&
                present_hand_rect[2] >= present_rect[0] &&
                present_hand_rect[2] <= present_rect[2] &&
                present_hand_rect[1] >= present_rect[1] &&
                present_hand_rect[1] <= present_rect[3] &&
                present_hand_rect[3] >= present_rect[1] &&
                present_hand_rect[3] <= present_rect[3]) {
              // 检查hand rect的中心店是否在人体肩部（人体骨骼关键点的index5和6）以上，避免误触发
              bool cancel = false;
              if (body_kps_5_y < 0 || body_kps_6_y < 0) {
                // match the body box
                cancel = true;
              } else {
                int hand_center_y = (present_hand_rect[1] + present_hand_rect[3]) / 2;
                if (hand_center_y < body_kps_5_y && hand_center_y < body_kps_6_y) {
                  cancel = true;
                } else {
                  cancel = false;
                }
              }
              if (cancel) {
                // match the body box
                RCLCPP_WARN(
                    rclcpp::get_logger("TrackingManager"),
                    "frame_ts %llu, track id: %d recved cancel gesture: %d",
                    frame_ts,
                    track_info_.track_id,
                    tar_gesture);
                track_info_.tracking_sta = TrackingStatus::INITING;
                gesture = tar_gesture;
                track_info_.gesture = gesture;
                break;
              }
            }
          }
        } else {
          // tracking hand
          if (gesture == track_cfg_.cancel_tracking_gesture_) {
            RCLCPP_WARN(rclcpp::get_logger("TrackingManager"),
                        "frame_ts %llu, track id: %d recved cancel gesture: %d",
                        frame_ts,
                        track_info_.track_id,
                        gesture);
            track_info_.tracking_sta = TrackingStatus::INITING;
            track_info_.gesture = gesture;
          }
        }
      }

      // update rect
      track_info_.serial_lost_num = 0;
      track_info_.last_rect = track_info_.present_rect;
      track_info_.present_rect = present_rect;
      track_info_.frame_ts = frame_ts;
      track_info_.gesture = gesture;
    } else {
      RCLCPP_INFO(rclcpp::get_logger("TrackingManager"),
                  "find track fail! frame_ts %llu",
                  frame_ts);

      track_info_.gesture = gesture;
      track_info_.serial_lost_num++;

      if (track_info_.serial_lost_num > 5 &&
          track_info_.serial_lost_num % 10 == 0) {
        RCLCPP_WARN(rclcpp::get_logger("TrackingManager"),
                    "frame_ts %llu, track id: %d serial lost num: %d",
                    frame_ts,
                    track_info_.track_id,
                    track_info_.serial_lost_num);
      }

      if (track_info_.serial_lost_num >= track_cfg_.track_serial_lost_num_thr) {
        // track lost, activate reset tracking strategy
        RCLCPP_ERROR(rclcpp::get_logger("TrackingManager"),
                     "track id: %d serial lost num exceed limit: %d",
                     track_info_.track_id,
                     track_cfg_.track_serial_lost_num_thr);
        track_info_.~TrackInfo();
        new (&track_info_) TrackInfo();
        track_info_.is_movectrl_running = false;
        track_info_.tracking_sta = TrackingStatus::LOST;
      }
    }
  } else if (TrackingStatus::INITING == track_info_.tracking_sta ||
             TrackingStatus::LOST == track_info_.tracking_sta) {
    if (msg->targets.empty()) {
      return;
    }

    bool find_track = false;
    bool has_body = false;
    bool has_hand = false;
    uint64_t track_id;
    uint64_t body_id;
    uint64_t hand_id;
    int64_t hand_body_id = -1;
    std::vector<int> present_track_rect;
    std::vector<int> present_body_rect;
    std::vector<int> present_hand_rect;
    int gesture = 0;

    if (1 == track_cfg_.activate_wakeup_gesture) {
      // check if has activate gesture
      for (const auto &target : msg->targets) {
        bool tar_has_hand = false;
        std::vector<int> hand_rect;
        for (const auto &roi : target.rois) {
          if ("hand" == roi.type) {
            tar_has_hand = true;
            hand_rect.push_back(roi.rect.x_offset);
            hand_rect.push_back(roi.rect.y_offset);
            hand_rect.push_back(roi.rect.x_offset + roi.rect.width);
            hand_rect.push_back(roi.rect.y_offset + roi.rect.height);
            break;
          }
        }

        if (!tar_has_hand || hand_rect.empty()) continue;

        int tar_gesture = -1;
        int64_t tar_body_id = -1;
        for (const auto &attr : target.attributes) {
          RCLCPP_INFO(rclcpp::get_logger("TrackingManager"),
                      "track_id: %d, attr type: %s, val: %d",
                      target.track_id,
                      attr.type.c_str(),
                      attr.value);
          if ("gesture" == attr.type) {
            tar_gesture = attr.value;
          }
          if (attr.type == "body_track_id") tar_body_id = static_cast<int64_t>(attr.value);
        }

        if (tar_gesture < 0 ||
            tar_gesture != track_cfg_.wakeup_tracking_gesture_)
          continue;
        gesture = tar_gesture;

        // 找到了具有激活手势的hand
        const auto &rect = hand_rect;
        if (!has_hand) {
          has_hand = true;
          hand_id = target.track_id;
          hand_body_id = tar_body_id;
          present_hand_rect = rect;
        } else if ((present_hand_rect[2] - present_hand_rect[0]) <
                   (rect[2] - rect[0])) {
          // 具有多个激活手势的hand，选择宽度最大hand
          hand_id = target.track_id;
          hand_body_id = tar_body_id;
          present_hand_rect = rect;
        }
      }

      if (has_hand) {
        // found activate gesture
        // find the body, which includes has gesture
        if (track_cfg_.track_body) {
          // tracking body
          for (const auto &target : msg->targets) {
            if (hand_body_id >= 0 && target.track_id != static_cast<uint64_t>(hand_body_id)) continue;
            bool tar_has_body = false;
            std::vector<int> body_rect;
            for (const auto &roi : target.rois) {
              if ("body" == roi.type) {
                tar_has_body = true;
                body_rect.push_back(roi.rect.x_offset);
                body_rect.push_back(roi.rect.y_offset);
                body_rect.push_back(roi.rect.x_offset + roi.rect.width);
                body_rect.push_back(roi.rect.y_offset + roi.rect.height);
                break;
              }
            }

            if (!tar_has_body || body_rect.empty()) continue;
            const auto &rect = body_rect;
            // 检查hand rect是否在body rect内
            if (present_hand_rect[0] >= rect[0] &&
                present_hand_rect[0] <= rect[2] &&
                present_hand_rect[2] >= rect[0] &&
                present_hand_rect[2] <= rect[2] &&
                present_hand_rect[1] >= rect[1] &&
                present_hand_rect[1] <= rect[3] &&
                present_hand_rect[3] >= rect[1] &&
                present_hand_rect[3] <= rect[3]) {

              // 检查hand rect的中心店是否在人体肩部（人体骨骼关键点的index5和6）以上，避免误触发
              bool tar_has_body_kps = false;
              int body_kps_5_y = -1;
              int body_kps_6_y = -1;
              for (const auto &point : target.points) {
                if ("body_kps" == point.type) {
                  tar_has_body_kps = true;
                  body_kps_5_y = point.point.at(5).y;
                  body_kps_6_y = point.point.at(6).y;
                  break;
                }
              }
              if (!tar_has_body_kps) {
                // match the body box
                has_body = true;
              } else {
                int hand_center_y = (present_hand_rect[1] + present_hand_rect[3]) / 2;
                if (hand_center_y < body_kps_5_y && hand_center_y < body_kps_6_y) {
                  has_body = true;
                } else {
                  has_body = false;
                }
              }
              if (has_body) {
                body_id = target.track_id;
                present_body_rect = rect;
                break;
              }
            }
          }

          if (has_body) {
            track_id = body_id;
            find_track = true;
            present_track_rect = present_body_rect;
          }
        } else {
          // tracking hand
          track_id = hand_id;
          find_track = true;
          present_track_rect = present_hand_rect;
        }
      }
    } else {
      for (const auto &target : msg->targets) {
        bool tar_has_body = false;
        std::vector<int> body_rect;
        for (const auto &roi : target.rois) {
          if ("body" == roi.type) {
            tar_has_body = true;
            body_rect.push_back(roi.rect.x_offset);
            body_rect.push_back(roi.rect.y_offset);
            body_rect.push_back(roi.rect.x_offset + roi.rect.width);
            body_rect.push_back(roi.rect.y_offset + roi.rect.height);
            break;
          }
        }

        if (!tar_has_body || body_rect.empty()) continue;
        const auto &rect = body_rect;
        if (!has_body) {
          has_body = true;
          body_id = target.track_id;
          present_body_rect = rect;
        } else if ((present_body_rect[2] - present_body_rect[0]) <
                   (rect[2] - rect[0])) {
          body_id = target.track_id;
          present_body_rect = rect;
        }
      }

      if (has_body) {
        track_id = body_id;
        find_track = true;
        present_track_rect = present_body_rect;
      }
    }

    if (find_track) {
      track_info_.~TrackInfo();
      new (&track_info_) TrackInfo();
      track_info_.is_movectrl_running = false;
      track_info_.tracking_sta = TrackingStatus::TRACKING;
      track_info_.track_id = track_id;
      track_info_.present_rect = present_track_rect;
      track_info_.gesture = gesture;
      track_info_.frame_ts = frame_ts;
      RCLCPP_WARN(rclcpp::get_logger("TrackingManager"),
                  "update frame_ts %llu, %d",
                  frame_ts,
                  __LINE__);

      std::stringstream ss;
      ss << "Tracking " << (track_cfg_.track_body ? "body" : "hand")
         << " start!"
         << ", track_id: " << track_info_.track_id
         << ", frame_ts: " << track_info_.frame_ts
         << ", tracking_sta(0:INITING, 1:TRACKING, 2:LOST): "
         << static_cast<int>(track_info_.tracking_sta)
         << ", gesture: " << track_info_.gesture;
      RCLCPP_WARN(rclcpp::get_logger("TrackingManager"), "%s", ss.str().data());
    }
  }

  if (TrackingStatus::TRACKING == track_info_.tracking_sta) {
    track_info_.has_face_head = false;
    for (const auto &target : msg->targets) {
      auto match_rect = [](std::vector<int> body_rect,
                           std::vector<int> face_head_rect) -> bool {
        if (body_rect.size() < 4 || face_head_rect.size() < 4) return false;
        if (body_rect[0] <= face_head_rect[0] &&
            body_rect[1] <= face_head_rect[1] &&
            body_rect[2] >= face_head_rect[2] &&
            body_rect[3] >= face_head_rect[3]) {
          return true;
        }
        return false;
      };

      bool has_face = false;
      std::vector<int> face_rect;
      bool has_head = false;
      std::vector<int> head_rect;
      for (const auto &roi : target.rois) {
        if ("face" == roi.type) {
          has_face = true;
          face_rect.push_back(roi.rect.x_offset);
          face_rect.push_back(roi.rect.y_offset);
          face_rect.push_back(roi.rect.x_offset + roi.rect.width);
          face_rect.push_back(roi.rect.y_offset + roi.rect.height);
        }

        if ("head" == roi.type) {
          has_head = true;
          head_rect.push_back(roi.rect.x_offset);
          head_rect.push_back(roi.rect.y_offset);
          head_rect.push_back(roi.rect.x_offset + roi.rect.width);
          head_rect.push_back(roi.rect.y_offset + roi.rect.height);
        }

        if (has_face && has_head) {
          break;
        }
      }

      if (has_face && !track_info_.has_face_head) {
        auto &rect = face_rect;
        if (match_rect(track_info_.present_rect, rect)) {
          track_info_.has_face_head = true;
          break;
        }
      }
      if (has_head && !track_info_.has_face_head) {
        auto &rect = head_rect;
        if (match_rect(track_info_.present_rect, rect)) {
          track_info_.has_face_head = true;
          break;
        }
      }
    }

    if (track_info_.has_face_head) {
      track_info_.serial_lost_face_head_num = 0;
    } else {
      track_info_.serial_lost_face_head_num++;
    }

    RCLCPP_INFO_STREAM(
        rclcpp::get_logger("TrackingManager"),
        "serial_lost_face_head_num: " << track_info_.serial_lost_face_head_num);
  }
}

void TrackingManager::RunTrackLostProtectionStrategy() {
  if (track_info_.serial_lost_face_head_num >= 20) {
    // start protection strategy
    RCLCPP_INFO(rclcpp::get_logger("TrackingManager"),
                "track lost warnning! serial_lost_face_head_num: %d",
                track_info_.serial_lost_face_head_num);
    // cancel move goal
    CancelMove();
  }
  return;

  int angle_with_track = std::abs(track_info_.angel_with_robot_ - 90);
  // start protection strategy
  RCLCPP_INFO(rclcpp::get_logger("TrackingManager"),
              "The angle between robot and track is %d, limit is %d",
              angle_with_track,
              track_cfg_.track_lost_protection_angel_thr);

  if (angle_with_track < track_cfg_.track_lost_protection_angel_thr) {
    return;
  }

  // start protection strategy
  RCLCPP_WARN(rclcpp::get_logger("TrackingManager"),
              "track lost warnning! The angle between robot and track is %d "
              "exceeds limit %d, track lost protection strategy is activated!",
              std::abs(track_info_.angel_with_robot_ - 90),
              track_cfg_.track_lost_protection_angel_thr);
  // cancel move goal
  CancelMove();
}

void TrackingManager::RunOverMovingProtectionStrategy() {
  if (!last_cmdvel_is_cancel_ && 0 == last_cmdvel_type_ &&
      (std::abs(track_info_.angel_with_robot_ - 90) <
       track_cfg_.track_overmoving_protection_angel_thr)) {
    // start protection strategy
    RCLCPP_WARN(rclcpp::get_logger("TrackingManager"),
                "frame_ts %llu, robot over moving warnning! The angle between "
                "robot and track is %d, less than limit %d, robot overmoving "
                "strategy is activated!",
                track_info_.frame_ts,
                std::abs(track_info_.angel_with_robot_ - 90),
                track_cfg_.track_overmoving_protection_angel_thr);
    CancelMove();
  }
}

void TrackingManager::UpdateDepthBackoff(
    const ai_msgs::msg::PerceptionTargets::ConstSharedPtr &msg) {
  const int64_t identity = track_info_.tracking_sta == TrackingStatus::TRACKING
      ? static_cast<int64_t>(track_info_.track_id) : -1;
  depth_backoff_.SetTarget(robot_cmdvel_node_->TargetDistance());
  robot_cmdvel_node_->ApplyTuning(depth_backoff_, centering_);
  double range = 0., sample_age = 1.;
  bearing_valid_ = false;
  bool found = false;
  for (const auto &target : msg->targets) {
    if (static_cast<int64_t>(target.track_id) != identity) continue;
    for (const auto &attribute : target.attributes) {
      if (attribute.type == "bearing_rad" && std::isfinite(attribute.value)) {
        bearing_error_ = attribute.value; bearing_valid_ = true;
      }
      if (attribute.type == "range_base_m") { range = attribute.value; found = true; }
      if (attribute.type == "range_age_s") sample_age = attribute.value;
    }
  }
  const double frame_age = (robot_cmdvel_node_->now() - rclcpp::Time(msg->header.stamp)).seconds();
  depth_backoff_.Observe(identity, found && sample_age >= 0. && sample_age <= .35 &&
                        frame_age >= -.1 && frame_age <= .35, range);
}

void TrackingManager::ApplyMotionGestures(
    const ai_msgs::msg::PerceptionTargets::ConstSharedPtr &msg) {
  const bool completed_turn = gesture_motion_ >= 3 && robot_cmdvel_node_->RotationDone();
  const int64_t locked = track_info_.tracking_sta == TrackingStatus::TRACKING && !completed_turn
      ? static_cast<int64_t>(track_info_.track_id) : -1;
  for (const auto &person : msg->targets) {
    if (locked >= 0 && static_cast<int64_t>(person.track_id) != locked) continue;
    for (const auto &attr : person.attributes) {
      if (attr.type == "hand_gesture_observation" && attr.value == 0.) last_motion_gesture_ = 0;
    }
  }
  for (const auto &hand : msg->targets) {
    int gesture = -1;
    int64_t owner = -1;
    bool has_hand = false;
    for (const auto &roi : hand.rois) if (roi.type == "hand") has_hand = true;
    if (!has_hand) continue;
    for (const auto &attr : hand.attributes) {
      if (attr.type == "gesture") gesture = static_cast<int>(attr.value);
      if (attr.type == "body_track_id") owner = static_cast<int64_t>(attr.value);
    }
    if (owner < 0 || (locked >= 0 && owner != locked)) continue;
    bool present = false;
    for (const auto &person : msg->targets) {
      if (static_cast<int64_t>(person.track_id) != owner) continue;
      for (const auto &roi : person.rois) if (roi.type == "body") present = true;
    }
    if (!present) continue;
    if (gesture == 5) {
      robot_cmdvel_node_->StopRotation();
      last_motion_gesture_ = gesture;
      gesture_motion_ = 0;
      track_info_.tracking_sta = TrackingStatus::INITING;
      track_info_.track_id = 0;
      CancelMove();
      return;
    }
    if (gesture == 11) {
      robot_cmdvel_node_->StopRotation();
      last_motion_gesture_ = gesture;
      gesture_motion_ = 0;
      if (completed_turn) {
        track_info_.tracking_sta = TrackingStatus::INITING;
        track_info_.track_id = 0;
      }
      return;
    }
    if (gesture >= 101 && gesture <= 104) {
      const int requested = gesture-100;
      if (requested <= 2) robot_cmdvel_node_->StopRotation();
      else if (last_motion_gesture_ != gesture &&
               !(gesture_motion_ == requested && robot_cmdvel_node_->RotationActive())) {
        robot_cmdvel_node_->StartRotation(requested == 3 ? -1 : 1,track_cfg_.rotate_step);
      }
      last_motion_gesture_ = gesture;
      gesture_motion_ = gesture-100;
      track_info_.tracking_sta = TrackingStatus::TRACKING;
      track_info_.track_id = static_cast<uint64_t>(owner);
      track_info_.serial_lost_num = 0;
      return;
    }
  }
}

// 不支持避障的跟随策略，适用于只有camera，没有imu lidar等传感器的情况
void TrackingManager::TrackingWithoutNavStrategy(
    const ai_msgs::msg::PerceptionTargets::ConstSharedPtr &msg) {
  RCLCPP_INFO(rclcpp::get_logger("TrackingManager"),
              "Run TrackingWithoutNav strategy");

  if (!last_frame_done_) {
    RCLCPP_WARN(rclcpp::get_logger("TrackingManager"),
                "last frame is not done");
    return;
  }

  // 1. update track info
  ApplyMotionGestures(msg);
  if (gesture_motion_ >= 3) {
    // A complete turn necessarily moves the operator out of the camera view.
    // The bounded odometry goal keeps running independently of body visibility.
    UpdateDepthBackoff(msg);
    robot_cmdvel_node_->PublishRotation();
    last_cmdvel_is_cancel_ = false;
    last_frame_done_ = true;
    return;
  }
  ProcessSmart(msg);
  UpdateDepthBackoff(msg);

  last_frame_done_ = false;

  if (TrackingStatus::INITING == track_info_.tracking_sta) {
    robot_cmdvel_node_->StopRotation();
    last_motion_gesture_ = 0;
    gesture_motion_ = 0;
    CancelMove();
    last_frame_done_ = true;
    return;
  }

  uint64_t frame_ts = (msg->header.stamp.sec % 1000) * 1000 +
                      msg->header.stamp.nanosec / 1000 / 1000;
  {
    std::stringstream ss;
    ss << "track_id: " << track_info_.track_id
       << ", frame_ts: " << track_info_.frame_ts
       << ", tracking_sta(0:INITING, 1:TRACKING, 2:LOST): "
       << static_cast<int>(track_info_.tracking_sta)
       << ", gesture: " << track_info_.gesture << ", y pixel to robot: "
       << (track_info_.present_rect.empty()
               ? -1
               : (track_cfg_.img_height - track_info_.present_rect[3]));
    if (!track_info_.present_rect.empty()) {
      ss << ", present_rect: " << track_info_.present_rect[0] << " "
         << track_info_.present_rect[1] << " " << track_info_.present_rect[2]
         << " " << track_info_.present_rect[3];
    }
    RCLCPP_INFO(rclcpp::get_logger("TrackingManager"), "%s", ss.str().data());
  }

  if (TrackingStatus::TRACKING != track_info_.tracking_sta) {
    robot_cmdvel_node_->StopRotation();
    last_motion_gesture_ = 0;
    gesture_motion_ = 0;
    RCLCPP_DEBUG(rclcpp::get_logger("TrackingManager"), "track is lost");
    CancelMove();
    track_info_.tracking_sta = TrackingStatus::INITING;
    last_frame_done_ = true;
    return;
  }

  if (frame_ts != track_info_.frame_ts) {
    // 如果当前帧中没有被跟随的track信息，track info只更新lost
    // info，当前帧不做跟随
    RCLCPP_INFO(rclcpp::get_logger("TrackingManager"),
                "update smart fail! msg frame_ts %llu, track frame_ts %llu",
                frame_ts,
                track_info_.frame_ts);
    CancelMove();
    last_frame_done_ = true;

    return;
  }

  if (gesture_motion_ != 0) {
    Twist command;
    if (gesture_motion_ == 1) command.linear.x = track_cfg_.move_step;
    if (gesture_motion_ == 2) command.linear.x = -depth_backoff_.ReverseMaximum();
    last_cmdvel_is_cancel_ = false;
    last_cmdvel_type_ = 2;
    robot_cmdvel_node_->RobotCtl(command);
    last_frame_done_ = true;
    return;
  }

  // 2. cal the angle of robot and track
  UpdateTrackAngle();

  if (!last_cmdvel_is_cancel_) {
    RunOverMovingProtectionStrategy();
  }

  RunTrackLostProtectionStrategy();
  DoRotateMove();
  last_frame_done_ = true;
  return;
}

void TrackingManager::RunTrackingStrategy(
    const ai_msgs::msg::PerceptionTargets::ConstSharedPtr &msg) {
  std::unique_lock<std::mutex> lg(robot_strategy_mtx_);

  RCLCPP_INFO(rclcpp::get_logger("TrackingManager"), "Run TrackingStrategy");
  {
    static auto last_tracking_ts = TimeHelper::GetCurrentTimestampMillSec();
    auto present_tracking_ts = TimeHelper::GetCurrentTimestampMillSec();
    RCLCPP_INFO(rclcpp::get_logger("TrackingManager"),
                "Run TrackingStrategy time ms diff: %llu",
                present_tracking_ts - last_tracking_ts);
    last_tracking_ts = present_tracking_ts;
  }

  auto start_tracking_ts = TimeHelper::GetCurrentTimestampMillSec();

  // 只使用视觉感知结果实现跟随，不支持避障
  TrackingWithoutNavStrategy(msg);
  robot_cmdvel_node_->PublishTrackingState(track_info_, msg->header.stamp, depth_backoff_, centering_, GestureMotion());

  auto present_tracking_ts = TimeHelper::GetCurrentTimestampMillSec();
  RCLCPP_INFO(rclcpp::get_logger("TrackingManager"),
              "Run TrackingStrategy time ms cost: %llu",
              present_tracking_ts - start_tracking_ts);

  return;
}

void TrackingManager::FeedSmart(
    const ai_msgs::msg::PerceptionTargets::ConstSharedPtr &msg) {
  if (!rclcpp::ok()) return;
  std::unique_lock<std::mutex> lg(smart_queue_mtx_);
  smart_queue_.push(msg);
  if (smart_queue_.size() > queue_len_limit_) {
    RCLCPP_INFO(rclcpp::get_logger("TrackingManager"),
                "smart queue len exceed limit: %d",
                queue_len_limit_);
    smart_queue_.pop();
  }
  smart_queue_condition_.notify_one();
  lg.unlock();
}

std::vector<std::shared_ptr<rclcpp::Node>> TrackingManager::GetNodes() {
  std::vector<std::shared_ptr<rclcpp::Node>> node_ptrs;
  node_ptrs.push_back(param_node_);
  node_ptrs.push_back(robot_cmdvel_node_);
  return node_ptrs;
}

const TrackCfg &TrackingManager::GetTrackCfg() const { return track_cfg_; }
