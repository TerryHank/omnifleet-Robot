#!/usr/bin/env python3
"""Robot Wi-Fi management over the receiver LAN."""
import concurrent.futures
import copy
import json
import ssl
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import dbus

NM = 'org.freedesktop.NetworkManager'
ROOT = '/org/freedesktop/NetworkManager'
DEVICE = NM + '.Device'
WIRELESS = DEVICE + '.Wireless'
SETTINGS = NM + '.Settings.Connection'
ACTIVE = NM + '.Connection.Active'


class NetworkManager:
    def __init__(self):
        self.bus = dbus.SystemBus(private=True)
        self.manager = dbus.Interface(self.bus.get_object(NM, ROOT), NM)
        self.device = self.manager.GetDeviceByIpIface('wlP1p1s0')

    def properties(self, path, interface):
        obj = self.bus.get_object(NM, path)
        return dbus.Interface(obj, dbus.PROPERTIES_IFACE).GetAll(interface)

    def connection(self, path):
        return dbus.Interface(self.bus.get_object(NM, path), SETTINGS)

    def profiles(self):
        settings = dbus.Interface(self.bus.get_object(NM, ROOT + '/Settings'), NM + '.Settings')
        result = []
        for path in settings.ListConnections():
            values = self.connection(path).GetSettings()
            wireless = values.get('802-11-wireless', {})
            if 'ssid' in wireless:
                result.append((path, values))
        return result

    def status(self):
        device = self.properties(self.device, DEVICE)
        active = device.get('ActiveConnection', '/')
        result = {'ssid': '', 'addresses': [], 'state': int(device['State']), 'connected': False}
        if active != '/':
            settings = self.connection(self.properties(active, ACTIVE)['Connection']).GetSettings()
            result['ssid'] = bytes(settings.get('802-11-wireless', {}).get('ssid', [])).decode('utf-8', 'replace')
        ip = device.get('Ip4Config', '/')
        if ip != '/':
            result['addresses'] = [str(a['address']) for a in self.properties(ip, NM + '.IP4Config').get('AddressData', [])]
        result['connected'] = result['state'] == 100 and bool(result['addresses'])
        return result

    def networks(self):
        saved = {bytes(v['802-11-wireless']['ssid']).decode('utf-8', 'replace') for _, v in self.profiles()}
        wireless = dbus.Interface(self.bus.get_object(NM, self.device), WIRELESS)
        result = {}
        for path in wireless.GetAllAccessPoints():
            ap = self.properties(path, NM + '.AccessPoint')
            ssid = bytes(ap['Ssid']).decode('utf-8', 'replace')
            if not ssid:
                continue
            flags = int(ap['WpaFlags']) | int(ap['RsnFlags'])
            security = 'wpa-psk' if flags & 0x100 else 'sae' if flags & 0x400 else 'unsupported' if flags or int(ap['Flags']) & 1 else 'open'
            item = {'ssid': ssid, 'security': security, 'signal': int(ap['Strength']), 'saved': ssid in saved}
            key = (ssid, security)
            if key not in result or item['signal'] > result[key]['signal']:
                result[key] = item
        return sorted(result.values(), key=lambda item: (-item['signal'], item['ssid']))

    def scan(self):
        wireless = dbus.Interface(self.bus.get_object(NM, self.device), WIRELESS)
        previous = self.properties(self.device, WIRELESS)['LastScan']
        threshold = Path('/proc/net/rtl88x2ce/wlP1p1s0/scan_interval_thr')
        original = None
        try:
            if threshold.exists():
                original = threshold.read_text().split('=')[1].strip().split()[0]
                # RTL8822CE otherwise reports a completed scan using stale results under traffic.
                threshold.write_text('4294967295\n')
            try:
                wireless.RequestScan(dbus.Dictionary({}, signature='sv'))
            except dbus.DBusException:
                return {'networks': self.networks(), 'message': '显示最近扫描结果，可稍后刷新'}
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                if self.properties(self.device, WIRELESS)['LastScan'] > previous:
                    return {'networks': self.networks(), 'message': '扫描完成'}
                time.sleep(0.5)
            return {'networks': self.networks(), 'message': '显示最近扫描结果'}
        finally:
            if original is not None:
                threshold.write_text(original + '\n')

    def connect(self, request):
        ssid = request.get('ssid', '')
        password = request.get('password', '')
        security = request.get('security', 'wpa-psk')
        hidden = bool(request.get('hidden', False))
        if not isinstance(ssid, str) or not 1 <= len(ssid.encode('utf-8')) <= 32:
            raise ValueError('网络名称须为 1–32 个字节')
        if security not in ('open', 'wpa-psk', 'sae') or not isinstance(password, str):
            raise ValueError('首版支持开放网络、WPA/WPA2 个人热点和 WPA3 个人热点')
        current = self.status()
        if current['connected'] and current['ssid'] == ssid and not password:
            return {'status': current, 'message': '机器人已连接该网络'}
        matches = [(p, v) for p, v in self.profiles()
                   if bytes(v['802-11-wireless']['ssid']) == ssid.encode('utf-8')
                   and str(v.get('802-11-wireless-security', {}).get('key-mgmt', 'open')) == security]
        matches.sort(key=lambda item: int(item[1]['connection'].get('timestamp', 0)), reverse=True)
        if security != 'open' and not password and not matches:
            raise ValueError('请输入该 Wi-Fi 的密码')
        previous_active = self.properties(self.device, DEVICE).get('ActiveConnection', '/')
        previous = self.properties(previous_active, ACTIVE)['Connection'] if previous_active != '/' else '/'
        checkpoint = self.manager.CheckpointCreate(dbus.Array([self.device], signature='o'), dbus.UInt32(95), dbus.UInt32(2))
        candidate = None
        deadline = time.monotonic() + 90
        try:
            if matches and not password:
                activation = self.manager.ActivateConnection(matches[0][0], self.device, dbus.ObjectPath('/'))
            else:
                values = {
                    'connection': {'id': 'Robot Wi-Fi ' + ssid, 'uuid': str(uuid.uuid4()), 'type': '802-11-wireless', 'interface-name': 'wlP1p1s0', 'autoconnect': True},
                    '802-11-wireless': {'ssid': dbus.ByteArray(ssid.encode('utf-8')), 'mode': 'infrastructure', 'hidden': hidden},
                    'ipv4': {'method': 'auto'}, 'ipv6': {'method': 'auto'},
                }
                if security != 'open':
                    values['802-11-wireless']['security'] = '802-11-wireless-security'
                    values['802-11-wireless-security'] = {'key-mgmt': security, 'psk': password}
                settings = dbus.Dictionary({k: dbus.Dictionary(v, signature='sv') for k, v in values.items()}, signature='sa{sv}')
                candidate, activation, _ = self.manager.AddAndActivateConnection2(settings, self.device, dbus.ObjectPath('/'), dbus.Dictionary({'persist': 'memory'}, signature='sv'))
            while time.monotonic() < deadline:
                status = self.status()
                active = self.properties(self.device, DEVICE).get('ActiveConnection', '/')
                if status['connected'] and status['ssid'] == ssid and active == activation and int(self.properties(activation, ACTIVE)['State']) == 2:
                    if candidate:
                        self.connection(candidate).Save()
                    self.manager.CheckpointDestroy(checkpoint)
                    return {'status': status, 'message': '连接成功，已保存并启用自动重连'}
                if status['state'] == 120:
                    break
                time.sleep(1)
            raise RuntimeError('连接失败，请检查密码、热点信号和 DHCP 地址分配')
        except Exception:
            restored = False
            try:
                self.manager.CheckpointRollback(checkpoint)
            except dbus.DBusException:
                pass
            try:
                deadline = time.monotonic() + 20
                while time.monotonic() < deadline:
                    active = self.properties(self.device, DEVICE).get('ActiveConnection', '/')
                    if previous == '/':
                        restored = True
                        break
                    if active != '/' and self.properties(active, ACTIVE)['Connection'] == previous and self.status()['connected']:
                        restored = True
                        break
                    time.sleep(0.5)
            except dbus.DBusException:
                pass
            finally:
                try:
                    self.manager.CheckpointDestroy(checkpoint)
                except dbus.DBusException:
                    pass
                if candidate:
                    try:
                        self.connection(candidate).Delete()
                    except dbus.DBusException:
                        pass
            suffix = '，已恢复原网络' if restored else '，原网络尚未恢复，可再次选择已保存网络连接'
            raise RuntimeError('连接未成功，请检查密码与热点状态' + suffix) from None


