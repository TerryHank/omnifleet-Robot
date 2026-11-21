"""Serve the onboard Foxglove dispatch layout and its same-origin endpoints."""

import asyncio
import gzip
import hashlib
import json
import mimetypes
import os
import stat
import tempfile
from pathlib import Path
import re

from aiohttp import ClientError, ClientSession, ClientTimeout, WSMsgType, web

from bag_routes import register_bag_routes
from single_cloud_proxy import cloud_relays
import slam_control


DIRECTORY = Path(__file__).resolve().parent
FOXGLOVE_SITE = Path('/opt/foxglove-studio-cn-122/site')
CONTROL_API = 'http://127.0.0.1:8081'
SINGLE_CONTROL_API = 'http://127.0.0.1:8781'
BRIDGE = 'ws://127.0.0.1:8768/'
SINGLE_BRIDGE = 'ws://127.0.0.1:8765/'
PROTOCOL = 'foxglove.sdk.v1'
STUDIO_OVERRIDE = DIRECTORY / 'foxglove-124'
GZIP_CACHE = DIRECTORY.parent / 'data' / 'web-gzip'
STUDIO_DIRS = (STUDIO_OVERRIDE, FOXGLOVE_SITE)
STARTUP_ENTRY = 'main.3baca1086ee5c90fe565.js'
STARTUP_CHUNKS = (
    '4656.965768ca7ed4ef6c8186.js',
    '3771.ec2d9a01d892f92a4612.js',
    '1362.5850e72d9de05d80fe9b.js',
    '4838.4144fe77b2db1994c140.js?v=waypoint-menu',
)

# Run before Foxglove hydrates its persisted workspace, including older tabs.
CLOSE_LEFT_SIDEBAR = """<script>
(() => {
  try{
    const key="fox.workspace";
    let workspace;
    try{workspace=JSON.parse(localStorage.getItem(key));}catch{}
    if(!workspace?.state || typeof workspace.state!=="object")workspace={version:1,state:{}};
    const state=workspace.state;
    if(workspace.version===0){
      state.leftSidebarOpen=false;
    }else{
      const sidebars=state.sidebars??{};
      state.sidebars={right:{open:false},...sidebars,
        left:{item:"panel-settings",...sidebars.left,open:false}};
    }
    localStorage.setItem(key,JSON.stringify(workspace));
  }catch{
    // Workspace storage may be unavailable in a restricted browsing session.
  }
})();
</script>"""


def startup_preloads(bundle_url):
    if bundle_url.split('?',1)[0] != '/studio-assets/' + STARTUP_ENTRY:
        return ''
    return ''.join(
        f'<link rel="preload" as="script" href="/studio-assets/{name}"'
        + (' fetchpriority="low">' if index >= 2 else '>')
        for index, name in enumerate(STARTUP_CHUNKS)
    )


def prepare_compressed_assets():
    """Build gzip variants once so serving scripts does not compete with navigation."""
    variants = {}
    for source in (*STUDIO_DIRS, DIRECTORY):
        for path in source.iterdir():
            if not path.is_file() or path.suffix not in ('.js', '.css', '.json', '.svg'):
                continue
            stat = path.stat()
            if stat.st_size < 1024:
                continue
            cache = GZIP_CACHE / source.name / (path.name + '.gz')
            try:
                if not cache.is_file() or cache.stat().st_mtime_ns != stat.st_mtime_ns:
                    cache.parent.mkdir(parents=True, exist_ok=True)
                    temporary = cache.with_suffix('.tmp')
                    temporary.write_bytes(gzip.compress(path.read_bytes(), compresslevel=3, mtime=0))
                    os.utime(temporary, ns=(stat.st_atime_ns, stat.st_mtime_ns))
                    temporary.replace(cache)
                variants[path.resolve()] = (stat.st_mtime_ns, stat.st_size, cache)
            except OSError as error:
                print(f'Could not precompress {path.name}: {error}', flush=True)
    return variants


def accepts_gzip(request):
    for entry in request.headers.get('Accept-Encoding', '').lower().split(','):
        name, _, parameter = entry.strip().partition(';')
        if name.strip() == 'gzip':
            try:
                return not parameter or float(parameter.strip().removeprefix('q=')) > 0
            except ValueError:
                return False
    return False


