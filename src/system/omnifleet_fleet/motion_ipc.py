"""Onboard handoff between the command arbiter and sole STM32 writer."""
import os
import socket
import struct
import time

from pathlib import Path


MOTION_PACKET = struct.Struct("!ddQQ")
MOTION_SOCKET = "/run/omnifleet-motion/selected.sock"


class MotionOutput:
    def __init__(self):
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._socket.setblocking(False)

    @staticmethod
    def available():
        return Path(MOTION_SOCKET).is_socket()

    def publish(self, command, issued):
        packet = MOTION_PACKET.pack(
            command.linear.x, command.angular.z, round(issued * 1e9), time.monotonic_ns()
        )
        try:
            self._socket.sendto(packet, MOTION_SOCKET)
        except (FileNotFoundError, ConnectionRefusedError, BlockingIOError):
            # The driver enforces source age even when a handoff is dropped.
            pass


class MotionInput:
    def __init__(self):
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._socket.setblocking(False)
        Path(MOTION_SOCKET).unlink(missing_ok=True)
        self._socket.bind(MOTION_SOCKET)
        os.chmod(MOTION_SOCKET, 0o600)
        self._selected = 0

    def latest(self):
        latest = None
        for _ in range(16):
            try:
                packet = self._socket.recv(MOTION_PACKET.size + 1)
            except BlockingIOError:
                break
            if len(packet) != MOTION_PACKET.size:
                continue
            vx, wz, issued, selected = MOTION_PACKET.unpack(packet)
            if 0 < issued <= selected <= time.monotonic_ns() and selected > self._selected:
                latest = vx, wz, issued
                self._selected = selected
        return latest

    def close(self):
        self._socket.close()
        Path(MOTION_SOCKET).unlink(missing_ok=True)