class Operations:
    def __init__(self, factory=NetworkManager):
        self.factory = factory
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.lock = threading.Lock()
        self.jobs = {}
        self.active = None

    def start(self, action, request):
        with self.lock:
            if self.active and self.jobs[self.active]['state'] == 'running':
                raise ValueError('机器人正在处理网络操作，请等待完成')
            identifier = uuid.uuid4().hex
            self.jobs = {k: v for k, v in list(self.jobs.items())[-7:]}
            self.jobs[identifier] = {'id': identifier, 'state': 'running', 'message': '正在扫描' if action == 'scan' else '正在连接，失败时将恢复原网络'}
            self.active = identifier
        self.executor.submit(self.run, identifier, action, request)
        return self.get(identifier)

    def run(self, identifier, action, request):
        try:
            manager = self.factory()
            result = manager.scan() if action == 'scan' else manager.connect(request)
            job = {'id': identifier, 'state': 'succeeded', **result}
        except ValueError as error:
            job = {'id': identifier, 'state': 'failed', 'message': str(error)}
        except RuntimeError as error:
            job = {'id': identifier, 'state': 'failed', 'message': str(error)}
        except Exception:
            job = {'id': identifier, 'state': 'failed', 'message': '配网服务暂时不可用，请刷新状态后重试'}
        finally:
            request.clear()
        with self.lock:
            self.jobs[identifier] = job

    def get(self, identifier):
        with self.lock:
            if identifier not in self.jobs:
                raise ValueError('操作记录已过期，请刷新状态')
            return copy.deepcopy(self.jobs[identifier])


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, status, value):
        body = json.dumps(value, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        try:
            if self.path == '/wifi/status':
                result = NetworkManager().status()
                result['operation'] = self.server.operations.get(self.server.operations.active) if self.server.operations.active else None
            elif self.path.startswith('/wifi/operations/'):
                result = self.server.operations.get(self.path.rsplit('/', 1)[-1])
            else:
                self.respond(404, {'message': '接口不存在'})
                return
            self.respond(200, result)
        except ValueError as error:
            self.respond(400, {'message': str(error)})
        except Exception:
            self.respond(503, {'message': '无法读取机器人网络状态'})

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 8192:
                raise ValueError('请求内容无效')
            request = json.loads(self.rfile.read(length))
            if not isinstance(request, dict):
                raise ValueError('请求内容无效')
            if self.path not in ('/wifi/scan', '/wifi/connect'):
                self.respond(404, {'message': '接口不存在'})
                return
            self.respond(202, self.server.operations.start(self.path.rsplit('/', 1)[-1], request))
        except (ValueError, TypeError) as error:
            self.respond(400, {'message': str(error) if not isinstance(error, json.JSONDecodeError) else '请求内容无效'})


def main():
    directory = Path('/etc/omnifleet-wifi')
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(directory / 'tls.crt', directory / 'tls.key')
    server = ThreadingHTTPServer(('192.168.144.108', 8766), Handler)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    server.operations = Operations()
    server.serve_forever()


if __name__ == '__main__':
    main()
