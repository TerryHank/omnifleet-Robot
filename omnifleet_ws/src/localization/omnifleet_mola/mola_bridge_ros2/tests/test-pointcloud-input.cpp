#ifdef NDEBUG
#undef NDEBUG
#endif
#include "PointCloudInput.h"
#include <cassert>
#include <chrono>
#include <cstring>
#include <iostream>
#include <limits>

sensor_msgs::msg::PointCloud2 validCloud()
{
  sensor_msgs::msg::PointCloud2 cloud;
  cloud.header.stamp.sec = 100;
  cloud.width = 100000;
  cloud.height = 1;
  cloud.point_step = 12;
  cloud.row_step = cloud.width * cloud.point_step;
  cloud.data.resize(cloud.row_step);
  for (unsigned i = 0; i < 3; ++i)
  {
    sensor_msgs::msg::PointField field;
    field.name = std::array<const char*, 3>{"x", "y", "z"}[i];
    field.offset = i * 4;
    field.datatype = 7;
    field.count = 1;
    cloud.fields.push_back(field);
  }
  return cloud;
}

int main()
{
  auto cloud = validCloud();
  double last = -std::numeric_limits<double>::infinity();
  assert(mola::pointCloudInputError(cloud, 100.1, 300, last) == nullptr);
  assert(last == 100);
  assert(std::strcmp(mola::pointCloudInputError(cloud, 100.1, 300, last), "duplicate_or_out_of_order") == 0);
  cloud.header.stamp.sec = 99;
  assert(std::strcmp(mola::pointCloudInputError(cloud, 99.1, 300, last), "duplicate_or_out_of_order") == 0);
  cloud.header.stamp.sec = 101;
  assert(std::strcmp(mola::pointCloudInputError(cloud, 101.31, 300, last), "late") == 0);
  assert(last == 100);
  const auto original = cloud;
  for (int damage = 0; damage < 8; ++damage)
  {
    cloud = original;
    if (damage == 0) cloud.data.pop_back();
    if (damage == 1) cloud.row_step--;
    if (damage == 2) cloud.width = 0;
    if (damage == 3) cloud.fields.pop_back();
    if (damage == 4) cloud.fields[0].offset = cloud.point_step;
    if (damage == 5) cloud.fields[0].datatype = 99;
    if (damage == 6) cloud.fields[0].count = 0xffffffffU;
    if (damage == 7) cloud.header.stamp.nanosec = 1000000000U;
    assert(mola::pointCloudInputError(cloud, 101.1, 300, last));
    assert(last == 100);
  }
  cloud = original;
  assert(mola::pointCloudInputError(cloud, 101.1, 300, last) == nullptr);
  const auto start = std::chrono::steady_clock::now();
  for (int i = 0; i < 100000; ++i)
  {
    last = 100;
    assert(mola::pointCloudInputError(cloud, 101.1, 300, last) == nullptr);
  }
  std::cout << "PointCloud2 input cases passed; mean header-check us="
            << std::chrono::duration<double, std::micro>(std::chrono::steady_clock::now()-start).count()/100000
            << '\n';
}
