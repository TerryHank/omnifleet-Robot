#include "mvs_camera_driver/rgbd_acceleration.hpp"

#include <opencv2/core.hpp>
#include <vpi/Image.h>
#include <vpi/OpenCVInterop.hpp>
#include <vpi/Status.h>
#include <vpi/Stream.h>
#include <vpi/algo/ConvertImageFormat.h>
#include <vpi/algo/Rescale.h>

#include <cstdio>
#include <cstring>
#include <mutex>

namespace mvs_camera_driver
{
namespace
{
void report_failure_once(const char * stage, VPIStatus status)
{
  static std::once_flag once;
  std::call_once(once, [stage, status]() {
    char message[1024] = {};
    vpiGetLastStatusMessage(message, sizeof(message));
    std::fprintf(
      stderr, "MVS VPI/VIC acceleration fell back at %s (status=%d): %s\n",
      stage, static_cast<int>(status), message);
  });
}

class VpiState
{
public:
  ~VpiState()
  {
    reset();
  }

  void reset()
  {
    if (stream != nullptr) {
      vpiStreamSync(stream);
    }
    destroy_images();
    if (stream != nullptr) {
      vpiStreamDestroy(stream);
    }
    stream = nullptr;
  }

  bool ensure_stream()
  {
    return stream != nullptr ||
           vpiStreamCreate(
      VPI_BACKEND_CUDA | VPI_BACKEND_VIC | VPI_REQUIRE_BACKENDS, &stream) == VPI_SUCCESS;
  }

  bool prepare(const cv::Mat & source, int target_width, int target_height)
  {
    if (source_image == nullptr || source.cols != source_width || source.rows != source_height) {
      destroy_images();
      VPIStatus status = vpiImageCreateWrapperOpenCVMat(
        source, VPI_IMAGE_FORMAT_RGB8, 0, &source_image);
      if (status != VPI_SUCCESS) {
        report_failure_once("RGB source wrapper creation", status);
        return false;
      }
      status = vpiImageCreate(
        source.cols, source.rows, VPI_IMAGE_FORMAT_NV12_ER, 0, &source_nv12);
      if (status != VPI_SUCCESS) {
        report_failure_once("source NV12 allocation", status);
        return false;
      }
      source_width = source.cols;
      source_height = source.rows;
    } else {
      const VPIStatus status = vpiImageSetWrappedOpenCVMat(source_image, source);
      if (status != VPI_SUCCESS) {
        report_failure_once("RGB source wrapper update", status);
        return false;
      }
    }

    if (target_rgb == nullptr || target_width != this->target_width ||
      target_height != this->target_height)
    {
      if (target_rgb != nullptr) {
        vpiImageDestroy(target_rgb);
        target_rgb = nullptr;
      }
      if (target_nv12 != nullptr) {
        vpiImageDestroy(target_nv12);
        target_nv12 = nullptr;
      }
      VPIStatus status = vpiImageCreate(
        target_width, target_height, VPI_IMAGE_FORMAT_NV12_ER,
        0, &target_nv12);
      if (status != VPI_SUCCESS) {
        report_failure_once("target NV12 allocation", status);
        return false;
      }
      status = vpiImageCreate(
        target_width, target_height, VPI_IMAGE_FORMAT_RGB8, 0, &target_rgb);
      if (status != VPI_SUCCESS) {
        report_failure_once("target RGB allocation", status);
        return false;
      }
      this->target_width = target_width;
      this->target_height = target_height;
    }
    return true;
  }

  void destroy_images()
  {
    if (target_rgb != nullptr) {
      vpiImageDestroy(target_rgb);
      target_rgb = nullptr;
    }
    if (target_nv12 != nullptr) {
      vpiImageDestroy(target_nv12);
      target_nv12 = nullptr;
    }
    if (source_nv12 != nullptr) {
      vpiImageDestroy(source_nv12);
      source_nv12 = nullptr;
    }
    if (source_image != nullptr) {
      vpiImageDestroy(source_image);
      source_image = nullptr;
    }
    source_width = 0;
    source_height = 0;
    target_width = 0;
    target_height = 0;
  }

