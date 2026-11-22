from collections import deque
from typing import Callable, Optional


class WonderEchoSerialParser:
    HEADER = b"\xAA\x55"
    FRAME_SIZE = 5
    TRAILER = 0xFB

    def __init__(self):
        self._buffer = bytearray()

    def feed(self, data: bytes):
        self._buffer.extend(data)
        events = []
        while True:
            start = self._buffer.find(self.HEADER)
            if start < 0:
                keep = self._buffer[-1:] if self._buffer[-1:] == b"\xAA" else b""
                self._buffer.clear()
                self._buffer.extend(keep)
                break
            if start:
                del self._buffer[:start]
            if len(self._buffer) < self.FRAME_SIZE:
                break
            if self._buffer[4] != self.TRAILER:
                del self._buffer[0]
                continue
            events.append((int(self._buffer[2]), int(self._buffer[3])))
            del self._buffer[:self.FRAME_SIZE]
        return events


class WonderEchoSerialDevice:
    def __init__(
        self,
        port: str = "/dev/wonderecho_flash",
        baudrate: int = 115200,
        serial_factory: Optional[Callable[..., object]] = None,
    ):
        if not str(port).strip():
            raise ValueError("serial port must not be empty")
        if not 1200 <= int(baudrate) <= 3_000_000:
            raise ValueError("serial baudrate must be in [1200, 3000000]")
        self.port = str(port)
        self.baudrate = int(baudrate)
        self._serial_factory = serial_factory
        self._serial = None
        self._parser = WonderEchoSerialParser()
        self._events = deque()

    @staticmethod
    def _default_serial_factory():
        import serial

        return serial.Serial

    def open(self) -> None:
        if self._serial is None:
            factory = self._serial_factory or self._default_serial_factory()
            self._serial = factory(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.0,
            )

    def read_event(self):
        self.open()
        if self._events:
            return self._events.popleft()
        waiting = int(getattr(self._serial, "in_waiting", 0))
        data = self._serial.read(waiting or 1)
        if data:
            self._events.extend(self._parser.feed(data))
        return self._events.popleft() if self._events else None

    def close(self) -> None:
        port = self._serial
        self._serial = None
        if port is not None and hasattr(port, "close"):
            port.close()


class WonderEchoDevice:
    def __init__(
        self,
        bus_number: int = 1,
        address: int = 0x34,
        result_register: int = 0x64,
        speak_register: int = 0x6E,
        bus_factory: Optional[Callable[[int], object]] = None,
    ):
        if int(bus_number) < 0:
            raise ValueError("I2C bus number must not be negative")
        if not 0x03 <= int(address) <= 0x77:
            raise ValueError("I2C address must be a 7-bit device address")
        for name, value in (
            ("result_register", result_register),
            ("speak_register", speak_register),
        ):
            if not 0 <= int(value) <= 0xFF:
                raise ValueError(f"{name} must fit in one byte")

        self.bus_number = int(bus_number)
        self.address = int(address)
        self.result_register = int(result_register)
        self.speak_register = int(speak_register)
        self._bus_factory = bus_factory
        self._bus = None

    @staticmethod
    def _default_bus_factory():
        try:
            import smbus

            return smbus.SMBus
        except ImportError:
            import smbus2

            return smbus2.SMBus

    def open(self) -> None:
        if self._bus is None:
            factory = self._bus_factory or self._default_bus_factory()
            self._bus = factory(self.bus_number)

    def read_command(self) -> int:
        self.open()
        values = self._bus.read_i2c_block_data(
            self.address, self.result_register, 1
        )
        if not values:
            raise OSError("WonderEcho returned an empty result")
        return int(values[0])

    def speak_command(self, command_id: int, phrase_type: int = 0x00) -> None:
        if not 0 <= int(command_id) <= 0xFF:
            raise ValueError("speech ID must fit in one byte")
        if int(phrase_type) not in (0x00, 0xFF):
            raise ValueError("phrase_type must be 0x00 or 0xFF")
        self.open()
        self._bus.write_i2c_block_data(
            self.address,
            self.speak_register,
            [int(phrase_type), int(command_id)],
        )

    def close(self) -> None:
        bus = self._bus
        self._bus = None
        if bus is not None and hasattr(bus, "close"):
            bus.close()
