#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>

int main(int argc, char** argv)
{
  if (argc != 3) { std::cerr << "Usage: pcd_to_xyz input.pcd output.xyz\n"; return 2; }
  pcl::PointCloud<pcl::PointXYZ> cloud;
  if (pcl::io::loadPCDFile(argv[1], cloud) < 0) return 1;
  std::ofstream output(argv[2]);
  if (!output) return 1;
  output << std::setprecision(9);
  size_t count = 0;
  for (const auto& p : cloud) {
    if (!std::isfinite(p.x) || !std::isfinite(p.y) || !std::isfinite(p.z)) continue;
    output << p.x << ' ' << p.y << ' ' << p.z << '\n';
    ++count;
  }
  if (!output || count == 0) return 1;
  std::cout << "Exported " << count << " finite points\n";
}
