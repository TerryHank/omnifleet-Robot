"""Persist the parameters used by the 124 A2 Nav2 launch."""

from pathlib import Path
import math
import json
import re
import os
import tempfile
import threading

from rcl_interfaces.msg import Parameter, ParameterType, ParameterValue
from rcl_interfaces.srv import GetParameters, SetParametersAtomically
import yaml


CONFIG = Path(__file__).resolve().parents[2] / "src/omnifleet_a2_planner/config"
BASE = "nav2_glim.yaml"
RPP = "controller_rpp.yaml"
WORKSPACE = Path(__file__).resolve().parents[2]
MOLA = WORKSPACE / "src/localization/omnifleet_mola"
MAP_GRID = WORKSPACE / "src/map/omnifleet_map_tf_generator/omnifleet_map_tf_generator/mola_realtime_nav_grid.py"
LOCAL = "/local_costmap/local_costmap"
GLOBAL = "/global_costmap/global_costmap"
CONTROLLER = "/controller_server"
PLANNER = "/planner_server"

# Shared field IDs and labels match the 105 single-robot page.
# label, group, unit, file, ROS node, parameter name
FIELDS = {
    "geometry_local_inflation_radius": ("障碍膨胀半径 · inflation_radius", "避障与车体", "m", BASE, LOCAL, "inflation_layer.inflation_radius"),
    "costmap_scaling": ("膨胀代价衰减系数 · cost_scaling_factor", "避障与车体", "", BASE, LOCAL, "inflation_layer.cost_scaling_factor"),
    "geometry_local_footprint_padding": ("额外车体余量 · footprint_padding", "避障与车体", "m", BASE, LOCAL, "footprint_padding"),
    "geometry_local_resolution": ("栅格分辨率 · resolution", "避障与车体", "m", BASE, LOCAL, "resolution"),
    "planner_tolerance": ("路线终点容差 · tolerance", "全局规划", "m", BASE, PLANNER, "GridBased.tolerance"),
    "forward_cost_penalty": ("通行代价权重 · cost_penalty", "全局规划", "", BASE, PLANNER, "GridBased.cost_penalty"),
    "planner_allow_unknown": ("允许未知区域 · allow_unknown", "全局规划", "", BASE, PLANNER, "GridBased.allow_unknown"),
    "forward_radius": ("最小转弯半径 · minimum_turning_radius", "全局规划", "m", BASE, PLANNER, "GridBased.minimum_turning_radius"),
    "reverse_penalty": ("规划倒车代价 · reverse_penalty", "全局规划", "", BASE, PLANNER, "GridBased.reverse_penalty"),
    "planner_max_iterations": ("最大搜索迭代次数 · max_iterations", "全局规划", "", BASE, PLANNER, "GridBased.max_iterations"),
    "forward_approach_iterations": ("最大接近迭代次数 · max_on_approach_iterations", "全局规划", "", BASE, PLANNER, "GridBased.max_on_approach_iterations"),
    "planner_max_planning_time": ("最大规划时间 · max_planning_time", "全局规划", "s", BASE, PLANNER, "GridBased.max_planning_time"),
    "forward_angle_bins": ("航向离散数 · angle_quantization_bins", "全局规划", "", BASE, PLANNER, "GridBased.angle_quantization_bins"),
    "rpp_desired_linear_vel": ("期望线速度 · desired_linear_vel", "局部控制", "m/s", RPP, CONTROLLER, "FollowPath.desired_linear_vel"),
    "rpp_allow_reversing": ("允许沿倒车段行驶 · allow_reversing", "局部控制", "", RPP, CONTROLLER, "FollowPath.allow_reversing"),
    "rpp_velocity_scaled_lookahead": ("速度自适应前视 · use_velocity_scaled_lookahead_dist", "局部控制", "", RPP, CONTROLLER, "FollowPath.use_velocity_scaled_lookahead_dist"),
    "rpp_lookahead_dist": ("固定前视距离 · lookahead_dist", "局部控制", "m", RPP, CONTROLLER, "FollowPath.lookahead_dist"),
    "rpp_min_lookahead_dist": ("最小前视距离 · min_lookahead_dist", "局部控制", "m", RPP, CONTROLLER, "FollowPath.min_lookahead_dist"),
    "rpp_max_lookahead_dist": ("最大前视距离 · max_lookahead_dist", "局部控制", "m", RPP, CONTROLLER, "FollowPath.max_lookahead_dist"),
    "rpp_lookahead_time": ("前视时间 · lookahead_time", "局部控制", "s", RPP, CONTROLLER, "FollowPath.lookahead_time"),
    "rpp_use_regulated_linear_velocity_scaling": ("曲率速度调节 · use_regulated_linear_velocity_scaling", "局部控制", "", RPP, CONTROLLER, "FollowPath.use_regulated_linear_velocity_scaling"),
    "rpp_curve_radius": ("曲率减速半径阈值 · regulated_linear_scaling_min_radius", "局部控制", "m", RPP, CONTROLLER, "FollowPath.regulated_linear_scaling_min_radius"),
    "rpp_curve_min_speed": ("调速最小线速度 · regulated_linear_scaling_min_speed", "局部控制", "m/s", RPP, CONTROLLER, "FollowPath.regulated_linear_scaling_min_speed"),
    "rpp_use_cost_regulated_linear_velocity_scaling": ("障碍代价速度调节 · use_cost_regulated_linear_velocity_scaling", "局部控制", "", RPP, CONTROLLER, "FollowPath.use_cost_regulated_linear_velocity_scaling"),
    "rpp_cost_scaling_dist": ("障碍减速距离 · cost_scaling_dist", "局部控制", "m", RPP, CONTROLLER, "FollowPath.cost_scaling_dist"),
    "rpp_cost_scaling_gain": ("障碍减速增益 · cost_scaling_gain", "局部控制", "", RPP, CONTROLLER, "FollowPath.cost_scaling_gain"),
    "goal_xy_tolerance": ("到点距离容差 · xy_goal_tolerance", "局部控制", "m", BASE, CONTROLLER, "general_goal_checker.xy_goal_tolerance"),
    "goal_yaw_tolerance": ("到点角度容差 · yaw_goal_tolerance", "局部控制", "rad", BASE, CONTROLLER, "general_goal_checker.yaw_goal_tolerance"),
    "rpp_approach_distance": ("终点减速距离 · approach_velocity_scaling_dist", "局部控制", "m", RPP, CONTROLLER, "FollowPath.approach_velocity_scaling_dist"),
    "rpp_approach_min_speed": ("终点接近最小线速度 · min_approach_linear_velocity", "局部控制", "m/s", RPP, CONTROLLER, "FollowPath.min_approach_linear_velocity"),
    "progress_distance": ("最小进展距离 · required_movement_radius", "导航恢复", "m", BASE, CONTROLLER, "progress_checker.required_movement_radius"),
    "progress_time": ("进展超时时间 · movement_time_allowance", "导航恢复", "s", BASE, CONTROLLER, "progress_checker.movement_time_allowance"),
}
SHARED = {
    "forward_radius": ((RPP, CONTROLLER, "FollowPath.minimum_turning_radius"),),
    "geometry_local_inflation_radius": ((BASE, GLOBAL, "inflation_layer.inflation_radius"),),
    "costmap_scaling": (
        (BASE, GLOBAL, "inflation_layer.cost_scaling_factor"),
        (RPP, CONTROLLER, "FollowPath.inflation_cost_scaling_factor"),
    ),
    "geometry_local_footprint_padding": ((BASE, GLOBAL, "footprint_padding"),),
}
SHARED_BOUNDS = {
    "geometry_local_inflation_radius": (0., 3.),
    "costmap_scaling": (.01, 20.),
    "geometry_local_footprint_padding": (0., .30),
}
ALIASES = {
    "local_inflation": "geometry_local_inflation_radius",
    "global_inflation": "geometry_local_inflation_radius",
    "costmap_radius": "geometry_local_inflation_radius",
    "local_decay": "costmap_scaling",
    "global_decay": "costmap_scaling",
    "costmap_padding": "geometry_local_footprint_padding",
    "forward_tolerance": "planner_tolerance",
    "forward_allow_unknown": "planner_allow_unknown",
    "forward_iterations": "planner_max_iterations",
    "forward_planning_time": "planner_max_planning_time",
    "desired_speed": "rpp_desired_linear_vel",
    "lookahead": "rpp_lookahead_dist",
    "min_lookahead": "rpp_min_lookahead_dist",
    "max_lookahead": "rpp_max_lookahead_dist",
    "lookahead_time": "rpp_lookahead_time",
    "approach_speed": "rpp_approach_min_speed",
    "approach_distance": "rpp_approach_distance",
    "goal_distance": "goal_xy_tolerance",
    "goal_heading": "goal_yaw_tolerance",
    "progress_radius": "progress_distance",
}
HELP = {
    "forward_radius": "统一全局规划和局部控制的阿克曼最小转弯半径。",
    "geometry_local_inflation_radius": "同时设置全局和局部代价地图的障碍膨胀范围。增大后路径更远离障碍，但窄道可能不可通行。",
    "costmap_scaling": "同时设置全局和局部代价地图的代价衰减速度。增大后代价下降更快；减小后高代价影响更宽。124 的 RPP 障碍减速计算跟随此值。",
    "geometry_local_footprint_padding": "同时设置全局和局部代价地图的车体额外余量。",
    "geometry_local_resolution": "设置局部代价地图的单格尺寸。格子越细，边缘越精确，地图更新开销也越高。",
    "goal_xy_tolerance": "设置 Nav2 位姿目标的到点距离容差。124 的无方向航点按 10 cm 位置容差停止。",
}


