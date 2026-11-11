#include <algorithm>
#include <array>
#include <cmath>
#include <functional>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/imu.hpp>

#include "omnifleet_localization/conversions.hpp"

namespace omnifleet_localization
{

class AiryImuAdapterNode : public rclcpp::Node
{
public:
  AiryImuAdapterNode()
  : Node("omnifleet_t2_airy_imu_adapter")
  {
    const auto input_topic = declare_parameter<std::string>(
      "input_topic", "/rslidar_imu_data");
    const auto output_topic = declare_parameter<std::string>(
      "output_topic", "/rslidar_imu_data_corrected");
    const auto legacy_output_topic = declare_parameter<std::string>("legacy_output_topic", "");
    output_frame_ = declare_parameter<std::string>("output_frame", "rslidar");
    linear_acceleration_scale_ =
      declare_parameter<double>("linear_acceleration_scale", 1.0);
    drop_non_increasing_timestamps_ =
      declare_parameter<bool>("drop_non_increasing_timestamps", false);
    if (!std::isfinite(linear_acceleration_scale_) || linear_acceleration_scale_ <= 0.0) {
      throw std::invalid_argument("linear_acceleration_scale must be finite and positive");
    }
    const auto angular_velocity_bias = declare_parameter<std::vector<double>>(
      "angular_velocity_bias", {0.0, 0.0, 0.0});
    if (angular_velocity_bias.size() != angular_velocity_bias_.size() ||
      !std::all_of(
        angular_velocity_bias.begin(), angular_velocity_bias.end(),
        [](double value) {return std::isfinite(value);}))
    {
      throw std::invalid_argument(
              "angular_velocity_bias must contain exactly three finite values");
    }
    std::copy(
      angular_velocity_bias.begin(), angular_velocity_bias.end(),
      angular_velocity_bias_.begin());
    const auto rotation = declare_parameter<std::vector<double>>(
      "rotation_xyzw",
      {-0.7068467736244202, 0.7073657512664795,
        -0.0005705897347070277, 0.000999057781882584});
    if (rotation.size() != rotation_xyzw_.size()) {
      throw std::invalid_argument("rotation_xyzw must contain exactly four values");
    }
    std::copy(rotation.begin(), rotation.end(), rotation_xyzw_.begin());
    rotate_vector_xyzw({0.0, 0.0, 1.0}, rotation_xyzw_);
    for (size_t axis = 0; axis < 3; ++axis) {
      std::array<double, 3> basis{};
      basis[axis] = 1.0;
      const auto column = rotate_vector_xyzw(basis, rotation_xyzw_);
      for (size_t row = 0; row < 3; ++row) rotation_matrix_[row * 3 + axis] = column[row];
    }


    const auto qos = rclcpp::SensorDataQoS();
    auto input_qos = rclcpp::SensorDataQoS();
    input_qos.keep_last(100);
    publisher_ = create_publisher<sensor_msgs::msg::Imu>(output_topic, qos);
    if (!legacy_output_topic.empty() && legacy_output_topic != output_topic) {
      legacy_publisher_ = create_publisher<sensor_msgs::msg::Imu>(legacy_output_topic, qos);
    }
    subscription_ = create_subscription<sensor_msgs::msg::Imu>(
      input_topic, input_qos,
      std::bind(&AiryImuAdapterNode::on_imu, this, std::placeholders::_1));
    RCLCPP_INFO(
      get_logger(),
      "Airy IMU axes: %s -> %s, output frame=%s, acceleration scale=%.6f, "
      "gyro bias=[%.6f, %.6f, %.6f], drop non-increasing timestamps=%s",
      input_topic.c_str(), output_topic.c_str(), output_frame_.c_str(),
      linear_acceleration_scale_, angular_velocity_bias_[0],
      angular_velocity_bias_[1], angular_velocity_bias_[2],
      drop_non_increasing_timestamps_ ? "true" : "false");
  }

private:
  void on_imu(const sensor_msgs::msg::Imu::SharedPtr input)
  {
    const auto stamp_ns = rclcpp::Time(input->header.stamp).nanoseconds();
    if (drop_non_increasing_timestamps_ && has_last_stamp_ && stamp_ns <= last_stamp_ns_) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000,
        "Dropping non-increasing IMU timestamp: current=%ld previous=%ld",
        stamp_ns, last_stamp_ns_);
      return;
    }
    has_last_stamp_ = true;
    last_stamp_ns_ = stamp_ns;

    auto output = *input;
    const auto acceleration = rotate_vector_xyzw(
      {input->linear_acceleration.x, input->linear_acceleration.y,
        input->linear_acceleration.z},
      rotation_xyzw_);
    const auto angular_velocity = rotate_vector_xyzw(
      {input->angular_velocity.x, input->angular_velocity.y,
        input->angular_velocity.z},
      rotation_xyzw_);
    output.header.frame_id = output_frame_;
    output.orientation.x = 0.0;
    output.orientation.y = 0.0;
    output.orientation.z = 0.0;
    output.orientation.w = 1.0;
    output.orientation_covariance.fill(0.0);
    output.orientation_covariance[0] = -1.0;
    output.linear_acceleration.x = acceleration[0] * linear_acceleration_scale_;
    output.linear_acceleration.y = acceleration[1] * linear_acceleration_scale_;
    output.linear_acceleration.z = acceleration[2] * linear_acceleration_scale_;
    output.angular_velocity.x = angular_velocity[0] - angular_velocity_bias_[0];
    output.angular_velocity.y = angular_velocity[1] - angular_velocity_bias_[1];
    output.angular_velocity.z = angular_velocity[2] - angular_velocity_bias_[2];

    // Rotate the driver's filter covariance into the same axes as the measurements.
    output.angular_velocity_covariance = rotate_covariance(input->angular_velocity_covariance, 1.0);
    output.linear_acceleration_covariance = rotate_covariance(
      input->linear_acceleration_covariance, linear_acceleration_scale_);
    publisher_->publish(output);
    if (legacy_publisher_) legacy_publisher_->publish(output);
  }


  std::array<double, 9> rotate_covariance(const std::array<double, 9> & covariance, double scale) const
  {
    // REP-145: -1 means the measurement is unavailable, not a covariance to rotate.
    if (covariance[0] == -1.0) {
      std::array<double, 9> unavailable{};
      unavailable[0] = -1.0;
      return unavailable;
    }
    std::array<double, 9> result{};
    for (size_t row = 0; row < 3; ++row)
      for (size_t col = 0; col < 3; ++col)
        for (size_t i = 0; i < 3; ++i)
          for (size_t j = 0; j < 3; ++j)
            result[row * 3 + col] += rotation_matrix_[row * 3 + i] * covariance[i * 3 + j] *
              rotation_matrix_[col * 3 + j] * scale * scale;
    return result;
  }

  std::array<double, 9> rotation_matrix_{};
  std::string output_frame_;
  double linear_acceleration_scale_{1.0};
  bool drop_non_increasing_timestamps_{false};
  bool has_last_stamp_{false};
  int64_t last_stamp_ns_{0};
  std::array<double, 4> rotation_xyzw_{};
  std::array<double, 3> angular_velocity_bias_{};
  rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr publisher_;
  rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr legacy_publisher_;
  rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr subscription_;
};

}  // namespace omnifleet_localization

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<omnifleet_localization::AiryImuAdapterNode>());
  rclcpp::shutdown();
  return 0;
}
