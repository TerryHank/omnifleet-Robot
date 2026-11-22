import threading
from types import SimpleNamespace as NS
import numpy as np
import pytest
from omnifleet_hikrobot_rgbd.local_frames import LocalFrameReader, LocalFrameWriter


def test_local_frame_latest_pair_timestamp_and_no_duplicate():
    writer=LocalFrameWriter((3,4,3),(2,2));reader=LocalFrameReader()
    try:
        first=writer.write(np.full((3,4,3),1,np.uint8),np.full((2,2),1001,np.uint16),NS(sec=8,nanosec=10),11)
        writer.write(np.full((3,4,3),2,np.uint8),np.full((2,2),1002,np.uint16),NS(sec=8,nanosec=20),12)
        assert reader.read(first,exact=True) is None
        color,depth,sec,nanosec,number=reader.read(first)
        assert (sec,nanosec,number)==(8,20,12)
        assert np.all(color==2) and np.all(depth==1002)
        assert reader.read(first) is None
        writer.write(np.zeros((3,4,3),np.uint8),np.zeros((2,2),np.uint16),NS(sec=9,nanosec=0),13)
        assert np.all(color==2) and np.all(depth==1002)  # owned reader snapshots
    finally:
        reader.close();writer.close()
    assert not writer.path.exists()


def test_concurrent_pairs_never_mix_rgb_and_depth_frames():
    writer=LocalFrameWriter((32,48,3),(16,24));reader=LocalFrameReader()
    notification={'path':str(writer.path)}
    ready=threading.Event()
    def produce():
        for i in range(1,151):
            writer.write(np.full((32,48,3),i,np.uint8),np.full((16,24),1000+i,np.uint16),NS(sec=1,nanosec=i),i)
            ready.set()
    thread=threading.Thread(target=produce);thread.start();ready.wait(2)
    try:
        while thread.is_alive():
            pair=reader.read(notification)
            if pair is not None:
                color,depth,sec,nanosec,number=pair
                assert sec==1 and nanosec==number
                assert np.all(color==number) and np.all(depth==1000+number)
        thread.join()
    finally:
        thread.join();reader.close();writer.close()


def test_reader_rejects_paths_outside_camera_shared_ram():
    with pytest.raises(ValueError):LocalFrameReader().read({'path':'/etc/passwd'})
