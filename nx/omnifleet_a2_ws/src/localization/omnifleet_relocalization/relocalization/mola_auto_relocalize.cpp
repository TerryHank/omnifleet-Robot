#include <mola_relocalization/relocalization.h>
#include <mola_metric_maps/HashedVoxelPointCloud.h>
#include <mp2p_icp/metricmap.h>
#include <mrpt/maps/CSimplePointsMap.h>
#include <mrpt/obs/CObservationPointCloud.h>
#include <mrpt/obs/CSensoryFrame.h>
#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <string>

int main(int argc,char** argv){
  if(argc<4){std::cerr<<"usage: mola_auto_relocalize MAP.mm SCAN.pcd OUT.json [resolution_xy] [resolution_deg]\n";return 2;}
  const double res=argc>4?std::stod(argv[4]):0.35, deg=argc>5?std::stod(argv[5]):15.0;
  mp2p_icp::metric_map_t map; std::string error;
  if(!map.load_from_file(argv[1],error)){std::cerr<<error<<"\n";return 3;}
  auto cloud=mrpt::maps::CSimplePointsMap::Create(); pcl::PointCloud<pcl::PointXYZ> scan;
  if(pcl::io::loadPCDFile(argv[2],scan)!=0){std::cerr<<"cannot load scan\n";return 4;}
  // A single live scan can contain 80k+ points.  Relocalization is a
  // startup gate, so keep enough structure for matching while bounding the
  // CPU cost before MOLA/Nav2 are allowed to start.
  for(size_t i=0;i<scan.points.size();i+=10){const auto&p=scan.points[i]; if(std::isfinite(p.x)&&std::isfinite(p.y)&&std::isfinite(p.z)) cloud->insertPoint(p.x,p.y,p.z);}
  auto obs=mrpt::obs::CObservationPointCloud::Create(); obs->pointcloud=cloud; mrpt::obs::CSensoryFrame sf; sf.insert(obs);
  auto hv=map.layer<mola::HashedVoxelPointCloud>("localmap");
  hv->likelihoodOptions.decimation=20;
  hv->likelihoodOptions.max_corr_distance=1.5;
  hv->likelihoodOptions.sigma_dist=0.2;
  auto bb=hv->boundingBox();
  mola::RelocalizationLikelihood_SE2::Input in; in.reference_map=map; in.observations=sf;
  in.corner_min={bb.min.x,bb.min.y,-M_PI}; in.corner_max={bb.max.x,bb.max.y,M_PI}; in.resolution_xy=res; in.resolution_phi=deg*M_PI/180.0;
  auto out=mola::RelocalizationLikelihood_SE2::run(in); auto candidates=mola::find_best_poses_se2(out.likelihood_grid,.90);
  std::ofstream f(argv[3]); f<<std::setprecision(12)<<"{\"success\":"<<(!candidates.empty()?"true":"false")<<",\"time_s\":"<<out.time_cost<<",\"candidates\":"<<candidates.size();
  if(!candidates.empty()){auto it=candidates.rbegin();auto p=it->second;f<<",\"x\":"<<p.x<<",\"y\":"<<p.y<<",\"yaw\":"<<p.phi<<",\"score\":"<<it->first; if(candidates.size()>1){auto second=std::prev(it);f<<",\"second_score\":"<<second->first;} }
  f<<"}\n"; std::cout<<f.rdbuf(); return candidates.empty()?5:0;
}
