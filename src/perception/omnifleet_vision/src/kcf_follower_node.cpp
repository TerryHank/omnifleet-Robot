#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <functional>
#include <limits>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#if __has_include(<cv_bridge/cv_bridge.hpp>)
#include <cv_bridge/cv_bridge.hpp>
#else
#include <cv_bridge/cv_bridge.h>
#endif
#include <geometry_msgs/msg/twist.hpp>
#include <message_filters/subscriber.h>
#include <message_filters/sync_policies/approximate_time.h>
#include <message_filters/synchronizer.h>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/image_encodings.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <std_msgs/msg/header.hpp>

#include "kcftracker.h"

class KcfFollowerNode : public rclcpp::Node
{
public:
  using Image = sensor_msgs::msg::Image;
  using SyncPolicy = message_filters::sync_policies::ApproximateTime<Image, Image>;
  using SteadyClock = std::chrono::steady_clock;

  KcfFollowerNode()
  : Node("kcf_follower")
  {
    tracker_color_topic_ = declare_parameter<std::string>(
      "tracker_color_topic", "/camera/color/image_raw");
    aligned_color_topic_ = declare_parameter<std::string>(
      "aligned_color_topic", "/camera/color/image_raw");
    depth_topic_ = declare_parameter<std::string>(
      "depth_topic", "/camera/depth/image_raw");
    output_image_topic_ = declare_parameter<std::string>(
      "output_image_topic", "/omnifleet_vision/kcf/image");
    cmd_vel_topic_ = declare_parameter<std::string>(
      "cmd_vel_topic", "/cmd_vel_vision");

    enable_motion_ = declare_parameter<bool>("enable_motion", false);
    use_gui_ = declare_parameter<bool>("use_gui", true);
    tracking_scale_ = declare_parameter<double>("tracking_scale", 0.4);
    sync_queue_size_ = declare_parameter<int>("sync_queue_size", 10);
    max_pair_delta_ = declare_parameter<double>("max_pair_delta", 0.8);
    tracking_timeout_ = declare_parameter<double>("tracking_timeout", 0.5);
    depth_timeout_ = declare_parameter<double>("depth_timeout", 0.5);
    control_rate_ = declare_parameter<double>("control_rate", 10.0);

    roi_x_ = declare_parameter<int>("roi_x", 0);
    roi_y_ = declare_parameter<int>("roi_y", 0);
    roi_width_ = declare_parameter<int>("roi_width", 0);
    roi_height_ = declare_parameter<int>("roi_height", 0);

    target_distance_ = declare_parameter<double>("target_distance", 0.8);
    depth_scale_16u_ = declare_parameter<double>("depth_scale_16u", 0.001);
    depth_scale_32f_ = declare_parameter<double>("depth_scale_32f", 1.0);
    min_depth_ = declare_parameter<double>("min_depth", 0.2);
    max_depth_ = declare_parameter<double>("max_depth", 3.5);
    linear_kp_ = declare_parameter<double>("linear_kp", 0.6);
    angular_kp_ = declare_parameter<double>("angular_kp", 0.8);
    linear_deadband_ = declare_parameter<double>("linear_deadband", 0.15);
    angular_deadband_ = declare_parameter<double>("angular_deadband", 0.05);
    minimum_linear_speed_ = declare_parameter<double>("minimum_linear_speed", 0.40);
    max_linear_speed_ = declare_parameter<double>("max_linear_speed", 0.40);
    max_angular_speed_ = declare_parameter<double>("max_angular_speed", 0.30);

    const std::vector<double> finite_parameters = {
      max_pair_delta_, tracking_timeout_, depth_timeout_, control_rate_, target_distance_,
      depth_scale_16u_, depth_scale_32f_, min_depth_, max_depth_, linear_kp_, angular_kp_,
      linear_deadband_, angular_deadband_, minimum_linear_speed_, max_linear_speed_,
      max_angular_speed_, tracking_scale_};
    if (std::any_of(
        finite_parameters.begin(), finite_parameters.end(),
        [](double value) {return !std::isfinite(value);} ))
    {
      throw std::invalid_argument("all numeric control parameters must be finite");
    }
    if (sync_queue_size_ < 1) {
      throw std::invalid_argument("sync_queue_size must be positive");
    }
    if (max_pair_delta_ <= 0.0 || tracking_timeout_ <= 0.0 || depth_timeout_ <= 0.0 ||
      control_rate_ <= 0.0)
    {
      throw std::invalid_argument(
              "max_pair_delta, tracking_timeout, depth_timeout and control_rate must be positive");
    }
    if (tracking_scale_ <= 0.0 || tracking_scale_ > 1.0) {
      throw std::invalid_argument("tracking_scale must be in the interval (0, 1]");
    }
    if (minimum_linear_speed_ < 0.0 || max_linear_speed_ < minimum_linear_speed_) {
      throw std::invalid_argument(
              "max_linear_speed must be greater than or equal to minimum_linear_speed");
    }
    if (linear_kp_ < 0.0 || angular_kp_ < 0.0 || linear_deadband_ < 0.0 ||
      angular_deadband_ < 0.0 || max_angular_speed_ < 0.0)
    {
      throw std::invalid_argument("gains, deadbands and speed limits must not be negative");
    }
    if (depth_scale_16u_ <= 0.0 || depth_scale_32f_ <= 0.0 || min_depth_ < 0.0 ||
      max_depth_ <= min_depth_ || target_distance_ <= min_depth_ || target_distance_ >= max_depth_)
    {
      throw std::invalid_argument(
              "depth scales and min_depth < target_distance < max_depth must be valid");
    }
    if (cmd_vel_topic_ != "/cmd_vel_vision") {
      throw std::invalid_argument(
              "cmd_vel_topic must be exactly /cmd_vel_vision; direct or relative cmd_vel is forbidden");
    }

    debug_image_pub_ = create_publisher<Image>(
      output_image_topic_, rclcpp::SensorDataQoS());
    cmd_vel_pub_ = create_publisher<geometry_msgs::msg::Twist>(cmd_vel_topic_, 10);

    tracker_color_sub_ = create_subscription<Image>(
      tracker_color_topic_, rclcpp::SensorDataQoS(),
      std::bind(&KcfFollowerNode::tracker_color_callback, this, std::placeholders::_1));
    aligned_color_sub_.subscribe(this, aligned_color_topic_, rmw_qos_profile_sensor_data);
    depth_sub_.subscribe(this, depth_topic_, rmw_qos_profile_sensor_data);
    sync_ = std::make_shared<message_filters::Synchronizer<SyncPolicy>>(
      SyncPolicy(sync_queue_size_), aligned_color_sub_, depth_sub_);
    sync_->registerCallback(
      std::bind(
        &KcfFollowerNode::aligned_depth_callback, this,
        std::placeholders::_1, std::placeholders::_2));

    const auto control_period = std::chrono::duration_cast<std::chrono::nanoseconds>(
      std::chrono::duration<double>(1.0 / control_rate_));
    control_timer_ = create_wall_timer(
      control_period, std::bind(&KcfFollowerNode::control_timer_callback, this));

    tracker_ = make_tracker();
    RCLCPP_INFO(
      get_logger(),
      "KCF ready: tracker=%s aligned=%s depth=%s output=%s motion=%s cmd=%s scale=%.2f",
      tracker_color_topic_.c_str(), aligned_color_topic_.c_str(), depth_topic_.c_str(),
      output_image_topic_.c_str(), enable_motion_ ? "enabled" : "disabled",
      cmd_vel_topic_.c_str(), tracking_scale_);
    if (!enable_motion_) {
      RCLCPP_WARN(
        get_logger(),
        "Motion is disabled. Tracking and debug image output remain active.");
    }
  }

