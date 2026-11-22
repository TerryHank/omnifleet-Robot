#include <gtest/gtest.h>
#include <mola_yaml/yaml_helpers.h>
#include <mp2p_icp_filters/FilterDeskew.h>
#include <mp2p_icp_filters/FilterDecimateAdaptive.h>
#include <mrpt/maps/CGenericPointsMap.h>

TEST(SingleDeskew, ProductionPipelineUsesFullRangeInputOnce)
{
  const auto config = mola::load_yaml_file(SINGLE_DESKEW_PIPELINE);
  ASSERT_FALSE(config.has("observations_navigation_deskew_pass"));
  const auto& filters = config["observations_deskew_pass"];
  ASSERT_EQ(filters.asSequence().size(), 1u);
  EXPECT_EQ(filters(0)["class_name"].as<std::string>(), "mp2p_icp_filters::FilterDeskew");
  EXPECT_EQ(filters(0)["params"]["input_pointcloud_layer"].as<std::string>(), "raw");
  EXPECT_EQ(filters(0)["params"]["output_pointcloud_layer"].as<std::string>(), "deskewed");
}

TEST(SingleDeskew, NavigationGeometryFieldsAndOwnershipArePreserved)
{
  auto raw = mrpt::maps::CGenericPointsMap::Create();
  raw->registerField_float("t");
  raw->registerField_float("intensity");
  raw->registerField_uint16("ring");
  raw->resize(300);
  for (std::size_t i = 0; i < raw->size(); ++i) {
    // Include both near returns and distant points formerly excluded from localization.
    raw->setPointFast(i, i == 0 ? .1f : static_cast<float>(i), .2f, .3f);
    raw->setPointField_float(i, "t", static_cast<float>(i) * .0003f);
    raw->setPointField_float(i, "intensity", static_cast<float>(i));
    raw->setPointField_uint16(i, "ring", i % 32);
  }
  const auto originalX = raw->getPointsBufferRef_x();
  mp2p_icp::metric_map_t legacy, shared;
  legacy.layers["raw"] = raw;
  shared.layers["raw"] = raw;
  auto configure = [](auto& filter, const std::string& output) {
    filter.input_pointcloud_layer = "raw";
    filter.output_pointcloud_layer = output;
    filter.method = mp2p_icp_filters::MotionCompensationMethod::Linear;
    filter.twist = mrpt::math::TTwist3D{.8, 0., 0., 0., 0., .2};
  };
  mp2p_icp_filters::FilterDeskew oldNavigation, unified;
  configure(oldNavigation, "nav_deskewed");
  configure(unified, "deskewed");
  oldNavigation.filter(legacy);
  unified.filter(shared);
  const auto expected = std::dynamic_pointer_cast<mrpt::maps::CGenericPointsMap>(legacy.layers.at("nav_deskewed"));
  const auto result = std::dynamic_pointer_cast<mrpt::maps::CGenericPointsMap>(shared.layers.at("deskewed"));
  ASSERT_TRUE(expected);
  ASSERT_TRUE(result);
  ASSERT_EQ(result->size(), raw->size());
  EXPECT_EQ(result->getPointsBufferRef_x(), expected->getPointsBufferRef_x());
  EXPECT_EQ(result->getPointsBufferRef_y(), expected->getPointsBufferRef_y());
  EXPECT_EQ(result->getPointsBufferRef_z(), expected->getPointsBufferRef_z());
  EXPECT_EQ(result->float_fields(), expected->float_fields());
  EXPECT_EQ(result->uint16_fields(), expected->uint16_fields());
  const auto xBefore = result->getPointsBufferRef_x();
  const auto fieldsBefore = result->float_fields();
  mp2p_icp_filters::FilterDecimateAdaptive decimate;
  decimate.params.input_pointcloud_layer = "deskewed";
  decimate.params.outputs.push_back({"decimated_for_map", 30, 0});
  decimate.filter(shared);
  EXPECT_EQ(shared.layers.at("deskewed"), result);
  EXPECT_EQ(result->getPointsBufferRef_x(), xBefore);
  EXPECT_EQ(result->float_fields(), fieldsBefore);
  EXPECT_EQ(raw->getPointsBufferRef_x(), originalX);
}
