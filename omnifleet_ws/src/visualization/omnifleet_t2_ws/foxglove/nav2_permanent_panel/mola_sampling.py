"""Save the two startup sampling targets used by integrated MOLA."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time

RUNTIME_FILE = Path('/home/iecme/omnifleet_a2_ws/src/localization/omnifleet_mola/mola_state_estimation_simple/config/tracked-integrated-live-runtime.json')
KEYS = {'mola_map_points': 'MOLA_DECIMATED_POINTS_MAP',
        'mola_icp_points': 'MOLA_DECIMATED_POINTS_ICP'}


def values(path=None):
    data = json.loads((path or RUNTIME_FILE).read_text())
    return {key: {name: int(data[name])} for key, name in KEYS.items()}


def save(changes, backups, path=None):
    if not changes or any(key not in KEYS for key in changes):
        raise ValueError('MOLA 采样点数必须单独提交')
    for value in changes.values():
        if type(value) is not int or not 1 <= value <= 1000000:
            raise ValueError('采样目标点数必须是 1 到 1000000 之间的整数')
    target = (path or RUNTIME_FILE).resolve(strict=True)
    old = target.read_bytes()
    data = json.loads(old)
    data.update({KEYS[key]: str(value) for key, value in changes.items()})
    # Preserve the exact file on a no-op save, including its formatting.
    new = old if data == json.loads(old) else (json.dumps(data, indent=2, ensure_ascii=False) + '\n').encode()
    backup = None
    if new != old:
        backups.mkdir(parents=True, exist_ok=True)
        backup = backups / f'mola-runtime.{time.time_ns()}.json'
        backup.write_bytes(old)
        fd, name = tempfile.mkstemp(prefix='.mola-sampling-', dir=target.parent)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(new)
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(name, target.stat().st_mode & 0o777)
            if target.read_bytes() != old:
                raise OSError('运行配置已被其他操作修改，请重新读取后保存')
            os.replace(name, target)
        finally:
            if os.path.exists(name):
                os.unlink(name)
    if target.read_bytes() != new:
        raise OSError('采样配置写入后回读不一致')
    return {'path': str(target), 'backup': str(backup) if backup else None,
            'sha256': hashlib.sha256(new).hexdigest(), 'restart_required': True,
            'runtime_confirmed': False,
            'runtime': {'MOLA': '已永久保存；重启导航栈后生效，当前 MOLA 继续使用启动时的值'}}
