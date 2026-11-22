#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstddef>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <iomanip>
#include <memory>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

#include <ament_index_cpp/get_package_prefix.hpp>
#include <image_transport/image_transport.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/image_encodings.hpp>
#include <sensor_msgs/msg/camera_info.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sensor_msgs/point_cloud2_iterator.hpp>
#include <std_msgs/msg/header.hpp>

#include "MvCameraControl.h"
#include "mvs_camera_driver/rgbd_decoder.hpp"
#ifdef MVS_HAS_JETSON_ACCELERATION
#include "mvs_camera_driver/rgbd_acceleration.hpp"
#endif

namespace
{
// MV-DT01SNU is a native USB3 Vision device. Enumerating every GenTL producer
// makes the aarch64 MVS runtime load unrelated CXP/XoF plugins concurrently;
// MVS 5.0.1 can crash inside those plugins before USB enumeration completes.
constexpr unsigned int kSupportedTransports = MV_USB_DEVICE;

std::string error_code(int code)
{
  std::ostringstream stream;
  stream << "0x" << std::hex << std::uppercase << code;
  return stream.str();
}

uint32_t frame_width(const MV_FRAME_OUT_INFO_EX & info)
{
  return info.nExtendWidth > 0 ? info.nExtendWidth : info.nWidth;
}

uint32_t frame_height(const MV_FRAME_OUT_INFO_EX & info)
{
  return info.nExtendHeight > 0 ? info.nExtendHeight : info.nHeight;
}

uint64_t frame_length(const MV_FRAME_OUT_INFO_EX & info)
{
  return info.nFrameLenEx > 0 ? info.nFrameLenEx : info.nFrameLen;
}

std::string gig_e_serial(const MV_CC_DEVICE_INFO * info)
{
  return reinterpret_cast<const char *>(info->SpecialInfo.stGigEInfo.chSerialNumber);
}

std::string gig_e_user_name(const MV_CC_DEVICE_INFO * info)
{
  return reinterpret_cast<const char *>(info->SpecialInfo.stGigEInfo.chUserDefinedName);
}

std::string usb_serial(const MV_CC_DEVICE_INFO * info)
{
  return reinterpret_cast<const char *>(info->SpecialInfo.stUsb3VInfo.chSerialNumber);
}

std::string usb_user_name(const MV_CC_DEVICE_INFO * info)
{
  return reinterpret_cast<const char *>(info->SpecialInfo.stUsb3VInfo.chUserDefinedName);
}

std::string device_serial(const MV_CC_DEVICE_INFO * info)
{
  if (info == nullptr) {
    return {};
  }

  switch (info->nTLayerType) {
    case MV_GIGE_DEVICE:
    case MV_GENTL_GIGE_DEVICE:
      return gig_e_serial(info);
    case MV_USB_DEVICE:
      return usb_serial(info);
    case MV_GENTL_CAMERALINK_DEVICE:
      return reinterpret_cast<const char *>(info->SpecialInfo.stCMLInfo.chSerialNumber);
    case MV_GENTL_CXP_DEVICE:
      return reinterpret_cast<const char *>(info->SpecialInfo.stCXPInfo.chSerialNumber);
    case MV_GENTL_XOF_DEVICE:
      return reinterpret_cast<const char *>(info->SpecialInfo.stXoFInfo.chSerialNumber);
    default:
      return {};
  }
}

std::string device_user_name(const MV_CC_DEVICE_INFO * info)
{
  if (info == nullptr) {
    return {};
  }

  switch (info->nTLayerType) {
    case MV_GIGE_DEVICE:
    case MV_GENTL_GIGE_DEVICE:
      return gig_e_user_name(info);
    case MV_USB_DEVICE:
      return usb_user_name(info);
    case MV_GENTL_CAMERALINK_DEVICE:
      return reinterpret_cast<const char *>(info->SpecialInfo.stCMLInfo.chUserDefinedName);
    case MV_GENTL_CXP_DEVICE:
      return reinterpret_cast<const char *>(info->SpecialInfo.stCXPInfo.chUserDefinedName);
    case MV_GENTL_XOF_DEVICE:
      return reinterpret_cast<const char *>(info->SpecialInfo.stXoFInfo.chUserDefinedName);
    default:
      return {};
  }
}

std::string device_model(const MV_CC_DEVICE_INFO * info)
{
  if (info == nullptr) {
    return {};
  }

  switch (info->nTLayerType) {
    case MV_GIGE_DEVICE:
    case MV_GENTL_GIGE_DEVICE:
      return reinterpret_cast<const char *>(info->SpecialInfo.stGigEInfo.chModelName);
    case MV_USB_DEVICE:
      return reinterpret_cast<const char *>(info->SpecialInfo.stUsb3VInfo.chModelName);
    case MV_GENTL_CAMERALINK_DEVICE:
      return reinterpret_cast<const char *>(info->SpecialInfo.stCMLInfo.chModelName);
    case MV_GENTL_CXP_DEVICE:
      return reinterpret_cast<const char *>(info->SpecialInfo.stCXPInfo.chModelName);
    case MV_GENTL_XOF_DEVICE:
      return reinterpret_cast<const char *>(info->SpecialInfo.stXoFInfo.chModelName);
    default:
      return {};
  }
}

bool is_gige_transport(const MV_CC_DEVICE_INFO * info)
{
  return info != nullptr &&
         (info->nTLayerType == MV_GIGE_DEVICE || info->nTLayerType == MV_GENTL_GIGE_DEVICE);
}
}  // namespace

class MvsCameraNode final : public rclcpp::Node
{
public:
  MvsCameraNode()
  : Node("mvs_camera_node")
  {
    declare_and_read_parameters();
    configure_runtime_environment();

#ifdef MVS_HAS_JETSON_ACCELERATION
    RCLCPP_INFO(
      get_logger(), "Jetson acceleration: CUDA RGB-D projection=%s, VPI/VIC resize=%s",
      jetson_cuda_pointcloud_ ?
      (mvs_camera_driver::cuda_rgbd_available() ? "ready" : "unavailable") : "disabled",
      jetson_vpi_resize_ ?
      (mvs_camera_driver::vpi_vic_available() ? "ready" : "unavailable") : "disabled");
#endif
    RCLCPP_INFO(
      get_logger(),
      "Point-cloud spatial confidence filter=%s, min_neighbors=%d/8, tolerance=max(%.3fm, %.1f%% range)",
      pointcloud_spatial_filter_ ? "enabled" : "disabled",
      pointcloud_filter_min_neighbors_, pointcloud_filter_depth_tolerance_,
      pointcloud_filter_depth_tolerance_ratio_ * 100.0);

    if (rgbd_enabled_) {
      color_image_pub_ = image_transport::create_publisher(this, color_image_topic_);
      rgbd_color_image_pub_ = image_transport::create_publisher(this, rgbd_color_image_topic_);
      depth_image_pub_ = image_transport::create_publisher(this, depth_image_topic_);
      color_camera_info_pub_ = create_publisher<sensor_msgs::msg::CameraInfo>(
        color_camera_info_topic_, rclcpp::SensorDataQoS());
      rgbd_color_camera_info_pub_ = create_publisher<sensor_msgs::msg::CameraInfo>(
        rgbd_color_camera_info_topic_, rclcpp::SensorDataQoS());
      depth_camera_info_pub_ = create_publisher<sensor_msgs::msg::CameraInfo>(
        depth_camera_info_topic_, rclcpp::SensorDataQoS());
      pointcloud_pub_ = create_publisher<sensor_msgs::msg::PointCloud2>(
        pointcloud_topic_, rclcpp::SensorDataQoS());
      colorized_pointcloud_pub_ = create_publisher<sensor_msgs::msg::PointCloud2>(
        colorized_pointcloud_topic_, rclcpp::SensorDataQoS());
    } else {
      image_pub_ = image_transport::create_publisher(this, image_topic_);
      camera_info_pub_ = create_publisher<sensor_msgs::msg::CameraInfo>(
        camera_info_topic_, rclcpp::SensorDataQoS());
    }

    try {
      initialize_sdk();
      open_camera();
      apply_camera_settings();
      start_streaming();
    } catch (...) {
      cleanup();
      throw;
    }
  }