def same_origin(request):
    return request.headers.get('Origin') == f'{request.scheme}://{request.host}'


async def api(request):
    return await forward_json(request, CONTROL_API + '/' + request.match_info['endpoint'])


async def single_control_api(request):
    return await forward_json(request, SINGLE_CONTROL_API + request.path)


async def forward_json(request, target):
    headers = {}
    body = None
    if request.method == 'POST':
        if not same_origin(request):
            raise web.HTTPForbidden(text='Origin must match the dispatch page')
        headers['Content-Type'] = 'application/json'
        headers['X-OmniFleet-Token'] = request.headers.get('X-OmniFleet-Token', '')
        body = await request.read()
    try:
        async with request.app['client'].request(request.method, target,
                                                 headers=headers, data=body) as upstream:
            response = web.Response(status=upstream.status, body=await upstream.read(),
                                    content_type='application/json', headers={'Cache-Control': 'no-store'})
            if request.method == 'GET':
                response.headers['Vary'] = 'Accept-Encoding'
                response.enable_compression()
            return response
    except (ClientError, asyncio.TimeoutError) as error:
        message = 'Single-vehicle controls are unavailable' if target.startswith(SINGLE_CONTROL_API) else 'Onboard dispatch is unavailable'
        raise web.HTTPBadGateway(text=message) from error


CARD_KEYS = frozenset(('robots', 'squads', 'waypoints', 'maps'))
CARD_ORDER = DIRECTORY.parent / 'data' / 'fleet-card-order.json'


async def fleet_card_order(request):
    if request.method == 'POST':
        if not same_origin(request):
            raise web.HTTPForbidden(text='Origin must match the dispatch page')
        try:
            payload = await request.json()
        except ValueError:
            raise web.HTTPBadRequest(text='Invalid card order')
        order = payload.get('order') if isinstance(payload, dict) else None
        if (not isinstance(order, list) or len(order) != len(CARD_KEYS)
                or not all(isinstance(key, str) for key in order) or set(order) != CARD_KEYS):
            raise web.HTTPBadRequest(text='Invalid card order')
        if payload.get('initialize') is not True or not CARD_ORDER.exists():
            CARD_ORDER.parent.mkdir(parents=True, exist_ok=True)
            temporary = CARD_ORDER.with_suffix('.tmp')
            temporary.write_text(json.dumps(order), encoding='utf8')
            temporary.replace(CARD_ORDER)
    order = json.loads(CARD_ORDER.read_text(encoding='utf8')) if CARD_ORDER.exists() else None
    return web.json_response({'order': order}, headers={'Cache-Control': 'no-store'})


async def forward(source, target):
    async for message in source:
        if message.type == WSMsgType.TEXT:
            await target.send_str(message.data)
        elif message.type == WSMsgType.BINARY:
            await target.send_bytes(message.data)


SINGLE_SAVED_MAPS = Path('/var/lib/omnifleet_a2/maps/112-live/saved')


def single_saved_map_entries():
    files = (path for path in SINGLE_SAVED_MAPS.glob('*.mm')
             if path.is_file() and not path.is_symlink())
    return [{'name': path.stem, 'path': str(path.with_suffix(''))}
            for path in sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)]


async def single_map_catalog(request):
    return web.json_response({'directory': str(SINGLE_SAVED_MAPS), 'maps': single_saved_map_entries()},
                             headers={'Cache-Control': 'no-store'})


async def single_map_delete(request):
    if not same_origin(request):
        raise web.HTTPForbidden(text='请求来源必须与当前车端页面一致')
    data = await request.json()
    chosen = data.get('path') if isinstance(data, dict) else None
    if not any(entry['path'] == chosen for entry in single_saved_map_entries()):
        raise web.HTTPBadRequest(text='所选地图不在保存目录中')
    prefix = Path(chosen)
    destination = SINGLE_SAVED_MAPS.parent / 'trash'
    destination.mkdir(exist_ok=True)
    archive = Path(tempfile.mkdtemp(prefix='map-', dir=destination))
    moved = []
    try:
        for suffix in ('.mm', '.simplemap', '.waypoints.json', '.road_network.geojson'):
            item = prefix.parent / (prefix.name + suffix)
            if not item.exists():
                continue
            if not stat.S_ISREG(item.lstat().st_mode):
                raise web.HTTPBadRequest(text='地图包含非普通文件')
            target = archive / item.name
            item.rename(target)
            moved.append((item, target))
    except Exception:
        for item, target in reversed(moved):
            target.rename(item)
        archive.rmdir()
        raise
    return await single_map_catalog(request)