  std::mutex mutex;
  VPIStream stream{nullptr};
  VPIImage source_image{nullptr};
  VPIImage source_nv12{nullptr};
  VPIImage target_nv12{nullptr};
  VPIImage target_rgb{nullptr};
  int source_width{0};
  int source_height{0};
  int target_width{0};
  int target_height{0};
};

VpiState & state()
{
  // The NVIDIA VPI runtime also owns process-wide static state. Let our
  // process-lifetime holder survive C++ static destruction and release all VPI
  // resources explicitly from shutdown_vpi_vic(); this avoids an intermittent
  // second teardown after main() that used to end in SIGSEGV.
  static VpiState * instance = new VpiState();
  return *instance;
}
}  // namespace

bool vpi_vic_available()
{
  auto & instance = state();
  std::lock_guard<std::mutex> lock(instance.mutex);
  return instance.ensure_stream();
}

void shutdown_vpi_vic()
{
  auto & instance = state();
  std::lock_guard<std::mutex> lock(instance.mutex);
  instance.reset();
}

bool resize_rgb8_vpi_vic(
  const std::uint8_t * source,
  std::uint32_t source_width,
  std::uint32_t source_height,
  std::uint32_t target_width,
  std::uint32_t target_height,
  std::vector<std::uint8_t> & target)
{
  if (source == nullptr || source_width == 0U || source_height == 0U ||
    target_width == 0U || target_height == 0U)
  {
    return false;
  }

  auto & instance = state();
  std::lock_guard<std::mutex> lock(instance.mutex);
  if (!instance.ensure_stream()) {
    return false;
  }

  cv::Mat source_mat(
    static_cast<int>(source_height), static_cast<int>(source_width), CV_8UC3,
    const_cast<std::uint8_t *>(source));
  if (!instance.prepare(
      source_mat, static_cast<int>(target_width), static_cast<int>(target_height)))
  {
    return false;
  }

  VPIStatus status = vpiSubmitConvertImageFormat(
    instance.stream, VPI_BACKEND_CUDA, instance.source_image, instance.source_nv12, nullptr);
  if (status == VPI_SUCCESS) {
    status = vpiSubmitRescale(
      instance.stream, VPI_BACKEND_VIC, instance.source_nv12, instance.target_nv12,
      VPI_INTERP_LINEAR, VPI_BORDER_CLAMP, 0);
  }
  if (status == VPI_SUCCESS) {
    status = vpiSubmitConvertImageFormat(
      instance.stream, VPI_BACKEND_CUDA, instance.target_nv12, instance.target_rgb, nullptr);
  }
  if (status == VPI_SUCCESS) {
    status = vpiStreamSync(instance.stream);
  }
  if (status != VPI_SUCCESS) {
    report_failure_once("CUDA/VIC RGB resize pipeline", status);
    return false;
  }

  VPIImageData output_data{};
  status = vpiImageLockData(
    instance.target_rgb, VPI_LOCK_READ, VPI_IMAGE_BUFFER_HOST_PITCH_LINEAR, &output_data);
  if (status != VPI_SUCCESS) {
    report_failure_once("RGB output lock", status);
    return false;
  }

  target.resize(static_cast<std::size_t>(target_width) * target_height * 3U);
  const auto & plane = output_data.buffer.pitch.planes[0];
  const std::size_t row_bytes = static_cast<std::size_t>(target_width) * 3U;
  for (std::uint32_t row = 0; row < target_height; ++row) {
    std::memcpy(
      target.data() + static_cast<std::size_t>(row) * row_bytes,
      static_cast<const std::uint8_t *>(plane.data) + static_cast<std::size_t>(row) * plane.pitchBytes,
      row_bytes);
  }
  status = vpiImageUnlock(instance.target_rgb);
  if (status != VPI_SUCCESS) {
    report_failure_once("RGB output unlock", status);
    return false;
  }
  return true;
}
}  // namespace mvs_camera_driver
