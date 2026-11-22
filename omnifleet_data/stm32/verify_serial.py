import re
import struct
import sys
import time
import serial

def crc8(data):
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0x8c if crc & 1 else 0)
    return crc

def frames(buf):
    i = 0
    while True:
        i = buf.find(b'\xaa\x55', i)
        if i < 0 or i + 5 > len(buf):
            return
        end = i + 5 + buf[i + 3]
        if end <= len(buf) and crc8(buf[i + 2:end - 1]) == buf[end - 1]:
            yield buf[i + 2], buf[i + 4:end - 1]
            i = end
        else:
            i += 1

port = serial.Serial(baudrate=115200, timeout=0.15, exclusive=True)
port.port = sys.argv[1]
port.dtr = False
port.rts = False
with port:
    data = port.read(2048)
    reports = [p for fn, p in frames(data) if fn == 0 and p.startswith(b'RRC\x01') and len(p) == 88]
    print(f"received_bytes={len(data)} valid_RRC_reports={len(reports)}")
    if len(reports) < 2:
        print(f"serial_prefix={data[:96].hex()}")
        sys.exit(2)
    payload = bytes([3, 9, 4]) + struct.pack('<ff', 0.0, 0.0)
    port.write(b'\xaa\x55' + payload + bytes([crc8(payload)]))
    reply = list(frames(port.read(2048)))
    assert any(fn == 0 and p == b'ROS\x04' for fn, p in reply), "No Ackermann command ACK"
    reports = [p for fn, p in reply if fn == 0 and p.startswith(b'RRC\x01') and len(p) == 88]
    assert reports, "No telemetry after zero command"
    targets = [struct.unpack_from('<f', reports[-1], 20 + 20*n)[0] for n in range(4)]
    print(f"ackermann_zero_ack=true motor_targets_rps={targets}")
    assert all(v == 0.0 for v in targets), "Nonzero motor target"

