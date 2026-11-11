#!/usr/bin/env python3
# encoding: utf-8

import os
import re
import subprocess
import tempfile
import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Int16MultiArray, MultiArrayDimension, UInt8MultiArray, Int32, String


class SbusDebugNode(Node):
    def __init__(self):
        super().__init__('sbus_debug_node')
        self.declare_parameter('firmware_elf', '/home/iecme/driver_ws/src/robot_stm32/V3.5.1/build/rosmaster.elf')
        self.declare_parameter('symbol_name', 'sbus_data')
        self.declare_parameter('sbus_data_address', '0x20000368')
        self.declare_parameter('auto_symbol', True)
        self.declare_parameter('publish_rate_hz', 2.0)
        self.declare_parameter('st_flash', 'st-flash')
        self.declare_parameter('log_every_sample', True)
        self.declare_parameter('log_changes_only', False)
        self.declare_parameter('change_threshold', 10)

        self.firmware_elf = self.get_parameter('firmware_elf').value
        self.symbol_name = self.get_parameter('symbol_name').value
        self.sbus_data_address = self.get_parameter('sbus_data_address').value
        self.auto_symbol = bool(self.get_parameter('auto_symbol').value)
        self.st_flash = self.get_parameter('st_flash').value
        self.log_every_sample = bool(self.get_parameter('log_every_sample').value)
        self.log_changes_only = bool(self.get_parameter('log_changes_only').value)
        self.change_threshold = int(self.get_parameter('change_threshold').value)

        rate_hz = float(self.get_parameter('publish_rate_hz').value)
        if rate_hz <= 0.0:
            rate_hz = 2.0
        self.period = 1.0 / rate_hz

        self.raw_size = 25
        self.temp_file = os.path.join(tempfile.gettempdir(), f'sbus_debug_{os.getpid()}.bin')
        self.last_channels = None
        self.last_error_time = 0.0

        resolved = self.resolve_symbol_address()
        if resolved:
            self.sbus_data_address = resolved

        self.channels_pub = self.create_publisher(Int16MultiArray, '/sbus/channels', 10)
        self.raw_pub = self.create_publisher(UInt8MultiArray, '/sbus/raw', 10)
        self.flags_pub = self.create_publisher(Int32, '/sbus/flags', 10)
        self.debug_pub = self.create_publisher(String, '/sbus/debug', 10)
        self.timer = self.create_timer(self.period, self.poll_once)

        self.get_logger().info(
            f'SBUS debug node started: address={self.sbus_data_address}, rate={rate_hz:.2f} Hz, '
            f'topics=/sbus/channels /sbus/raw /sbus/flags /sbus/debug'
        )

    def resolve_symbol_address(self):
        if not self.auto_symbol:
            return None
        if not self.firmware_elf or not os.path.exists(self.firmware_elf):
            self.get_logger().warn(f'Firmware ELF not found, using parameter address: {self.firmware_elf}')
            return None
        try:
            proc = subprocess.run(
                ['arm-none-eabi-nm', '-n', self.firmware_elf],
                text=True,
                capture_output=True,
                timeout=3.0,
                check=False,
            )
        except Exception as exc:
            self.get_logger().warn(f'Failed to run arm-none-eabi-nm, using parameter address: {exc}')
            return None
        if proc.returncode != 0:
            self.get_logger().warn(f'arm-none-eabi-nm failed, using parameter address: {proc.stderr.strip()}')
            return None
        pattern = re.compile(r'^([0-9a-fA-F]+)\s+\w\s+' + re.escape(self.symbol_name) + r'$')
        for line in proc.stdout.splitlines():
            match = pattern.match(line.strip())
            if match:
                address = '0x' + match.group(1).lower()
                self.get_logger().info(f'Resolved {self.symbol_name} from ELF: {address}')
                return address
        self.get_logger().warn(f'Symbol {self.symbol_name} not found in ELF, using parameter address')
        return None

    @staticmethod
    def decode_sbus(raw):
        data = list(raw[:25])
        if len(data) < 25:
            raise ValueError(f'need 25 bytes, got {len(data)}')
        channels = [0] * 16
        channels[0] = ((data[1] | data[2] << 8) & 0x07FF)
        channels[1] = ((data[2] >> 3 | data[3] << 5) & 0x07FF)
        channels[2] = ((data[3] >> 6 | data[4] << 2 | data[5] << 10) & 0x07FF)
        channels[3] = ((data[5] >> 1 | data[6] << 7) & 0x07FF)
        channels[4] = ((data[6] >> 4 | data[7] << 4) & 0x07FF)
        channels[5] = ((data[7] >> 7 | data[8] << 1 | data[9] << 9) & 0x07FF)
        channels[6] = ((data[9] >> 2 | data[10] << 6) & 0x07FF)
        channels[7] = ((data[10] >> 5 | data[11] << 3) & 0x07FF)
        channels[8] = ((data[12] | data[13] << 8) & 0x07FF)
        channels[9] = ((data[13] >> 3 | data[14] << 5) & 0x07FF)
        channels[10] = ((data[14] >> 6 | data[15] << 2 | data[16] << 10) & 0x07FF)
        channels[11] = ((data[16] >> 1 | data[17] << 7) & 0x07FF)
        channels[12] = ((data[17] >> 4 | data[18] << 4) & 0x07FF)
        channels[13] = ((data[18] >> 7 | data[19] << 1 | data[20] << 9) & 0x07FF)
        channels[14] = ((data[20] >> 2 | data[21] << 6) & 0x07FF)
        channels[15] = ((data[21] >> 5 | data[22] << 3) & 0x07FF)
        flags = data[23]
        return channels, flags

    def read_raw_frame(self):
        proc = subprocess.run(
            [self.st_flash, '--hot-plug', 'read', self.temp_file, self.sbus_data_address, hex(self.raw_size)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=3.0,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.decode(errors='replace').strip())
        with open(self.temp_file, 'rb') as handle:
            return handle.read(self.raw_size)

    def poll_once(self):
        try:
            raw = self.read_raw_frame()
            channels, flags = self.decode_sbus(raw)
        except Exception as exc:
            now = time.monotonic()
            if now - self.last_error_time > 2.0:
                self.get_logger().error(f'SBUS read failed: {exc}')
                self.last_error_time = now
            return

        channels_msg = Int16MultiArray()
        dim = MultiArrayDimension()
        dim.label = 'sbus_channels'
        dim.size = 16
        dim.stride = 16
        channels_msg.layout.dim.append(dim)
        channels_msg.data = [int(v) for v in channels]
        self.channels_pub.publish(channels_msg)

        raw_msg = UInt8MultiArray()
        raw_msg.data = [int(v) for v in raw[:25]]
        self.raw_pub.publish(raw_msg)

        flags_msg = Int32()
        flags_msg.data = int(flags)
        self.flags_pub.publish(flags_msg)

        text = ' '.join(f'CH{i + 1}={value}' for i, value in enumerate(channels)) + f' FLAGS={flags}'
        debug_msg = String()
        debug_msg.data = text
        self.debug_pub.publish(debug_msg)

        should_log = self.log_every_sample
        if self.log_changes_only and self.last_channels is not None:
            should_log = any(abs(channels[i] - self.last_channels[i]) >= self.change_threshold for i in range(16))
        if should_log:
            self.get_logger().info(text)
        self.last_channels = channels


def main(args=None):
    rclpy.init(args=args)
    node = SbusDebugNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        try:
            node.destroy_node()
        except Exception:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

