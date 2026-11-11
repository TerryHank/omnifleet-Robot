"""Stable user-facing descriptions for navigation errors shown in Foxglove."""
import re


NAVIGATION_ERROR_MAP = {
    "ordered_route_lateral_deviation": {
        "patterns": (r"ordered route lateral deviation exceeds",),
        "title": "当前顺序路段距离超限",
        "meaning": "当前定位到已确认顺序路段的距离持续超过0.30米。该距离与进度搜索窗口误差分别计算；仍需核对真实位置。",
        "action": "查看失败记录中的定位、当前顺序路段和代价地图，确认是实际偏离还是定位异常。",
        "priority": 5,
    },
    "ordered_route_progress_mismatch": {
        "patterns": (r"ordered route progress matching failed", r"ordered route progress version mismatch",),
        "title": "路线进度匹配失效",
        "meaning": "车辆定位与当前允许的进度区间或路径版本不一致，持续等待后仍未恢复；不等同于真实路径偏离。",
        "action": "查看任务与路径版本、检查点、搜索区间、累计预算及控制器确认记录，不能只放宽距离门限。",
        "priority": 5,
    },
    "ordered_route_progress_unavailable": {
        "patterns": (r"ordered route progress state unavailable",),
        "title": "控制器未取得有效路线进度",
        "meaning": "MPPI未收到与当前执行路径匹配且新鲜的BT进度快照，已保持零速。",
        "action": "检查执行状态话题、路径版本与时间戳，确认BT仍在正常更新。",
        "priority": 5,
    },
    "ordered_route_deviation": {
        "patterns": (
            r"deviated from ordered route",
            r"ordered route tracking deviation exceeds",
        ),
        "title": "有序路线进度偏离",
        "meaning": "路线进度游标与机器人当前所在的顺序路径段相差超过0.30米；这不一定表示车身真的离开了整条路径。",
        "action": "检查实际执行路径、当前航点、进度游标和失败前的定位采样；折返或重叠路线要确认游标没有落后或跳段。",
        "priority": 5,
    },
    "stale_localization": {
        "patterns": (r"stale localization transform", r"MOLA位姿/TF不新鲜"),
        "title": "定位数据过期",
        "meaning": "导航使用的地图到车体坐标变换超过新鲜度要求，系统已停止继续执行。",
        "action": "检查点云时间、MOLA处理耗时、TF时间戳和系统时钟；不要通过放宽门限掩盖持续延迟。",
        "priority": 5,
    },
    "missing_localization": {
        "patterns": (r"missing localization transform", r"找不到.*(?:map|地图).*base_link.*TF"),
        "title": "缺少定位坐标变换",
        "meaning": "当前无法取得地图到车体的定位变换。",
        "action": "确认MOLA仍在运行并持续发布位姿，检查map、base_link及命名空间是否一致。",
        "priority": 5,
    },
    "initial_localization_timeout": {
        "patterns": (
            r"initial localization did not stabilize",
            r"initial localization stability timeout",
            r"连续段初始化超时",
        ),
        "title": "启动定位未稳定",
        "meaning": "连续路线启动阶段没有在限定时间内取得持续新鲜的定位。",
        "action": "保持车辆静止，检查MOLA位姿与TF是否连续更新，再重新开始路线。",
        "priority": 5,
    },
    "localization_jump": {
        "patterns": (r"localization pose jumped", r"定位.*跳变"),
        "title": "定位发生跳变",
        "meaning": "相邻定位结果的位移超过车辆在该时间内可能产生的运动。",
        "action": "检查重定位、地图匹配、雷达时间戳和点云重影；确认真实位置后再启动导航。",
        "priority": 5,
    },
    "global_costmap_stale": {
        "patterns": (r"global costmap not fresh", r"全局代价地图.*(?:过期|未更新|不新鲜)"),
        "title": "全局代价地图未更新",
        "meaning": "路线检查没有取得足够新的全局代价地图。",
        "action": "检查全局代价地图节点状态、地图与TF输入及更新时间，不要反复清图代替排查。",
        "priority": 4,
    },
    "route_goals_changed": {
        "patterns": (r"route goals changed while tracking", r"协同路线已修改"),
        "title": "执行中的路线被修改",
        "meaning": "当前目标序列在跟踪期间发生变化，旧任务不能继续安全执行。",
        "action": "等待旧目标取消和底盘停稳，再使用最新航点重新预检整条路线。",
        "priority": 4,
    },
    "missing_route_goals": {
        "patterns": (r"missing route goals", r"没有.*航点|航点列表为空"),
        "title": "路线没有有效航点",
        "meaning": "连续导航请求中没有可执行的目标点。",
        "action": "确认面板航点数量和路线文件内容，再重新提交。",
        "priority": 3,
    },
    "replanning_timeout": {
        "patterns": (r"replanning timeout", r"重规划.*超时"),
        "title": "剩余路线重规划超时",
        "meaning": "前方路线失效后，系统未能在时间预算内生成新的剩余路线。",
        "action": "检查阻塞位置、动态代价地图、规划器负载和未完成航点的顺序可达性。",
        "priority": 4,
    },
    "remaining_route_planning_failed": {
        "patterns": (r"remaining route planning failed", r"剩余路线.*规划失败"),
        "title": "剩余路线规划失败",
        "meaning": "当前点到尚未完成航点的有序路线无法规划。",
        "action": "检查每个未完成航点是否在空闲区，并逐段确认地图中存在按顺序连通的通道。",
        "priority": 4,
    },
    "empty_planned_path": {
        "patterns": (r"empty planned path", r"规划结果.*空"),
        "title": "规划器返回空路径",
        "meaning": "规划动作结束但没有返回可跟踪的路径点。",
        "action": "检查规划器日志、起点和目标有效性，以及地图与坐标系。",
        "priority": 4,
    },
    "ordered_goals_not_visited": {
        "patterns": (r"planned path does not visit ordered goals",),
        "title": "规划路径没有依次经过航点",
        "meaning": "规划结果未能在允许误差内按顺序包含全部请求航点。",
        "action": "检查航点顺序、坐标系和每段可达性；不要使用直达最终点的路径代替。",
        "priority": 5,
    },
    "new_plan_start_mismatch": {
        "patterns": (r"new plan start no longer matches robot position",),
        "title": "新路径起点与车辆位置不一致",
        "meaning": "重规划完成时车辆位置已经与新路径起点相差过大。",
        "action": "检查重规划期间定位是否变化、路径是否使用最新起点，并核对TF时间。",
        "priority": 5,
    },
    "path_tracking_failed": {
        "patterns": (r"path tracking failed", r"navigation失败：action状态=6"),
        "title": "路径跟踪失败",
        "meaning": "Nav2控制阶段中止，连续路线没有完成。",
        "action": "查看此前最近一条更具体的控制器、定位或障碍错误；不要只凭最终状态修改参数。",
        "priority": 3,
    },
    "path_ended_early": {
        "patterns": (r"path ended before ordered waypoint verification",),
        "title": "路径提前结束",
        "meaning": "控制器报告路径完成时，仍有顺序航点没有被确认通过。",
        "action": "检查航点通过半径、路径累计进度和路径是否被错误裁剪。",
        "priority": 5,
    },
    "route_reference_outside_local_map": {
        "patterns": (r"ordered route reference outside local costmap",),
        "title": "有序路径不在局部代价地图内",
        "meaning": "当前用于控制的路径参考段无法映射到局部代价地图。",
        "action": "检查局部代价地图尺寸、原点、全局坐标系及车辆定位。",
        "priority": 4,
    },
    "start_blocked": {
        "patterns": (r"starting point in lethal space", r"start.*(?:occupied|lethal)"),
        "title": "规划起点被判为致命障碍",
        "meaning": "机器人当前位置在全局代价地图中属于不可通行区域。",
        "action": "分别检查静态地图、本车点云障碍和跨车障碍，并核对定位与车体轮廓。",
        "priority": 5,
    },
    "goal_blocked": {
        "patterns": (r"goal.*(?:occupied|lethal)", r"goal.*outside.*map", r"目标点.*(?:障碍|地图外)"),
        "title": "目标点不可用",
        "meaning": "目标位于障碍区、未知禁行区或地图边界外。",
        "action": "在当前地图选择明确空闲且能容纳车体的目标，并重新规划检查。",
        "priority": 4,
    },
    "no_global_path": {
        "patterns": (r"no valid path", r"no path.*found", r"failed to generate a valid path", r"路线预览规划失败"),
        "title": "未找到可通行的全局路径",
        "meaning": "规划器无法连接起点与目标或某两个顺序航点。",
        "action": "检查通道连通性、动态障碍、未知区域、车体轮廓与膨胀层，再定位具体失败段。",
        "priority": 4,
    },
    "no_local_control": {
        "patterns": (r"no (?:valid|legal) trajector", r"could not find a valid trajector", r"no valid control", r"collision detected ahead"),
        "title": "局部控制没有可行轨迹",
        "meaning": "当前局部环境中没有满足碰撞和运动约束的控制轨迹。",
        "action": "检查车辆周围真实障碍、瞬时飞点、局部代价地图和车体轮廓。",
        "priority": 4,
    },
    "progress_timeout": {
        "patterns": (r"failed to make progress",),
        "title": "车辆长时间没有取得进展",
        "meaning": "规定时间内的实际位姿变化没有达到进度检查要求。",
        "action": "检查底盘是否执行速度、车辆是否受阻以及定位是否真实变化，再看进度检查运行值。",
        "priority": 4,
    },
    "goal_safety_check_failed": {
        "patterns": (r"到点安全检查失败",),
        "title": "最终点车体安全检查失败",
        "meaning": "到点时完整车体轮廓覆盖了障碍、未知区或地图外区域。",
        "action": "将最终点移到能完整容纳车体的位置，并检查障碍来源。",
        "priority": 5,
    },
    "controller_patience_exceeded": {
        "patterns": (r"controller patience exceeded",),
        "title": "控制器连续无法输出有效控制",
        "meaning": "控制器错误持续超过允许等待时间，Nav2中止了路径跟踪。",
        "action": "查看此错误之前的具体警告；它通常是结果，不是最底层原因。",
        "priority": 2,
    },
    "action_rejected": {
        "patterns": (r"action请求被拒绝", r"本地模块拒绝目标", r"规划器拒绝请求"),
        "title": "导航请求被执行端拒绝",
        "meaning": "目标没有被对应的Nav2或本地导航接口接受。",
        "action": "检查执行接口是否就绪、是否已有任务，以及请求使用的action和命名空间。",
        "priority": 4,
    },
    "request_timeout": {
        "patterns": (r"请求超时", r"读取规划配置超时", r"提交失败", r"请求发送失败"),
        "title": "导航请求或配置读取超时",
        "meaning": "请求在限定时间内没有得到确定结果。",
        "action": "确认action服务仍在线，检查负载和通信；迟到结果不得自动启动后续航段。",
        "priority": 4,
    },
    "cancel_unconfirmed": {
        "patterns": (r"取消未确认", r"停止尚未确认", r"关闭前未确认取消导航"),
        "title": "导航取消尚未确认",
        "meaning": "系统已经要求停车，但旧目标是否完全结束仍不确定。",
        "action": "保持车辆停止，检查action服务和导航栈；确认旧目标终止前不要发送新目标。",
        "priority": 5,
    },
    "stop_not_confirmed": {
        "patterns": (r"段末未确认底盘停止", r"停靠期间底盘反馈不满足停止条件"),
        "title": "底盘停车状态未确认",
        "meaning": "段末或停靠期间的底盘反馈没有满足停止条件。",
        "action": "检查底盘速度反馈是否新鲜且实际为零，并确认车辆已经停稳。",
        "priority": 5,
    },
    "map_waypoint_io_failed": {
        "patterns": (r"地图航点(?:保存|加载)失败", r"无法加载已有路线", r"航点设置未保存"),
        "title": "航点文件读写失败",
        "meaning": "路线文件或地图关联航点文件没有成功读取或保存。",
        "action": "检查文件路径、权限、JSON格式和地图关联文件，修复后重新读取。",
        "priority": 3,
    },
    "goal_canceled": {
        "patterns": (r"action状态=5", r"client requested to cancel", r"goal canceled"),
        "title": "导航目标已取消",
        "meaning": "目标进入取消终态，没有到达最终点。",
        "action": "确认这是用户停止、任务接管还是故障保护触发，再决定是否重新开始。",
        "priority": 2,
    },
    "goal_failed": {
        "patterns": (r"goal fail(?:ed|d)", r"aborting handle", r"action状态=6"),
        "title": "Nav2目标失败",
        "meaning": "Nav2报告本次目标未完成；该消息是汇总结果。",
        "action": "查看它前面的具体规划、控制、定位或安全检查错误，优先按更具体的错误处理。",
        "priority": 1,
    },
}

_COMPILED = [
    (code, item, tuple(re.compile(pattern, re.IGNORECASE) for pattern in item["patterns"]))
    for code, item in NAVIGATION_ERROR_MAP.items()
]
_GENERIC_ERROR = re.compile(r"失败|超时|错误|拒绝|中止|未确认|failed|failure|timeout|error|abort", re.IGNORECASE)


def lookup_navigation_error(message, node=""):
    text = str(message or "").strip()
    for code, item, patterns in _COMPILED:
        if any(pattern.search(text) for pattern in patterns):
            return {
                "code": code,
                "title": item["title"],
                "meaning": item["meaning"],
                "action": item["action"],
                "raw": text[:1200],
                "node": str(node or "")[:200],
                "priority": item["priority"],
            }
    if _GENERIC_ERROR.search(text):
        return {
            "code": "unclassified_navigation_error",
            "title": "未分类的导航错误",
            "meaning": "系统报告了错误，但当前词典没有更具体的匹配项。",
            "action": "保留原始错误和发生时间，结合错误前后的规划、控制、定位及障碍日志诊断。",
            "raw": text[:1200],
            "node": str(node or "")[:200],
            "priority": 0,
        }
    return None