  ~KcfFollowerNode() override
  {
    publish_stop();
    if (use_gui_) {
      cv::destroyAllWindows();
    }
  }

private:
  struct RoiSelectorState
  {
    cv::Point origin;
    cv::Point current;
    cv::Rect result;
    bool dragging = false;
    bool finished = false;
    bool cancelled = false;
  };

  static void roi_mouse_callback(int event, int x, int y, int, void * user_data)
  {
    auto * state = static_cast<RoiSelectorState *>(user_data);
    if (event == cv::EVENT_LBUTTONDOWN) {
      state->origin = cv::Point(x, y);
      state->current = state->origin;
      state->dragging = true;
    } else if (event == cv::EVENT_MOUSEMOVE && state->dragging) {
      state->current = cv::Point(x, y);
    } else if (event == cv::EVENT_LBUTTONUP && state->dragging) {
      state->current = cv::Point(x, y);
      state->dragging = false;
      const int left = std::min(state->origin.x, state->current.x);
      const int top = std::min(state->origin.y, state->current.y);
      state->result = cv::Rect(
        left, top, std::abs(state->current.x - state->origin.x),
        std::abs(state->current.y - state->origin.y));
      // 学生松开鼠标后直接确认，避免焦点留在 SSH 终端时回车无效。
      state->finished = state->result.width > 5 && state->result.height > 5;
    }
  }

