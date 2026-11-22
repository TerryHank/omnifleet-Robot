#include "preprocess.h"
#include <gtest/gtest.h>

TEST(AiryPreprocess, EmptyCloudDoesNotDereferenceFirstPoint)
{
  Preprocess processor;
  processor.set(false, ROBOSENSE, 0.3, 1);
  pcl::PointCloud<robosense_ros::Point> input;
  auto message = std::make_shared<sensor_msgs::msg::PointCloud2>();
  pcl::toROSMsg(input, *message);
  PointCloudXYZI::Ptr output(new PointCloudXYZI);
  processor.process(message, output);
  EXPECT_TRUE(output->empty());
}

TEST(AiryPreprocess, AppliesConfiguredBlindRadiusAndMillisecondOffsets)
{
  Preprocess processor;
  processor.set(false, ROBOSENSE, 0.3, 1);
  pcl::PointCloud<robosense_ros::Point> input;
  robosense_ros::Point near{}, far{};
  near.x=0.1; near.timestamp=100.0;
  far.x=2.0; far.timestamp=100.02;
  input.push_back(near); input.push_back(far);
  auto message = std::make_shared<sensor_msgs::msg::PointCloud2>();
  pcl::toROSMsg(input, *message);
  PointCloudXYZI::Ptr output(new PointCloudXYZI);
  processor.process(message, output);
  ASSERT_EQ(output->size(), 1u);
  EXPECT_NEAR(output->points.front().curvature, 20.0, 1e-4);
}
