"""Serve the onboard Foxglove dispatch layout and its same-origin endpoints."""

import asyncio
import json
from pathlib import Path
import re

from aiohttp import ClientError, ClientSession, ClientTimeout, WSMsgType, web


DIRECTORY = Path(__file__).resolve().parent
FOXGLOVE_SITE = Path('/opt/foxglove-studio-cn-104/site')
CONTROL_API = 'http://127.0.0.1:8081'
BRIDGE = 'ws://127.0.0.1:8768/'
PROTOCOL = 'foxglove.sdk.v1'


def same_origin(request):
    return request.headers.get('Origin') == f'{request.scheme}://{request.host}'


async def api(request):
    endpoint = request.match_info['endpoint']
    headers = {}
    body = None
    if request.method == 'POST':
        if not same_origin(request):
            raise web.HTTPForbidden(text='Origin must match the dispatch page')
        headers['Content-Type'] = 'application/json'
        headers['X-OmniFleet-Token'] = request.headers.get('X-OmniFleet-Token', '')
        body = await request.read()
    try:
        async with request.app['client'].request(request.method, CONTROL_API + '/' + endpoint,
                                                 headers=headers, data=body) as upstream:
            return web.Response(status=upstream.status, body=await upstream.read(),
                                content_type='application/json', headers={'Cache-Control': 'no-store'})
    except (ClientError, asyncio.TimeoutError) as error:
        raise web.HTTPBadGateway(text='Onboard dispatch is unavailable') from error


async def forward(source, target):
    async for message in source:
        if message.type == WSMsgType.TEXT:
            await target.send_str(message.data)
        elif message.type == WSMsgType.BINARY:
            await target.send_bytes(message.data)


async def socket(request):
    if 'Origin' in request.headers and not same_origin(request):
        raise web.HTTPForbidden(text='Origin must match the dispatch page')
    if PROTOCOL not in request.headers.get('Sec-WebSocket-Protocol', '').replace(' ', '').split(','):
        raise web.HTTPBadRequest(text=f'WebSocket subprotocol {PROTOCOL} is required')
    ws = web.WebSocketResponse(protocols=(PROTOCOL,), max_msg_size=0, compress=False)
    try:
        async with request.app['client'].ws_connect(BRIDGE, protocols=(PROTOCOL,), max_msg_size=0) as upstream:
            if upstream.protocol != PROTOCOL:
                raise web.HTTPBadGateway(text='Onboard bridge did not negotiate the Foxglove SDK protocol')
            await ws.prepare(request)
            request.app['websockets'].add(ws)
            tasks = [asyncio.create_task(forward(ws, upstream)), asyncio.create_task(forward(upstream, ws))]
            try:
                await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
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


def load_single_index(original):
    bundle = re.search(r'src="(main\.[a-f0-9]+\.js)"', original).group(1)
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
    height: 100%; padding: 0 20px 0 6px; border: 0; color: inherit; background: transparent;
    font: inherit; cursor: text; user-select: none; }}
  #vehicle-name {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 600; }}
  #vehicle-edit-icon {{ position: absolute; right: 0; bottom: 2px; font-size: 12px; line-height: 16px; cursor: pointer; }}
  #rename-vehicle:focus-visible {{ outline: 1px solid #9480ed; outline-offset: -2px; }}
  .vehicle-toolbar {{ position: relative; display: flex; align-items: center; gap: 6px;
    margin-inline: 8px; white-space: nowrap; font-size: 13px; }}
  .vehicle-toolbar a, #rename-form button {{ color: inherit; font: inherit; background: transparent;
    border: 1px solid #635879; border-radius: 5px; padding: 4px 8px; text-decoration: none; cursor: pointer; }}
  .vehicle-toolbar a:hover, #rename-form button:enabled:hover {{ background: #9480ed26; }}
  #rename-form button:disabled {{ cursor: default; opacity: .55; }}
  #rename-form input {{ min-width: 0; color: inherit; background: #17151c; border: 1px solid #635879;
    border-radius: 4px; padding: 4px 6px; }}
  #rename-dialog {{ top: 56px; margin: 0 auto; padding: 10px; max-width: calc(100vw - 24px);
    color: #fff; background: #23212b; border: 1px solid #494453; border-radius: 5px; }}
  #rename-dialog::backdrop {{ background: #0003; }}
  #rename-form {{ display: grid; grid-template-columns: minmax(0, 12rem) auto auto;
    gap: 6px; align-items: center; }}
  #rename-status {{ grid-column: 1 / -1; white-space: normal; }}
  #rename-status:empty, .vehicle-toolbar[hidden], #vehicle-identity[hidden], #rename-form[hidden] {{ display: none; }}
  @media (max-width: 640px) {{
    [data-single-vehicle-header] {{ grid-template-columns: max-content minmax(0, 1fr) max-content !important; }}
    .vehicle-toolbar {{ margin-inline: 4px; gap: 4px; }}
    .vehicle-toolbar a {{ padding-inline: 4px; }}
    #vehicle-name {{ max-width: 100%; }}
  }}
