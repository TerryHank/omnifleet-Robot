/**
* @file ranger_messenger.cpp
* @date 2021-04-20
* @brief
*
# @copyright Copyright (c) 2021 AgileX Robotics
* @copyright Copyright (c) 2023 Weston Robot Pte. Ltd.
*/

#include "ranger_base/ranger_messenger.hpp"

#include "ranger_base/kinematics_model.hpp"

#include <algorithm>
#include <stdexcept>

using namespace rclcpp;
using namespace ranger_msgs::msg;

namespace westonrobot {
// namespace {
// double DegreeToRadian(double x) { return x * M_PI / 180.0; }
// }  // namespace

///////////////////////////////////////////////////////////////////////////////////
RangerROSMessenger::RangerROSMessenger(rclcpp::Node::SharedPtr& node){

  node_ = node;
  LoadParameters();

  // connect to robot and setup ROS subscription
  if (robot_type_ == RangerSubType::kRangerMiniV1) {
    robot_ = std::make_shared<RangerRobot>(RangerRobot::Variant::kRangerMiniV1);
  } else if (robot_type_ == RangerSubType::kRangerMiniV2) {
    robot_ = std::make_shared<RangerRobot>(RangerRobot::Variant::kRangerMiniV2);
  } else if (robot_type_ == RangerSubType::kRangerMiniV3) {
    robot_ = std::make_shared<RangerRobot>(RangerRobot::Variant::kRangerMiniV3);
  } else {
    robot_ = std::make_shared<RangerRobot>(RangerRobot::Variant::kRanger);
  }

  if (port_name_.find("can") != std::string::npos) {
    if (!robot_->Connect(port_name_)) {
      throw std::runtime_error("Failed to connect to CAN port " + port_name_);
    }
    if (!receive_only_) {
      robot_->EnableCommandedMode();
    }
  } else {
    throw std::runtime_error("Invalid CAN port " + port_name_);
  }

  SetupSubscription();
}

void RangerROSMessenger::Run() {
  rclcpp::Rate rate(update_rate_);
  while (rclcpp::ok()) {
    PublishStateToROS();
    rclcpp::spin_some(node_);
    rate.sleep();
  }
}

void RangerROSMessenger::LoadParameters() {
  //load parameter from launch files
  port_name_ = node_->declare_parameter<std::string>("port_name","can0");
  robot_model_ = node_->declare_parameter<std::string>("robot_model","ranger");
  odom_frame_ =  node_->declare_parameter<std::string>("odom_frame","odom");
  base_frame_ = node_->declare_parameter<std::string>("base_frame", "base_link");
  update_rate_ = node_->declare_parameter<int>("update_rate", 50);
  odom_topic_name_ = node_->declare_parameter<std::string>("odom_topic_name", "odom");
  publish_odom_tf_ = node_->declare_parameter<bool>("publish_odom_tf",false);
  receive_only_ = node_->declare_parameter<bool>("receive_only", false);

  RCLCPP_INFO(node_->get_logger(),
      "Successfully loaded the following parameters: \n port_name: %s\n "
      "robot_model: %s\n odom_frame: %s\n base_frame: %s\n "
      "update_rate: %d\n odom_topic_name: %s\n "
      "publish_odom_tf: %d\n",
      port_name_.c_str(), robot_model_.c_str(), odom_frame_.c_str(),
      base_frame_.c_str(), update_rate_, odom_topic_name_.c_str(),
      publish_odom_tf_);

  // load robot parameters
  if (robot_model_ == "ranger_mini_v1") {
    robot_type_ = RangerSubType::kRangerMiniV1;

    robot_params_.track = RangerMiniV1Params::track;
    robot_params_.wheelbase = RangerMiniV1Params::wheelbase;
    robot_params_.max_linear_speed = RangerMiniV1Params::max_linear_speed;
    robot_params_.max_angular_speed = RangerMiniV1Params::max_angular_speed;
    robot_params_.max_speed_cmd = RangerMiniV1Params::max_speed_cmd;
    robot_params_.max_steer_angle_central =
        RangerMiniV1Params::max_steer_angle_central;
    robot_params_.max_steer_angle_parallel =
        RangerMiniV1Params::max_steer_angle_parallel;
    robot_params_.max_round_angle = RangerMiniV1Params::max_round_angle;
    robot_params_.min_turn_radius = RangerMiniV1Params::min_turn_radius;
      robot_params_.max_steer_angle_ackermann =
          RangerMiniV1Params::max_steer_angle_ackermann;
  } else {
    if (robot_model_ == "ranger_mini_v2") {
      robot_type_ = RangerSubType::kRangerMiniV2;

      robot_params_.track = RangerMiniV2Params::track;
      robot_params_.wheelbase = RangerMiniV2Params::wheelbase;
      robot_params_.max_linear_speed = RangerMiniV2Params::max_linear_speed;
      robot_params_.max_angular_speed = RangerMiniV2Params::max_angular_speed;
      robot_params_.max_speed_cmd = RangerMiniV2Params::max_speed_cmd;
      robot_params_.max_steer_angle_central =
          RangerMiniV2Params::max_steer_angle_central;
      robot_params_.max_steer_angle_parallel =
          RangerMiniV2Params::max_steer_angle_parallel;
      robot_params_.max_round_angle = RangerMiniV2Params::max_round_angle;
      robot_params_.min_turn_radius = RangerMiniV2Params::min_turn_radius;
      robot_params_.max_steer_angle_ackermann =
          RangerMiniV2Params::max_steer_angle_ackermann;
    }
    if (robot_model_ == "ranger_mini_v3") {
      robot_type_ = RangerSubType::kRangerMiniV3;

      robot_params_.track = RangerMiniV3Params::track;
      robot_params_.wheelbase = RangerMiniV3Params::wheelbase;
      robot_params_.max_linear_speed = RangerMiniV3Params::max_linear_speed;
      robot_params_.max_angular_speed = RangerMiniV3Params::max_angular_speed;
      robot_params_.max_speed_cmd = RangerMiniV3Params::max_speed_cmd;
      robot_params_.max_steer_angle_central =
          RangerMiniV3Params::max_steer_angle_central;
      robot_params_.max_steer_angle_parallel =
          RangerMiniV3Params::max_steer_angle_parallel;
      robot_params_.max_round_angle = RangerMiniV3Params::max_round_angle;
      robot_params_.min_turn_radius = RangerMiniV3Params::min_turn_radius;
      robot_params_.max_steer_angle_ackermann =
          RangerMiniV3Params::max_steer_angle_ackermann;
    }
     else {
      robot_type_ = RangerSubType::kRanger;

      robot_params_.track = RangerParams::track;
      robot_params_.wheelbase = RangerParams::wheelbase;
      robot_params_.max_linear_speed = RangerParams::max_linear_speed;
      robot_params_.max_angular_speed = RangerParams::max_angular_speed;
      robot_params_.max_speed_cmd = RangerParams::max_speed_cmd;
      robot_params_.max_steer_angle_central =
          RangerParams::max_steer_angle_central;
      robot_params_.max_steer_angle_parallel =
          RangerParams::max_steer_angle_parallel;
      robot_params_.max_round_angle = RangerParams::max_round_angle;
      robot_params_.min_turn_radius = RangerParams::min_turn_radius;
      robot_params_.max_steer_angle_ackermann =
          RangerParams::max_steer_angle_ackermann;
    }
  }
    parking_mode_ = false;

}

void RangerROSMessenger::SetupSubscription() {
  // publisher
  system_state_pub_ =
      node_->create_publisher<ranger_msgs::msg::SystemState>("/system_state", 10);
  motion_state_pub_ =
      node_->create_publisher<ranger_msgs::msg::MotionState>("/motion_state", 10);
  actuator_state_pub_ =
      node_->create_publisher<ranger_msgs::msg::ActuatorStateArray>("/actuator_state", 10);
  odom_pub_ = node_->create_publisher<nav_msgs::msg::Odometry>(odom_topic_name_, 10);
  battery_state_pub_ =
      node_->create_publisher<sensor_msgs::msg::BatteryState>("/battery_state", 10);

  // subscriber
  if (!receive_only_) {
    motion_cmd_sub_ = node_->create_subscription<geometry_msgs::msg::Twist>(
        "/cmd_vel", 5, std::bind(&RangerROSMessenger::TwistCmdCallback, this, std::placeholders::_1));
    if (robot_type_ == RangerSubType::kRangerMiniV3) {
      using Parking = std_srvs::srv::SetBool;
      parking_service_ = node_->create_service<Parking>(
          "ranger/parking", [this](const Parking::Request::SharedPtr request,
                                    Parking::Response::SharedPtr response) {
            parking_mode_ = request->data;
            robot_->SetMotionMode(parking_mode_ ? RangerInterface::kPark : RangerInterface::kDualAckerman);
            response->success = true;
            response->message = "Mode request sent. See motion_state for feedback.";
          });
    }
  }
  tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(node_);
}

void RangerROSMessenger::PublishStateToROS() {
  current_time_ = node_->get_clock()->now();

  static bool init_run = true;
  if (init_run) {
    last_time_ = current_time_;
    init_run = false;
    return;
  }

  auto state = robot_->GetRobotState();
  if (robot_type_ == RangerSubType::kRangerMiniV3 && state.time_stamp == SdkTimePoint{}) {
    last_time_ = current_time_;
    return;
  }
  motion_mode_ = state.motion_mode_state.motion_mode;
  auto actuator_state = robot_->GetActuatorState();

  // update odometry
  {
    double dt = (current_time_ - last_time_).seconds();
    UpdateOdometry(state.motion_state.linear_velocity,
                   state.motion_state.angular_velocity,
                   state.motion_state.steering_angle, dt);
    last_time_ = current_time_;
  }

  // publish system state
  {
    ranger_msgs::msg::SystemState system_msg;
    system_msg.header.stamp = current_time_;
    system_msg.vehicle_state = state.system_state.vehicle_state;
    system_msg.control_mode = state.system_state.control_mode;
    system_msg.error_code = state.system_state.error_code;
    system_msg.battery_voltage = state.system_state.battery_voltage;
    system_msg.motion_mode = state.motion_mode_state.motion_mode;

    system_state_pub_->publish(system_msg);
  }

  // publish motion mode
  {
    ranger_msgs::msg::MotionState motion_msg;
    motion_msg.header.stamp = current_time_;
    motion_msg.motion_mode = state.motion_mode_state.motion_mode;

    motion_state_pub_->publish(motion_msg);
  }

  // publish actuator state
  {
    // RCLCPP_DEBUG(node_->get_logger(),"feedback", "Angle_5:%f Angle_6:%f Angle_7:%f Angle_8:%f",
    //                 actuator_state.motor_angles.angle_5,
    //                 actuator_state.motor_angles.angle_6,
    //                 actuator_state.motor_angles.angle_7,
    //                 actuator_state.motor_angles.angle_8);
    // RCLCPP_DEBUG(node_->get_logger(),"feedback", "speed_1:%f speed_2:%f speed_3:%f speed_4:%f",
    //                 actuator_state.motor_speeds.speed_1,
    //                 actuator_state.motor_speeds.speed_2,
    //                 actuator_state.motor_speeds.speed_3,
    //                 actuator_state.motor_speeds.speed_4);

    const double angles[] = {actuator_state.motor_angles.angle_5, actuator_state.motor_angles.angle_6,
                             actuator_state.motor_angles.angle_7, actuator_state.motor_angles.angle_8};
    const double speeds[] = {actuator_state.motor_speeds.speed_1, actuator_state.motor_speeds.speed_2,
                             actuator_state.motor_speeds.speed_3, actuator_state.motor_speeds.speed_4};
    ranger_msgs::msg::ActuatorStateArray actuator_msg;
    actuator_msg.header.stamp = current_time_;
    for (int i = 0; i < 8; i++) {
      ranger_msgs::msg::DriverState driver_state_msg;
      const auto &driver = actuator_state.actuator_ls_state[i];
      driver_state_msg.driver_voltage = driver.driver_voltage;
      driver_state_msg.driver_temperature = driver.driver_temp;
      driver_state_msg.motor_temperature = driver.motor_temp;
      driver_state_msg.driver_state = driver.driver_state;

      const auto &motor = actuator_state.actuator_hs_state[i];
      ranger_msgs::msg::MotorState motor_state_msg;
      motor_state_msg.current = motor.current;
      motor_state_msg.pulse_count = motor.pulse_count;
      motor_state_msg.rpm = motor.rpm;
      motor_state_msg.motor_angles = i >= 4 ? angles[i - 4] : 0.0;
      motor_state_msg.motor_speeds = i < 4 ? speeds[i] : 0.0;
      
      ranger_msgs::msg::ActuatorState actuator_state_msg;
      actuator_state_msg.id = i;
      actuator_state_msg.driver = driver_state_msg;
      actuator_state_msg.motor = motor_state_msg;

      actuator_msg.states.push_back(actuator_state_msg);
    }

    actuator_state_pub_->publish(actuator_msg);
  }

  // publish BMS state
  {
    auto common_sensor_state = robot_->GetCommonSensorState();

    sensor_msgs::msg::BatteryState batt_msg;
    batt_msg.header.stamp = current_time_;
    batt_msg.voltage = common_sensor_state.bms_basic_state.voltage;
    batt_msg.temperature = common_sensor_state.bms_basic_state.temperature;
    batt_msg.current = common_sensor_state.bms_basic_state.current;
    batt_msg.percentage = common_sensor_state.bms_basic_state.battery_soc;
    batt_msg.charge = std::numeric_limits<float>::quiet_NaN();
    batt_msg.capacity = std::numeric_limits<float>::quiet_NaN();
    batt_msg.design_capacity = std::numeric_limits<float>::quiet_NaN();
    batt_msg.power_supply_status =
        sensor_msgs::msg::BatteryState::POWER_SUPPLY_STATUS_UNKNOWN;
    batt_msg.power_supply_health =
        sensor_msgs::msg::BatteryState::POWER_SUPPLY_HEALTH_UNKNOWN;
    batt_msg.power_supply_technology =
        sensor_msgs::msg::BatteryState::POWER_SUPPLY_TECHNOLOGY_LION;
    batt_msg.present = std::numeric_limits<uint8_t>::quiet_NaN();
    if (robot_type_ == RangerSubType::kRangerMiniV3) {
      // On 104, 0x361 uses a different scale than the generic parser assumes.
      batt_msg.voltage = state.system_state.battery_voltage;
      batt_msg.present = common_sensor_state.time_stamp != SdkTimePoint{};
      batt_msg.percentage = batt_msg.present ? batt_msg.percentage / 100.0f
                                            : std::numeric_limits<float>::quiet_NaN();
    }

    battery_state_pub_->publish(batt_msg);
  }
}

void RangerROSMessenger::UpdateOdometry(double linear, double angular,
                                        double angle, double dt) {
  const bool v3 = robot_type_ == RangerSubType::kRangerMiniV3;
  const bool side_slip = !v3 && motion_mode_ == MotionState::MOTION_MODE_SIDE_SLIP;
  const double central_angle = v3 ? ConvertV3AckermannFeedback(angle) : ConvertInnerAngleToCentral(angle);
  // update odometry calculations
  if (motion_mode_ == MotionState::MOTION_MODE_DUAL_ACKERMAN) {
    DualAckermanModel::state_type x = {position_x_, position_y_, theta_};
    DualAckermanModel::control_type u;
    u.v = linear;
    u.phi = central_angle;

    boost::numeric::odeint::integrate_const(
        boost::numeric::odeint::runge_kutta4<DualAckermanModel::state_type>(),
        DualAckermanModel(robot_params_.wheelbase, u), x, 0.0, dt, (dt / 10.0));
    //std::cout<<" steer: "<<angle<<" central: "<<u.phi<<std::endl;
    position_x_ = x[0];
    position_y_ = x[1];
    theta_ = x[2];
  } else if (motion_mode_ == MotionState::MOTION_MODE_PARALLEL || side_slip) {
    ParallelModel::state_type x = {position_x_, position_y_, theta_};
    ParallelModel::control_type u;
    u.v = linear;
    if (side_slip) {
      u.phi = M_PI / 2.0;
    } else {
      u.phi = angle;
    }
    boost::numeric::odeint::integrate_const(
        boost::numeric::odeint::runge_kutta4<ParallelModel::state_type>(),
        ParallelModel(u), x, 0.0, dt, (dt / 10.0));

    position_x_ = x[0];
    position_y_ = x[1];
    theta_ = x[2];
  } else if (motion_mode_ == MotionState::MOTION_MODE_SPINNING) {
    SpinningModel::state_type x = {position_x_, position_y_, theta_};
    SpinningModel::control_type u;
    u.w = angular;

    boost::numeric::odeint::integrate_const(
        boost::numeric::odeint::runge_kutta4<SpinningModel::state_type>(),
        SpinningModel(u), x, 0.0, dt, (dt / 10.0));

    position_x_ = x[0];
    position_y_ = x[1];
    theta_ = x[2];
  }

  // update odometry topics
  geometry_msgs::msg::Quaternion odom_quat = createQuaternionMsgFromYaw(theta_);

  // publish odometry and tf messages
  nav_msgs::msg::Odometry odom_msg;
  odom_msg.header.stamp = current_time_;
  odom_msg.header.frame_id = odom_frame_;
  odom_msg.child_frame_id = base_frame_;

  odom_msg.pose.pose.position.x = position_x_;
  odom_msg.pose.pose.position.y = position_y_;
  odom_msg.pose.pose.position.z = 0.0;
  odom_msg.pose.pose.orientation = odom_quat;

  if (motion_mode_ == MotionState::MOTION_MODE_DUAL_ACKERMAN) {
    odom_msg.twist.twist.linear.x = linear;
    odom_msg.twist.twist.linear.y = 0.0;
    odom_msg.twist.twist.angular.z =
        2 * linear * std::sin(central_angle) /
        robot_params_.wheelbase;
  } else if (motion_mode_ == MotionState::MOTION_MODE_PARALLEL || side_slip) {
    double phi = angle;

    if (side_slip) {
      phi = M_PI / 2.0;
    }
    odom_msg.twist.twist.linear.x = linear * std::cos(phi);
    odom_msg.twist.twist.linear.y = linear * std::sin(phi);

    odom_msg.twist.twist.angular.z = 0;
  } else if (motion_mode_ == MotionState::MOTION_MODE_SPINNING) {
    odom_msg.twist.twist.linear.x = 0;
    odom_msg.twist.twist.linear.y = 0;
    odom_msg.twist.twist.angular.z = angular;
  }

  odom_pub_->publish(odom_msg);

  // // publish tf transformation
  if (publish_odom_tf_) {
    geometry_msgs::msg::TransformStamped tf_msg;
    tf_msg.header.stamp = current_time_;
    tf_msg.header.frame_id = odom_frame_;
    tf_msg.child_frame_id = base_frame_;

    tf_msg.transform.translation.x = position_x_;
    tf_msg.transform.translation.y = position_y_;
    tf_msg.transform.translation.z = 0.0;
    tf_msg.transform.rotation = odom_quat;

    tf_broadcaster_->sendTransform(tf_msg);
  }
}

void RangerROSMessenger::SendV3Twist(const geometry_msgs::msg::Twist &msg) {
  const double x = msg.linear.x, y = msg.linear.y, yaw = msg.angular.z;
  const double wheel_angle = msg.angular.y;
  if (parking_mode_ || !std::isfinite(x) || !std::isfinite(y) || !std::isfinite(yaw) ||
      !std::isfinite(wheel_angle)) {
    return;
  }

  const bool stop = x == 0.0 && y == 0.0 && yaw == 0.0;
  if (stop && msg.angular.x != 1.0 && wheel_angle == 0.0) {
    // A stop must not select a new steering mode.
    robot_->SetMotionCommand(0.0, 0.0, 0.0);
    return;
  }

  const auto state = robot_->GetRobotState();
  uint8_t mode = RangerInterface::kDualAckerman;
  double speed = x, steer = 0.0, spin = 0.0;
  const bool fixed_lateral = x == 0.0 && y != 0.0 && wheel_angle != 0.0;
  if (stop) {
    if (state.motion_state.linear_velocity != 0.0 || state.motion_state.angular_velocity != 0.0) {
      const double held = state.motion_mode_state.motion_mode == RangerInterface::kParallel
                          ? state.motion_state.steering_angle : 0.0;
      robot_->SetMotionCommand(0.0, held, 0.0);
      return;
    }
    if (wheel_angle != 0.0) mode = RangerInterface::kParallel;
    steer = wheel_angle;
  } else if (fixed_lateral) {
    mode = RangerInterface::kParallel;
    steer = wheel_angle;
    speed = y * std::copysign(1.0, wheel_angle);
  } else if (y != 0.0) {
    mode = RangerInterface::kParallel;
    speed = std::copysign(std::hypot(x, y), x == 0.0 ? 1.0 : x);
    steer = std::atan2(std::copysign(1.0, speed) * y, std::abs(x));
  } else if (yaw != 0.0) {
    const double radius = std::abs(x / yaw);
    if (radius < robot_params_.min_turn_radius) {
      mode = RangerInterface::kSpinning;
      speed = 0.0;
      spin = std::max(-robot_params_.max_angular_speed, std::min(yaw, robot_params_.max_angular_speed));
    } else {
      steer = std::copysign(std::atan2(robot_params_.wheelbase / 2, radius - robot_params_.track / 2), x * yaw);
    }
  }
  const double steering_limit = mode == RangerInterface::kParallel ? robot_params_.max_steer_angle_parallel
                                                                   : robot_params_.max_steer_angle_ackermann;
  steer = std::max(-steering_limit, std::min(steer, steering_limit));
  const double speed_limit = std::abs(steer) > M_PI / 9 ? 0.7 : robot_params_.max_linear_speed;
  speed = std::max(-speed_limit, std::min(speed, speed_limit));

  if (state.system_state.control_mode == 0) {
    robot_->EnableCommandedMode();
  }
  if (state.motion_mode_state.mode_changing) {
    return;
  }
  if (state.motion_mode_state.motion_mode != mode) {
    robot_->SetMotionMode(mode);
    return;
  }
  if (fixed_lateral && std::abs(state.motion_state.steering_angle - steer) > 0.03) {
    speed = 0.0;
  }
  robot_->SetMotionCommand(speed, steer, spin);
}

void RangerROSMessenger::TwistCmdCallback(geometry_msgs::msg::Twist::SharedPtr msg) {
  if (robot_type_ == RangerSubType::kRangerMiniV3) {
    SendV3Twist(*msg);
    return;
  }
  double steer_cmd;
  double radius;

  // analyze Twist msg and switch motion_mode
  // check for parking mode, only applicable to RangerMiniV2
  if (parking_mode_ && robot_type_ == RangerSubType::kRangerMiniV2) {
    return;
  } else if (msg->linear.y != 0) {
    if (msg->linear.x == 0.0 && robot_type_ == RangerSubType::kRangerMiniV1) {
      motion_mode_ = MotionState::MOTION_MODE_SIDE_SLIP;
      robot_->SetMotionMode(MotionState::MOTION_MODE_SIDE_SLIP);
    } else {
      motion_mode_ = MotionState::MOTION_MODE_PARALLEL;
      robot_->SetMotionMode(MotionState::MOTION_MODE_PARALLEL);
    }
  } else {
    steer_cmd = CalculateSteeringAngle(*msg, radius);
    // Use minimum turn radius to switch between dual ackerman and spinning mode
    if (radius < robot_params_.min_turn_radius) {
      motion_mode_ = MotionState::MOTION_MODE_SPINNING;
      robot_->SetMotionMode(MotionState::MOTION_MODE_SPINNING);
    } else {
      motion_mode_ = MotionState::MOTION_MODE_DUAL_ACKERMAN;
      robot_->SetMotionMode(MotionState::MOTION_MODE_DUAL_ACKERMAN);
    }
  }
  // send motion command to robot
  switch (motion_mode_) {
    case MotionState::MOTION_MODE_DUAL_ACKERMAN: {
      if (steer_cmd > robot_params_.max_steer_angle_ackermann) {
        steer_cmd = robot_params_.max_steer_angle_ackermann;
      }
      if (steer_cmd < -robot_params_.max_steer_angle_ackermann) {
        steer_cmd = -robot_params_.max_steer_angle_ackermann;
      }
      robot_->SetMotionCommand(msg->linear.x, steer_cmd);
      break;
    }
    case MotionState::MOTION_MODE_PARALLEL: {
      steer_cmd = atan(msg->linear.y / msg->linear.x);

      static double last_nonzero_x = 1.0; 
      
      if (msg->linear.x != 0.0) {
          last_nonzero_x = msg->linear.x; 
      }

      if (std::signbit(msg->linear.x))
      {
        steer_cmd = -steer_cmd;
      }
      
      if (steer_cmd > robot_params_.max_steer_angle_parallel) {
        steer_cmd = robot_params_.max_steer_angle_parallel;
      }
      if (steer_cmd < -robot_params_.max_steer_angle_parallel) {
        steer_cmd = -robot_params_.max_steer_angle_parallel;
      }
      double vel = 1.0;
      
      if (msg->linear.x == 0.0 && msg->linear.y != 0.0) {
          // std::cout << "MOTION_MODE_SIDE_SLIP" << std::endl;
          
          if (std::signbit(last_nonzero_x)) {
              steer_cmd = -std::abs(steer_cmd); 
          } else {
              steer_cmd = std::abs(steer_cmd);
          }
          vel = msg->linear.y >= 0 ? 1.0 : -1.0;
      } else {
          vel = msg->linear.x >= 0 ? 1.0 : -1.0;
      }
      robot_->SetMotionCommand(vel * sqrt(msg->linear.x * msg->linear.x +
                                          msg->linear.y * msg->linear.y),
                               steer_cmd);
      break;
    }
    case MotionState::MOTION_MODE_SPINNING: {
      double a_v = msg->angular.z;
      if (a_v > robot_params_.max_angular_speed) {
        a_v = robot_params_.max_angular_speed;
      }
      if (a_v < -robot_params_.max_angular_speed) {
        a_v = -robot_params_.max_angular_speed;
      }
      robot_->SetMotionCommand(0.0, 0.0, a_v);
      break;
    }
    case MotionState::MOTION_MODE_SIDE_SLIP: {
      double l_v = msg->linear.y;
      if (l_v > robot_params_.max_linear_speed) {
        l_v = robot_params_.max_linear_speed;
      }
      if (l_v < -robot_params_.max_linear_speed) {
        l_v = -robot_params_.max_linear_speed;
      }
      robot_->SetMotionCommand(0.0, 0.0, l_v);
      break;
    }
  }
}


geometry_msgs::msg::Quaternion RangerROSMessenger::createQuaternionMsgFromYaw(double yaw) {
    tf2::Quaternion q;
    q.setRPY(0, 0, yaw);
    return tf2::toMsg(q);
}

double RangerROSMessenger::CalculateSteeringAngle(geometry_msgs::msg::Twist msg,
                                                  double& radius) {
  double linear = std::abs(msg.linear.x);
  double angular = std::abs(msg.angular.z);

  if (angular < 1e-6) {
    radius = std::numeric_limits<double>::infinity(); 
    return 0.0; 
  }
  // Circular motion
  radius = linear / angular;
  int k = (msg.angular.z * msg.linear.x) >= 0 ? 1 : -1;

  double l, w, phi_i, x;
  l = robot_params_.wheelbase;
  w = robot_params_.track;
  x = sqrt(radius * radius + (l / 2) * (l / 2));
  // phi_i = atan((l / 2) / (x - w / 2));
  phi_i = atan((l / 2) / radius);

  const double max_phi_rad = 40.0 * M_PI / 180.0;
  phi_i = std::min(phi_i, max_phi_rad);

  return k * phi_i;
}

double RangerROSMessenger::ConvertV3AckermannFeedback(double angle) {
  if (angle == 0.0) {
    return 0.0;
  }
  // 0x221 reports the mean of the inner and outer angles, right-positive.
  const double sine = std::sin(2 * std::abs(angle));
  const double half_wheelbase = robot_params_.wheelbase / 2;
  const double radius = (half_wheelbase * std::cos(2 * angle) +
                         std::hypot(half_wheelbase, robot_params_.track / 2 * sine)) / sine;
  return std::copysign(std::atan2(half_wheelbase, radius), -angle);
}

double RangerROSMessenger::ConvertInnerAngleToCentral(double angle) {
  double phi = 0;
  double phi_i = std::abs(angle);

  phi = std::atan(robot_params_.wheelbase * std::sin(phi_i) /
                  (robot_params_.wheelbase * std::cos(phi_i) +
                   robot_params_.track * std::sin(phi_i)));

  phi *= angle >= 0 ? 1.0 : -1.0;
  return phi;
}

double RangerROSMessenger::ConvertCentralAngleToInner(double angle) {
  double phi = std::abs(angle);
  double phi_i = 0;

  phi_i = std::atan(robot_params_.wheelbase * std::sin(phi) /
                    (robot_params_.wheelbase * std::cos(phi) -
                     robot_params_.track * std::sin(phi)));
  phi_i *= angle >= 0 ? 1.0 : -1.0;
  return phi_i;
}
}  // namespace westonrobot
