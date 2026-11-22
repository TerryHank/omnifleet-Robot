#include "omnifleet_planner/normalize_path.hpp"
#include "nav2_mppi_controller/tools/utils.hpp"
#include <nlohmann/json.hpp>
#include <fstream>
#include <iostream>
#include <stdexcept>

void check(bool value, const char * message) {
  if (!value) {throw std::runtime_error(message);}
  std::cout << "PASS " << message << std::endl;
}

int main(int argc, char ** argv) {
  nav_msgs::msg::Path raw;
  raw.header.frame_id = "map";
  for (double x : {0., 1., 1., 0., -1.}) {
    geometry_msgs::msg::PoseStamped p;
    p.pose.position.x=x;p.pose.orientation.w=1.;raw.poses.push_back(p);
  }
  raw.poses[2].pose.orientation.z=.5;raw.poses[2].pose.orientation.w=std::sqrt(.75);
  raw.poses.back().pose.orientation.z=.25;
  check(mppi::utils::findFirstPathInversion(raw)==raw.poses.size(),"duplicate junction reproduces missed cusp in native MPPI");
  auto clean=omnifleet_planner::normalizePathJunctions(raw);
  check(clean.poses.size()==4 && mppi::utils::findFirstPathInversion(clean)==2,"native MPPI detects cusp after normalization");
  check(clean.header==raw.header && clean.poses.back()==raw.poses.back(),"frame and exact final goal are preserved");
  check(clean.poses[1]==raw.poses[2],"junction keeps outgoing heading");
  check(omnifleet_planner::normalizePathJunctions(clean)==clean,"normalization is idempotent");
  check(omnifleet_planner::normalizePathJunctions(nav_msgs::msg::Path{}).poses.empty(),"empty plan stays empty");
  nav_msgs::msg::Path repeated;repeated.poses={raw.poses[1],raw.poses[2]};
  check(omnifleet_planner::normalizePathJunctions(repeated).poses.back()==repeated.poses.back(),"coincident final goal retains final orientation");
  if (argc>1) {
    nlohmann::json plans;std::ifstream(argv[1])>>plans;
    size_t reproduced=0,fixed=0;
    for (const auto & points : plans) {
      nav_msgs::msg::Path path;
      for (const auto & point : points) {
        geometry_msgs::msg::PoseStamped p;p.pose.position.x=point[0];p.pose.position.y=point[1];p.pose.orientation.w=1.;path.poses.push_back(p);
      }
      reproduced+=mppi::utils::findFirstPathInversion(path)==path.poses.size();
      auto normalized=omnifleet_planner::normalizePathJunctions(path);
      fixed+=mppi::utils::findFirstPathInversion(normalized)<normalized.poses.size();
      check(normalized.poses.back()==path.poses.back(),"recorded plan final pose unchanged");
    }
    check(reproduced==plans.size() && fixed==plans.size(),"all recorded missed cusps now detected by native MPPI");
    std::cout<<"Recorded plans: "<<plans.size()<<std::endl;
  }
}
