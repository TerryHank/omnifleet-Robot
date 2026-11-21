"""Single-robot SLAM toolbar actions with live progress."""
import asyncio
from pathlib import Path
import json

from aiohttp import web


def install(app, same_origin):
    root=Path(__file__).resolve().parent
    state={"phase":"idle","message":"待命"}
    current=None

    async def run():
        nonlocal state
        process=None
        try:
            launch="/home/iecme/omnifleet_a2_ws"
            process=await asyncio.create_subprocess_exec(
                "/bin/bash","-c",
                'cd "$1" && source deploy/chassis-111/chassis_env.bash && exec /usr/bin/python3 "$2"',
                "single-slam-restart",launch,str(root/"slam_restart_worker.py"),
                stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.STDOUT
            )
            async def stream():
                nonlocal state
                async for raw in process.stdout:
                    msg=raw.decode("utf-8",errors="replace").strip()
                    if msg.startswith("SLAM_STATE "):
                        state=json.loads(msg.removeprefix("SLAM_STATE "))
                return await process.wait()
            code=await asyncio.wait_for(stream(),timeout=144)
            if state.get("phase") not in ("done","failed"):
                state={"phase":"failed","message":f"SLAM 重启进程未返回有效结果（{code}）"}
        except (OSError,ValueError,asyncio.TimeoutError) as error:
            state={"phase":"failed","message":str(error) or "车端重启等待超时"}
            if process and process.returncode is None:
                process.terminate()
                await process.wait()

    async def start(request):
        nonlocal current,state
        if not same_origin(request):
            raise web.HTTPForbidden(text="页面来源与车端不一致")
        if current and not current.done():
            return web.json_response(state,status=202,headers={"Cache-Control":"no-store"})
        state={"phase":"saving","message":"已受理，正在保存地图"}
        current=asyncio.create_task(run())
        return web.json_response(state,status=202,headers={"Cache-Control":"no-store"})

    async def status(request):
        return web.json_response(state,headers={"Cache-Control":"no-store"})

    app.router.add_post("/single-slam/restart",start)
    app.router.add_get("/single-slam/status",status)

