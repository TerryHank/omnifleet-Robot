#include "gtest/gtest.h"
#include "omnifleet_planner/short_follow_plan.hpp"
TEST(ShortFollow,ExactShortForwardAndReverseTargets) {
 nav2_costmap_2d::Costmap2D map(200,200,.01,-1.,-1.,0);
 nav2_costmap_2d::Footprint body;for(auto v:{std::pair<double,double>{.27,.205},{.27,-.205},{-.27,-.205},{-.27,.205}}){geometry_msgs::msg::Point p;p.x=v.first;p.y=v.second;body.push_back(p);}
 geometry_msgs::msg::PoseStamped a,b;a.header.frame_id=b.header.frame_id="map";a.pose.orientation.w=b.pose.orientation.w=1.;
 for(double x:{.025,-.025}){b.pose.position.x=x;auto path=omnifleet_planner::shortKinematicPlan(&map,body,a,b,.4,.2,true,true);ASSERT_FALSE(path.poses.empty());EXPECT_DOUBLE_EQ(path.poses.back().pose.position.x,x);}
 auto captured_a=a,captured_b=b;
 captured_a.pose.position.x=-.14151566149691705;captured_a.pose.position.y=.025142169683019418;
 captured_a.pose.orientation=nav2_util::geometry_utils::orientationAroundZAxis(-.0598773546733975);
 captured_b.pose.position.x=-.16633682746119893;captured_b.pose.position.y=.02522729230908255;
 captured_b.pose.orientation=nav2_util::geometry_utils::orientationAroundZAxis(-.003429423600720849);
 EXPECT_FALSE(omnifleet_planner::shortKinematicPlan(&map,body,captured_a,captured_b,.4,.2,true,true).poses.empty());
 b.pose.position.x=.025;unsigned int mx,my;map.worldToMap(.1,.1,mx,my);map.setCost(mx,my,254);
 EXPECT_TRUE(omnifleet_planner::shortKinematicPlan(&map,body,a,b,.4,.2,true,true).poses.empty());
 map.setCost(mx,my,0);b.pose.position.x=.3;
 EXPECT_TRUE(omnifleet_planner::shortKinematicPlan(&map,body,a,b,.4,.2,true,true).poses.empty());
}
