"""One persistent dispatch simulator. The only moving objects live in this process."""
import asyncio
from copy import deepcopy
import bisect
import heapq
import json
import math
import os
from pathlib import Path
import time
import uuid

from aiohttp import web


ROOT = Path(__file__).resolve().parent
FILE = Path(os.environ.get("SIM_STATE_FILE", ROOT / "state.json"))
MODE = "simulation"
STEP = 0.5
RADIUS = 0.32
SPEED = 1.6
ROBOTS = ("sim_105", "sim_124")
SCENE = {"width": 16, "height": 12, "obstacles": [[6.5, 2.5, 8.5, 7.5], [10, 8, 13, 9.5], [2.5, 7.5, 4.5, 9.5]]}
INITIAL = dict(zip(ROBOTS, ([2.0, 2.0], [4.0, 2.0])))


def initial_state():
    return {"mode": MODE, "scene": deepcopy(SCENE), "robots": deepcopy(INITIAL),
            "formations": [], "maps": [], "tasks": []}


def clear(position, scene, stationary=()):
    x, y = position
    return (
        RADIUS <= x <= scene["width"] - RADIUS
        and RADIUS <= y <= scene["height"] - RADIUS
        and all(not (a - RADIUS <= x <= c + RADIUS and b - RADIUS <= y <= d + RADIUS)
                for a, b, c, d in scene["obstacles"])
        and all(math.dist(position, other) >= 2 * RADIUS for other in stationary)
    )


