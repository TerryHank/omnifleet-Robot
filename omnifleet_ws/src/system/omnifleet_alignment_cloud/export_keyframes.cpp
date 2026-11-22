#include <mp2p_icp/metricmap.h>
#include <mrpt/maps/CSimplePointsMap.h>
#include <mrpt/system/os.h>
#include <fstream>
#include <iostream>

int main(int argc,char** argv) {
  if(argc!=4)return 2;
  std::string error;
  if(!mrpt::system::loadPluginModules(argv[1],error)){std::cerr<<error;return 3;}
  mp2p_icp::metric_map_t map;
  if(!map.load_from_file(argv[2]))return 4;
  for(const auto& [name,layer]:map.layers){
    const auto* points=layer->getAsSimplePointsMap();
    std::cout<<name<<" type="<<layer->GetRuntimeClass()->className<<" points="<<(points?points->size():0)<<std::endl;
    if(!points)continue;
    std::ofstream out(std::string(argv[3])+"_"+name+".xyz",std::ios::binary);
    for(size_t i=0;i<points->size();++i){float xyz[3];points->getPointFast(i,xyz[0],xyz[1],xyz[2]);out.write(reinterpret_cast<char*>(xyz),sizeof(xyz));}
  }
}
