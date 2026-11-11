#include "omnifleet_mola_grid/grid_core.hpp"
#include <message_filters/subscriber.h>
#include <message_filters/synchronizer.h>
#include <message_filters/sync_policies/approximate_time.h>
#include <mrpt/ros2bridge/point_cloud2.h>
#include <nav_msgs/msg/odometry.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <cmath>

class RegisteredCloudGrid : public rclcpp::Node
{
  using Cloud = sensor_msgs::msg::PointCloud2;
  using Odom = nav_msgs::msg::Odometry;
  using Policy = message_filters::sync_policies::ApproximateTime<Cloud, Odom>;
public:
  RegisteredCloudGrid() : Node("registered_cloud_grid")
  {
    const double resolution = declare_parameter("resolution", 0.1);
    const double max_range = declare_parameter("max_range", 25.0);
    z_min_ = declare_parameter("slice_z_min_from_sensor", -0.1);
    z_max_ = declare_parameter("slice_z_max_from_sensor", 1.35);
    max_cells_ = declare_parameter("max_grid_cells", 2000000);
    if (!std::isfinite(resolution) || resolution <= 0 || !std::isfinite(max_range) || max_range <= 0 ||
        !std::isfinite(z_min_) || !std::isfinite(z_max_) || z_min_ > z_max_ || max_cells_ <= 0)
      throw std::invalid_argument("invalid voxel/grid parameters");
    voxels_ = std::make_shared<mrpt::maps::CVoxelMap>(resolution);
    voxels_->insertionOptions.max_range = max_range;
    voxels_->insertionOptions.decimation = 4;
    pub_ = create_publisher<nav_msgs::msg::OccupancyGrid>("map", rclcpp::QoS(1).reliable().transient_local());
    clouds_.subscribe(this, "cloud_registered", rmw_qos_profile_sensor_data);
    odometry_.subscribe(this, "odom", rmw_qos_profile_sensor_data);
    sync_ = std::make_shared<message_filters::Synchronizer<Policy>>(Policy(10), clouds_, odometry_);
    sync_->setMaxIntervalDuration(rclcpp::Duration::from_seconds(0.05));
    sync_->registerCallback(std::bind(&RegisteredCloudGrid::observe, this, std::placeholders::_1, std::placeholders::_2));
  }
private:
  void observe(const Cloud::ConstSharedPtr& cloud, const Odom::ConstSharedPtr& odom)
  {
    const auto& position = odom->pose.pose.position;
    if (cloud->header.frame_id.empty() || cloud->header.frame_id != odom->header.frame_id ||
        !std::isfinite(position.x) || !std::isfinite(position.y) || !std::isfinite(position.z))
    {
      RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000, "Cloud and odometry must share a world frame and finite sensor origin");
      return;
    }
    try
    {
      if ((rclcpp::Time(cloud->header.stamp) - last_publish_).seconds() < 0.5) return;
      mrpt::maps::CSimplePointsMap input, finite;
      if (!mrpt::ros2bridge::fromROS(*cloud, input)) return;
      for (size_t i = 0; i < input.size(); ++i)
      {
        float x, y, z;
        input.getPointFast(i, x, y, z);
        if (std::isfinite(x) && std::isfinite(y) && std::isfinite(z)) finite.insertPointFast(x, y, z);
      }
      if (finite.size() == 0) return;
      voxels_->insertPointCloudAsRays(finite, {position.x, position.y, position.z});
      auto map = omnifleet_mola_grid::slice(voxels_, position.z + z_min_, position.z + z_max_, cloud->header, max_cells_);
      map.info.map_load_time = cloud->header.stamp;
      pub_->publish(map);
      last_publish_ = rclcpp::Time(cloud->header.stamp);
    }
    catch (const std::exception& error)
    {
      RCLCPP_ERROR_THROTTLE(get_logger(), *get_clock(), 5000, "%s", error.what());
    }
  }
  double z_min_, z_max_;
  int max_cells_;
  rclcpp::Time last_publish_{0, 0, RCL_ROS_TIME};
  mrpt::maps::CVoxelMap::Ptr voxels_;
  message_filters::Subscriber<Cloud> clouds_;
  message_filters::Subscriber<Odom> odometry_;
  std::shared_ptr<message_filters::Synchronizer<Policy>> sync_;
  rclcpp::Publisher<nav_msgs::msg::OccupancyGrid>::SharedPtr pub_;
};

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<RegisteredCloudGrid>());
  rclcpp::shutdown();
}
