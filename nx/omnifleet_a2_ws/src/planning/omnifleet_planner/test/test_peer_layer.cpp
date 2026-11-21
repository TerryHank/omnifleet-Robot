#include "omnifleet_planner/peer_layer.hpp"
#include <nav2_costmap_2d/layered_costmap.hpp>

class Probe : public omnifleet_planner::PeerLayer {
public:
  Probe() {peerPolicy();}
  unsigned char value(unsigned char v) {return interpretValue(v);}
  bool maximum() {return use_maximum_;}
  void noPeerMap() {
    map_received_ = map_received_in_update_bounds_ = current_ = false;
    clock_ = std::make_shared<rclcpp::Clock>(RCL_STEADY_TIME);
  }
  void setup(nav2_costmap_2d::LayeredCostmap & parent) {
    layered_costmap_ = &parent; enabled_ = true;
    global_frame_ = map_frame_ = "map";tf_ = &transforms_;
    map_received_in_update_bounds_ = true;
    resizeMap(8, 8, .5, -1., -1.);
    std::fill(getCharMap(),getCharMap()+64,nav2_costmap_2d::NO_INFORMATION);
  }
private:
  tf2_ros::Buffer transforms_{std::make_shared<rclcpp::Clock>(RCL_ROS_TIME)};
};

int main() {
  rclcpp::init(0,nullptr);
  using namespace nav2_costmap_2d;
  Probe layer;
  if (layer.value(255) != NO_INFORMATION) {return 1;}
  if (layer.value(100) != LETHAL_OBSTACLE) {return 2;}
  if (!layer.maximum()) {return 3;}
  LayeredCostmap rolling("map",true,false);
  auto & master=*rolling.getCostmap();
  master.resizeMap(4,4,.5,0.,0.);
  std::fill(master.getCharMap(),master.getCharMap()+16,FREE_SPACE);
  master.setCost(0,0,LETHAL_OBSTACLE);master.setCost(1,0,150);master.setCost(2,0,NO_INFORMATION);
  layer.setup(rolling);
  layer.setCost(3,3,LETHAL_OBSTACLE); // world (.75,.75), shifted peer-map origin.
  layer.updateCosts(master,0,0,4,4);
  if (master.getCost(3,3)!=FREE_SPACE) {return 4;}
  if (master.getCost(0,0)!=LETHAL_OBSTACLE || master.getCost(1,0)!=150) {return 5;}
  if (master.getCost(2,0)!=NO_INFORMATION) {return 6;}
  if (master.getCost(1,1)!=LETHAL_OBSTACLE) {return 7;}
  // A vanished peer must not leave a lethal cell behind after the master reset.
  layer.setCost(3,3,NO_INFORMATION);master.setCost(1,1,FREE_SPACE);
  layer.updateCosts(master,0,0,4,4);
  if (master.getCost(1,1)!=FREE_SPACE) {return 8;}
  // The same skip-unknown behavior already works in the non-rolling branch.
  LayeredCostmap global("map",false,true);
  global.getCostmap()->resizeMap(8,8,.5,-1.,-1.);
  std::fill(global.getCostmap()->getCharMap(),global.getCostmap()->getCharMap()+64,FREE_SPACE);
  layer.setup(global);layer.setCost(3,3,LETHAL_OBSTACLE);
  layer.updateCosts(*global.getCostmap(),0,0,8,8);
  if (global.getCostmap()->getCost(0,0)!=FREE_SPACE || global.getCostmap()->getCost(3,3)!=LETHAL_OBSTACLE) {return 9;}
  // An optional peer layer with no publisher must not block local planning.
  for (bool is_rolling : {false, true}) {
    LayeredCostmap empty_parent("map",is_rolling,false);
    empty_parent.getCostmap()->resizeMap(8,8,.5,-1.,-1.);
    auto absent = std::make_shared<Probe>();
    absent->setup(empty_parent);absent->noPeerMap();
    empty_parent.addPlugin(absent);
    double min_x=1.,min_y=2.,max_x=3.,max_y=4.;
    absent->updateBounds(0.,0.,0.,&min_x,&min_y,&max_x,&max_y);
    if (!empty_parent.isCurrent()) {return 10;}
    if (min_x!=1. || min_y!=2. || max_x!=3. || max_y!=4.) {return 11;}
    empty_parent.getCostmap()->setCost(2,2,LETHAL_OBSTACLE);
    absent->updateCosts(*empty_parent.getCostmap(),0,0,8,8);
    if (empty_parent.getCostmap()->getCost(2,2)!=LETHAL_OBSTACLE) {return 12;}
  }
  rclcpp::shutdown();return 0;
}