  ~MvsCameraNode() override
  {
    cleanup();
  }

private:
  void declare_and_read_parameters()
  {
    camera_index_ = declare_parameter<int>("camera_index", 0);
    serial_number_ = declare_parameter<std::string>("serial_number", "");
    user_defined_name_ = declare_parameter<std::string>("user_defined_name", "");
    frame_id_ = declare_parameter<std::string>("frame_id", "mvs_camera");
    image_topic_ = declare_parameter<std::string>("image_topic", "image_raw");
    camera_info_topic_ = declare_parameter<std::string>("camera_info_topic", "camera_info");
    runtime_sdk_dir_ = declare_parameter<std::string>("runtime_sdk_dir", "");
    pixel_format_ = declare_parameter<std::string>("pixel_format", "");
    exposure_time_ = declare_parameter<double>("exposure_time", -1.0);
    gain_ = declare_parameter<double>("gain", -1.0);
    auto_packet_size_ = declare_parameter<bool>("auto_packet_size", true);
    trigger_mode_ = declare_parameter<bool>("trigger_mode", false);
    trigger_source_ = declare_parameter<std::string>("trigger_source", "");
    grab_timeout_ms_ = declare_parameter<int>("grab_timeout_ms", 1000);

    rgbd_enabled_ = declare_parameter<bool>("rgbd_enabled", false);
    camera_working_mode_ = declare_parameter<std::string>("camera_working_mode", "DepthMode");
    image_mode_ = declare_parameter<std::string>("image_mode", "RGBD");
    rgbd_capture_strategy_ = declare_parameter<std::string>(
      "rgbd_capture_strategy", "subimages");
    color_frames_per_cycle_ = declare_parameter<int>("color_frames_per_cycle", 1);
    depth_frames_per_cycle_ = declare_parameter<int>("depth_frames_per_cycle", 1);
    color_image_mode_ = declare_parameter<std::string>("color_image_mode", "Color");
    depth_image_mode_ = declare_parameter<std::string>("depth_image_mode", "Depth");
    color_exposure_mode_ = declare_parameter<std::string>("color_exposure_mode", "");
    rgbd_align_coord_ = declare_parameter<std::string>(
      "rgbd_align_coord", "TransformDepthToRGBCoordinate");
    acquisition_mode_ = declare_parameter<std::string>("acquisition_mode", "Continuous");
    color_frame_id_ = declare_parameter<std::string>(
      "color_frame_id", "camera_color_optical_frame");
    depth_frame_id_ = declare_parameter<std::string>(
      "depth_frame_id", "camera_color_optical_frame");
    color_image_topic_ = declare_parameter<std::string>(
      "color_image_topic", "/tof/color/image_raw");
    color_camera_info_topic_ = declare_parameter<std::string>(
      "color_camera_info_topic", "/tof/color/camera_info");
    rgbd_color_image_topic_ = declare_parameter<std::string>(
      "rgbd_color_image_topic", "/tof/rgbd/color/image_raw");
    rgbd_color_camera_info_topic_ = declare_parameter<std::string>(
      "rgbd_color_camera_info_topic", "/tof/rgbd/color/camera_info");
    depth_image_topic_ = declare_parameter<std::string>(
      "depth_image_topic", "/tof/aligned_depth_to_color/image_raw");
    depth_camera_info_topic_ = declare_parameter<std::string>(
      "depth_camera_info_topic", "/tof/aligned_depth_to_color/camera_info");
    pointcloud_topic_ = declare_parameter<std::string>("pointcloud_topic", "/tof/points");
    colorized_pointcloud_topic_ = declare_parameter<std::string>(
      "colorized_pointcloud_topic", "/tof/points_colorized");
    rgbd_max_pair_delta_ms_ = declare_parameter<int>("rgbd_max_pair_delta_ms", 750);
    publish_pointcloud_ = declare_parameter<bool>("publish_pointcloud", true);
    pointcloud_decimation_ = declare_parameter<int>("pointcloud_decimation", 2);
    depth_scale_ = declare_parameter<double>("depth_scale", 0.001);
    depth_min_ = declare_parameter<double>("depth_min", 0.2);
    depth_max_ = declare_parameter<double>("depth_max", 3.5);
    pointcloud_spatial_filter_ = declare_parameter<bool>("pointcloud_spatial_filter", true);
    pointcloud_filter_min_neighbors_ = declare_parameter<int>(
      "pointcloud_filter_min_neighbors", 6);
    pointcloud_filter_depth_tolerance_ = declare_parameter<double>(
      "pointcloud_filter_depth_tolerance", 0.04);
    pointcloud_filter_depth_tolerance_ratio_ = declare_parameter<double>(
      "pointcloud_filter_depth_tolerance_ratio", 0.02);
#ifdef MVS_HAS_JETSON_ACCELERATION
    jetson_cuda_pointcloud_ = declare_parameter<bool>("jetson_cuda_pointcloud", true);
    jetson_vpi_resize_ = declare_parameter<bool>("jetson_vpi_resize", true);
#endif
    nominal_intrinsics_.fx = declare_parameter<double>("camera_fx", 1019.1704230044749);
    nominal_intrinsics_.fy = declare_parameter<double>("camera_fy", 1044.3850797624254);
    nominal_intrinsics_.cx = declare_parameter<double>("camera_cx", 767.5);
    nominal_intrinsics_.cy = declare_parameter<double>("camera_cy", 639.5);
    nominal_intrinsics_.width = static_cast<uint32_t>(
      declare_parameter<int>("camera_nominal_width", 1536));
    nominal_intrinsics_.height = static_cast<uint32_t>(
      declare_parameter<int>("camera_nominal_height", 1280));

    if (grab_timeout_ms_ <= 0) {
      throw std::runtime_error("grab_timeout_ms must be greater than zero");
    }
    if (pointcloud_decimation_ <= 0) {
      throw std::runtime_error("pointcloud_decimation must be greater than zero");
    }
    if (rgbd_max_pair_delta_ms_ <= 0) {
      throw std::runtime_error("rgbd_max_pair_delta_ms must be greater than zero");
    }
    if (pointcloud_filter_min_neighbors_ < 0 || pointcloud_filter_min_neighbors_ > 8 ||
      pointcloud_filter_depth_tolerance_ < 0.0 ||
      pointcloud_filter_depth_tolerance_ratio_ < 0.0)
    {
      throw std::runtime_error("invalid pointcloud spatial confidence filter parameters");
    }
    if (rgbd_enabled_ &&
        (depth_scale_ <= 0.0 || depth_min_ < 0.0 || depth_max_ <= depth_min_ ||
        nominal_intrinsics_.fx <= 0.0 || nominal_intrinsics_.fy <= 0.0 ||
        nominal_intrinsics_.width == 0U || nominal_intrinsics_.height == 0U)) {
      throw std::runtime_error("invalid RGB-D depth or camera calibration parameters");
    }
    if (rgbd_enabled_ && rgbd_capture_strategy_ != "subimages" &&
      rgbd_capture_strategy_ != "alternating" &&
      rgbd_capture_strategy_ != "batched" &&
      rgbd_capture_strategy_ != "color_only")
    {
      throw std::runtime_error(
              "rgbd_capture_strategy must be subimages, alternating, batched, or color_only");
    }
    if (rgbd_enabled_ && rgbd_capture_strategy_ == "batched" &&
      (color_frames_per_cycle_ <= 0 || depth_frames_per_cycle_ <= 0))
    {
      throw std::runtime_error("batched RGB-D frame counts must be greater than zero");
    }
  }

  void configure_runtime_environment()
  {
    std::string runtime_dir = runtime_sdk_dir_;
    if (runtime_dir.empty()) {
      try {
        const auto prefix = ament_index_cpp::get_package_prefix(MVS_CAMERA_DRIVER_PACKAGE_NAME);
        const std::filesystem::path candidate =
          std::filesystem::path(prefix) / "share" / MVS_CAMERA_DRIVER_PACKAGE_NAME / "mvs";
        if (std::filesystem::exists(candidate)) {
          runtime_dir = candidate.string();
        }
      } catch (const std::exception & ex) {
        RCLCPP_DEBUG(get_logger(), "Could not resolve package prefix: %s", ex.what());
      }
    }

    if (!runtime_dir.empty()) {
      setenv("MVCAM_COMMON_RUNENV", runtime_dir.c_str(), 0);
      RCLCPP_INFO(get_logger(), "Using MVS runtime directory: %s", runtime_dir.c_str());
    }
  }

  void initialize_sdk()
  {
    const int ret = MV_CC_Initialize();
    if (ret != MV_OK) {
      throw std::runtime_error("MV_CC_Initialize failed: " + error_code(ret));
    }
    sdk_initialized_ = true;
  }

  void open_camera()
  {
    MV_CC_DEVICE_INFO_LIST device_list;
    std::memset(&device_list, 0, sizeof(device_list));

    int ret = MV_CC_EnumDevices(kSupportedTransports, &device_list);
    if (ret != MV_OK) {
      throw std::runtime_error("MV_CC_EnumDevices failed: " + error_code(ret));
    }
    if (device_list.nDeviceNum == 0) {
      throw std::runtime_error("No MVS cameras found");
    }

    const unsigned int selected_index = select_device(device_list);
    MV_CC_DEVICE_INFO * selected_device = device_list.pDeviceInfo[selected_index];
    if (selected_device == nullptr) {
      throw std::runtime_error("Selected MVS device entry is null");
    }
    selected_is_gige_ = is_gige_transport(selected_device);

    RCLCPP_INFO(
      get_logger(), "Opening MVS camera index=%u model='%s' serial='%s' user='%s'",
      selected_index,
      device_model(selected_device).c_str(),
      device_serial(selected_device).c_str(),
      device_user_name(selected_device).c_str());

    ret = MV_CC_CreateHandle(&handle_, selected_device);
    if (ret != MV_OK) {
      throw std::runtime_error("MV_CC_CreateHandle failed: " + error_code(ret));
    }

    ret = MV_CC_OpenDevice(handle_);
    if (ret != MV_OK) {
      throw std::runtime_error("MV_CC_OpenDevice failed: " + error_code(ret));
    }
    device_open_ = true;
  }

