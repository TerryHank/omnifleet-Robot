#include <libobsensor/ObSensor.hpp>
#include <libobsensor/hpp/Utils.hpp>
#include <cmath>
#include <cstddef>
#include <limits>

// Batched ABI for NumPy/ctypes. All camera parameters are the existing ROS
// calibration; SDK input/output XYZ uses millimetres, ROS uses metres.
extern "C" int omnifleet_orbbec_project(
    const float *pixels, std::size_t count, const double *kd, const double *kr,
    const double *rotation, const double *translation, const double *distortion,
    int depth_width, int depth_height, int rgb_width, int rgb_height, float *output) {
  try {
    OBCalibrationParam calibration{};
    calibration.intrinsics[OB_SENSOR_DEPTH] = {
        float(kd[0]),float(kd[4]),float(kd[2]),float(kd[5]),
        int16_t(depth_width),int16_t(depth_height)};
    calibration.intrinsics[OB_SENSOR_COLOR] = {
        float(kr[0]),float(kr[4]),float(kr[2]),float(kr[5]),
        int16_t(rgb_width),int16_t(rgb_height)};
    calibration.distortion[OB_SENSOR_COLOR] = {
        float(distortion[0]),float(distortion[1]),float(distortion[4]),
        float(distortion[5]),float(distortion[6]),float(distortion[7]),
        float(distortion[2]),float(distortion[3])};
    auto &extrinsic = calibration.extrinsics[OB_SENSOR_DEPTH][OB_SENSOR_COLOR];
    for (int i=0;i<9;++i) extrinsic.rot[i]=float(rotation[i]);
    for (int i=0;i<3;++i) extrinsic.trans[i]=float(translation[i]*1000.);
    auto &identity = calibration.extrinsics[OB_SENSOR_COLOR][OB_SENSOR_COLOR];
    identity.rot[0]=identity.rot[4]=identity.rot[8]=1.f;
    bool distorted=false;
    for (int i=0;i<8;++i) distorted=distorted || distortion[i]!=0.;
    const float nan=std::numeric_limits<float>::quiet_NaN();
    for (std::size_t i=0;i<count;++i) {
      float *result=output+5*i;
      for (int j=0;j<5;++j) result[j]=nan;
      const OBPoint2f pixel{pixels[3*i],pixels[3*i+1]};
      const float depth=pixels[3*i+2];
      if (!(depth>0) || depth>=65535) continue;
      OBPoint3f xyz{};OBPoint2f rgb{};
      if (!ob::CoordinateTransformHelper::calibration2dTo3d(
              calibration,pixel,depth,OB_SENSOR_DEPTH,OB_SENSOR_COLOR,&xyz)) continue;
      // Raw distorted RGB is projected in one native OpenCV batch by the caller.
      // Do not repeat the SDK depth unprojection just to produce unused ideal UV.
      if (!distorted && !ob::CoordinateTransformHelper::calibration3dTo2d(
              calibration,xyz,OB_SENSOR_COLOR,OB_SENSOR_COLOR,&rgb)) continue;
      result[0]=xyz.x*.001f;result[1]=xyz.y*.001f;result[2]=xyz.z*.001f;
      result[3]=rgb.x;result[4]=rgb.y;
    }
    return 0;
  } catch (...) { return -1; }
}