  cv::Rect select_roi(const cv::Mat & frame) const
  {
    RoiSelectorState state;
    // 固定按原图像素显示，保证鼠标坐标与相机帧坐标一一对应。
    cv::namedWindow(window_name_, cv::WINDOW_AUTOSIZE);
    cv::setMouseCallback(window_name_, roi_mouse_callback, &state);
    while (rclcpp::ok() && !state.finished && !state.cancelled) {
      cv::Mat canvas = frame.clone();
      cv::Rect preview = state.result;
      if (state.dragging) {
        const int left = std::min(state.origin.x, state.current.x);
        const int top = std::min(state.origin.y, state.current.y);
        preview = cv::Rect(
          left, top, std::abs(state.current.x - state.origin.x),
          std::abs(state.current.y - state.origin.y));
      }
      if (preview.width > 1 && preview.height > 1) {
        cv::rectangle(canvas, preview, cv::Scalar(0, 255, 255), 2);
      }
      cv::imshow(window_name_, canvas);
      const int key = cv::waitKey(20) & 0xff;
      if ((key == 13 || key == 32) && state.result.width > 1 && state.result.height > 1) {
        state.finished = true;
      } else if (key == 27 || key == 'q') {
        state.cancelled = true;
      }
    }
    cv::setMouseCallback(window_name_, nullptr, nullptr);
    return state.cancelled ? cv::Rect() : state.result;
  }

  static std::unique_ptr<KCFTracker> make_tracker()
  {
    return std::make_unique<KCFTracker>(true, false, true, false);
  }

  cv::Rect configured_roi(const cv::Mat & frame) const
  {
    cv::Rect roi(roi_x_, roi_y_, roi_width_, roi_height_);
    roi &= cv::Rect(0, 0, frame.cols, frame.rows);
    return roi;
  }

  bool initialize_tracker(const cv::Mat & frame)
  {
    cv::Rect roi = configured_roi(frame);
    if (roi.width <= 0 || roi.height <= 0) {
      if (!use_gui_) {
        RCLCPP_ERROR_THROTTLE(
          get_logger(), *get_clock(), 5000,
          "No valid initial ROI. Set roi_x/roi_y/roi_width/roi_height or enable GUI.");
        return false;
      }
      const char * display = std::getenv("DISPLAY");
      if (display == nullptr || display[0] == '\0') {
        RCLCPP_ERROR_THROTTLE(
          get_logger(), *get_clock(), 5000,
          "use_gui=true but DISPLAY is unavailable; pass an initial ROI for headless use.");
        return false;
      }
      RCLCPP_INFO(
        get_logger(),
        "Drag a target ROI in the OmniFleet KCF window; release mouse to confirm "
        "(ENTER/SPACE also accepted). Keyboard focus must be on the image window.");
      roi = select_roi(frame);
    }

    if (roi.width <= 1 || roi.height <= 1) {
      RCLCPP_WARN(get_logger(), "ROI selection was cancelled or too small.");
      return false;
    }
    tracker_ = make_tracker();
    tracker_->init(roi, frame);
    tracked_roi_ = roi;
    tracker_width_ = frame.cols;
    tracker_height_ = frame.rows;
    tracker_initialized_ = true;
    last_tracking_update_ = SteadyClock::now();
    invalidate_depth_candidate();
    RCLCPP_INFO(
      get_logger(), "KCF initialized at x=%d y=%d w=%d h=%d",
      roi.x, roi.y, roi.width, roi.height);
    return true;
  }