  unsigned int select_device(const MV_CC_DEVICE_INFO_LIST & device_list) const
  {
    if (!serial_number_.empty()) {
      for (unsigned int i = 0; i < device_list.nDeviceNum; ++i) {
        if (device_serial(device_list.pDeviceInfo[i]) == serial_number_) {
          return i;
        }
      }
      throw std::runtime_error("No MVS camera matched serial_number=" + serial_number_);
    }

    if (!user_defined_name_.empty()) {
      for (unsigned int i = 0; i < device_list.nDeviceNum; ++i) {
        if (device_user_name(device_list.pDeviceInfo[i]) == user_defined_name_) {
          return i;
        }
      }
      throw std::runtime_error("No MVS camera matched user_defined_name=" + user_defined_name_);
    }

    if (camera_index_ < 0 ||
        static_cast<unsigned int>(camera_index_) >= device_list.nDeviceNum) {
      std::ostringstream stream;
      stream << "camera_index " << camera_index_ << " is out of range; found "
             << device_list.nDeviceNum << " device(s)";
      throw std::runtime_error(stream.str());
    }

    return static_cast<unsigned int>(camera_index_);
  }

  void apply_camera_settings()
  {
    if (selected_is_gige_ && auto_packet_size_) {
      const int packet_size = MV_CC_GetOptimalPacketSize(handle_);
      if (packet_size > 0) {
        const int ret = MV_CC_SetIntValueEx(handle_, "GevSCPSPacketSize", packet_size);
        if (ret != MV_OK) {
          RCLCPP_WARN(get_logger(), "Failed to set GevSCPSPacketSize: %s", error_code(ret).c_str());
        }
      } else {
        RCLCPP_WARN(get_logger(), "MV_CC_GetOptimalPacketSize failed: %s", error_code(packet_size).c_str());
      }
    }

    if (rgbd_enabled_) {
      log_enum_entries("CameraWorkingMode");
      log_enum_entries("ImageMode");
      log_enum_entries("RGBDAlignCoord");
      set_enum_by_string("CameraWorkingMode", camera_working_mode_, true);
      if (rgbd_capture_strategy_ == "subimages" ||
        rgbd_capture_strategy_ == "color_only")
      {
        set_enum_by_string("ImageMode", image_mode_, true);
      } else if (!color_exposure_mode_.empty()) {
        // This RGB-D firmware exposes color exposure only while Color mode is selected.
        set_enum_by_string("ImageMode", color_image_mode_, true);
      }
      set_enum_by_string("RGBDAlignCoord", rgbd_align_coord_, true);
      set_enum_by_string("AcquisitionMode", acquisition_mode_, true);
      if (!color_exposure_mode_.empty()) {
        log_enum_entries("ColorExposureModeSelector");
        set_enum_by_string("ColorExposureModeSelector", color_exposure_mode_, true);
        RCLCPP_INFO(
          get_logger(), "Color exposure mode set to %s", color_exposure_mode_.c_str());
      }
    }

    set_enum("TriggerMode", trigger_mode_ ? 1 : 0, true);
    if (trigger_mode_ && !trigger_source_.empty()) {
      set_enum_by_string("TriggerSource", trigger_source_, false);
    }
    if (!pixel_format_.empty()) {
      set_enum_by_string("PixelFormat", pixel_format_, false);
    }
    if (exposure_time_ > 0.0) {
      set_enum_by_string("ExposureAuto", "Off", false);
      set_float("ExposureTime", static_cast<float>(exposure_time_), false);
    }
    if (gain_ > 0.0) {
      set_enum_by_string("GainAuto", "Off", false);
      set_float("Gain", static_cast<float>(gain_), false);
    }
  }

  void log_enum_entries(const char * key)
  {
    MVCC_ENUMVALUE_EX values;
    std::memset(&values, 0, sizeof(values));
    const int ret = MV_CC_GetEnumValueEx(handle_, key, &values);
    if (ret != MV_OK) {
      RCLCPP_WARN(
        get_logger(), "Could not enumerate %s: %s", key, error_code(ret).c_str());
      return;
    }

    std::ostringstream supported;
    for (unsigned int i = 0; i < values.nSupportedNum; ++i) {
      MVCC_ENUMENTRY entry;
      std::memset(&entry, 0, sizeof(entry));
      entry.nValue = values.nSupportValue[i];
      const int entry_ret = MV_CC_GetEnumEntrySymbolic(handle_, key, &entry);
      if (i > 0U) {
        supported << ", ";
      }
      if (entry_ret == MV_OK) {
        supported << entry.chSymbolic;
      } else {
        supported << values.nSupportValue[i];
      }
    }
    RCLCPP_INFO(
      get_logger(), "%s supported values: [%s]", key, supported.str().c_str());
  }

  void set_enum(const char * key, unsigned int value, bool required)
  {
    const int ret = MV_CC_SetEnumValue(handle_, key, value);
    if (ret != MV_OK) {
      const std::string message =
        std::string("MV_CC_SetEnumValue failed for ") + key + ": " + error_code(ret);
      if (required) {
        throw std::runtime_error(message);
      }
      RCLCPP_WARN(get_logger(), "%s", message.c_str());
    }
  }

  void set_enum_by_string(const char * key, const std::string & value, bool required)
  {
    const int ret = MV_CC_SetEnumValueByString(handle_, key, value.c_str());
    if (ret != MV_OK) {
      const std::string message =
        std::string("MV_CC_SetEnumValueByString failed for ") + key + "=" + value + ": " + error_code(ret);
      if (required) {
        throw std::runtime_error(message);
      }
      RCLCPP_WARN(get_logger(), "%s", message.c_str());
    }
  }

  void set_float(const char * key, float value, bool required)
  {
    const int ret = MV_CC_SetFloatValue(handle_, key, value);
    if (ret != MV_OK) {
      const std::string message =
        std::string("MV_CC_SetFloatValue failed for ") + key + ": " + error_code(ret);
      if (required) {
        throw std::runtime_error(message);
      }
      RCLCPP_WARN(get_logger(), "%s", message.c_str());
    }
  }

  void start_streaming()
  {
    running_.store(true);
    if (rgbd_enabled_ && rgbd_capture_strategy_ == "alternating") {
      RCLCPP_INFO(
        get_logger(), "Starting alternating MVS RGB-D acquisition: color='%s' depth='%s'",
        color_image_mode_.c_str(), depth_image_mode_.c_str());
      worker_ = std::thread(&MvsCameraNode::alternating_rgbd_loop, this);
      return;
    }
    if (rgbd_enabled_ && rgbd_capture_strategy_ == "batched") {
      RCLCPP_INFO(
        get_logger(),
        "Starting batched MVS RGB-D acquisition: %d color frames then %d depth frames",
        color_frames_per_cycle_, depth_frames_per_cycle_);
      worker_ = std::thread(&MvsCameraNode::batched_rgbd_loop, this);
      return;
    }

    const int ret = MV_CC_StartGrabbing(handle_);
    if (ret != MV_OK) {
      running_.store(false);
      throw std::runtime_error("MV_CC_StartGrabbing failed: " + error_code(ret));
    }

    grabbing_ = true;
    worker_ = std::thread(&MvsCameraNode::grab_loop, this);
  }