def path(start, end, scene, offsets=((0, 0),), stationary=()):
    def point(cell):
        return (cell[0] * STEP, cell[1] * STEP)

    def cell(p):
        return tuple(round(v / STEP) for v in p)

    def allowed(p):
        return all(clear((p[0] + dx, p[1] + dy), scene, stationary) for dx, dy in offsets)

    def valid_segment(a, b):
        return all(allowed((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
                   for t in (0, .25, .5, .75, 1))

    src, dst = cell(start), cell(end)
    if not valid_segment(start, point(src)) or not valid_segment(point(dst), end):
        return None
    queue = [(0, 0, src)]
    parents = {src: None}
    cost = {src: 0}
    while queue:
        _, distance, current = heapq.heappop(queue)
        if current == dst:
            waypoints = []
            while current is not None:
                waypoints.append(point(current))
                current = parents[current]
            return [*reversed(waypoints), tuple(end)]
        if distance != cost[current]:
            continue
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            n = (current[0] + dx, current[1] + dy)
            if distance + 1 >= cost.get(n, math.inf) or not valid_segment(point(current), point(n)):
                continue
            cost[n] = distance + 1
            parents[n] = current
            heuristic = abs(n[0] - dst[0]) + abs(n[1] - dst[1])
            heapq.heappush(queue, (distance + 1 + heuristic, distance + 1, n))
    return None

def route_index(points):
    lengths = [0.]
    for a, b in zip(points, points[1:]):
        lengths.append(lengths[-1] + math.dist(a, b))
    return lengths


def position_at(points, lengths, distance):
    distance = min(max(distance, 0.), lengths[-1])
    index = min(len(lengths)-1, bisect.bisect_right(lengths, distance))
    if not index or distance == lengths[-1]:
        return tuple(points[-1] if index else points[0])
    low, high = lengths[index-1:index+1]
    fraction = (distance-low)/(high-low)
    return tuple(a + (b-a)*fraction for a,b in zip(points[index-1], points[index]))


def follow_path(leader, follower, target, spacing, scene):
    lead = path(leader, target, scene)
    if lead is None:
        return None
    lead = [tuple(leader), *lead]
    first = next((p for p in lead if math.dist(p, leader) > .001), None)
    if first is None:
        return []
    dx, dy = (first[0]-leader[0], first[1]-leader[1])
    distance = math.hypot(dx, dy)
    direct = (dx/distance, dy/distance)
    # Prefer a trail behind the departure direction. Use a side approach
    # if the parking spot has insufficient room to assemble from behind.
    headings = (direct, (-direct[1],direct[0]), (direct[1],-direct[0]))
    for vx, vy in headings:
        tail = (leader[0]-spacing*vx, leader[1]-spacing*vy)
        if any(not clear((tail[0] + (leader[0]-tail[0])*i/20,
                          tail[1] + (leader[1]-tail[1])*i/20), scene) for i in range(21)):
            continue
        join = path(follower, tail, scene, stationary=[leader])
        if join is None:
            continue
        trail = [tail, *lead]
        lengths = route_index(trail)
        total = lengths[-1]
        positions = []
        count = math.ceil((total-spacing)/.10)
        for i in range(1, count+1):
            along = spacing + (total-spacing)*i/count
            ahead = position_at(trail, lengths, along)
            behind = position_at(trail, lengths, along-spacing)
            if math.dist(ahead,behind) < 2*RADIUS or not all(clear(p,scene) for p in (ahead,behind)):
                break
            positions.append((ahead,behind))
        else:
            return join,positions
    return None


class Simulation:
    def __init__(self):
        self.state = initial_state() if not FILE.exists() else json.loads(FILE.read_text(encoding="utf-8"))
        if self.state.get("mode") != MODE or set(self.state.get("robots", {})) != set(ROBOTS):
            raise ValueError("The state file does not belong to this simulator")
        self.segments = []
        self.active = None
        for task in self.state["tasks"]:
            if task["status"] == "running":
                task["status"] = "interrupted"
                task["message"] = "模拟服务重启"
        self.save()

    def save(self):
        FILE.parent.mkdir(parents=True, exist_ok=True)
        temp = FILE.with_suffix(".tmp")
        temp.write_text(json.dumps(self.state, ensure_ascii=False, allow_nan=False), encoding="utf-8")
        temp.replace(FILE)

    def plan(self, task):
        positions = self.state["robots"]
        scene = self.state["scene"]
        target = task["target"]
        if not task.get("formation"):
            robot = task["robot"]
            others = [v for k, v in positions.items() if k != robot]
            moves = path(positions[robot], target, scene, stationary=others)
            if moves is None:
                return None
            return [{robot: p} for p in moves]
        formation = task["formation"]
        leader = formation["leader"]
        follower = next(robot for robot in ROBOTS if robot != leader)
        result = follow_path(positions[leader],positions[follower],target,formation["spacing"],scene)
        if result is None:
            return None
        if not result:
            return []
        join, trail = result
        return ([{follower:p} for p in join]
                + [{leader:ahead,follower:behind} for ahead,behind in trail])

    def tick(self, dt):
        if self.active is None:
            task = next((t for t in self.state["tasks"] if t["status"] == "queued"), None)
            if task is None:
                return
            self.segments = self.plan(task)
            if self.segments is None:
                task.update(status="blocked", message="当前场景下找不到可通行的模拟路线", completed_at=time.time())
                self.save()
                return
            self.active = task
            task.update(status="running", message="模拟执行中", started_at=time.time())
            self.save()
        if self.segments:
            targets = self.segments[0]
            positions = self.state["robots"]
            distance = max(math.dist(positions[robot], target) for robot, target in targets.items())
            fraction = min(1, SPEED * dt / distance) if distance else 1
            for robot, target in targets.items():
                position = positions[robot]
                positions[robot] = [a + (b - a) * fraction for a, b in zip(position, target)]
            if fraction == 1:
                self.segments.pop(0)
            return
        self.active.update(status="completed", message="模拟到达", completed_at=time.time())
        self.active = None
        self.save()

    async def clock(self):
        last = time.monotonic()
        while True:
            await asyncio.sleep(.10)
            now = time.monotonic()
            self.tick(min(now - last, .25))
            last = now


def bad(message):
    raise web.HTTPBadRequest(text=message)


def name_of(body):
    name = body.get("name")
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 48:
        bad("请输入 1–48 个字符的名称")
    return name.strip()


def numeric(value):
    return type(value) in (float, int) and math.isfinite(value)


def create_app():
    sim = Simulation()
    app = web.Application(client_max_size=12000)

    async def lifecycle(_):
        clock = asyncio.create_task(sim.clock())
        try:
            yield
        finally:
            clock.cancel()
            await asyncio.gather(clock, return_exceptions=True)
            sim.save()

    async def state(_):
        return web.json_response(sim.state, headers={"Cache-Control": "no-store"})

    async def submit(request):
        try:
            body = await request.json()
        except ValueError:
            bad("请求必须是 JSON")
        if not isinstance(body, dict):
            bad("参数格式不正确")
        kind = request.match_info["kind"]
        request_id = body.get("request_id")
        if not isinstance(request_id, str) or not 8 <= len(request_id) <= 80:
            bad("请求编号无效")
        existing = next((item for item in sim.state[kind] if item.get("request_id") == request_id), None)
        if existing:
            return web.json_response(existing)
        record = {"id": uuid.uuid4().hex, "request_id": request_id, "created_at": time.time()}
        if kind == "formations":
            leader, spacing = body.get("leader"), body.get("spacing")
            if leader not in ROBOTS or not numeric(spacing) or not 1 <= spacing <= 4:
                bad("请选择模拟领队，间距设为 1–4 米")
            record.update(name=name_of(body), leader=leader, spacing=float(spacing), members=list(ROBOTS))
        elif kind == "maps":
            record.update(name=name_of(body), scene=deepcopy(sim.state["scene"]))
        else:
            x, y = body.get("x"), body.get("y")
            if not numeric(x) or not numeric(y) or not 0 <= x <= sim.state["scene"]["width"] or not 0 <= y <= sim.state["scene"]["height"]:
                bad("目标点须位于模拟场景内")
            formation, robot = body.get("formation"), body.get("robot")
            if formation:
                match = next((f for f in sim.state["formations"] if f["id"] == formation), None)
                if match is None:
                    bad("该模拟编队不存在")
                record["formation"] = deepcopy(match)
            elif robot in ROBOTS:
                record["robot"] = robot
            else:
                bad("请选择模拟车或模拟编队")
            record.update(target=[float(x), float(y)], status="queued", message="等待模拟执行")
        sim.state[kind].append(record)
        try:
            sim.save()
        except OSError:
            sim.state[kind].pop()
            raise web.HTTPServiceUnavailable(text="共享数据暂无法保存")
        return web.json_response(record, status=201)

    async def root(_):
        return web.FileResponse(ROOT / "index.html")

    async def asset(request):
        return web.FileResponse(ROOT / request.match_info["name"])

    app.cleanup_ctx.append(lifecycle)
    app.router.add_get("/", root)
    app.router.add_get("/{name:app.js|style.css}", asset)
    app.router.add_get("/api/state", state)
    app.router.add_post("/api/{kind:formations|maps|tasks}", submit)
    return app


if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=int(os.environ.get("SIM_PORT", "8082")), access_log=None)
