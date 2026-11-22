#include "mvs_camera_driver/rgbd_acceleration.hpp"

#include <cuda_runtime.h>
#include <math_constants.h>

#include <algorithm>
#include <cstddef>
#include <mutex>

namespace mvs_camera_driver
{
static_assert(sizeof(PointXyzRgb) == 16U, "PointXyzRgb layout must match CUDA transfer layout");

namespace
{
__global__ void project_kernel(
  const std::uint16_t * depth,
  const std::uint8_t * rgb,
  std::uint32_t source_width,
  std::uint32_t source_height,
  std::uint32_t output_width,
  std::uint32_t output_height,
  std::uint32_t step,
  float fx,
  float fy,
  float cx,
  float cy,
  float depth_scale,
  float minimum_depth,
  float maximum_depth,
  bool spatial_filter_enabled,
  std::uint32_t minimum_consistent_neighbors,
  float neighbor_depth_tolerance,
  float neighbor_depth_tolerance_ratio,
  PointXyzRgb * output)
{
  const std::size_t index = blockIdx.x * blockDim.x + threadIdx.x;
  const std::size_t count = static_cast<std::size_t>(output_width) * output_height;
  if (index >= count) {
    return;
  }

  const std::uint32_t u = static_cast<std::uint32_t>(index % output_width) * step;
  const std::uint32_t v = static_cast<std::uint32_t>(index / output_width) * step;
  const std::size_t source_index = static_cast<std::size_t>(v) * source_width + u;
  const float z = static_cast<float>(depth[source_index]) * depth_scale;
  PointXyzRgb point{};
  point.r = rgb[source_index * 3U];
  point.g = rgb[source_index * 3U + 1U];
  point.b = rgb[source_index * 3U + 2U];

  bool valid = depth[source_index] != 0U && z >= minimum_depth && z <= maximum_depth;
  if (valid && spatial_filter_enabled) {
    std::uint32_t consistent_neighbors = 0U;
    const float tolerance = fmaxf(neighbor_depth_tolerance, z * neighbor_depth_tolerance_ratio);
    for (int offset_v = -1; offset_v <= 1; ++offset_v) {
      for (int offset_u = -1; offset_u <= 1; ++offset_u) {
        if (offset_u == 0 && offset_v == 0) {
          continue;
        }
        const int neighbor_u = static_cast<int>(u) + offset_u;
        const int neighbor_v = static_cast<int>(v) + offset_v;
        if (neighbor_u < 0 || neighbor_v < 0 ||
          neighbor_u >= static_cast<int>(source_width) ||
          neighbor_v >= static_cast<int>(source_height))
        {
          continue;
        }
        const std::size_t neighbor_index =
          static_cast<std::size_t>(neighbor_v) * source_width + neighbor_u;
        const std::uint16_t neighbor_raw = depth[neighbor_index];
        if (neighbor_raw == 0U) {
          continue;
        }
        const float neighbor_z = static_cast<float>(neighbor_raw) * depth_scale;
        if (neighbor_z >= minimum_depth && neighbor_z <= maximum_depth &&
          fabsf(neighbor_z - z) <= tolerance)
        {
          ++consistent_neighbors;
        }
      }
    }
    valid = consistent_neighbors >= minimum_consistent_neighbors;
  }

  if (!valid) {
    point.x = CUDART_NAN_F;
    point.y = CUDART_NAN_F;
    point.z = CUDART_NAN_F;
  } else {
    point.x = (static_cast<float>(u) - cx) * z / fx;
    point.y = (static_cast<float>(v) - cy) * z / fy;
    point.z = z;
  }
  output[index] = point;
}

class CudaBuffers
{
public:
  ~CudaBuffers()
  {
    reset();
  }

  void reset()
  {
    if (stream_ != nullptr) {
      cudaStreamSynchronize(stream_);
    }
    cudaFree(depth_);
    cudaFree(rgb_);
    cudaFree(points_);
    if (stream_ != nullptr) {
      cudaStreamDestroy(stream_);
    }
    stream_ = nullptr;
    depth_ = nullptr;
    rgb_ = nullptr;
    points_ = nullptr;
    source_capacity_ = 0U;
    output_capacity_ = 0U;
  }

