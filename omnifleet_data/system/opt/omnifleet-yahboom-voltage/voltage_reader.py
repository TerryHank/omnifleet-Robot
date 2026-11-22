#!/usr/bin/env python3
"""Read battery voltage from the Yahboom serial telemetry frame."""
REPORT_HEADER = b'\xff\xfb'
PORT = '/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0'


def read_reports(buffer):
    """Consume complete, checksummed frames and return battery volts."""
    while len(buffer) >= 5:
        index = buffer.find(REPORT_HEADER)
        if index < 0:
            del buffer[:-1]
            return
        del buffer[:index]
        if len(buffer) < 5:
            return
        size = buffer[2] + 2
        if not 5 <= size <= 64:
            del buffer[0]
            continue
        if len(buffer) < size:
            return
        frame = buffer[:size]
        if sum(frame[2:-1]) & 255 != frame[-1]:
            del buffer[0]
            continue
        del buffer[:size]
        if frame[3] == 0x0a and size == 12 and frame[10]:
            yield frame[10] / 10.0


def main():
    import rclpy
    from rclpy.executors import ExternalShutdownException
    import serial
    from std_msgs.msg import Float32, String

    rclpy.init()
    node = rclpy.create_node('yahboom_battery_voltage')
    voltage = node.create_publisher(Float32, '/voltage', 10)
    display = node.create_publisher(String, '/voltage/display', 10)
    buffer = bytearray()
    port = None

    def sample():
        nonlocal port
        try:
            if port is None:
                port = serial.Serial(
                    port=None, baudrate=115200, timeout=0, exclusive=True,
                )
                port.dtr = False
                port.rts = False
                port.port = PORT
                port.open()
                buffer.clear()
            buffer.extend(port.read(min(port.in_waiting, 4096)))
            reports = list(read_reports(buffer))
            if reports:
                value = reports[-1]
                voltage.publish(Float32(data=value))
                display.publish(String(data=f'{value:.1f} V'))
        except (serial.SerialException, OSError) as error:
            if port is not None:
                port.close()
                port = None
            node.get_logger().warning(str(error), throttle_duration_sec=10.)

    node.create_timer(.5, sample)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if port is not None:
            port.close()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
