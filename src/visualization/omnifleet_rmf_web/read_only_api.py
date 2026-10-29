import base64
from fastapi.responses import Response
import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import Request
from fastapi.responses import StreamingResponse
from api_server.ros import ros_node
from live_status import LiveStatus
from fastapi.responses import JSONResponse
from api_server.app import app
from api_server.__main__ import main
from operator_api import router as operator_router

app.include_router(operator_router)


@app.middleware("http")
async def read_only_requests(request, call_next):
    if request.method not in {"GET", "HEAD", "OPTIONS"} and request.url.path not in {
        "/socket.io", "/socket.io/", "/omnifleet/operator/command"
    }:
        return JSONResponse(
            {"detail": "当前部署为只读模式，任务下发和设备控制已禁用。"},
            status_code=403,
            headers={"Access-Control-Allow-Origin": "http://localhost:3000"},
        )
    return await call_next(request)



original_lifespan = app.router.lifespan_context


@asynccontextmanager
async def live_lifespan(application):
    async with original_lifespan(application):
        monitor = LiveStatus(ros_node())
        application.state.live_status = monitor
        try:
            yield
        finally:
            monitor.close()


app.router.lifespan_context = live_lifespan



@app.get('/omnifleet/robots/robot_104/map.png', tags=['OmniFleet live status'])
async def robot_map_image():
    monitor = app.state.live_status
    with monitor.lock:
        image = monitor.vehicle.get('map') if monitor.vehicle else None
        if not image or not image.get('image_base64'):
            return JSONResponse({'detail': '104 地图尚未收到'}, status_code=404)
        encoded, fingerprint = image['image_base64'], image['hash']
    return Response(base64.b64decode(encoded), media_type='image/png', headers={'Cache-Control': 'no-cache', 'ETag': fingerprint})

@app.get('/omnifleet/status', tags=['OmniFleet live status'])
async def live_snapshot():
    return app.state.live_status.snapshot()


@app.get('/omnifleet/status/stream', tags=['OmniFleet live status'])
async def live_stream(request: Request):
    async def events():
        while not await request.is_disconnected():
            payload = json.dumps(app.state.live_status.snapshot(), ensure_ascii=False, allow_nan=False)
            yield f'data: {payload}\n\n'
            await asyncio.sleep(1)
    return StreamingResponse(events(), media_type='text/event-stream', headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


if __name__ == "__main__":
    main()