  static double median(std::vector<double> values)
  {
    if (values.empty()) {
      return std::numeric_limits<double>::quiet_NaN();
    }
    const auto middle = values.begin() + static_cast<long>(values.size() / 2);
    std::nth_element(values.begin(), middle, values.end());
    return *middle;
  }

  double depth_at_target(
    const cv::Mat & depth, const std::string & encoding,
    const cv::Rect & tracker_roi, int tracker_width, int tracker_height,
    int aligned_width, int aligned_height) const
  {
    if (depth.empty() || tracker_roi.width <= 0 || tracker_roi.height <= 0 ||
      tracker_width <= 0 || tracker_height <= 0 || aligned_width <= 0 || aligned_height <= 0)
    {
      return std::numeric_limits<double>::quiet_NaN();
    }

    const double normalized_x =
      (tracker_roi.x + tracker_roi.width * 0.5) / static_cast<double>(tracker_width);
    const double normalized_y =
      (tracker_roi.y + tracker_roi.height * 0.5) / static_cast<double>(tracker_height);
    const double aligned_x = normalized_x * aligned_width;
    const double aligned_y = normalized_y * aligned_height;
    const int depth_x = std::clamp(
      static_cast<int>(aligned_x * depth.cols / aligned_width), 0, depth.cols - 1);
    const int depth_y = std::clamp(
      static_cast<int>(aligned_y * depth.rows / aligned_height), 0, depth.rows - 1);

    std::vector<double> samples;
    for (int dy = -2; dy <= 2; ++dy) {
      for (int dx = -2; dx <= 2; ++dx) {
        const int x = std::clamp(depth_x + dx, 0, depth.cols - 1);
        const int y = std::clamp(depth_y + dy, 0, depth.rows - 1);
        double meters = std::numeric_limits<double>::quiet_NaN();
        if (encoding == sensor_msgs::image_encodings::TYPE_16UC1) {
          meters = static_cast<double>(depth.at<uint16_t>(y, x)) * depth_scale_16u_;
        } else if (encoding == sensor_msgs::image_encodings::TYPE_32FC1) {
          meters = static_cast<double>(depth.at<float>(y, x)) * depth_scale_32f_;
        }
        if (std::isfinite(meters) && meters >= min_depth_ && meters <= max_depth_) {
          samples.push_back(meters);
        }
      }
    }
    return median(std::move(samples));
  }

  void invalidate_depth_candidate()
  {
    depth_candidate_valid_ = false;
    last_depth_update_.reset();
  }

  void lose_target()
  {
    tracker_initialized_ = false;
    last_tracking_update_.reset();
    invalidate_depth_candidate();
    publish_stop();
  }

  void publish_stop()
  {
    if (enable_motion_ && cmd_vel_pub_) {
      cmd_vel_pub_->publish(geometry_msgs::msg::Twist());
    }
  }

  void publish_motion_candidate()
  {
    const double distance_error = depth_candidate_ - target_distance_;
    const double normalized_x_error =
      ((tracked_roi_.x + tracked_roi_.width * 0.5) - tracker_width_ * 0.5) /
      (tracker_width_ * 0.5);
    geometry_msgs::msg::Twist command;
    if (std::abs(distance_error) > linear_deadband_) {
      const double requested_linear = std::clamp(
        linear_kp_ * distance_error, -max_linear_speed_, max_linear_speed_);
      command.linear.x = std::abs(requested_linear) > 1.0e-9 &&
        std::abs(requested_linear) < minimum_linear_speed_ ?
        std::copysign(minimum_linear_speed_, requested_linear) : requested_linear;
    }
    if (std::abs(normalized_x_error) > angular_deadband_) {
      command.angular.z = std::clamp(
        -angular_kp_ * normalized_x_error,
        -max_angular_speed_, max_angular_speed_);
    }
    cmd_vel_pub_->publish(command);
  }

