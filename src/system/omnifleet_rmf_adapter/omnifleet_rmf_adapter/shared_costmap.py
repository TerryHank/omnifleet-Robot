"""Independent WSL inflation for the shared occupancy map and fleet overview."""
from array import array
import copy
import json
import math
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt


FIELDS = {
    'inflation_radius': ('膨胀半径（米）', 0., 3., .01),
    'cost_scaling_factor': ('代价衰减系数', .01, 20., .01),
    'robot_radius': ('膨胀计算用车体半径（米）', .001, 3., .001),
    'footprint_padding': ('额外车体余量（米）', 0., .3, .01),
}
DEFAULTS = {'inflation_radius': .4, 'cost_scaling_factor': 3., 'robot_radius': .01, 'footprint_padding': 0.}


def inflate(grid, parameters):
    """Nav2 Humble exponential costs, exported using its OccupancyGrid scale."""
    result = copy.deepcopy(grid)
    values = np.asarray(grid.data, dtype=np.int16).reshape(grid.info.height, grid.info.width)
    lethal = values >= 100
    if not lethal.any() or parameters['inflation_radius'] == 0:
        return result
    distance = distance_transform_edt(~lethal)*grid.info.resolution
    inscribed = parameters['robot_radius']+parameters['footprint_padding']
    costs = np.floor(252.*np.exp(-parameters['cost_scaling_factor']*np.maximum(0., distance-inscribed))).astype(np.int16)
    costs[distance <= inscribed] = 253
    costs[lethal] = 254
    radius = math.ceil(parameters['inflation_radius']/grid.info.resolution)*grid.info.resolution
    costs[distance > radius] = 0
    translated = np.where(costs >= 253, costs-154, np.where(costs > 0, 1+(costs-1)*97//251, 0))
    # Preserve unknown cells except lethal/inscribed obstacles, as inflate_unknown=false.
    output = np.where((values >= 0) | (costs >= 253), np.maximum(np.maximum(values, 0), translated), -1)
    result.data = array('b', output.astype(np.int8).tobytes())
    return result


class SharedCostmap:
    def __init__(self, data):
        self.path = Path(data)/'shared_costmap.json'
        self.saved = json.loads(self.path.read_text()) if self.path.exists() else {
            'revision': 0, 'parameters': dict(DEFAULTS), 'seed': {'robot_name': 'car1', 'copied_once': True}}
        self.updated = False

    def configure(self, packet):
        if packet.get('shared_costmap_revision') != self.saved['revision']:
            raise ValueError('共享代价参数已被另一个前端修改，请刷新后重试')
        changes = packet.get('parameters')
        if not isinstance(changes, dict) or not changes or set(changes)-set(FIELDS):
            raise ValueError('共享代价参数字段无效')
        for key, value in changes.items():
            if type(value) not in (int, float) or not math.isfinite(value) or not FIELDS[key][1] <= value <= FIELDS[key][2]:
                raise ValueError('共享代价参数超出范围：'+FIELDS[key][0])
        saved = {**self.saved, 'parameters': {**self.saved['parameters'], **changes}, 'revision': self.saved['revision']+1}
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(saved, ensure_ascii=False, indent=2))
        temporary.replace(self.path)
        self.saved = saved
        return {'phase': 'saved', 'message': '已保存到 WSL；共享代价地图独立生效，车端导航参数保持不变',
                'shared_costmap_revision': saved['revision'], 'parameters': dict(saved['parameters'])}

    def snapshot(self):
        return {**copy.deepcopy(self.saved), 'ready': self.updated, 'owner': 'wsl',
                'topic': '/fleet/global_costmap/costmap', 'scope': '共享态势显示；实际行驶规划沿用各车 Nav2',
                'fields': [{'id': key, 'label': value[0], 'min': value[1], 'max': value[2], 'step': value[3]} for key, value in FIELDS.items()]}