  bool begin_mode_capture(const std::string & image_mode, MV_FRAME_OUT & frame)
  {
    int ret = MV_CC_SetEnumValueByString(handle_, "ImageMode", image_mode.c_str());
    if (ret != MV_OK) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000, "Failed to select ImageMode=%s: %s",
        image_mode.c_str(), error_code(ret).c_str());
      return false;
    }
    if (image_mode == depth_image_mode_) {
      ret = MV_CC_SetEnumValueByString(handle_, "RGBDAlignCoord", rgbd_align_coord_.c_str());
      if (ret != MV_OK) {
        RCLCPP_WARN_THROTTLE(
          get_logger(), *get_clock(), 5000,
          "Failed to reapply RGBDAlignCoord=%s before depth capture: %s",
          rgbd_align_coord_.c_str(), error_code(ret).c_str());
        return false;
      }
    }

    ret = MV_CC_StartGrabbing(handle_);
    if (ret != MV_OK) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000, "Failed to start ImageMode=%s: %s",
        image_mode.c_str(), error_code(ret).c_str());
      return false;
    }
    grabbing_ = true;

    std::memset(&frame, 0, sizeof(frame));
    ret = MV_CC_GetImageBuffer(handle_, &frame, static_cast<unsigned int>(grab_timeout_ms_));
    if (ret == MV_OK) {
      return true;
    }

    RCLCPP_WARN_THROTTLE(
      get_logger(), *get_clock(), 5000, "No frame for ImageMode=%s: %s",
      image_mode.c_str(), error_code(ret).c_str());
    MV_CC_StopGrabbing(handle_);
    grabbing_ = false;
    return false;
  }

  void end_mode_capture(MV_FRAME_OUT & frame)
  {
    const int free_ret = MV_CC_FreeImageBuffer(handle_, &frame);
    if (free_ret != MV_OK) {
      RCLCPP_WARN(get_logger(), "MV_CC_FreeImageBuffer failed: %s", error_code(free_ret).c_str());
    }
    const int stop_ret = MV_CC_StopGrabbing(handle_);
    if (stop_ret != MV_OK) {
      RCLCPP_WARN(get_logger(), "MV_CC_StopGrabbing failed: %s", error_code(stop_ret).c_str());
    }
    grabbing_ = false;
  }

  bool capture_color_frame(uint32_t & width, uint32_t & height)
  {
    MV_FRAME_OUT frame;
    if (!begin_mode_capture(color_image_mode_, frame)) {
      return false;
    }

    width = frame_width(frame.stFrameInfo);
    height = frame_height(frame.stFrameInfo);
    const unsigned char * data = frame.pBufAddr;
    size_t data_size = static_cast<size_t>(frame_length(frame.stFrameInfo));
    bool converted = width > 0U && height > 0U && data != nullptr;
    if (converted && frame.stFrameInfo.enPixelType != PixelType_Gvsp_RGB8_Packed) {
      converted = convert_to_rgb8(frame, width, height, data, data_size);
    }
    const size_t expected_size = static_cast<size_t>(width) * height * 3U;
    if (converted && data_size >= expected_size) {
      captured_color_buffer_.assign(data, data + expected_size);
      const auto capture_time = now();
      captured_color_header_.stamp = capture_time;
      captured_color_header_.frame_id = color_frame_id_;
      captured_color_time_ns_ = capture_time.nanoseconds();

      sensor_msgs::msg::Image color_message;
      color_message.header = captured_color_header_;
      color_message.height = height;
      color_message.width = width;
      color_message.encoding = sensor_msgs::image_encodings::RGB8;
      color_message.is_bigendian = false;
      color_message.step = width * 3U;
      color_message.data = captured_color_buffer_;
      const auto color_intrinsics = mvs_camera_driver::scale_intrinsics(
        nominal_intrinsics_, width, height);
      color_image_pub_.publish(color_message);
      color_camera_info_pub_->publish(
        make_camera_info(captured_color_header_, color_intrinsics));
    } else {
      converted = false;
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000, "Alternating RGB frame is incomplete");
    }
    end_mode_capture(frame);
    return converted;
  }

  bool capture_depth_frame(uint32_t & width, uint32_t & height)
  {
    MV_FRAME_OUT frame;
    if (!begin_mode_capture(depth_image_mode_, frame)) {
      return false;
    }

    width = frame_width(frame.stFrameInfo);
    height = frame_height(frame.stFrameInfo);
    const size_t pixel_count = static_cast<size_t>(width) * height;
    const size_t bytes = static_cast<size_t>(frame_length(frame.stFrameInfo));
    bool valid = frame.pBufAddr != nullptr && width > 0U && height > 0U &&
      mvs_camera_driver::classify_pixel_type(frame.stFrameInfo.enPixelType) ==
      mvs_camera_driver::ImageKind::Depth16 && bytes >= pixel_count * sizeof(uint16_t);
    if (valid) {
      const auto * depth = reinterpret_cast<const uint16_t *>(frame.pBufAddr);
      captured_depth_buffer_.assign(depth, depth + pixel_count);
      const auto capture_time = now();
      captured_depth_header_.stamp = capture_time;
      captured_depth_header_.frame_id = depth_frame_id_;
      captured_depth_time_ns_ = capture_time.nanoseconds();
    } else {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000, "Alternating depth frame is incomplete or unsupported");
    }
    end_mode_capture(frame);
    return valid;
  }

  void alternating_rgbd_loop()
  {
    while (rclcpp::ok() && running_.load()) {
      uint32_t color_width = 0U;
      uint32_t color_height = 0U;
      uint32_t depth_width = 0U;
      uint32_t depth_height = 0U;
      if (!capture_color_frame(color_width, color_height)) {
        continue;
      }
      if (!running_.load() || !capture_depth_frame(depth_width, depth_height)) {
        continue;
      }
      if (!rclcpp::ok() || !running_.load()) {
        continue;
      }
      publish_alternating_rgbd_pair(color_width, color_height, depth_width, depth_height);
    }
  }

  bool start_mode_stream(const std::string & image_mode)
  {
    int ret = MV_CC_SetEnumValueByString(handle_, "ImageMode", image_mode.c_str());
    if (ret != MV_OK) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000, "Failed to select ImageMode=%s: %s",
        image_mode.c_str(), error_code(ret).c_str());
      return false;
    }
    if (image_mode == depth_image_mode_) {
      ret = MV_CC_SetEnumValueByString(handle_, "RGBDAlignCoord", rgbd_align_coord_.c_str());
      if (ret != MV_OK) {
        RCLCPP_WARN_THROTTLE(
          get_logger(), *get_clock(), 5000,
          "Failed to reapply RGBDAlignCoord=%s before depth stream: %s",
          rgbd_align_coord_.c_str(), error_code(ret).c_str());
        return false;
      }
    }
    ret = MV_CC_StartGrabbing(handle_);
    if (ret != MV_OK) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000, "Failed to start ImageMode=%s: %s",
        image_mode.c_str(), error_code(ret).c_str());
      return false;
    }
    grabbing_ = true;
    return true;
  }

  void stop_mode_stream()
  {
    if (!grabbing_) {
      return;
    }
    const int ret = MV_CC_StopGrabbing(handle_);
    if (ret != MV_OK) {
      RCLCPP_WARN(get_logger(), "MV_CC_StopGrabbing failed: %s", error_code(ret).c_str());
    }
    grabbing_ = false;
  }

  bool grab_stream_frame(MV_FRAME_OUT & frame)
  {
    std::memset(&frame, 0, sizeof(frame));
    const int ret = MV_CC_GetImageBuffer(
      handle_, &frame, static_cast<unsigned int>(grab_timeout_ms_));
    if (ret == MV_OK) {
      return true;
    }
    RCLCPP_WARN_THROTTLE(
      get_logger(), *get_clock(), 5000, "No MVS batched frame: %s",
      error_code(ret).c_str());
    return false;
  }

  bool save_color_frame(
    const MV_FRAME_OUT & frame, uint32_t & width, uint32_t & height)
  {
    width = frame_width(frame.stFrameInfo);
    height = frame_height(frame.stFrameInfo);
    const unsigned char * data = frame.pBufAddr;
    size_t data_size = static_cast<size_t>(frame_length(frame.stFrameInfo));
    if (data == nullptr || width == 0U || height == 0U) {
      return false;
    }
    if (frame.stFrameInfo.enPixelType != PixelType_Gvsp_RGB8_Packed &&
      !convert_to_rgb8(frame, width, height, data, data_size))
    {
      return false;
    }
    const size_t expected = static_cast<size_t>(width) * height * 3U;
    if (data_size < expected) {
      return false;
    }
    captured_color_buffer_.assign(data, data + expected);
    const auto capture_time = now();
    captured_color_header_.stamp = capture_time;
    captured_color_header_.frame_id = color_frame_id_;
    captured_color_time_ns_ = capture_time.nanoseconds();
    color_pair_available_ = true;
    return true;
  }

  bool save_depth_frame(
    const MV_FRAME_OUT & frame, uint32_t & width, uint32_t & height)
  {
    width = frame_width(frame.stFrameInfo);
    height = frame_height(frame.stFrameInfo);
    const size_t pixels = static_cast<size_t>(width) * height;
    const size_t bytes = static_cast<size_t>(frame_length(frame.stFrameInfo));
    if (frame.pBufAddr == nullptr || width == 0U || height == 0U ||
      mvs_camera_driver::classify_pixel_type(frame.stFrameInfo.enPixelType) !=
      mvs_camera_driver::ImageKind::Depth16 || bytes < pixels * sizeof(uint16_t))
    {
      return false;
    }
    const auto * depth = reinterpret_cast<const uint16_t *>(frame.pBufAddr);
    captured_depth_buffer_.assign(depth, depth + pixels);
    const auto capture_time = now();
    captured_depth_header_.stamp = capture_time;
    captured_depth_header_.frame_id = depth_frame_id_;
    captured_depth_time_ns_ = capture_time.nanoseconds();
    return true;
  }

  void batched_rgbd_loop()
  {
    uint32_t color_width = 0U;
    uint32_t color_height = 0U;
    while (rclcpp::ok() && running_.load()) {
      if (!start_mode_stream(color_image_mode_)) {
        continue;
      }
      for (int i = 0; i < color_frames_per_cycle_ && running_.load(); ++i) {
        MV_FRAME_OUT frame;
        if (!grab_stream_frame(frame)) {
          continue;
        }
        if (!rclcpp::ok() || !running_.load()) {
          MV_CC_FreeImageBuffer(handle_, &frame);
          break;
        }
        publish_color_frame(frame);
        if (i == color_frames_per_cycle_ - 1 || captured_color_buffer_.empty()) {
          save_color_frame(frame, color_width, color_height);
        }
        MV_CC_FreeImageBuffer(handle_, &frame);
      }
      stop_mode_stream();
      if (!running_.load() || captured_color_buffer_.empty()) {
        continue;
      }

      if (!start_mode_stream(depth_image_mode_)) {
        continue;
      }
      for (int i = 0; i < depth_frames_per_cycle_ && running_.load(); ++i) {
        MV_FRAME_OUT frame;
        if (!grab_stream_frame(frame)) {
          continue;
        }
        if (!rclcpp::ok() || !running_.load()) {
          MV_CC_FreeImageBuffer(handle_, &frame);
          break;
        }
        uint32_t depth_width = 0U;
        uint32_t depth_height = 0U;
        const bool valid = save_depth_frame(frame, depth_width, depth_height);
        MV_CC_FreeImageBuffer(handle_, &frame);
        if (valid) {
          publish_batched_rgbd_pair(
            color_width, color_height, depth_width, depth_height);
        }
      }
      stop_mode_stream();
    }
    stop_mode_stream();
  }

  void grab_loop()
  {
    unsigned int missed_frame_count = 0;
    while (rclcpp::ok() && running_.load()) {
      MV_FRAME_OUT frame;
      std::memset(&frame, 0, sizeof(frame));

      const int ret = MV_CC_GetImageBuffer(handle_, &frame, static_cast<unsigned int>(grab_timeout_ms_));
      if (ret == MV_OK) {
        missed_frame_count = 0;
        if (rclcpp::ok() && running_.load()) {
          publish_frame(frame);
        }
        MV_CC_FreeImageBuffer(handle_, &frame);
      } else {
        ++missed_frame_count;
        if (missed_frame_count % 50 == 0) {
          RCLCPP_WARN(
            get_logger(), "No image buffer after %u attempts, last error: %s",
            missed_frame_count, error_code(ret).c_str());
        }
      }
    }
  }

  void publish_frame(const MV_FRAME_OUT & frame)
  {
    if (rgbd_enabled_) {
      if (rgbd_capture_strategy_ == "color_only") {
        publish_color_frame(frame);
      } else {
        publish_rgbd_frame(frame);
      }
      return;
    }

    const auto & info = frame.stFrameInfo;
    const uint32_t width = frame_width(info);
    const uint32_t height = frame_height(info);
    const uint64_t bytes = frame_length(info);

    if (frame.pBufAddr == nullptr || width == 0 || height == 0 || bytes == 0) {
      RCLCPP_WARN(get_logger(), "Skipping empty MVS frame");
      return;
    }

    std::string encoding;
    uint32_t step = 0;
    const unsigned char * data = frame.pBufAddr;
    size_t data_size = static_cast<size_t>(bytes);

    if (info.enPixelType == PixelType_Gvsp_Mono8) {
      encoding = sensor_msgs::image_encodings::MONO8;
      step = width;
    } else if (info.enPixelType == PixelType_Gvsp_RGB8_Packed) {
      encoding = sensor_msgs::image_encodings::RGB8;
      step = width * 3;
    } else if (info.enPixelType == PixelType_Gvsp_BGR8_Packed) {
      encoding = sensor_msgs::image_encodings::BGR8;
      step = width * 3;
    } else {
      if (!convert_to_rgb8(frame, width, height, data, data_size)) {
        return;
      }
      encoding = sensor_msgs::image_encodings::RGB8;
      step = width * 3;
    }

    sensor_msgs::msg::Image image;
    image.header.stamp = now();
    image.header.frame_id = frame_id_;
    image.height = height;
    image.width = width;
    image.encoding = encoding;
    image.is_bigendian = false;
    image.step = step;
    image.data.resize(data_size);
    std::memcpy(image.data.data(), data, data_size);

    image_pub_.publish(image);

    sensor_msgs::msg::CameraInfo camera_info;
    camera_info.header = image.header;
    camera_info.width = width;
    camera_info.height = height;
    camera_info_pub_->publish(camera_info);
  }

  void publish_color_frame(const MV_FRAME_OUT & frame)
  {
    const auto & info = frame.stFrameInfo;
    const uint32_t width = frame_width(info);
    const uint32_t height = frame_height(info);
    const unsigned char * data = frame.pBufAddr;
    size_t data_size = static_cast<size_t>(frame_length(info));

    if (data == nullptr || width == 0U || height == 0U || data_size == 0U) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000, "Skipping empty MVS color frame");
      return;
    }

    if (info.enPixelType != PixelType_Gvsp_RGB8_Packed &&
      !convert_to_rgb8(frame, width, height, data, data_size))
    {
      return;
    }

    const size_t expected_size = static_cast<size_t>(width) * height * 3U;
    if (data_size < expected_size) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000,
        "MVS color frame is incomplete: got %zu bytes, expected %zu",
        data_size, expected_size);
      return;
    }

    std_msgs::msg::Header header;
    header.stamp = now();
    header.frame_id = color_frame_id_;

    sensor_msgs::msg::Image message;
    message.header = header;
    message.height = height;
    message.width = width;
    message.encoding = sensor_msgs::image_encodings::RGB8;
    message.is_bigendian = false;
    message.step = width * 3U;
    message.data.assign(data, data + expected_size);

    const auto intrinsics = mvs_camera_driver::scale_intrinsics(
      nominal_intrinsics_, width, height);
    color_image_pub_.publish(message);
    color_camera_info_pub_->publish(make_camera_info(header, intrinsics));
  }

  void log_rgbd_layout(const MV_FRAME_OUT & frame)
  {
    const auto & info = frame.stFrameInfo;
    RCLCPP_INFO(
      get_logger(),
      "RGB-D frame layout: extra_type=%u subimages=%u main=%ux%u pixel_type=%d bytes=%llu",
      info.nExtraType, info.nSubImageNum, frame_width(info), frame_height(info),
      static_cast<int>(info.enPixelType),
      static_cast<unsigned long long>(frame_length(info)));

    if (info.nExtraType == MV_FRAME_EXTRA_SUBIMAGES &&
      info.nSubImageNum <= 16U && info.SubImageList.pstSubImage != nullptr)
    {
      for (unsigned int i = 0; i < info.nSubImageNum; ++i) {
        const auto & image = info.SubImageList.pstSubImage[i];
        RCLCPP_INFO(
          get_logger(), "RGB-D subimage[%u]: %ux%u pixel_type=%d bytes=%llu buffer=%s",
          i, image.nWidth, image.nHeight, static_cast<int>(image.enPixelType),
          static_cast<unsigned long long>(image.nImageLen),
          image.pImageBuf == nullptr ? "null" : "set");
      }
    }
  }

  bool convert_image_to_rgb8(const MV_CC_IMAGE & image, std::vector<unsigned char> & output)
  {
    const size_t pixel_count = static_cast<size_t>(image.nWidth) * image.nHeight;
    if (image.pImageBuf == nullptr || pixel_count == 0U) {
      return false;
    }

    output.resize(pixel_count * 3U);
    const auto kind = mvs_camera_driver::classify_pixel_type(image.enPixelType);
    if (kind == mvs_camera_driver::ImageKind::ColorRgb8) {
      if (image.nImageLen < output.size()) {
        return false;
      }
      std::memcpy(output.data(), image.pImageBuf, output.size());
      return true;
    }
    if (kind == mvs_camera_driver::ImageKind::ColorBgr8) {
      if (image.nImageLen < output.size()) {
        return false;
      }
      for (size_t i = 0; i < pixel_count; ++i) {
        output[i * 3U] = image.pImageBuf[i * 3U + 2U];
        output[i * 3U + 1U] = image.pImageBuf[i * 3U + 1U];
        output[i * 3U + 2U] = image.pImageBuf[i * 3U];
      }
      return true;
    }
    if (kind == mvs_camera_driver::ImageKind::ColorMono8) {
      if (image.nImageLen < pixel_count) {
        return false;
      }
      for (size_t i = 0; i < pixel_count; ++i) {
        output[i * 3U] = image.pImageBuf[i];
        output[i * 3U + 1U] = image.pImageBuf[i];
        output[i * 3U + 2U] = image.pImageBuf[i];
      }
      return true;
    }

    MV_CC_PIXEL_CONVERT_PARAM_EX convert_param;
    std::memset(&convert_param, 0, sizeof(convert_param));
    convert_param.nWidth = image.nWidth;
    convert_param.nHeight = image.nHeight;
    convert_param.enSrcPixelType = image.enPixelType;
    convert_param.pSrcData = image.pImageBuf;
    convert_param.nSrcDataLen = static_cast<unsigned int>(image.nImageLen);
    convert_param.enDstPixelType = PixelType_Gvsp_RGB8_Packed;
    convert_param.pDstBuffer = output.data();
    convert_param.nDstBufferSize = static_cast<unsigned int>(output.size());

    const int ret = MV_CC_ConvertPixelTypeEx(handle_, &convert_param);
    if (ret != MV_OK || convert_param.nDstLen != output.size()) {
      RCLCPP_WARN(
        get_logger(), "Could not convert RGB-D color subimage pixel type %d: %s",
        static_cast<int>(image.enPixelType), error_code(ret).c_str());
      return false;
    }
    return true;
  }

  sensor_msgs::msg::CameraInfo make_camera_info(
    const std_msgs::msg::Header & header,
    const mvs_camera_driver::CameraIntrinsics & intrinsics) const
  {
    sensor_msgs::msg::CameraInfo info;
    info.header = header;
    info.width = intrinsics.width;
    info.height = intrinsics.height;
    info.distortion_model = "plumb_bob";
    info.d.assign(5U, 0.0);
    info.k = {
      intrinsics.fx, 0.0, intrinsics.cx,
      0.0, intrinsics.fy, intrinsics.cy,
      0.0, 0.0, 1.0};
    info.r = {1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0};
    info.p = {
      intrinsics.fx, 0.0, intrinsics.cx, 0.0,
      0.0, intrinsics.fy, intrinsics.cy, 0.0,
      0.0, 0.0, 1.0, 0.0};
    return info;
  }

  void publish_pointcloud(
    const rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr & publisher,
    const std_msgs::msg::Header & header,
    const std::vector<mvs_camera_driver::PointXyzRgb> & points,
    uint32_t width,
    uint32_t height)
  {
    sensor_msgs::msg::PointCloud2 cloud;
    cloud.header = header;
    cloud.is_dense = false;
    sensor_msgs::PointCloud2Modifier modifier(cloud);
    modifier.setPointCloud2Fields(
      4,
      "x", 1, sensor_msgs::msg::PointField::FLOAT32,
      "y", 1, sensor_msgs::msg::PointField::FLOAT32,
      "z", 1, sensor_msgs::msg::PointField::FLOAT32,
      "rgb", 1, sensor_msgs::msg::PointField::FLOAT32);
    modifier.resize(points.size());
    cloud.height = height;
    cloud.width = width;
    cloud.row_step = cloud.point_step * cloud.width;

    static_assert(
      sizeof(mvs_camera_driver::PointXyzRgb) == 16U,
      "PointXyzRgb must match the ROS xyz/rgb point layout");
    static_assert(
      offsetof(mvs_camera_driver::PointXyzRgb, b) == 12U &&
      offsetof(mvs_camera_driver::PointXyzRgb, g) == 13U &&
      offsetof(mvs_camera_driver::PointXyzRgb, r) == 14U,
      "PointXyzRgb color bytes must match ROS packed RGB on little-endian hosts");
    if (!cloud.is_bigendian && cloud.point_step == sizeof(mvs_camera_driver::PointXyzRgb)) {
      std::memcpy(cloud.data.data(), points.data(), cloud.data.size());
      publisher->publish(cloud);
      return;
    }

    sensor_msgs::PointCloud2Iterator<float> iter_x(cloud, "x");
    sensor_msgs::PointCloud2Iterator<float> iter_y(cloud, "y");
    sensor_msgs::PointCloud2Iterator<float> iter_z(cloud, "z");
    sensor_msgs::PointCloud2Iterator<uint8_t> iter_r(cloud, "r");
    sensor_msgs::PointCloud2Iterator<uint8_t> iter_g(cloud, "g");
    sensor_msgs::PointCloud2Iterator<uint8_t> iter_b(cloud, "b");
    for (const auto & point : points) {
      *iter_x = point.x;
      *iter_y = point.y;
      *iter_z = point.z;
      *iter_r = point.r;
      *iter_g = point.g;
      *iter_b = point.b;
      ++iter_x;
      ++iter_y;
      ++iter_z;
      ++iter_r;
      ++iter_g;
      ++iter_b;
    }
    publisher->publish(cloud);
  }

  bool build_decimated_pointcloud(
    const std_msgs::msg::Header & header,
    const uint16_t * depth,
    const uint8_t * rgb,
    uint32_t width,
    uint32_t height,
    const mvs_camera_driver::CameraIntrinsics & intrinsics,
    uint32_t & cloud_width,
    uint32_t & cloud_height)
  {
    (void)header;
    const uint32_t step = static_cast<uint32_t>(pointcloud_decimation_);
    cloud_width = std::max(1U, width / step);
    cloud_height = std::max(1U, height / step);
#ifdef MVS_HAS_JETSON_ACCELERATION
    if (jetson_cuda_pointcloud_ && mvs_camera_driver::project_rgbd_decimated_cuda(
        depth, rgb, width, height, step, intrinsics,
        static_cast<float>(depth_scale_), static_cast<float>(depth_min_),
        static_cast<float>(depth_max_), pointcloud_spatial_filter_,
        static_cast<uint32_t>(pointcloud_filter_min_neighbors_),
        static_cast<float>(pointcloud_filter_depth_tolerance_),
        static_cast<float>(pointcloud_filter_depth_tolerance_ratio_),
        projected_points_buffer_))
    {
      if (!cuda_projection_active_logged_) {
        RCLCPP_INFO(get_logger(), "CUDA RGB-D point projection is active");
        cuda_projection_active_logged_ = true;
      }
      return true;
    }
#endif
    if (step == 1U) {
      projected_points_buffer_ = mvs_camera_driver::project_rgbd(
        depth, rgb, width, height, intrinsics,
        static_cast<float>(depth_scale_), static_cast<float>(depth_min_),
        static_cast<float>(depth_max_));
      cloud_width = width;
      cloud_height = height;
      return true;
    }

    const size_t cloud_pixels = static_cast<size_t>(cloud_width) * cloud_height;
    std::vector<uint16_t> sampled_depth(cloud_pixels);
    std::vector<uint8_t> sampled_rgb(cloud_pixels * 3U);
    for (uint32_t v = 0; v < cloud_height; ++v) {
      for (uint32_t u = 0; u < cloud_width; ++u) {
        const size_t source = static_cast<size_t>(v * step) * width + u * step;
        const size_t destination = static_cast<size_t>(v) * cloud_width + u;
        sampled_depth[destination] = depth[source];
        sampled_rgb[destination * 3U] = rgb[source * 3U];
        sampled_rgb[destination * 3U + 1U] = rgb[source * 3U + 1U];
        sampled_rgb[destination * 3U + 2U] = rgb[source * 3U + 2U];
      }
    }

    auto cloud_intrinsics = intrinsics;
    cloud_intrinsics.fx /= step;
    cloud_intrinsics.fy /= step;
    cloud_intrinsics.cx /= step;
    cloud_intrinsics.cy /= step;
    cloud_intrinsics.width = cloud_width;
    cloud_intrinsics.height = cloud_height;
    projected_points_buffer_ = mvs_camera_driver::project_rgbd(
      sampled_depth.data(), sampled_rgb.data(), cloud_width, cloud_height, cloud_intrinsics,
      static_cast<float>(depth_scale_), static_cast<float>(depth_min_),
      static_cast<float>(depth_max_));
    return true;
  }

  void publish_decimated_pointclouds(
    const std_msgs::msg::Header & header,
    const uint16_t * depth,
    const uint8_t * rgb,
    uint32_t width,
    uint32_t height,
    const mvs_camera_driver::CameraIntrinsics & intrinsics,
    bool color_pair_valid)
  {
    const bool geometry_requested = pointcloud_pub_->get_subscription_count() > 0U;
    const bool colorized_requested =
      color_pair_valid && colorized_pointcloud_pub_->get_subscription_count() > 0U;
    if (!geometry_requested && !colorized_requested) {
      return;
    }

    uint32_t cloud_width = 0U;
    uint32_t cloud_height = 0U;
    if (!build_decimated_pointcloud(
        header, depth, rgb, width, height, intrinsics, cloud_width, cloud_height))
    {
      return;
    }

    if (colorized_requested) {
      publish_pointcloud(
        colorized_pointcloud_pub_, header, projected_points_buffer_, cloud_width, cloud_height);
    }

    if (geometry_requested) {
      for (auto & point : projected_points_buffer_) {
        point.r = 0U;
        point.g = 0U;
        point.b = 0U;
      }
      publish_pointcloud(
        pointcloud_pub_, header, projected_points_buffer_, cloud_width, cloud_height);
    }
  }

  std::vector<std::uint8_t> resize_rgb_for_depth(
    const std::uint8_t * source,
    uint32_t source_width,
    uint32_t source_height,
    uint32_t target_width,
    uint32_t target_height)
  {
    bool vpi_used = false;
    auto target = mvs_camera_driver::resize_rgb8_nearest(
      source, source_width, source_height, target_width, target_height,
      jetson_vpi_resize_, &vpi_used);
    if (vpi_used && !vpi_resize_active_logged_) {
      RCLCPP_INFO(get_logger(), "VPI/VIC RGB resize is active");
      vpi_resize_active_logged_ = true;
    }
    return target;
  }

  void publish_rgbd_frame(const MV_FRAME_OUT & frame)
  {
    const auto & info = frame.stFrameInfo;
    if (!rgbd_layout_logged_) {
      log_rgbd_layout(frame);
      rgbd_layout_logged_ = true;
    }

    if (info.nExtraType != MV_FRAME_EXTRA_SUBIMAGES || info.nSubImageNum < 2U ||
        info.SubImageList.pstSubImage == nullptr) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000,
        "RGB-D frame does not contain the expected MVS subimages");
      return;
    }

    const MV_CC_IMAGE * color = nullptr;
    const MV_CC_IMAGE * depth = nullptr;
    for (unsigned int i = 0; i < info.nSubImageNum; ++i) {
      const auto & candidate = info.SubImageList.pstSubImage[i];
      const auto kind = mvs_camera_driver::classify_pixel_type(candidate.enPixelType);
      if (depth == nullptr && kind == mvs_camera_driver::ImageKind::Depth16) {
        depth = &candidate;
      } else if (color == nullptr &&
          (kind == mvs_camera_driver::ImageKind::ColorRgb8 ||
          kind == mvs_camera_driver::ImageKind::ColorBgr8 ||
          kind == mvs_camera_driver::ImageKind::ColorMono8)) {
        color = &candidate;
      }
    }

    if (color == nullptr || depth == nullptr) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000,
        "RGB-D frame is missing a supported color or 16-bit depth subimage");
      return;
    }
    if (color->nWidth != depth->nWidth || color->nHeight != depth->nHeight) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000,
        "Aligned RGB-D dimensions differ: color=%ux%u depth=%ux%u",
        color->nWidth, color->nHeight, depth->nWidth, depth->nHeight);
      return;
    }

    const size_t pixel_count = static_cast<size_t>(depth->nWidth) * depth->nHeight;
    if (depth->pImageBuf == nullptr || depth->nImageLen < pixel_count * sizeof(uint16_t)) {
      RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000, "RGB-D depth buffer is incomplete");
      return;
    }
    if (!convert_image_to_rgb8(*color, rgb_buffer_)) {
      return;
    }

    const auto stamp = now();
    std_msgs::msg::Header color_header;
    color_header.stamp = stamp;
    color_header.frame_id = color_frame_id_;
    std_msgs::msg::Header depth_header;
    depth_header.stamp = stamp;
    depth_header.frame_id = depth_frame_id_;

    sensor_msgs::msg::Image color_message;
    color_message.header = color_header;
    color_message.height = color->nHeight;
    color_message.width = color->nWidth;
    color_message.encoding = sensor_msgs::image_encodings::RGB8;
    color_message.is_bigendian = false;
    color_message.step = color->nWidth * 3U;
    color_message.data = rgb_buffer_;

    const auto intrinsics = mvs_camera_driver::scale_intrinsics(
      nominal_intrinsics_, color->nWidth, color->nHeight);
    const auto * raw_depth = reinterpret_cast<const uint16_t *>(depth->pImageBuf);
    sensor_msgs::msg::Image depth_message;
    depth_message.header = depth_header;
    depth_message.height = depth->nHeight;
    depth_message.width = depth->nWidth;
    depth_message.encoding = sensor_msgs::image_encodings::TYPE_16UC1;
    depth_message.is_bigendian = false;
    depth_message.step = depth->nWidth * sizeof(uint16_t);
    depth_message.data.resize(pixel_count * sizeof(uint16_t));
    std::memcpy(
      depth_message.data.data(), raw_depth, depth_message.data.size());

    color_image_pub_.publish(color_message);
    depth_image_pub_.publish(depth_message);
    color_camera_info_pub_->publish(make_camera_info(color_header, intrinsics));
    depth_camera_info_pub_->publish(make_camera_info(depth_header, intrinsics));

    if (publish_pointcloud_) {
      publish_decimated_pointclouds(
        depth_header, raw_depth, rgb_buffer_.data(), depth->nWidth, depth->nHeight,
        intrinsics, true);
    }
  }

  void publish_alternating_rgbd_pair(
    uint32_t color_width,
    uint32_t color_height,
    uint32_t depth_width,
    uint32_t depth_height)
  {
    const size_t pixel_count = static_cast<size_t>(depth_width) * depth_height;
    if (captured_color_buffer_.empty() || captured_depth_buffer_.size() != pixel_count) {
      return;
    }

    rgb_buffer_ = resize_rgb_for_depth(
      captured_color_buffer_.data(), color_width, color_height, depth_width, depth_height);
    const auto intrinsics = mvs_camera_driver::scale_intrinsics(
      nominal_intrinsics_, depth_width, depth_height);
    const auto color_header = captured_color_header_;
    const auto depth_header = captured_depth_header_;
    const int64_t pair_delta_ns = captured_depth_time_ns_ >= captured_color_time_ns_ ?
      captured_depth_time_ns_ - captured_color_time_ns_ :
      captured_color_time_ns_ - captured_depth_time_ns_;
    const double pair_delta_ms = static_cast<double>(pair_delta_ns) / 1.0e6;
    const bool color_pair_valid = captured_color_time_ns_ > 0 && captured_depth_time_ns_ > 0 &&
      pair_delta_ms <= static_cast<double>(rgbd_max_pair_delta_ms_);
    if (!color_pair_valid) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000,
        "Skipping colorized cloud: nearest one-to-one RGB-D pair delta %.1f ms exceeds %d ms",
        pair_delta_ms, rgbd_max_pair_delta_ms_);
    }

    sensor_msgs::msg::Image color_message;
    color_message.header = color_header;
    color_message.height = depth_height;
    color_message.width = depth_width;
    color_message.encoding = sensor_msgs::image_encodings::RGB8;
    color_message.is_bigendian = false;
    color_message.step = depth_width * 3U;
    color_message.data = rgb_buffer_;

    sensor_msgs::msg::Image depth_message;
    depth_message.header = depth_header;
    depth_message.height = depth_height;
    depth_message.width = depth_width;
    depth_message.encoding = sensor_msgs::image_encodings::TYPE_16UC1;
    depth_message.is_bigendian = false;
    depth_message.step = depth_width * sizeof(uint16_t);
    depth_message.data.resize(captured_depth_buffer_.size() * sizeof(uint16_t));
    std::memcpy(
      depth_message.data.data(), captured_depth_buffer_.data(), depth_message.data.size());

    rgbd_color_image_pub_.publish(color_message);
    depth_image_pub_.publish(depth_message);
    rgbd_color_camera_info_pub_->publish(make_camera_info(color_header, intrinsics));
    depth_camera_info_pub_->publish(make_camera_info(depth_header, intrinsics));

    if (publish_pointcloud_) {
      publish_decimated_pointclouds(
        depth_header, captured_depth_buffer_.data(), rgb_buffer_.data(),
        depth_width, depth_height, intrinsics, color_pair_valid);
    }
  }

  void publish_batched_rgbd_pair(
    uint32_t color_width,
    uint32_t color_height,
    uint32_t depth_width,
    uint32_t depth_height)
  {
    const size_t pixel_count = static_cast<size_t>(depth_width) * depth_height;
    if (captured_color_buffer_.empty() || captured_depth_buffer_.size() != pixel_count) {
      return;
    }

    if (color_pair_available_) {
      rgb_buffer_ = resize_rgb_for_depth(
        captured_color_buffer_.data(), color_width, color_height, depth_width, depth_height);
    }
    if (rgb_buffer_.size() != pixel_count * 3U) {
      return;
    }
    const auto intrinsics = mvs_camera_driver::scale_intrinsics(
      nominal_intrinsics_, depth_width, depth_height);
    const auto color_header = captured_color_header_;
    const auto depth_header = captured_depth_header_;
    const int64_t pair_delta_ns = captured_depth_time_ns_ >= captured_color_time_ns_ ?
      captured_depth_time_ns_ - captured_color_time_ns_ :
      captured_color_time_ns_ - captured_depth_time_ns_;
    const double pair_delta_ms = static_cast<double>(pair_delta_ns) / 1.0e6;
    const bool color_pair_valid = color_pair_available_ && captured_color_time_ns_ > 0 &&
      captured_depth_time_ns_ > 0 &&
      pair_delta_ms <= static_cast<double>(rgbd_max_pair_delta_ms_);
    if (color_pair_available_ && !color_pair_valid) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 5000,
        "Skipping colorized cloud: nearest one-to-one RGB-D pair delta %.1f ms exceeds %d ms",
        pair_delta_ms, rgbd_max_pair_delta_ms_);
    }
    // Consume the cached color after the nearest depth frame, whether the pair
    // passed the age gate or not. Later depth frames remain geometry-only.
    color_pair_available_ = false;

    sensor_msgs::msg::Image color_message;
    color_message.header = color_header;
    color_message.height = depth_height;
    color_message.width = depth_width;
    color_message.encoding = sensor_msgs::image_encodings::RGB8;
    color_message.is_bigendian = false;
    color_message.step = depth_width * 3U;
    color_message.data = rgb_buffer_;

    sensor_msgs::msg::Image depth_message;
    depth_message.header = depth_header;
    depth_message.height = depth_height;
    depth_message.width = depth_width;
    depth_message.encoding = sensor_msgs::image_encodings::TYPE_16UC1;
    depth_message.is_bigendian = false;
    depth_message.step = depth_width * sizeof(uint16_t);
    depth_message.data.resize(captured_depth_buffer_.size() * sizeof(uint16_t));
    std::memcpy(
      depth_message.data.data(), captured_depth_buffer_.data(), depth_message.data.size());

    if (color_pair_valid) {
      rgbd_color_image_pub_.publish(color_message);
      rgbd_color_camera_info_pub_->publish(make_camera_info(color_header, intrinsics));
    }
    depth_image_pub_.publish(depth_message);
    depth_camera_info_pub_->publish(make_camera_info(depth_header, intrinsics));

    if (publish_pointcloud_) {
      publish_decimated_pointclouds(
        depth_header, captured_depth_buffer_.data(), rgb_buffer_.data(),
        depth_width, depth_height, intrinsics, color_pair_valid);
    }
  }

  bool convert_to_rgb8(
    const MV_FRAME_OUT & frame,
    uint32_t width,
    uint32_t height,
    const unsigned char *& data,
    size_t & data_size)
  {
    converted_buffer_.resize(static_cast<size_t>(width) * static_cast<size_t>(height) * 3U);

    MV_CC_PIXEL_CONVERT_PARAM_EX convert_param;
    std::memset(&convert_param, 0, sizeof(convert_param));
    convert_param.nWidth = width;
    convert_param.nHeight = height;
    convert_param.enSrcPixelType = frame.stFrameInfo.enPixelType;
    convert_param.pSrcData = frame.pBufAddr;
    convert_param.nSrcDataLen = static_cast<unsigned int>(frame_length(frame.stFrameInfo));
    convert_param.enDstPixelType = PixelType_Gvsp_RGB8_Packed;
    convert_param.pDstBuffer = converted_buffer_.data();
    convert_param.nDstBufferSize = static_cast<unsigned int>(converted_buffer_.size());

    const int ret = MV_CC_ConvertPixelTypeEx(handle_, &convert_param);
    if (ret != MV_OK) {
      RCLCPP_WARN(
        get_logger(), "MV_CC_ConvertPixelTypeEx failed for pixel type %d: %s",
        static_cast<int>(frame.stFrameInfo.enPixelType), error_code(ret).c_str());
      return false;
    }

    data = converted_buffer_.data();
    data_size = convert_param.nDstLen;
    return true;
  }

  void cleanup()
  {
    if (cleanup_started_.exchange(true)) {
      return;
    }
    RCLCPP_INFO(get_logger(), "MVS cleanup: stopping capture worker");
    running_.store(false);
    if (worker_.joinable()) {
      worker_.join();
    }
    RCLCPP_INFO(get_logger(), "MVS cleanup: capture worker stopped");

#ifdef MVS_HAS_JETSON_ACCELERATION
    mvs_camera_driver::shutdown_vpi_vic();
    mvs_camera_driver::shutdown_cuda_rgbd();
    RCLCPP_INFO(get_logger(), "MVS cleanup: Jetson acceleration released");
#endif

    if (grabbing_ && handle_ != nullptr) {
      const int ret = MV_CC_StopGrabbing(handle_);
      if (ret != MV_OK) {
        RCLCPP_WARN(get_logger(), "MV_CC_StopGrabbing failed during cleanup: %s", error_code(ret).c_str());
      }
      grabbing_ = false;
    }
    RCLCPP_INFO(get_logger(), "MVS cleanup: grabbing stopped");

    if (device_open_ && handle_ != nullptr) {
      const int ret = MV_CC_CloseDevice(handle_);
      if (ret != MV_OK) {
        RCLCPP_WARN(get_logger(), "MV_CC_CloseDevice failed during cleanup: %s", error_code(ret).c_str());
      }
      device_open_ = false;
    }
    RCLCPP_INFO(get_logger(), "MVS cleanup: device closed");

    if (handle_ != nullptr) {
      const int ret = MV_CC_DestroyHandle(handle_);
      if (ret != MV_OK) {
        RCLCPP_WARN(get_logger(), "MV_CC_DestroyHandle failed during cleanup: %s", error_code(ret).c_str());
      }
      handle_ = nullptr;
    }
    RCLCPP_INFO(get_logger(), "MVS cleanup: handle destroyed");

    if (sdk_initialized_) {
      const int ret = MV_CC_Finalize();
      if (ret != MV_OK) {
        RCLCPP_WARN(get_logger(), "MV_CC_Finalize failed during cleanup: %s", error_code(ret).c_str());
      }
      sdk_initialized_ = false;
    }
    RCLCPP_INFO(get_logger(), "MVS cleanup complete");
  }

  image_transport::Publisher image_pub_;
  image_transport::Publisher color_image_pub_;
  image_transport::Publisher rgbd_color_image_pub_;
  image_transport::Publisher depth_image_pub_;
  rclcpp::Publisher<sensor_msgs::msg::CameraInfo>::SharedPtr camera_info_pub_;
  rclcpp::Publisher<sensor_msgs::msg::CameraInfo>::SharedPtr color_camera_info_pub_;
  rclcpp::Publisher<sensor_msgs::msg::CameraInfo>::SharedPtr rgbd_color_camera_info_pub_;
  rclcpp::Publisher<sensor_msgs::msg::CameraInfo>::SharedPtr depth_camera_info_pub_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr pointcloud_pub_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr colorized_pointcloud_pub_;

  std::thread worker_;
  std::atomic_bool running_{false};
  std::atomic_bool cleanup_started_{false};
  std::vector<unsigned char> converted_buffer_;
  std::vector<unsigned char> rgb_buffer_;
  std::vector<unsigned char> captured_color_buffer_;
  std::vector<uint16_t> captured_depth_buffer_;
  std::vector<mvs_camera_driver::PointXyzRgb> projected_points_buffer_;
  std_msgs::msg::Header captured_color_header_;
  std_msgs::msg::Header captured_depth_header_;
  int64_t captured_color_time_ns_{0};
  int64_t captured_depth_time_ns_{0};

  void * handle_{nullptr};
  bool sdk_initialized_{false};
  bool device_open_{false};
  bool grabbing_{false};
  bool selected_is_gige_{false};
  bool rgbd_layout_logged_{false};
  bool color_pair_available_{false};

  int camera_index_{0};
  int grab_timeout_ms_{1000};
  int color_frames_per_cycle_{1};
  int depth_frames_per_cycle_{1};
  std::string serial_number_;
  std::string user_defined_name_;
  std::string frame_id_;
  std::string image_topic_;
  std::string camera_info_topic_;
  std::string runtime_sdk_dir_;
  std::string pixel_format_;
  std::string trigger_source_;
  double exposure_time_{-1.0};
  double gain_{-1.0};
  bool auto_packet_size_{true};
  bool trigger_mode_{false};
  bool rgbd_enabled_{false};
  bool publish_pointcloud_{true};
  bool jetson_cuda_pointcloud_{false};
  bool jetson_vpi_resize_{false};
  bool cuda_projection_active_logged_{false};
  bool vpi_resize_active_logged_{false};
  bool pointcloud_spatial_filter_{true};
  int pointcloud_decimation_{2};
  int pointcloud_filter_min_neighbors_{6};
  int rgbd_max_pair_delta_ms_{750};
  std::string camera_working_mode_;
  std::string image_mode_;
  std::string rgbd_capture_strategy_;
  std::string color_image_mode_;
  std::string depth_image_mode_;
  std::string color_exposure_mode_;
  std::string rgbd_align_coord_;
  std::string acquisition_mode_;
  std::string color_frame_id_;
  std::string depth_frame_id_;
  std::string color_image_topic_;
  std::string color_camera_info_topic_;
  std::string rgbd_color_image_topic_;
  std::string rgbd_color_camera_info_topic_;
  std::string depth_image_topic_;
  std::string depth_camera_info_topic_;
  std::string pointcloud_topic_;
  std::string colorized_pointcloud_topic_;
  double depth_scale_{0.001};
  double depth_min_{0.2};
  double depth_max_{3.5};
  double pointcloud_filter_depth_tolerance_{0.04};
  double pointcloud_filter_depth_tolerance_ratio_{0.02};
  mvs_camera_driver::CameraIntrinsics nominal_intrinsics_{};
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);

  try {
    auto node = std::make_shared<MvsCameraNode>();
    rclcpp::spin(node);
  } catch (const std::exception & ex) {
    RCLCPP_FATAL(rclcpp::get_logger("mvs_camera_node"), "%s", ex.what());
    if (rclcpp::ok()) {
      rclcpp::shutdown();
    }
    return 1;
  }

  // SIGINT already shuts down the default context. A second shutdown raced
  // with vendor/NVIDIA process teardown intermittently on Jetson.
  if (rclcpp::ok()) {
    rclcpp::shutdown();
  }
  return 0;
}