  void control_timer_callback()
  {
    if (!enable_motion_) {
      return;
    }
    const auto now = SteadyClock::now();
    const bool tracking_fresh = tracker_initialized_ && last_tracking_update_.has_value() &&
      std::chrono::duration<double>(now - *last_tracking_update_).count() <= tracking_timeout_;
    const bool depth_fresh = depth_candidate_valid_ && last_depth_update_.has_value() &&
      std::chrono::duration<double>(now - *last_depth_update_).count() <= depth_timeout_;
    if (!tracking_fresh || !depth_fresh) {
      publish_stop();
      return;
    }
    publish_motion_candidate();
  }

  void publish_debug_image(const cv::Mat & frame, const std_msgs::msg::Header & header)
  {
    auto message = cv_bridge::CvImage(
      header, sensor_msgs::image_encodings::BGR8, frame).toImageMsg();
    debug_image_pub_->publish(*message);
  }

  void render_and_publish_tracker_frame(
    cv::Mat & display, const std_msgs::msg::Header & header)
  {
    if (tracker_initialized_) {
      cv::rectangle(display, tracked_roi_, cv::Scalar(0, 255, 255), 2);
      cv::circle(
        display,
        cv::Point(
          tracked_roi_.x + tracked_roi_.width / 2,
          tracked_roi_.y + tracked_roi_.height / 2),
        3, cv::Scalar(0, 0, 255), -1);
    }

    const auto now = SteadyClock::now();
    const bool depth_fresh = depth_candidate_valid_ && last_depth_update_.has_value() &&
      std::chrono::duration<double>(now - *last_depth_update_).count() <= depth_timeout_;
    const std::string distance_text = depth_fresh ?
      cv::format("%.2f m", depth_candidate_) : "depth invalid/stale";
    const std::string tracker_text = std::string("KCF ") +
      (tracker_initialized_ ? "tracking" : "waiting") + " | " + distance_text +
      " | motion=" + (enable_motion_ ? "ON" : "OFF");
    const cv::Point text_origin = tracker_initialized_ ?
      cv::Point(tracked_roi_.x, std::max(20, tracked_roi_.y - 8)) : cv::Point(10, 25);
    cv::putText(
      display, tracker_text, text_origin,
      cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0, 255, 255), 2);

