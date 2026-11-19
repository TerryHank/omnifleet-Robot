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
PROTOCOL = 'foxglove.websocket.v1'


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
    if not same_origin(request):
        raise web.HTTPForbidden(text='Origin must match the dispatch page')
    if PROTOCOL not in request.headers.get('Sec-WebSocket-Protocol', '').replace(' ', '').split(','):
        raise web.HTTPBadRequest(text='Foxglove WebSocket protocol is required')
    ws = web.WebSocketResponse(protocols=(PROTOCOL,), max_msg_size=0, compress=False)
    try:
        async with request.app['client'].ws_connect(BRIDGE, protocols=(PROTOCOL,), max_msg_size=0) as upstream:
            await ws.prepare(request)
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
        if ws.prepared:
            await ws.close()
    return ws


def load_index():
    original = (FOXGLOVE_SITE / 'index.html').read_text(encoding='utf-8')
    bundle = re.search(r'src="(main\.[a-f0-9]+\.js)"', original).group(1)
    page = re.sub(r'<script\b[^>]*>.*?</script>', '', original, flags=re.S)
    page = re.sub(r'<title>[^<]*</title>', '<title>OmniFleet · 车载协同调度</title>', page, count=1)
    return page.replace('</head>', f'''<script src="/dispatch-layout.js"></script>
<script src="/dispatch-bootstrap.js"></script>
<script src="/waypoint-drag.js"></script>
<script defer src="/{bundle}"></script>
<script defer src="/omnifleet-wsl-panel.js"></script>
</head>''', 1)


def build_app():
    page = load_index()
    layout = json.loads((DIRECTORY / 'layout.json').read_text(encoding='utf-8-sig'))['data']
    layout_script = 'window.global = window; window.FOXGLOVE_STUDIO_DEFAULT_LAYOUT = ' + json.dumps(layout) + ';'

    async def clients(app):
        async with ClientSession(timeout=ClientTimeout(total=8)) as client:
            app['client'] = client
            yield

    async def index(_):
        return web.Response(text=page, content_type='text/html', headers={'Cache-Control': 'no-cache'})

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

    app = web.Application(client_max_size=16 * 1024)
    app.cleanup_ctx.append(clients)
    app.router.add_get('/dispatch-api/{endpoint:state}', api, allow_head=False)
    app.router.add_post('/dispatch-api/{endpoint:command}', api)
    app.router.add_get('/dispatch-socket', socket, allow_head=False)
    app.router.add_get('/', index)
    app.router.add_get('/index.html', index)
    app.router.add_get('/{name:.+}', asset)
    return app


if __name__ == '__main__':
    web.run_app(build_app(), host='0.0.0.0', port=8080, access_log=None)