  bool ensure(std::size_t source_pixels, std::size_t output_pixels)
  {
    if (stream_ == nullptr && cudaStreamCreateWithFlags(&stream_, cudaStreamNonBlocking) != cudaSuccess) {
      return false;
    }
    if (source_pixels > source_capacity_) {
      cudaFree(depth_);
      cudaFree(rgb_);
      depth_ = nullptr;
      rgb_ = nullptr;
      if (cudaMalloc(&depth_, source_pixels * sizeof(std::uint16_t)) != cudaSuccess ||
        cudaMalloc(&rgb_, source_pixels * 3U) != cudaSuccess)
      {
        return false;
      }
      source_capacity_ = source_pixels;
    }
    if (output_pixels > output_capacity_) {
      cudaFree(points_);
      points_ = nullptr;
      if (cudaMalloc(&points_, output_pixels * sizeof(PointXyzRgb)) != cudaSuccess) {
        return false;
      }
      output_capacity_ = output_pixels;
    }
    return true;
  }

  std::mutex mutex;
  cudaStream_t stream_{nullptr};
  std::uint16_t * depth_{nullptr};
  std::uint8_t * rgb_{nullptr};
  PointXyzRgb * points_{nullptr};
  std::size_t source_capacity_{0};
  std::size_t output_capacity_{0};
};

CudaBuffers & buffers()
{
  // CUDA process teardown may run after dependent NVIDIA libraries have begun
  // static destruction. Resources are released explicitly by
  // shutdown_cuda_rgbd(), so keep only the empty holder alive until exit.
  static CudaBuffers * instance = new CudaBuffers();
  return *instance;
}
}  // namespace

bool cuda_rgbd_available()
{
  int count = 0;
  return cudaGetDeviceCount(&count) == cudaSuccess && count > 0;
}

void shutdown_cuda_rgbd()
{
  auto & state = buffers();
  std::lock_guard<std::mutex> lock(state.mutex);
  state.reset();
}

bool project_rgbd_decimated_cuda(
  const std::uint16_t * depth,
  const std::uint8_t * rgb,
  std::uint32_t width,
  std::uint32_t height,
  std::uint32_t step,
  const CameraIntrinsics & intrinsics,
  float depth_scale,
  float minimum_depth,
  float maximum_depth,
  bool spatial_filter_enabled,
  std::uint32_t minimum_consistent_neighbors,
  float neighbor_depth_tolerance,
  float neighbor_depth_tolerance_ratio,
  std::vector<PointXyzRgb> & points)
{
  if (depth == nullptr || rgb == nullptr || width == 0U || height == 0U || step == 0U ||
    intrinsics.fx <= 0.0 || intrinsics.fy <= 0.0 || minimum_consistent_neighbors > 8U ||
    neighbor_depth_tolerance < 0.0F || neighbor_depth_tolerance_ratio < 0.0F)
  {
    return false;
  }

  const std::uint32_t output_width = std::max(1U, width / step);
  const std::uint32_t output_height = std::max(1U, height / step);
  const std::size_t source_pixels = static_cast<std::size_t>(width) * height;
  const std::size_t output_pixels = static_cast<std::size_t>(output_width) * output_height;
  auto & state = buffers();
  std::lock_guard<std::mutex> lock(state.mutex);
  if (!state.ensure(source_pixels, output_pixels)) {
    return false;
  }

  if (cudaMemcpyAsync(
      state.depth_, depth, source_pixels * sizeof(std::uint16_t),
      cudaMemcpyHostToDevice, state.stream_) != cudaSuccess ||
    cudaMemcpyAsync(
      state.rgb_, rgb, source_pixels * 3U,
      cudaMemcpyHostToDevice, state.stream_) != cudaSuccess)
  {
    return false;
  }

  constexpr int threads = 256;
  const int blocks = static_cast<int>((output_pixels + threads - 1U) / threads);
  project_kernel<<<blocks, threads, 0, state.stream_>>>(
    state.depth_, state.rgb_, width, height, output_width, output_height, step,
    static_cast<float>(intrinsics.fx), static_cast<float>(intrinsics.fy),
    static_cast<float>(intrinsics.cx), static_cast<float>(intrinsics.cy),
    depth_scale, minimum_depth, maximum_depth,
    spatial_filter_enabled, minimum_consistent_neighbors,
    neighbor_depth_tolerance, neighbor_depth_tolerance_ratio, state.points_);
  if (cudaPeekAtLastError() != cudaSuccess) {
    return false;
  }

  points.resize(output_pixels);
  if (cudaMemcpyAsync(
      points.data(), state.points_, output_pixels * sizeof(PointXyzRgb),
      cudaMemcpyDeviceToHost, state.stream_) != cudaSuccess)
  {
    return false;
  }
  return cudaStreamSynchronize(state.stream_) == cudaSuccess;
}
}  // namespace mvs_camera_driver
