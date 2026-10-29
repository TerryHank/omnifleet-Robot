import struct

import numpy as np
from sensor_msgs.msg import PointCloud2, PointField

from omnifleet_rmf_adapter.cloud_quality import cloud_xyz, scan_quality


def message(rows, padding=0):
    width=len(rows[0]);payload=bytearray()
    for row in rows:
        for xyz in row:payload.extend(struct.pack('<fff',*xyz))
        payload.extend(b'\xff'*padding)
    return PointCloud2(height=len(rows),width=width,
        fields=[PointField(name=k,offset=i*4,datatype=PointField.FLOAT32,count=1) for i,k in enumerate(('x','y','z'))],
        point_step=12,row_step=width*12+padding,data=bytes(payload))


def test_organized_rows_with_padding_keep_real_geometry_only():
    cloud=message([[(1.,0.,0.),(2.,0.,0.)],[(3.,0.,0.),(float('nan'),0.,0.)]],8)
    np.testing.assert_equal(cloud_xyz(cloud),[[1.,0.,0.],[2.,0.,0.],[3.,0.,0.]])


def test_complete_scan_scores_above_missing_sector_frame():
    points=[(3.*np.cos(a),3.*np.sin(a),0.) for a in np.linspace(-np.pi,np.pi,360,endpoint=False)]
    complete=message([points]);missing=message([points[:140]+[(0.,0.,0.)]*40+points[180:]])
    assert scan_quality(complete)['voxels_8cm']>scan_quality(missing)['voxels_8cm']
    assert min(scan_quality(complete)['azimuth_10deg_bins'])>0
    assert min(scan_quality(missing)['azimuth_10deg_bins'])==0
