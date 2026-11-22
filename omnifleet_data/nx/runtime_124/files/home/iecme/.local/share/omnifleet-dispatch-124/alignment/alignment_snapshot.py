"""Export current MOLA registration geometry without changing localization."""
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading

import numpy as np
import rclpy
from mola_msgs.srv import MapSave
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.serialization import serialize_message
from sensor_msgs.msg import PointCloud2, PointField
from std_srvs.srv import Trigger


class AlignmentSnapshot(Node):
    def __init__(self):
        super().__init__('omnifleet_alignment_snapshot')
        self.map_save = self.create_client(MapSave, '/map_save')
        self.capture_group = MutuallyExclusiveCallbackGroup()
        self.create_service(Trigger, '/fleet/alignment_map_snapshot', self.capture,
                            callback_group=self.capture_group)

    def capture(self, request, response):
        release = Path(os.environ['OMNIFLEET_MOLA_RELEASE'])
        try:
            if not self.map_save.wait_for_service(timeout_sec=1.0):
                raise ValueError('MOLA 地图保存服务不可用')
            with tempfile.TemporaryDirectory(prefix='omnifleet-map-') as temporary:
                folder = Path(temporary)
                future = self.map_save.call_async(MapSave.Request(map_path=str(folder / 'current')))
                done = threading.Event()
                future.add_done_callback(lambda _: done.set())
                if not done.wait(15.0):
                    self.map_save.remove_pending_request(future)
                    raise TimeoutError('MOLA 当前地图导出超时')
                result = future.result()
                if not result.success:
                    raise ValueError(result.error_message)
                library_path = ':'.join(str(release / directory) for directory in
                                        ('full-arm64-install/lib', 'runtime-deps', 'ros-core-lib'))
                command = [str(Path(__file__).with_name('export-keyframes')),
                           str(release / 'full-arm64-install/lib/libmola_metric_maps.so'),
                           str(folder / 'current.mm'), str(folder / 'map')]
                features = subprocess.run(command, env={**os.environ, 'LD_LIBRARY_PATH': library_path,
                                          'LD_PRELOAD': ''}, capture_output=True, text=True, timeout=25.0)
                if features.returncode:
                    raise ValueError(features.stderr.strip() or f'MOLA 地图解析失败 {features.returncode}')
                layer = folder / 'map_localmap.xyz'
                if not layer.exists():
                    raise ValueError(f'MOLA localmap 点层不可用 {features.stdout.strip()}')
                xyz = np.fromfile(layer, dtype='<f4').reshape(-1, 3)
            xyz = xyz[np.isfinite(xyz).all(axis=1)]
            if not len(xyz):
                raise ValueError('当前 MOLA 地图点层为空')
            voxel_m = 0.16
            _, inverse = np.unique(np.floor(xyz / voxel_m).astype(np.int64), axis=0, return_inverse=True)
            counts = np.bincount(inverse)
            points = np.column_stack([np.bincount(inverse, weights=xyz[:, axis]) / counts
                                      for axis in range(3)]).astype('<f4')
            fields = [PointField(name=name, offset=4 * index, datatype=PointField.FLOAT32, count=1)
                      for index, name in enumerate(('x', 'y', 'z'))]
            cloud = PointCloud2(height=1, width=len(points), fields=fields, point_step=12,
                                row_step=12 * len(points), data=points.tobytes(), is_dense=True)
            cloud.header.frame_id = 'map'
            cloud.header.stamp = self.get_clock().now().to_msg()
            response.message = json.dumps({
                'kind': 'current_mola_keyframes', 'points': len(points), 'voxel_m': voxel_m,
                'cloud_cdr_base64': base64.b64encode(serialize_message(cloud)).decode('ascii'),
            })
            response.success = True
        except (OSError, ValueError, TimeoutError, subprocess.SubprocessError) as error:
            response.message = str(error)
            self.get_logger().warning(response.message)
        return response


if __name__ == '__main__':
    rclpy.init()
    node = AlignmentSnapshot()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()