async def socket(request):
    if 'Origin' in request.headers and not same_origin(request):
        raise web.HTTPForbidden(text='Origin must match the dispatch page')
    if PROTOCOL not in request.headers.get('Sec-WebSocket-Protocol', '').replace(' ', '').split(','):
        raise web.HTTPBadRequest(text=f'WebSocket subprotocol {PROTOCOL} is required')
    ws = web.WebSocketResponse(protocols=(PROTOCOL,), max_msg_size=0, compress=False)
    single_cloud = request.path == '/single-cloud-socket'
    bridge = SINGLE_BRIDGE if single_cloud else BRIDGE
    client = request.app['cloud_client'] if single_cloud else request.app['client']
    try:
        async with client.ws_connect(bridge, protocols=(PROTOCOL,), max_msg_size=0) as upstream:
            if upstream.protocol != PROTOCOL:
                raise web.HTTPBadGateway(text='Onboard bridge did not negotiate the Foxglove SDK protocol')
            await ws.prepare(request)
            request.app['websockets'].add(ws)
            relays = cloud_relays(ws, upstream) if single_cloud else (forward(ws, upstream), forward(upstream, ws))
            tasks = [asyncio.create_task(relay) for relay in relays]
            try:
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                if single_cloud:
                    for task in done:
                        if not task.cancelled() and task.exception() is not None:
                            request.app.logger.warning('Single-vehicle WebSocket relay: %r', task.exception())
            finally:
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
    except (ClientError, asyncio.TimeoutError) as error:
        if not ws.prepared:
            raise web.HTTPBadGateway(text='Onboard Foxglove bridge is unavailable') from error
    finally:
        request.app['websockets'].discard(ws)
        if ws.prepared:
            await ws.close()
    return ws


def load_index(original):
    bundle = re.search(r'src="(main\.[a-f0-9]+\.js)"', original).group(1)
    page = re.sub(r'<script\b[^>]*>.*?</script>', '', original, flags=re.S)
    page = re.sub(r'<title>[^<]*</title>', '<title>OmniFleet · 车载协同调度</title>', page, count=1)
    return page.replace('</head>', f'''<script src="/dispatch-layout.js"></script>
<script src="/dispatch-bootstrap.js"></script>
<script src="/waypoint-drag.js"></script>
<script defer src="/{bundle}"></script>
<script defer src="/omnifleet-wsl-panel.js"></script>
</head>''', 1)