</style>
<script src="single-layout.js"></script>
<script src="single-bootstrap.js" data-bundle="{bundle}"></script>
<script defer src="single-toolbar.js?v=appbar-3"></script>
</head>''', 1)
    toolbar = '''<nav class="vehicle-toolbar" aria-label="单车控制" hidden>
  <a href="/">返回首页</a>
</nav>
<div id="vehicle-identity" hidden>
  <button id="rename-vehicle" type="button" title="双击车辆名称更名" aria-label="双击车辆名称更名"
    aria-expanded="false" aria-controls="rename-form" disabled>
    <span id="vehicle-name">单车控制</span><span id="vehicle-edit-icon" aria-hidden="true">🖊️</span>
  </button>
</div>
<dialog id="rename-dialog" aria-label="更改车辆名称">
  <form id="rename-form" hidden>
    <input id="vehicle-new-name" aria-label="车辆显示名称" maxlength="40" placeholder="车辆显示名称">
    <button type="submit">保存</button>
    <button id="cancel-rename" type="button">取消</button>
    <span id="rename-status" role="status"></span>
  </form>
</dialog>'''
    return re.sub(r'(<body\b[^>]*>)', lambda match: match[0] + toolbar, page, count=1)


def single_panel_script(source):
    source = (source.replace('omnifleet-113-panels', 'omnifleet-single-panels')
              .replace('omnifleet113-panels.js', 'single-panels.js')
              .replace('__robot113NativePanelsReady', '__omnifleetSinglePanelsReady')
              .replace('robot104-battery-voltage', 'single-battery-voltage'))
    # Adapt only the single-vehicle registrations. The original panels are shared assets.
    marker = r"(?m)^(\s*const name='local\.omnifleet-single-panels';)"
    adapters = '\n'.join(f' {name} = window.OmniFleetSingle.bindPanel({name});' for name in (
        'initBatteryVoltage', 'initSpeedGauge', 'initDriveJoystick', 'initNav2Builtin',
    ))
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
    original = (FOXGLOVE_SITE / 'index.html').read_text(encoding='utf-8')
    page = load_index(original)
    single_page = load_single_index(original)
    single_layout = json.loads((DIRECTORY / 'single-layout.json').read_text(encoding='utf-8'))
    single_scripts = {
        'single-layout.js': 'window.OmniFleetSingleLayout = ' + json.dumps(single_layout) + ';',
        'single-panels.js': single_panel_script((FOXGLOVE_SITE / 'omnifleet113-panels.js').read_text(encoding='utf-8')),
        'single-waypoints.js': single_waypoint_script((FOXGLOVE_SITE / 'waypoint-drag.js').read_text(encoding='utf-8')),
    }
    layout = json.loads((DIRECTORY / 'layout.json').read_text(encoding='utf-8-sig'))['data']
    layout_script = 'window.global = window; window.FOXGLOVE_STUDIO_DEFAULT_LAYOUT = ' + json.dumps(layout) + ';'

    async def clients(app):
        async with ClientSession(timeout=ClientTimeout(total=8)) as client:
            app['client'] = client
            yield

    async def close_sockets(app):
        await asyncio.gather(*(ws.close(code=1001) for ws in tuple(app['websockets'])), return_exceptions=True)

    async def index(_):
        return web.Response(text=page, content_type='text/html', headers={'Cache-Control': 'no-cache'})

    async def single_index(_):
        return web.Response(text=single_page, content_type='text/html', headers={'Cache-Control': 'no-cache'})

    async def single_redirect(request):
        raise web.HTTPFound(location=request.rel_url.with_path('/single/').with_query(request.query))

    async def asset(request):
        name = request.match_info['name']
        if name == 'dispatch-layout.js':
            return web.Response(text=layout_script, content_type='application/javascript')
        if name in {'dispatch-bootstrap.js', 'omnifleet-wsl-panel.js'}:
            return web.FileResponse(DIRECTORY / name)
        file = (FOXGLOVE_SITE / name).resolve()
        if not file.is_relative_to(FOXGLOVE_SITE) or not file.is_file():
            raise web.HTTPNotFound()
        return web.FileResponse(file)

    async def single_asset(request):
        name = request.match_info['name']
        if name in single_scripts:
            return web.Response(text=single_scripts[name], content_type='application/javascript')
        if name in {'single-bootstrap.js', 'single-toolbar.js'}:
            return web.FileResponse(DIRECTORY / name)
        return await asset(request)

    app = web.Application(client_max_size=16 * 1024)
    app['websockets'] = set()
    app.cleanup_ctx.append(clients)
    app.on_shutdown.append(close_sockets)
    app.router.add_get('/dispatch-api/{endpoint:state}', api, allow_head=False)
    app.router.add_post('/dispatch-api/{endpoint:command}', api)
    app.router.add_get('/dispatch-socket', socket, allow_head=False)
    app.router.add_get('/', index)
    app.router.add_get('/index.html', index)
    app.router.add_get('/single', single_redirect)
    app.router.add_get('/single/', single_index)
    app.router.add_get('/single/index.html', single_index)
    app.router.add_get('/single/{name:.+}', single_asset)
    app.router.add_get('/{name:.+}', asset)
    return app


if __name__ == '__main__':
    web.run_app(build_app(), host='0.0.0.0', port=8080, access_log=None)
