#pragma once
#include <algorithm>
#include <atomic>
#include <chrono>
#include <nav2_costmap_2d/static_layer.hpp>

namespace omnifleet_planner {
class PeerLayer : public nav2_costmap_2d::StaticLayer {
public:
  void onInitialize() override {
    nav2_costmap_2d::StaticLayer::onInitialize();
    peerPolicy();
    auto node = node_.lock();
    map_sub_.reset();
    map_sub_ = node->create_subscription<nav_msgs::msg::OccupancyGrid>(
      map_topic_, rclcpp::QoS(1).transient_local().reliable(),
      [this](nav_msgs::msg::OccupancyGrid::SharedPtr message) {
        if (message->header.frame_id != global_frame_) {return;}
        last_receive_.store(tick());
        incomingMap(message);
      });
  }

  void updateBounds(double x, double y, double yaw, double * min_x,
    double * min_y, double * max_x, double * max_y) override {
    {
      std::lock_guard<nav2_costmap_2d::Costmap2D::mutex_t> lock(*getMutex());
      // No peer map is an empty optional contribution, not stale local terrain.
      if (!map_received_) {
        map_received_in_update_bounds_ = false;
        current_ = true;
        return;
      }
      if (map_received_ && tick() - last_receive_.load() > 2000000000LL) {
        std::fill(getCharMap(), getCharMap() + getSizeInCellsX()*getSizeInCellsY(),
          nav2_costmap_2d::NO_INFORMATION);
        x_ = y_ = 0; width_ = getSizeInCellsX(); height_ = getSizeInCellsY();
        has_updated_data_ = true;
      }
    }
    nav2_costmap_2d::StaticLayer::updateBounds(x, y, yaw, min_x, min_y, max_x, max_y);
  }

  void updateCosts(nav2_costmap_2d::Costmap2D & master, int min_i, int min_j,
    int max_i, int max_j) override {
    if (!layered_costmap_->isRolling()) {
      if (!map_received_in_update_bounds_) {return;}
      nav2_costmap_2d::StaticLayer::updateCosts(master, min_i, min_j, max_i, max_j);
      return;
    }
    std::lock_guard<nav2_costmap_2d::Costmap2D::mutex_t> lock(*getMutex());
    if (!enabled_ || !map_received_in_update_bounds_) {return;}
    // Peer maps use the costmap frame. Unknown means no peer contribution,
    // not unknown terrain; never overwrite sensor costs with that value.
    for (int j = min_j; j < max_j; ++j) {
      for (int i = min_i; i < max_i; ++i) {
        double wx, wy; unsigned int mx, my;
        master.mapToWorld(i, j, wx, wy);
        if (worldToMap(wx, wy, mx, my) &&
          getCost(mx, my) == nav2_costmap_2d::LETHAL_OBSTACLE)
        {
          master.setCost(i, j, nav2_costmap_2d::LETHAL_OBSTACLE);
        }
      }
    }
    current_ = true;
  }

protected:
  void peerPolicy() {
    track_unknown_space_ = true;
    use_maximum_ = true;
    unknown_cost_value_ = 255;
    lethal_threshold_ = 100;
    trinary_costmap_ = true;
    footprint_clearing_enabled_ = false;
  }

private:
  static int64_t tick() {
    return std::chrono::duration_cast<std::chrono::nanoseconds>(
      std::chrono::steady_clock::now().time_since_epoch()).count();
  }
  std::atomic<int64_t> last_receive_{0};
};
}