def load_single_index(original, layout_script):
    bundle = re.search(r'src="(main\.[a-f0-9]+\.js)"', original).group(1)
    bundle_url = f'/studio-assets/{bundle}?v=waypoint-menu'
    page = re.sub(r'<script\b[^>]*>.*?</script>', '', original, flags=re.S)
    page = re.sub(r'<title>[^<]*</title>', '<title>单车控制</title>', page, count=1)
    page = page.replace('</head>', f'''<style>
  [data-single-vehicle-header] {{ height: 100%; min-height: 0; align-items: center !important;
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr) !important; }}
  [data-single-vehicle-header] > div {{ height: 100%; min-width: 0; align-items: center !important; }}
  [data-single-vehicle-header] > div > div {{ align-items: center !important; }}
  [data-single-vehicle-center] {{ position: relative; display: flex; align-items: center; gap: 4px;
    min-width: 0; overflow: visible !important; }}
  [data-single-vehicle-center] [class*="-sourceName"] {{ display: none; }}
  #vehicle-identity {{ position: relative; display: flex; align-items: center; height: 100%; }}
  #rename-vehicle {{ position: relative; display: flex; align-items: center; max-width: min(35vw, 24rem);
    height: 100%; padding: 0 6px; border: 0; color: inherit; background: transparent;
    font: inherit; cursor: text; user-select: none; }}
  #vehicle-name {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 600; }}
  #rename-vehicle:focus-visible {{ outline: 1px solid #9480ed; outline-offset: -2px; }}
  .vehicle-toolbar {{ position: relative; display: flex; align-items: center; gap: 6px;
    margin-inline: 8px; white-space: nowrap; font-size: 13px; }}
  .vehicle-toolbar a {{ color: inherit; font: inherit; background: transparent;
    border: 1px solid #635879; border-radius: 5px; padding: 4px 8px; text-decoration: none; cursor: pointer; }}
  .vehicle-toolbar a:hover {{ background: #9480ed26; }}
  #rename-form {{ display: flex; align-items: center; height: 100%; margin: 0; }}
  #rename-form input {{ width: clamp(8rem, 20vw, 20rem); min-width: 0; color: inherit;
    font: inherit; text-align: center; background: #17151c; border: 1px solid #9480ed;
    border-radius: 4px; padding: 4px 6px; }}
  #rename-status {{ position: absolute; top: 100%; left: 50%; transform: translateX(-50%);
    width: max-content; max-width: 24rem; padding: 4px 8px; color: #fff; background: #23212b;
    border-radius: 4px; white-space: normal; }}
  #rename-status:empty, .vehicle-toolbar[hidden], #vehicle-identity[hidden], #rename-form[hidden],
  #rename-vehicle[hidden] {{ display: none; }}
  @media (max-width: 640px) {{
    [data-single-vehicle-header] {{ grid-template-columns: max-content minmax(0, 1fr) max-content !important; }}
    .vehicle-toolbar {{ margin-inline: 4px; gap: 4px; }}
    .vehicle-toolbar a {{ padding-inline: 4px; }}
    #vehicle-name {{ max-width: 100%; }}
  }}
</style>
<link rel="preload" as="script" href="{bundle_url}">
{startup_preloads(bundle_url)}
<link rel="preload" as="script" href="single-waypoints.js">
<link rel="preload" as="script" href="single-panels.js">
<script>{layout_script}</script>
<script defer src="/fzstd-0.1.1.js"></script>
<script defer src="/single-cloud-client.js?v=2"></script>
<script defer src="single-bootstrap.js?v=124-panels-v2-20261121" data-bundle="{bundle_url}"></script>
<script defer src="single-toolbar.js?v=124-map-waypoints-20261121"></script>
<link rel="stylesheet" href="/bag-panel.css?v=1">
<script defer src="/bag-panel.js?v=1"></script>
</head>''', 1)
    toolbar = '''<nav class="vehicle-toolbar" aria-label="单车控制" hidden>
  <a href="/">返回首页</a>
  <button type="button" data-bag-open>Bag 录制</button>
</nav>
<div id="vehicle-identity" hidden>
  <button id="rename-vehicle" type="button" title="双击车辆名称更名" aria-label="双击车辆名称更名"
    aria-expanded="false" aria-controls="rename-form" disabled>
    <span id="vehicle-name">robot</span>
  </button>
  <form id="rename-form" hidden>
    <input id="vehicle-new-name" aria-label="车辆调度名称" maxlength="40" required
      pattern="[A-Za-z][A-Za-z0-9_]{0,39}" autocomplete="off" spellcheck="false"
      title="字母开头，可含英文字母、数字和下划线；回车保存，Esc取消">
  </form>
  <span id="rename-status" role="status"></span>
</div>'''
    return re.sub(r'(<body\b[^>]*>)', lambda match: match[0] + toolbar, page, count=1)


def single_panel_script(source):
    source = (source.replace('omnifleet-113-panels', 'omnifleet-single-panels')
              .replace('omnifleet113-panels.js', 'single-panels.js')
              .replace('__robot113NativePanelsReady', '__omnifleetSinglePanelsReady')
              .replace('robot104-battery-voltage', 'single-battery-voltage'))
    # Adapt only the single-vehicle registrations. The original panels are shared assets.
    marker = r"(?m)^(\s*const name='local\.omnifleet-single-panels';)"
    initializers = dict.fromkeys(re.findall(r'\binitPanel\s*:\s*(init\w+)\b', source))
    adapters = '\n'.join(
        f' {name} = window.OmniFleetSingle.bindPanel({name});' for name in initializers
    )
    source, matched = re.subn(marker, lambda match: adapters + '\n' + match[0], source)
    if matched != 1:
        raise ValueError('Single-vehicle panel registration was not found')
    return source


