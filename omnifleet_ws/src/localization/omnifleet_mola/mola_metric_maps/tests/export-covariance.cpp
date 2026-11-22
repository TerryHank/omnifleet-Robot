#include <mola_metric_maps/KeyframePointCloudMap.h>
#include <mrpt/maps/CGenericPointsMap.h>
#include <mrpt/obs/CObservationPointCloud.h>
#include <cmath>
#include <fstream>
#include <iomanip>

int main(int argc, char** argv)
{
  if (argc != 2) { return 2; }
  const auto cloud = mrpt::maps::CGenericPointsMap::Create();
  for (int x = 0; x < 80; ++x) {
    for (int y = 0; y < 40; ++y) {
      cloud->insertPoint(x * .05f, y * .05f, .02f * std::sin(x * .2f));
    }
  }
  for (int index = 0; index < 10; ++index) {
    cloud->insertPoint(20.f + index * 10.f, 20.f, 20.f);
  }
  const auto observation = mrpt::obs::CObservationPointCloud::Create();
  observation->pointcloud = cloud;
  mola::KeyframePointCloudMap global;
  mola::KeyframePointCloudMap local;
  global.creationOptions.use_view_direction_filter = false;
  global.creationOptions.k_correspondences_for_cov = 30;
  local.creationOptions.k_correspondences_for_cov = 30;
  global.insertObservation(*observation);
  local.insertObservation(*observation);
  global.icp_get_prepared_as_global(mrpt::poses::CPose3D::Identity());
  mp2p_icp::MatchedPointWithCovList pairs;
  global.nn_search_cov2cov(local, mrpt::poses::CPose3D::Identity(), 1.f, pairs);
  std::ofstream output(argv[1]);
  output << std::setprecision(9);
  for (const auto& pair : pairs) {
    output << pair.local_idx << ',' << pair.global_idx;
    for (int row = 0; row < 3; ++row) {
      for (int column = 0; column < 3; ++column) {
        output << ',' << pair.cov_inv(row, column);
      }
    }
    output << '\n';
  }
  return pairs.size() == cloud->size() && output.good() ? 0 : 1;
}