def yaml_field(document, node, name):
    for key in [*node.lstrip("/").split("/"), "ros__parameters", *name.split(".")]:
        document = next(value for label, value in document.value if label.value == key)
    return document


def persist(path, text):
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, path.stat().st_mode & 0o777)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class NavigationParameters:
    def __init__(self, node):
        self.lock = threading.Lock()
        nodes = {field[4] for field in FIELDS.values()}
        nodes.update(node for targets in SHARED.values() for _, node, _ in targets)
        self.clients = {
            name: node.create_client(SetParametersAtomically, name + "/set_parameters_atomically")
            for name in nodes
        }
        self.read_clients = {
            name: node.create_client(GetParameters, name + "/get_parameters")
            for name in nodes if name in (LOCAL, GLOBAL, CONTROLLER, PLANNER)
        }

    def read(self):
        with self.lock:
            documents = {file: yaml.compose((CONFIG / file).read_text())
                         for file in (BASE, RPP)}
            fields = []
            for key, (label, group, unit, file, node, name) in FIELDS.items():
                targets = ((file, node, name), *SHARED.get(key, ()))
                values = [
                    yaml.safe_load(yaml_field(documents[config], owner, param).value)
                    for config, owner, param in targets
                ]
                mixed = not all(value == values[0] for value in values)
                fields.append({
                    "id": key, "label": label, "group": group, "unit": unit,
                    "node": " + ".join(dict.fromkeys(owner for _, owner, _ in targets)),
                    "parameter": name, "value": None if mixed else values[0],
                    "mixed": mixed, "help": HELP.get(key, ""),
                    "integer": type(values[0]) is int,
                    "bounds": SHARED_BOUNDS.get(key),
                })
            return {
                "fields": fields,
                "footprint": yaml_field(documents[BASE], LOCAL, "footprint").value,
                "mola": self.read_mola(),
            }

    def read_mola(self):
        metrics = {}
        try:
            pipeline = (MOLA / "mola_lidar_odometry/pipelines/lidar3d-gicp.yaml").read_text()
            runtime = json.loads((MOLA / "mola_state_estimation_simple/config/tracked-integrated-live-runtime.json").read_text())
            points = re.search(r"^\s*desired_output_point_count:\s*(\d+)\s*$", pipeline, re.M)
            if points:
                metrics["sample_count"] = int(points.group(1))
            migration = Path.home() / "omnifleet_a2_backups/robot124-mola105-migration-20261121"
            if (migration / "restore-snapshot-verified").exists() and Path(
                "/etc/systemd/system/omnifleet-a2-mola.service.d/96-mola105-runtime.conf"
            ).exists():
                runtime = json.loads((migration / "release105/runtime124.json").read_text())
                metrics["map_sample_count"] = int(runtime["MOLA_DECIMATED_POINTS_MAP"])
                metrics["icp_sample_count"] = int(runtime["MOLA_DECIMATED_POINTS_ICP"])
            voxel_size = runtime.get("MOLA_CLOUD_DECIMATION_VOXEL_SIZE_MAP")
            if voxel_size is not None:
                metrics["voxel_size"] = float(voxel_size)
            grid = MAP_GRID.read_text()
            limits = re.search(r"hits = \(z >= (-?[\d.]+)\) & \(z <= (-?[\d.]+)\)", grid)
            if limits:
                metrics["heights"] = [float(x) for x in limits.groups()]
        except (OSError, ValueError):
            pass
        return metrics

    @staticmethod
    def request(client, message):
        future = client.call_async(message)
        done = threading.Event()
        future.add_done_callback(lambda _: done.set())
        if not done.wait(2):
            client.remove_pending_request(future)
            raise TimeoutError("ROS 参数服务未确认")
        return future.result()

    def set_shared(self, key, value):
        if type(value) not in (float, int) or not math.isfinite(value):
            raise ValueError("参数须为有限数值")
        value = float(value)
        bounds = SHARED_BOUNDS.get(key)
        if bounds is not None and not bounds[0] <= value <= bounds[1]:
            raise ValueError(f"允许范围 {bounds[0]:g} 至 {bounds[1]:g}")
        targets = (FIELDS[key][3:], *SHARED[key])
        with self.lock:
            sources = {file: (CONFIG / file).read_text() for file, _, _ in targets}
            edits = {file: [] for file in sources}
            docs = {file: yaml.compose(text) for file, text in sources.items()}
            for file, node, name in targets:
                field = yaml_field(docs[file], node, name)
                edits[file].append((field.start_mark.index, field.end_mark.index))
            updated = dict(sources)
            for file, positions in edits.items():
                text = updated[file]
                for start, end in sorted(positions, reverse=True):
                    text = text[:start] + json.dumps(value) + text[end:]
                yaml.safe_load(text)
                updated[file] = text

            live = {}
            if all(self.clients[node].service_is_ready() and self.read_clients[node].service_is_ready()
                   for _, node, _ in targets):
                try:
                    for _, node, name in targets:
                        current = self.request(self.read_clients[node], GetParameters.Request(names=[name])).values
                        if len(current) != 1 or current[0].type != ParameterType.PARAMETER_DOUBLE:
                            raise ValueError("当前导航参数尚未加载")
                        live[node, name] = current[0]
                except (OSError, ValueError):
                    live.clear()

            written = []
            attempted = []
            try:
                for file, text in updated.items():
                    persist(CONFIG / file, text)
                    written.append(file)
                if not live:
                    return {"saved": True, "applied": False, "value": value,
                            "message": "已统一保存，导航服务恢复或重启后生效"}
                desired = ParameterValue(type=ParameterType.PARAMETER_DOUBLE, double_value=value)
                for _, node, name in targets:
                    attempted.append((node, name))
                    self.apply_parameter(node, name, desired)
                for node, name in attempted:
                    actual = self.request(self.read_clients[node], GetParameters.Request(names=[name])).values[0]
                    if actual.type != desired.type or actual.double_value != value:
                        raise ValueError(f"{node} 回读值不一致")
            except (OSError, ValueError) as error:
                issues = []
                for node, name in reversed(attempted):
                    try:
                        self.apply_parameter(node, name, live[node, name])
                    except (OSError, ValueError):
                        issues.append(node)
                for file in reversed(written):
                    try:
                        persist(CONFIG / file, sources[file])
                    except OSError:
                        issues.append(file)
                if issues:
                    raise ValueError(f"保存失败，以下项回滚未确认：{', '.join(issues)}") from error
                raise ValueError(f"联动保存失败，已恢复旧值：{error}") from error
            return {"saved": True, "applied": True, "value": value,
                    "message": "已永久保存，全局与局部回读一致"}

    def apply_parameter(self, node, name, value):
        param = Parameter(name=name, value=value)
        result = self.request(
            self.clients[node], SetParametersAtomically.Request(parameters=[param])
        ).result
        if not result.successful:
            raise ValueError(f"{node}：{result.reason or 'ROS 拒绝参数'}")

    def set(self, key, value):
        if not isinstance(key, str):
            raise ValueError("未知参数")
        key = ALIASES.get(key, key)
        if key not in FIELDS:
            raise ValueError("未知参数")
        if key in SHARED:
            return self.set_shared(key, value)
        _, _, _, file, node, name = FIELDS[key]
        path = CONFIG / file
        with self.lock:
            previous = path.read_text()
            field = yaml_field(yaml.compose(previous), node, name)
            kind = type(yaml.safe_load(field.value))
            if kind is bool:
                if type(value) is not bool:
                    raise ValueError("参数须为布尔值")
                ros_value = ParameterValue(type=ParameterType.PARAMETER_BOOL, bool_value=value)
            elif kind is int:
                if type(value) is not int or not -(1 << 63) <= value < (1 << 63):
                    raise ValueError("参数须为整数")
                ros_value = ParameterValue(type=ParameterType.PARAMETER_INTEGER, integer_value=value)
            else:
                if type(value) not in (float, int) or not math.isfinite(value):
                    raise ValueError("参数须为有限数值")
                value = float(value)
                if key in ("rpp_desired_linear_vel", "rpp_curve_min_speed", "rpp_approach_min_speed"):
                    value = min(1.0, value)
                ros_value = ParameterValue(type=ParameterType.PARAMETER_DOUBLE, double_value=value)
            updated = previous[:field.start_mark.index] + json.dumps(value) + previous[field.end_mark.index:]
            yaml.safe_load(updated)
            persist(path, updated)
            client = self.clients[node]
            if not client.service_is_ready():
                return {"saved": True, "applied": False, "value": value, "message": "已保存，参数服务恢复或导航重启后读取"}
            param = Parameter(name=name, value=ros_value)
            future = client.call_async(SetParametersAtomically.Request(parameters=[param]))
            done = threading.Event()
            future.add_done_callback(lambda _: done.set())
            if not done.wait(2):
                client.remove_pending_request(future)
                return {"saved": True, "applied": False, "value": value, "message": "已保存，ROS 尚未确认"}
            result = future.result().result
            if not result.successful:
                persist(path, previous)
                raise ValueError(result.reason or "ROS 拒绝参数")
            return {"saved": True, "applied": True, "value": value, "message": "已永久保存，ROS 已接受"}

