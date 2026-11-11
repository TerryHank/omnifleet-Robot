"""Avoid CUDA busy waits competing with CPU vision/navigation on Jetson."""
import ctypes


def blocking_cuda_wait():
    runtime = ctypes.CDLL('/usr/local/cuda/lib64/libcudart.so')
    runtime.cudaSetDeviceFlags.argtypes = [ctypes.c_uint]
    runtime.cudaGetDeviceFlags.argtypes = [ctypes.POINTER(ctypes.c_uint)]
    result = runtime.cudaSetDeviceFlags(4)  # cudaDeviceScheduleBlockingSync
    flags = ctypes.c_uint()
    queried = runtime.cudaGetDeviceFlags(ctypes.byref(flags))
    return result == 0 and queried == 0 and flags.value & 7 == 4
