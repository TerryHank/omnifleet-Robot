"""Web controls for the onboard Nav2 Bag recorder."""

import asyncio
import os
from pathlib import Path
import shutil
import signal
import sys
import time
import uuid

from aiohttp import web


BAG_ROOT = Path.home() / 'omnifleet_data/recordings/bags/panel_bags'
FLEET_START = Path.home() / 'omnifleet_ws/src/system/omnifleet_fleet/start.sh'
NO_CACHE = {'Cache-Control': 'no-store'}
# Match the topics used by the onboard Nav2 Bag recorder on this single-cmd_vel vehicle.
BAG_TOPICS = (
    '/rslidar_points', '/rslidar_points_filtered', '/tf', '/tf_static', '/lidar_odometry/pose',
    '/plan', '/received_global_plan', '/transformed_global_plan', '/controller_server/local_plan',
    '/cmd_vel', '/lidar_odometry/nav_odom', '/local_costmap/costmap', '/global_costmap/costmap',
    '/diagnostics',
)


def valid_name(name):
    return bool(name and not name.startswith('.') and '/' not in name and '\\' not in name)


def active_recordings():
    root = BAG_ROOT.resolve()
    recordings = {}
    for process in Path('/proc').iterdir():
        if not process.name.isdecimal():
            continue
        try:
            args = list(map(os.fsdecode, (process / 'cmdline').read_bytes().rstrip(b'\0').split(b'\0')))
            for i, arg in enumerate(args[:-3]):
                if Path(arg).name != 'ros2' or args[i + 1:i + 4] != ['bag', 'record', '-o']:
                    continue
                if i + 4 < len(args):
                    location = Path(args[i + 4])
                    if location.is_absolute() and location.parent.resolve() == root and valid_name(location.name):
                        recordings[location.name] = int(process.name)
        except (OSError, ValueError):
            continue
    return recordings


def completed_bag(path):
    metadata = path / 'metadata.yaml'
    return (valid_name(path.name) and not path.is_symlink() and path.is_dir()
            and not metadata.is_symlink() and metadata.is_file())


def catalog():
    active = active_recordings()
    records = []
    if BAG_ROOT.is_dir():
        for path in BAG_ROOT.iterdir():
            if path.name in active or not completed_bag(path):
                continue
            try:
                records.append({
                    'name': path.name,
                    'date': path.stat().st_mtime,
                    'size': sum(item.stat().st_size for item in path.iterdir()
                                if not item.is_symlink() and item.is_file()),
                })
            except FileNotFoundError:
                continue
    records.sort(key=lambda bag: (bag['date'], bag['name']), reverse=True)
    return {'active': next(iter(active), None), 'bags': records}


def delete_completed(name):
    if not valid_name(name):
        raise web.HTTPBadRequest(text='Bag 名称无效')
    if name in active_recordings():
        raise web.HTTPConflict(text='正在录制，停止后才能删除')
    path = BAG_ROOT / name
    if not completed_bag(path):
        raise web.HTTPNotFound(text='未找到已完成的 Bag')
    shutil.rmtree(path)
    log_path = BAG_ROOT / f'{name}.record.log'
    if not log_path.is_symlink() and log_path.is_file():
        log_path.unlink(missing_ok=True)


async def start_recording():
    if await asyncio.to_thread(active_recordings):
        raise web.HTTPConflict(text='已有 Bag 正在录制')
    BAG_ROOT.mkdir(parents=True, exist_ok=True)
    name = time.strftime('motion_trace_%Y%m%d_%H%M%S_') + uuid.uuid4().hex[:6]
    bag = BAG_ROOT / name
    with bag.with_suffix('.record.log').open('xb') as log:
        process = await asyncio.create_subprocess_exec(
            '/bin/bash', str(FLEET_START), 'python', str(Path(__file__).resolve()), str(bag),
            stdout=log, stderr=asyncio.subprocess.STDOUT, start_new_session=True,
        )
    for _ in range(100):
        if process.returncode is not None:
            raise web.HTTPBadGateway(text='车端录包进程退出，请检查录制日志')
        if bag.is_dir() and name in await asyncio.to_thread(active_recordings):
            return name
        await asyncio.sleep(.2)
    if process.returncode is None:
        process.send_signal(signal.SIGINT)
    raise web.HTTPGatewayTimeout(text='录制启动超时，请刷新状态')


async def stop_recording():
    recordings = await asyncio.to_thread(active_recordings)
    if not recordings:
        raise web.HTTPConflict(text='当前没有正在录制的 Bag')
    name, pid = next(iter(recordings.items()))
    try:
        fd = os.pidfd_open(pid)
    except ProcessLookupError as error:
        raise web.HTTPConflict(text='录制进程已退出，请刷新列表') from error
    try:
        if (await asyncio.to_thread(active_recordings)).get(name) != pid:
            raise web.HTTPConflict(text='录制进程已变化，请刷新列表')
        try:
            signal.pidfd_send_signal(fd, signal.SIGINT)
        except ProcessLookupError as error:
            raise web.HTTPConflict(text='录制进程已退出，请刷新列表') from error
    finally:
        os.close(fd)
    for _ in range(100):
        if name not in await asyncio.to_thread(active_recordings):
            if not completed_bag(BAG_ROOT / name):
                raise web.HTTPBadGateway(text='录制已停止，但未生成完整的 Bag')
            return name
        await asyncio.sleep(.2)
    raise web.HTTPGatewayTimeout(text='正在等待 Bag 写盘结束，请刷新状态')


def register_bag_routes(app, same_origin):
    operations = asyncio.Lock()

    async def get_bags(_):
        return web.json_response(await asyncio.to_thread(catalog), headers=NO_CACHE)

    async def change_recording(request):
        if not same_origin(request):
            raise web.HTTPForbidden(text='请求必须来自本车网页')
        action = request.match_info['action']
        async with operations:
            name = await (start_recording() if action == 'start' else stop_recording())
        return web.json_response({'message': '正在录制' if action == 'start' else '录制已停止', 'name': name},
                                 headers=NO_CACHE)

    async def delete_bag(request):
        if not same_origin(request):
            raise web.HTTPForbidden(text='请求必须来自本车网页')
        async with operations:
            await asyncio.to_thread(delete_completed, request.match_info['name'])
        return web.json_response({'message': 'Bag 已删除'}, headers=NO_CACHE)

    app.router.add_get('/dispatch-api/bags', get_bags)
    app.router.add_post('/dispatch-api/bags/{action:start|stop}', change_recording)
    app.router.add_delete('/dispatch-api/bags/{name}', delete_bag)


if __name__ == '__main__':
    os.execvp('ros2', ['ros2', 'bag', 'record', '-o', sys.argv[1], *BAG_TOPICS])
