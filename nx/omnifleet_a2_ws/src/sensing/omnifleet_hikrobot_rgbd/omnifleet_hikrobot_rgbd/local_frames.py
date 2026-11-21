"""Single latest RGB/depth pair in Linux shared RAM; ROS carries notifications."""
import fcntl
from functools import lru_cache
import json
import mmap
import os
import struct
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


def read_native_mjpeg():
    """Read one coherent capture from the Gemini's atomic latest-frame slot."""
    try:
        packet = Path('/dev/shm/omnifleet-gemini-rgb1080.mjpeg').read_bytes()
    except FileNotFoundError:
        return None
    if len(packet) <= 8:
        return None
    return struct.unpack_from('<Q', packet)[0], memoryview(packet)[8:]


@lru_cache(maxsize=3)
def native_color_geometry(input_size=(1920, 1080), output_size=(1920, 1080)):
    """Use one rectified optical projection for inference, raw output and preview."""
    import cv2

    calibration = os.environ.get('OMNIFLEET_COLOR_CALIBRATION')
    if calibration:
        import yaml
        data = yaml.safe_load(Path(calibration).read_text())
        color = dict(width=data['image_width'],height=data['image_height'],
                     k=data['camera_matrix']['data'],d=data['distortion_coefficients']['data'],
                     distortion_model=data.get('distortion_model','rational_polynomial'))
    else:
        path = Path.home() / 'orbbec345lg-v2.10.6/rgb1080-calibration.json'
        color = json.loads(path.read_text())['color']
    native = (color['width'], color['height'])
    original = np.asarray(color['k']).reshape(3, 3)
    distortion = np.asarray(color['d'])
    rectified, _ = cv2.getOptimalNewCameraMatrix(
        original, distortion, native, 0, native, centerPrincipalPoint=True)

    def scaled(matrix, size):
        sx, sy = size[0] / native[0], size[1] / native[1]
        return np.array([[sx, 0., (sx - 1.) / 2.], [0., sy, (sy - 1.) / 2.], [0., 0., 1.]]) @ matrix

    output = scaled(rectified, output_size)
    maps = cv2.initUndistortRectifyMap(
        scaled(original, input_size), distortion, None, output, output_size, cv2.CV_16SC2)
    info = {**color, 'width': output_size[0], 'height': output_size[1],
            'd': [0.] * len(distortion), 'k': output.ravel().tolist(),
            'p': np.column_stack((output, np.zeros(3))).ravel().tolist()}
    return info, maps


@lru_cache(maxsize=1)
def _native_color_cuda_maps(size):
    import cv2

    _, maps = native_color_geometry(size, size)
    mx, my = cv2.convertMaps(*maps, cv2.CV_32FC1)
    gx, gy, source, target = (cv2.cuda_GpuMat() for _ in range(4))
    gx.upload(mx)
    gy.upload(my)
    return gx, gy, source, target


def rectify_native_color(image, output_size=None):
    import cv2

    input_size = (image.shape[1], image.shape[0])
    output_size = output_size or input_size
    if (input_size == output_size == (1920, 1080) and hasattr(cv2.cuda, 'remap')
            and cv2.cuda.getCudaEnabledDeviceCount() > 0):
        gx, gy, source, target = _native_color_cuda_maps(input_size)
        source.upload(image)
        return cv2.cuda.remap(source, gx, gy, cv2.INTER_LINEAR, dst=target).download()
    _, maps = native_color_geometry(input_size, output_size)
    return cv2.remap(image, *maps, interpolation=cv2.INTER_LINEAR)
