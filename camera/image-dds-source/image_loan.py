import ctypes as c
import os
from pathlib import Path

Callback = c.CFUNCTYPE(None, c.c_void_p, c.c_uint, c.c_uint64)
library = c.CDLL(str(Path(__file__).with_name('libimage_dds.so')))
library.image_open.argtypes = [c.c_uint, c.c_char_p, c.c_bool]
library.image_open.restype = c.c_void_p
library.image_publish.argtypes = [c.c_void_p,c.c_void_p,c.c_uint,c.c_uint64]
library.image_publish.restype = c.c_bool
library.image_take.argtypes = [c.c_void_p,Callback]
library.image_take.restype = c.c_int
library.image_close.argtypes = [c.c_void_p]
library.image_close.restype = None

class Images:
    def __init__(self, topic, publishing):
        self.handle = library.image_open(int(os.environ.get('ROS_DOMAIN_ID','0')),topic.encode(),publishing)
        if not self.handle:
            raise RuntimeError('Fast DDS image endpoint creation failed')

    def publish(self, address, size, stamp):
        return library.image_publish(self.handle,address,size,stamp)

    def take(self, callback):
        return library.image_take(self.handle,callback)

    def close(self):
        if self.handle:
            library.image_close(self.handle)
            self.handle = None