def single_waypoint_script(source):
    for variable in ('catalogTopic', 'stateTopic', 'updateTopic'):
        source, matched = re.subn(
            rf"\bconst {variable} = '/([^']+)';",
            rf"const {variable} = root.OmniFleetSingle.topic('\1');",
            source, count=1,
        )
        if not matched:
            raise ValueError(f'Single-vehicle waypoint binding was not found: {variable}')
    return source.replace('if (!renderer || !context || instances.has(renderer))',
                          'if (!updateTopic || !renderer || !context || instances.has(renderer))', 1)


def build_app():
    compressed_assets = prepare_compressed_assets()
    original = (FOXGLOVE_SITE / 'index.html').read_text(encoding='utf-8')
    page = (DIRECTORY/"index.html").read_text(encoding="utf8")
    single_layout = json.loads((DIRECTORY / 'single-layout.json').read_text(encoding='utf-8'))
    single_layout_script = 'window.OmniFleetSingleLayout = ' + json.dumps(single_layout).replace('<',r'\u003c') + ';'
    single_page = load_single_index(original, single_layout_script)
    single_page = single_page.replace('</head>', CLOSE_LEFT_SIDEBAR + '</head>', 1)
    single_scripts = {
        'single-layout.js': single_layout_script,
        'single-panels.js': single_panel_script((FOXGLOVE_SITE / 'omnifleet113-panels.js').read_text(encoding='utf-8')).replace('机器人', '智能移动平台'),
        'single-waypoints.js': single_waypoint_script((FOXGLOVE_SITE / 'waypoint-drag.js').read_text(encoding='utf-8')),
    }
    single_etags = {
        name: 'W/"' + hashlib.sha256(script.encode('utf-8')).hexdigest() + '"'
        for name, script in single_scripts.items()
    }
    layout = json.loads((DIRECTORY / 'layout.json').read_text(encoding='utf-8-sig'))['data']
    layout_script = 'window.global = window; window.FOXGLOVE_STUDIO_DEFAULT_LAYOUT = ' + json.dumps(layout).replace('<',r'\u003c') + ';'
    layout_script += (DIRECTORY/'onboard-bootstrap.js').read_text(encoding='utf8')
    page = page.replace('<script defer src="/dispatch-layout.js"></script>', f'<script>{layout_script}</script>',1)
    bundle = re.search(r'src="(/studio-assets/main\.[0-9a-f]+\.js[^"]*)"',page)
    if bundle:
        page = page.replace('</head>',startup_preloads(bundle[1])+'</head>',1)
    page = page.replace('</head>', CLOSE_LEFT_SIDEBAR + '</head>', 1)

    async def vehicle(request):
        async with request.app['client'].get(CONTROL_API+'/state') as res:
            state=await res.json()
        robot=request.match_info['robot']
        if robot==state.get('dispatcher_id'):
            raise web.HTTPFound('/single/')
        host=state.get('discovery',{}).get('control_hosts',{}).get(robot)
        if not host: raise web.HTTPNotFound(text='车辆尚未广播单车管理地址')
        from ipaddress import IPv4Address
        raise web.HTTPFound('http://'+str(IPv4Address(host))+'/single/')

    def file_response(request, file):
        versioned = re.fullmatch(r'[\w-]+\.[0-9a-f]{8,}\.(js|css|wasm)', file.name)
        cache_control = 'public, max-age=86400' if versioned and not file.is_relative_to(STUDIO_OVERRIDE) else 'no-cache'
        headers = {'Cache-Control': cache_control}
        variant = compressed_assets.get(file)
        if variant:
            headers['Vary'] = 'Accept-Encoding'
            mtime, size, gzip_file = variant
            if accepts_gzip(request) and 'Range' not in request.headers:
                stat = file.stat()
                if (stat.st_mtime_ns, stat.st_size) == (mtime, size):
                    headers['Content-Type'] = mimetypes.guess_type(file.name)[0] or 'application/octet-stream'
                    headers['Content-Encoding'] = 'gzip'
                    return web.FileResponse(gzip_file, headers=headers)
        return web.FileResponse(file, headers=headers)

    async def studio_asset(request):
        for directory in STUDIO_DIRS:
            file=(directory/request.match_info['name']).resolve()
            if file.is_relative_to(directory) and file.is_file():
                return file_response(request, file)
        raise web.HTTPNotFound()

    async def clients(app):
        streaming = ClientTimeout(total=None, connect=8, sock_connect=8)
        async with ClientSession(timeout=ClientTimeout(total=8)) as client, ClientSession(timeout=streaming) as cloud_client:
            app['client'] = client
            app['cloud_client'] = cloud_client
            yield

    async def close_sockets(app):
        await asyncio.gather(*(ws.close(code=1001) for ws in tuple(app['websockets'])), return_exceptions=True)

    async def index(_):
        response = web.Response(text=page, content_type='text/html',
                                headers={'Cache-Control':'no-cache', 'Vary':'Accept-Encoding'})
        response.enable_compression()
        return response

    async def single_index(_):
        response = web.Response(text=single_page, content_type='text/html',
                                headers={'Cache-Control':'no-cache', 'Vary':'Accept-Encoding'})
        response.enable_compression()
        return response

    async def single_redirect(request):
        raise web.HTTPFound(location=request.rel_url.with_path('/single/').with_query(request.query))

    async def asset(request):
        name = request.match_info['name']
        if name == 'dispatch-layout.js':
            return web.Response(text=layout_script, content_type='application/javascript')
        if name in {'app.js','style.css','native-panels.js','dispatch-bootstrap.js', 'omnifleet-wsl-panel.js',
                    'bag-panel.js','bag-panel.css','fzstd-0.1.1.js','fzstd-0.1.1.LICENSE.txt',
                    'single-cloud-client.js'}:
            return file_response(request, DIRECTORY / name)
        file = (FOXGLOVE_SITE / name).resolve()
        if not file.is_relative_to(FOXGLOVE_SITE) or not file.is_file():
            raise web.HTTPNotFound()
        return file_response(request, file)

    async def single_asset(request):
        name = request.match_info['name']
        if (STUDIO_OVERRIDE/name).is_file() and '/' not in name:
            return file_response(request, (STUDIO_OVERRIDE/name).resolve())
        if name in single_scripts:
            etag = single_etags[name]
            headers = {'Vary':'Accept-Encoding','Cache-Control':'no-cache','ETag':etag}
            matches = {value.strip() for value in request.headers.get('If-None-Match','').split(',')}
            if '*' in matches or etag in matches:
                return web.Response(status=304, headers=headers)
            response = web.Response(text=single_scripts[name], content_type='application/javascript',
                                    headers=headers)
            response.enable_compression()
            return response
        if name in {'single-bootstrap.js', 'single-toolbar.js'}:
            return file_response(request, DIRECTORY / name)
        return await asset(request)

    app = web.Application(client_max_size=16 * 1024)
    app['websockets'] = set()
    app.cleanup_ctx.append(clients)
    app.on_shutdown.append(close_sockets)
    register_bag_routes(app, same_origin)
    slam_control.install(app, same_origin)
    app.router.add_get('/dispatch-api/card-order', fleet_card_order)
    app.router.add_post('/dispatch-api/card-order', fleet_card_order)
    app.router.add_get('/dispatch-api/{endpoint:state}', api, allow_head=False)
    app.router.add_post('/dispatch-api/{endpoint:command}', api)
    app.router.add_get('/dispatch-socket', socket, allow_head=False)
    app.router.add_get('/single-cloud-socket', socket, allow_head=False)
    app.router.add_get('/api/{endpoint:nav2/parameters|steering-center|steering-limit}', single_control_api)
    app.router.add_post('/api/{endpoint:nav2/parameters|steering-center|steering-limit|drive}', single_control_api)
    app.router.add_get('/single-map-catalog', single_map_catalog)
    app.router.add_post('/single-map-catalog/delete', single_map_delete)
    app.router.add_get('/', index)
    app.router.add_get('/index.html', index)
    app.router.add_get('/vehicle/{robot}/',vehicle)
    app.router.add_get('/studio-assets/{name:.+}',studio_asset)
    app.router.add_get('/single', single_redirect)
    app.router.add_get('/single/', single_index)
    app.router.add_get('/single/index.html', single_index)
    app.router.add_get('/single/{name:.+}', single_asset)
    app.router.add_get('/{name:.+}', asset)
    return app


if __name__ == '__main__':
    web.run_app(build_app(), host='0.0.0.0', port=8080, access_log=None)
