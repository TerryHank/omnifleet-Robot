#pragma once

#include <mrpt/maps/CGenericPointsMap.h>
#include <mrpt/poses/CPose3D.h>

namespace mola
{
/** Own the filtered fields and transform them in-place; the input stays immutable. */
inline mrpt::maps::CGenericPointsMap::Ptr prepareNavigationCloud(
    const mrpt::maps::CPointsMap& input, const mrpt::poses::CPose3D& sensorPose,
    const mrpt::poses::CPose3D& mapPose)
{
  auto result = mrpt::maps::CGenericPointsMap::Create();
  result->registerPointFieldsFrom(input);
  result->reserve(input.size());
  auto context = result->prepareForInsertPointsFrom(input);
  const auto& xs = input.getPointsBufferRef_x();
  const auto& ys = input.getPointsBufferRef_y();
  const auto& zs = input.getPointsBufferRef_z();
  for (std::size_t i=0;i<input.size();++i) {
    const auto body = sensorPose.composePoint({xs[i],ys[i],zs[i]});
    if (std::abs(body.x)<.30 && std::abs(body.y)<.235 && body.z<.40) continue;
    result->insertPointFrom(i,context);
  }
  result->changeCoordinatesReference(mapPose);
  return result;
}
}  // namespace mola
