"""Select a complete stationary scan without changing registration acceptance."""
import numpy as np


def cloud_xyz(message):
    offsets = {field.name: field.offset for field in message.fields}
    dtype = np.dtype({'names': ['x', 'y', 'z'], 'formats': ['>f4' if message.is_bigendian else '<f4']*3,
                      'offsets': [offsets[k] for k in ('x', 'y', 'z')], 'itemsize': message.point_step})
    values = np.ndarray((message.height, message.width), dtype=dtype, buffer=message.data,
                        strides=(message.row_step, message.point_step))
    xyz = np.column_stack([values[k].reshape(-1) for k in ('x', 'y', 'z')]).astype(float)
    radius = np.linalg.norm(xyz[:, :2], axis=1)
    return xyz[np.isfinite(xyz).all(axis=1) & (radius > .5) & (radius < 18)
               & (xyz[:, 2] > -.8) & (xyz[:, 2] < 2.8)]


def scan_quality(message):
    xyz = cloud_xyz(message)
    return {'filtered_points': len(xyz),
            'voxels_8cm': len(np.unique(np.floor(xyz/.08).astype(int), axis=0)),
            'azimuth_10deg_bins': np.histogram(np.arctan2(xyz[:, 1], xyz[:, 0]),
                                             bins=np.linspace(-np.pi, np.pi, 37))[0].tolist()}
