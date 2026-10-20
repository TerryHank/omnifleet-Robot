#!/usr/bin/env bash
set -euo pipefail
root=/home/iecme/omnifleet_ws/src/system/omnifleet_fleet/relocalization
mkdir -p "$root"
export LD_LIBRARY_PATH=/home/iecme/omnifleet_ws/install/mola_relocalization/lib:/home/iecme/omnifleet_ws/install/mola_metric_maps/lib:/home/iecme/omnifleet_ws/install/mola_pose_list/lib:/home/iecme/omnifleet_ws/install/mola_imu_preintegration/lib:/home/iecme/omnifleet_ws/install/mp2p_icp_core/lib:/home/iecme/omnifleet_ws/install/mrpt/lib:${LD_LIBRARY_PATH:-}
inc="-I/usr/include/eigen3 -I/home/iecme/omnifleet_ws/install/mola_relocalization/include -I/home/iecme/omnifleet_ws/install/mola_metric_maps/include -I/home/iecme/omnifleet_ws/install/mola_pose_list/include -I/home/iecme/omnifleet_ws/install/mp2p_icp_core/include -I/usr/include/pcl-1.12 -I/home/iecme/omnifleet_ws/install/mrpt/include"
for d in /home/iecme/omnifleet_ws/install/mrpt/include/mrpt/*/include; do inc="$inc -I$d"; done
g++ -w -std=c++17 -O2 $inc /home/iecme/omnifleet_ws/src/system/omnifleet_fleet/relocalization/mola_auto_relocalize.cpp \
  -L/home/iecme/omnifleet_ws/install/mola_relocalization/lib -L/home/iecme/omnifleet_ws/install/mola_metric_maps/lib \
  -L/home/iecme/omnifleet_ws/install/mola_pose_list/lib -L/home/iecme/omnifleet_ws/install/mola_imu_preintegration/lib \
  -L/home/iecme/omnifleet_ws/install/mp2p_icp_core/lib -L/home/iecme/omnifleet_ws/install/mrpt/lib \
  -Wl,-rpath,/home/iecme/omnifleet_ws/install/mola_relocalization/lib:/home/iecme/omnifleet_ws/install/mola_metric_maps/lib:/home/iecme/omnifleet_ws/install/mola_pose_list/lib:/home/iecme/omnifleet_ws/install/mola_imu_preintegration/lib:/home/iecme/omnifleet_ws/install/mp2p_icp_core/lib:/home/iecme/omnifleet_ws/install/mrpt/lib \
  -Wl,--no-as-needed -lmola_relocalization -lmola_metric_maps -lmola_pose_list -lmola_imu_preintegration \
  -lmp2p_icp_map -lmp2p_icp -lmp2p_icp_common -lmrpt-maps -lmrpt-obs -lmrpt-serialization -lmrpt-io -lmrpt-poses -lmrpt-math -lmrpt-rtti -lmrpt-system -lmrpt-containers -lmrpt-core \
  -lpcl_io -lpcl_common -o "$root/mola_auto_relocalize"
