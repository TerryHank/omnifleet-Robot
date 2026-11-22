import argparse
import signal
import struct
import subprocess
import sys
import time


UNIT = "omnifleet-t2-raw-pwm.service"
CHASSIS_SERVICE = "omnifleet-t2-chassis.service"
NAV_SERVICE = "omnifleet-t2-navigation.service"
SERIAL_DEVICE = "/dev/omnifleet_t2_stm32"
INSTALLED_COMMAND = "/usr/local/bin/omnifleet-t2-raw-pwm"
LEGACY_UNITS = (
    "omnifleet-t2-raw-pwm50-observe.service",
    "omnifleet-t2-equal-pwm50-observe.service",
    "omnifleet-t2-equal-pwm30-observe.service",
)


def percent_to_raw_count(percent):
    value = int(percent)
    if not -100 <= value <= 100:
        raise ValueError("PWM percent must be in [-100, 100]")
    return int(round(value * 3600 / 100.0))


def packet(function, payload):
    raw = bytes([0xFF, 0xFC, len(payload) + 3, function]) + payload
    return raw + bytes([sum(raw[2:]) & 0xFF])


def extract_frames(buffer):
    result = []
    while len(buffer) >= 5:
        index = buffer.find(b"\xff")
        if index < 0:
            buffer.clear()
            break
        del buffer[:index]
        total = buffer[2] + 2
        if total < 5 or total > 64:
            del buffer[0]
            continue
        if len(buffer) < total:
            break
        frame = bytes(buffer[:total])
        del buffer[:total]
        if (sum(frame[2:-1]) & 0xFF) == frame[-1]:
            result.append(frame)
    return result


def run(command, check=True, capture=False):
    return subprocess.run(
        command,
        check=check,
        text=True,
        capture_output=capture,
    )


def is_active(unit):
    return run(
        ["systemctl", "is-active", unit], check=False, capture=True
    ).stdout.strip() == "active"


def stop_unit(unit):
    run(["sudo", "-n", "systemctl", "stop", unit], check=False)


def hold(m1_percent, m2_percent):
    import serial

    running = True

    def request_stop(_signum, _frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    port = serial.Serial(SERIAL_DEVICE, 115200, timeout=0.005)
    buffer = bytearray()
    latest = None

    def poll():
        nonlocal latest
        data = port.read(port.in_waiting or 1)
        if data:
            buffer.extend(data)
        for frame in extract_frames(buffer):
            if frame[3] == 0x0D and len(frame) == 21:
                latest = struct.unpack("<iiii", frame[4:20])

    body_zero = packet(0x12, struct.pack("<Bhhh", 0, 0, 0, 0))
    motor_zero = packet(0x10, struct.pack("<bbbb", 0, 0, 0, 0))
    raw_command = packet(
        0x10, struct.pack("<bbbb", m1_percent, m2_percent, 0, 0)
    )
    try:
        for _ in range(20):
            port.write(body_zero)
            port.flush()
            poll()
            time.sleep(0.025)
        print(
            "RAW_PWM_START "
            f"M1={m1_percent}%({percent_to_raw_count(m1_percent)}) "
            f"M2={m2_percent}%({percent_to_raw_count(m2_percent)}) "
            "PID=OFF DEADZONE=OFF",
            flush=True,
        )
        next_send = time.monotonic()
        next_report = next_send + 1.0
        previous = latest
        while running:
            now = time.monotonic()
            if now >= next_send:
                port.write(raw_command)
                port.flush()
                next_send += 0.05
            poll()
            if now >= next_report:
                if latest is not None and previous is not None:
                    d1 = latest[0] - previous[0]
                    d2 = latest[1] - previous[1]
                    print(f"ENCODER_1S M1={d1:+d} M2={d2:+d}", flush=True)
                previous = latest
                next_report += 1.0
    finally:
        for _ in range(40):
            port.write(motor_zero)
            port.write(body_zero)
            port.flush()
            poll()
            time.sleep(0.025)
        port.close()
        print("RAW_PWM_STOP FINAL_ZERO_SENT", flush=True)


def start(m1_percent, m2_percent):
    percent_to_raw_count(m1_percent)
    percent_to_raw_count(m2_percent)
    if is_active(NAV_SERVICE):
        raise RuntimeError("Refusing raw PWM while navigation is active")
    for unit in (UNIT,) + LEGACY_UNITS:
        stop_unit(unit)
    run(["sudo", "-n", "systemctl", "stop", CHASSIS_SERVICE])
    try:
        run(
            [
                "sudo", "-n", "systemd-run",
                f"--unit={UNIT}",
                "--property=User=iecme",
                "--property=Group=iecme",
                "--property=Restart=no",
                "--property=TimeoutStopSec=5s",
                INSTALLED_COMMAND, "hold",
                str(m1_percent), str(m2_percent),
            ]
        )
        time.sleep(2.0)
        if not is_active(UNIT):
            raise RuntimeError("raw PWM unit failed to start")
    except Exception:
        stop_unit(UNIT)
        run(["sudo", "-n", "systemctl", "start", CHASSIS_SERVICE])
        raise
    status()


def stop():
    for unit in (UNIT,) + LEGACY_UNITS:
        stop_unit(unit)
    run(["sudo", "-n", "systemctl", "start", CHASSIS_SERVICE])
    print("RAW_PWM_STOPPED chassis_service=active")


def status():
    print(f"raw_pwm_unit={'active' if is_active(UNIT) else 'inactive'}")
    print(
        f"chassis_service={'active' if is_active(CHASSIS_SERVICE) else 'inactive'}"
    )
    run(
        ["journalctl", "-u", UNIT, "-n", "12", "--no-pager"],
        check=False,
    )


def main():
    parser = argparse.ArgumentParser(
        prog="omnifleet-t2-raw-pwm",
        description="NX-adjustable raw STM32 PWM diagnostic control",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("start", "set"):
        command = sub.add_parser(name)
        command.add_argument("m1", type=int)
        command.add_argument("m2", type=int)
    sub.add_parser("status")
    sub.add_parser("stop")
    hold_parser = sub.add_parser("hold", help=argparse.SUPPRESS)
    hold_parser.add_argument("m1", type=int)
    hold_parser.add_argument("m2", type=int)
    args = parser.parse_args()
    try:
        if args.command in ("start", "set"):
            start(args.m1, args.m2)
        elif args.command == "stop":
            stop()
        elif args.command == "status":
            status()
        else:
            hold(args.m1, args.m2)
    except (RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