    publish_debug_image(display, header);
    if (use_gui_) {
      cv::imshow(window_name_, display);
      const int key = cv::waitKey(1) & 0xff;
      if (key == 'r') {
        lose_target();
      } else if (key == 'q') {
        publish_stop();
        rclcpp::shutdown();
      }
    }
  }

  void tracker_color_callback(const Image::ConstSharedPtr color_msg)
  {
    cv_bridge::CvImageConstPtr color_ptr;
    try {
      color_ptr = cv_bridge::toCvShare(color_msg, sensor_msgs::image_encodings::BGR8);
    } catch (const cv_bridge::Exception & error) {
      RCLCPP_ERROR_THROTTLE(
        get_logger(), *get_clock(), 5000, "tracker cv_bridge error: %s", error.what());
      lose_target();
      return;
    }

    cv::Mat display;
    if (tracking_scale_ < 0.999) {
      // KCF 在全分辨率 1536×1280 上只能达到个位数帧率；缩放后仍按归一化坐标映射深度。
      cv::resize(
        color_ptr->image, display, cv::Size(), tracking_scale_, tracking_scale_,
        cv::INTER_AREA);
    } else {
      display = color_ptr->image.clone();
    }
    if (!tracker_initialized_) {
      if (!initialize_tracker(display)) {
        publish_stop();
      }
      render_and_publish_tracker_frame(display, color_msg->header);
      return;
    }

    tracked_roi_ = tracker_->update(display);
    tracked_roi_ &= cv::Rect(0, 0, display.cols, display.rows);
    tracker_width_ = display.cols;
    tracker_height_ = display.rows;
    if (tracked_roi_.width <= 1 || tracked_roi_.height <= 1) {
      RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 2000, "KCF lost the target.");
      lose_target();
      render_and_publish_tracker_frame(display, color_msg->header);
      return;
    }
    last_tracking_update_ = SteadyClock::now();
    render_and_publish_tracker_frame(display, color_msg->header);
  }

  void aligned_depth_callback(
    const Image::ConstSharedPtr & aligned_color_msg,
    const Image::ConstSharedPtr & depth_msg)
  {
    const double pair_delta = std::fabs(
      (rclcpp::Time(aligned_color_msg->header.stamp) -
      rclcpp::Time(depth_msg->header.stamp)).seconds());
    if (pair_delta > max_pair_delta_) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 2000,
        "Rejected RGB-D pair with %.3f s timestamp delta (limit %.3f s).",
        pair_delta, max_pair_delta_);
      invalidate_depth_candidate();
      publish_stop();
      return;
    }
    if (!tracker_initialized_ || tracked_roi_.width <= 1 || tracked_roi_.height <= 1) {
      invalidate_depth_candidate();
      publish_stop();
      return;
    }

    cv_bridge::CvImageConstPtr depth_ptr;
    try {
      if (depth_msg->encoding == sensor_msgs::image_encodings::TYPE_16UC1) {
        depth_ptr = cv_bridge::toCvShare(
          depth_msg, sensor_msgs::image_encodings::TYPE_16UC1);
      } else if (depth_msg->encoding == sensor_msgs::image_encodings::TYPE_32FC1) {
        depth_ptr = cv_bridge::toCvShare(
          depth_msg, sensor_msgs::image_encodings::TYPE_32FC1);
      } else {
        RCLCPP_ERROR_THROTTLE(
          get_logger(), *get_clock(), 5000,
          "Unsupported depth encoding '%s'; expected 16UC1 or 32FC1.",
          depth_msg->encoding.c_str());
        invalidate_depth_candidate();
        publish_stop();
        return;
      }
    } catch (const cv_bridge::Exception & error) {
      RCLCPP_ERROR_THROTTLE(
        get_logger(), *get_clock(), 5000, "depth cv_bridge error: %s", error.what());
      invalidate_depth_candidate();
      publish_stop();
      return;
    }

    const double distance = depth_at_target(
      depth_ptr->image, depth_msg->encoding, tracked_roi_, tracker_width_, tracker_height_,
      static_cast<int>(aligned_color_msg->width), static_cast<int>(aligned_color_msg->height));
    if (!std::isfinite(distance)) {
      invalidate_depth_candidate();
      publish_stop();
      return;
    }

    depth_candidate_ = distance;
    depth_candidate_valid_ = true;
    last_depth_update_ = SteadyClock::now();
  }

  std::string tracker_color_topic_;
  std::string aligned_color_topic_;
  std::string depth_topic_;
  std::string output_image_topic_;
  std::string cmd_vel_topic_;
  bool enable_motion_;
  bool use_gui_;
  double tracking_scale_;
  int sync_queue_size_;
  double max_pair_delta_;
  double tracking_timeout_;
  double depth_timeout_;
  double control_rate_;
  int roi_x_;
  int roi_y_;
  int roi_width_;
  int roi_height_;
  double target_distance_;
  double depth_scale_16u_;
  double depth_scale_32f_;
  double min_depth_;
  double max_depth_;
  double linear_kp_;
  double angular_kp_;
  double linear_deadband_;
  double angular_deadband_;
  double minimum_linear_speed_;
  double max_linear_speed_;
  double max_angular_speed_;

  const std::string window_name_ = "OmniFleet KCF";
  bool tracker_initialized_ = false;
  int tracker_width_ = 0;
  int tracker_height_ = 0;
  cv::Rect tracked_roi_;
  std::unique_ptr<KCFTracker> tracker_;
  std::optional<SteadyClock::time_point> last_tracking_update_;
  bool depth_candidate_valid_ = false;
  double depth_candidate_ = std::numeric_limits<double>::quiet_NaN();
  std::optional<SteadyClock::time_point> last_depth_update_;

  rclcpp::Publisher<Image>::SharedPtr debug_image_pub_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;
  rclcpp::Subscription<Image>::SharedPtr tracker_color_sub_;
  message_filters::Subscriber<Image> aligned_color_sub_;
  message_filters::Subscriber<Image> depth_sub_;
  std::shared_ptr<message_filters::Synchronizer<SyncPolicy>> sync_;
  rclcpp::TimerBase::SharedPtr control_timer_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<KcfFollowerNode>());
  rclcpp::shutdown();
  return 0;
}
