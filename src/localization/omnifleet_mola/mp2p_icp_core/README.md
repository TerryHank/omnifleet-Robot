# mp2p_icp_core｜OmniFleet 工作区介绍

C++ libraries for multi primitive-to-primitive (MP2P) ICP algorithms and point cloud processing pipelines, plus headless CLI applications. No GUI/display dependencies; see mp2p_icp_viz for the GUI apps.

- 功能域：`localization`；源码：`/home/iecme/omnifleet_ws/src/localization/omnifleet_mola/mp2p_icp_core`。
- colcon 类型：`(ros.cmake)`。
- 状态（2026-11-06目录核对）：当前 install 下存在同名目录；不等于该组件正在运行或已完成实车验收。
- 所属域说明：[README.md](../../README.md)。

## 入口与目录

- [package.xml](package.xml)：包名称、描述与依赖声明。
- [CMakeLists.txt](CMakeLists.txt)：C++/资源的构建和安装定义。
- [scripts/](scripts)：可执行脚本。当前项：`formatter.sh`、`kitti-batch-convert.py`、`kitti-run-seq.py`、`viewSimilarityImages.m`。
- [tests/](tests)：测试。当前项：`CMakeLists.txt`、`test-georef-yaml.cpp`、`test-mp2p_FilterAbsoluteTimestamp.cpp`、`test-mp2p_FilterByExpression.cpp`、`test-mp2p_FilterByIntensity.cpp`、`test-mp2p_FilterByRange.cpp`、`test-mp2p_FilterByRing.cpp`、`test-mp2p_FilterClear.cpp`、`test-mp2p_FilterCurvature.cpp`、`test-mp2p_FilterDecimate.cpp`、`test-mp2p_FilterDecimateAdaptive.cpp`、`test-mp2p_FilterDecimateRangeAdaptive.cpp`、`test-mp2p_FilterDecimateVoxels.cpp`、`test-mp2p_FilterEdgesPlanes.cpp`、`test-mp2p_FilterFartherPointSampling.cpp`、`test-mp2p_FilterMerge_view.cpp`、`test-mp2p_FilterPlanePatches.cpp`、`test-mp2p_FilterPoleDetector.cpp`、`test-mp2p_FilterPolygon2D.cpp`、`test-mp2p_FilterRemovePointCloudField.cpp`、`test-mp2p_FilterRenameLayer.cpp`、`test-mp2p_FilterSOR.cpp`、`test-mp2p_FilterTransformPointCloud.cpp`、`test-mp2p_FilterVoxelSOR.cpp`、`test-mp2p_Filters.cpp`、`test-mp2p_LogRecord.cpp`、`test-mp2p_PairWeights.cpp`、`test-mp2p_Pairings.cpp`、`test-mp2p_PointCloudRobustRange.cpp`、`test-mp2p_WeightParameters.cpp`、`test-mp2p_censi3d_covariance.cpp`、`test-mp2p_class_factory.cpp`、`test-mp2p_cov2cov.cpp`、`test-mp2p_deskew.cpp`、`test-mp2p_deskew_empty_buffer.cpp`、`test-mp2p_error_terms_jacobians.cpp`、`test-mp2p_estimate_points_eigen.cpp`、`test-mp2p_generator.cpp`、`test-mp2p_generator_view_vector.cpp`、`test-mp2p_georef_yaml.cpp`、`test-mp2p_gicp_pipeline_benchmark.cpp`、`test-mp2p_gravity_prior.cpp`、`test-mp2p_icp_algos.cpp`、`test-mp2p_map_serialization.cpp`、`test-mp2p_matcher_knn_plane.cpp`、`test-mp2p_matcher_ndt_blend.cpp`、`test-mp2p_matcher_points_blend.cpp`、`test-mp2p_matcher_pt2ln.cpp`、`test-mp2p_matcher_pt2pl.cpp`、`test-mp2p_matcher_pt2pt.cpp`、`test-mp2p_matcher_pt2pt_parameterizable.cpp`、`test-mp2p_optimal_tf_algos.cpp`、`test-mp2p_optimize_cov2cov.cpp`、`test-mp2p_optimize_cov2cov_with_prior.cpp`、`test-mp2p_optimize_prior_referenced_kernel.cpp`、`test-mp2p_optimize_pt2ln.cpp`、`test-mp2p_optimize_pt2pl.cpp`、`test-mp2p_optimize_with_prior.cpp`、`test-mp2p_pipeline_from_yaml.cpp`、`test-mp2p_quality_reproject_ranges.cpp`、`test-mp2p_quality_voxels.cpp`、`test-mp2p_robust_kernel_scale.cpp`、`test-mp2p_viz_non_finite_points.cpp`、`test-sm2mm_georef.cpp`。

## 工作区内声明依赖

- [mola_common](../mola_common/README.omnifleet.md)
- [mola_imu_preintegration](../mola_imu_preintegration/README.omnifleet.md)

## 配置和数据边界

可维护的运行参数放本包所属 `config/`；已有兼容入口迁移时同步保存/加载路径。模型、录包、视频、地图等产物放 `/home/iecme/omnifleet_data`。未列出config目录表示清单未发现该目录，不凭空创建或修改配置。
