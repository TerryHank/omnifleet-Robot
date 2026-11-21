"""Compress only the single-vehicle Web point clouds, with bounded delivery."""

import asyncio
import ctypes
import json
import struct
import time

from aiohttp import WSMsgType


TOPICS = frozenset((
    '/visualization/web/deskewed_points',
    '/visualization/web/slam_points_below_1m',
    '/visualization/web/local_obstacle_points',
))
CLOUD_OPCODE = 0x7A
MESSAGE_DATA = 1
HEADER_SIZE = 13
MAX_CLOUD_BYTES = 2 * 1024 * 1024
MAX_QUEUE_AGE = 2.0
CLOUD_PERIOD = 1.0

_zstd = ctypes.CDLL('libzstd.so.1')
_zstd.ZSTD_compressBound.argtypes = (ctypes.c_size_t,)
_zstd.ZSTD_compressBound.restype = ctypes.c_size_t
_zstd.ZSTD_compress.argtypes = (
    ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
)
_zstd.ZSTD_compress.restype = ctypes.c_size_t
_zstd.ZSTD_isError.argtypes = (ctypes.c_size_t,)
_zstd.ZSTD_isError.restype = ctypes.c_uint


def compress(payload):
    capacity = _zstd.ZSTD_compressBound(len(payload))
    output = ctypes.create_string_buffer(capacity)
    size = _zstd.ZSTD_compress(output, capacity, payload, len(payload), 1)
    if _zstd.ZSTD_isError(size):
        raise RuntimeError('Zstd point-cloud compression failed')
    return output.raw[:size]


def json_packet(text):
    try:
        packet = json.loads(text)
    except ValueError:
        return {}
    return packet if isinstance(packet, dict) else {}


class CloudConnection:
    def __init__(self, browser, robot):
        self.browser = browser
        self.robot = robot
        self.channels = set()
        self.subscriptions = set()
        self.latest = {}
        self.next_send = {}
        self.waiting_for = None
        self.sequence = 0
        self.wakeup = asyncio.Event()

    async def browser_to_robot(self):
        async for message in self.browser:
            if message.type == WSMsgType.TEXT:
                packet = json_packet(message.data)
                operation = packet.get('op')
                if operation == 'webCloudAck':
                    if packet.get('seq') == self.waiting_for:
                        self.waiting_for = None
                        self.wakeup.set()
                    continue
                if operation == 'subscribe':
                    for entry in packet['subscriptions']:
                        if entry['channelId'] in self.channels:
                            self.subscriptions.add(entry['id'])
                elif operation == 'unsubscribe':
                    for subscription in packet['subscriptionIds']:
                        self.subscriptions.discard(subscription)
                        self.latest.pop(subscription, None)
                        self.next_send.pop(subscription, None)
                await self.robot.send_str(message.data)
            elif message.type == WSMsgType.BINARY:
                await self.robot.send_bytes(message.data)

    async def robot_to_browser(self):
        async for message in self.robot:
            if message.type == WSMsgType.TEXT:
                packet = json_packet(message.data)
                if packet.get('op') == 'advertise':
                    for channel in packet['channels']:
                        if channel['topic'] in TOPICS and channel['schemaName'] == 'sensor_msgs/msg/PointCloud2':
                            self.channels.add(channel['id'])
                elif packet.get('op') == 'unadvertise':
                    self.channels.difference_update(packet['channelIds'])
                await self.browser.send_str(message.data)
            elif message.type == WSMsgType.BINARY:
                frame = message.data
                if len(frame) >= HEADER_SIZE and frame[0] == MESSAGE_DATA:
                    subscription = struct.unpack_from('<I', frame, 1)[0]
                    if subscription in self.subscriptions:
                        if len(frame) - HEADER_SIZE <= MAX_CLOUD_BYTES:
                            self.latest[subscription] = (time.monotonic(), frame)
                            self.wakeup.set()
                        continue
                await self.browser.send_bytes(frame)

    async def send_clouds(self):
        while True:
            if self.waiting_for is not None or not self.latest:
                await self.wakeup.wait()
                self.wakeup.clear()
                continue
            now = time.monotonic()
            subscription = next((key for key in self.latest if self.next_send.get(key, 0) <= now), None)
            if subscription is None:
                delay = min(self.next_send[key] for key in self.latest) - now
                self.wakeup.clear()
                try:
                    await asyncio.wait_for(self.wakeup.wait(), delay)
                except asyncio.TimeoutError:
                    pass
                continue
            arrived, frame = self.latest.pop(subscription)
            if now - arrived > MAX_QUEUE_AGE:
                continue
            encoded = await asyncio.to_thread(compress, frame[HEADER_SIZE:])
            if subscription not in self.subscriptions or subscription in self.latest:
                continue
            now = time.monotonic()
            if now - arrived > MAX_QUEUE_AGE:
                continue
            self.sequence = (self.sequence + 1) & 0xFFFFFFFF
            self.waiting_for = self.sequence
            self.next_send[subscription] = now + CLOUD_PERIOD
            header = bytes((CLOUD_OPCODE,)) + frame[1:HEADER_SIZE]
            metadata = struct.pack('<II', len(frame) - HEADER_SIZE, self.sequence)
            await self.browser.send_bytes(header + metadata + encoded)


def cloud_relays(browser, robot):
    connection = CloudConnection(browser, robot)
    return connection.browser_to_robot(), connection.robot_to_browser(), connection.send_clouds()
