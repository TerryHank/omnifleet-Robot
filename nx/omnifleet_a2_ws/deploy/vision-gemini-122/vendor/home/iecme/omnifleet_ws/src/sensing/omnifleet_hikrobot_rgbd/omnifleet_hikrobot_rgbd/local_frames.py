"""Single latest RGB/depth pair in Linux shared RAM; ROS carries notifications."""
import fcntl
import mmap
import os
from pathlib import Path
import numpy as np

HEADER_BYTES = 64


class LocalFrameWriter:
    def __init__(self, color_shape, depth_shape):
        self.path = Path(f'/dev/shm/omnifleet_rgbd_104_{os.getpid()}.frame')
        self.fd = os.open(self.path,os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600)
        size = HEADER_BYTES+int(np.prod(color_shape))+int(np.prod(depth_shape))*2
        os.ftruncate(self.fd,size)
        self.memory = mmap.mmap(self.fd,size)
        self.header = np.ndarray((8,),'<u8',buffer=self.memory)
        self.color = np.ndarray(color_shape,np.uint8,buffer=self.memory,offset=HEADER_BYTES)
        self.depth = np.ndarray(depth_shape,'<u2',buffer=self.memory,offset=HEADER_BYTES+self.color.nbytes)
        self.sequence = 0

    def write(self, color, depth, stamp, frame_number):
        fcntl.flock(self.fd,fcntl.LOCK_EX)
        try:
            np.copyto(self.color,color)
            np.copyto(self.depth,depth)
            self.sequence += 1
            self.header[:] = [self.sequence,stamp.sec,stamp.nanosec,color.shape[1],color.shape[0],
                              depth.shape[1],depth.shape[0],frame_number]
        finally:
            fcntl.flock(self.fd,fcntl.LOCK_UN)
        return dict(path=str(self.path),sequence=self.sequence)

    def close(self):
        self.header = self.color = self.depth = None
        self.memory.close()
        os.close(self.fd)
        self.path.unlink(missing_ok=True)


class LocalFrameReader:
    def __init__(self):
        self.path, self.fd, self.memory, self.sequence = None, None, None, 0

    def read(self, notification, exact=False):
        path = Path(notification['path']).resolve()
        if path.parent != Path('/dev/shm') or not path.name.startswith('omnifleet_rgbd_104_'):
            raise ValueError('Unexpected local camera frame path')
        if path != self.path:
            self.close()
            self.fd = os.open(path,os.O_RDONLY)
            self.memory = mmap.mmap(self.fd,0,access=mmap.ACCESS_READ)
            self.path, self.sequence = path, 0
        fcntl.flock(self.fd,fcntl.LOCK_SH)
        try:
            header = np.ndarray((8,),'<u8',buffer=self.memory).copy()
            sequence,sec,nanosec,cw,ch,dw,dh,frame_number = map(int,header)
            if exact and sequence != notification['sequence']:
                return None
            if sequence <= self.sequence:
                return None
            color = np.ndarray((ch,cw,3),np.uint8,buffer=self.memory,offset=HEADER_BYTES).copy()
            depth = np.ndarray((dh,dw),'<u2',buffer=self.memory,offset=HEADER_BYTES+color.nbytes).copy()
            self.sequence = sequence
            return color,depth,sec,nanosec,frame_number
        finally:
            fcntl.flock(self.fd,fcntl.LOCK_UN)

    def close(self):
        if self.memory is not None:
            self.memory.close()
            os.close(self.fd)
        self.path = self.fd = self.memory = None
