"""Resolve allowlisted parameter IDs to live config positions and documentation."""
import json
import os
import subprocess
import threading
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
DOCS = json.loads((HERE / 'parameter_docs.json').read_text())
PWM_VIEW = Path('/home/iecme/.local/share/omnifleet_t2/pwm-compensation-readback.yaml')


def location(path, keys, label='', tree=None):
    path = path.resolve(strict=True)
    node = tree if tree is not None else yaml.compose(path.read_text())
    for key in keys:
        if not isinstance(node, yaml.MappingNode):
            raise ValueError('配置结构不匹配')
        matches = [(k, v) for k, v in node.value if k.value == key]
        if len(matches) != 1:
            raise ValueError('配置项缺失或重复：' + key)
        key_node, node = matches[0]
    return {'path': str(path), 'line': key_node.start_mark.line + 1,
            'column': key_node.start_mark.column + 1, 'label': label or keys[-1]}


def catalog(specs, yaml_file, height_file, selected_file):
    result = {}
    trees = {}
    def locate(path, keys, label=''):
        path = path.resolve(strict=True)
        if path not in trees:
            trees[path] = yaml.compose(path.read_text())
        return location(path, keys, label, tree=trees[path])
    for key, spec in specs.items():
        targets = []
        for leaf in spec[1]:
            try:
                target = locate(yaml_file, spec[0] + (leaf,))
            except ValueError:
                if not key.startswith('geometry_'):
                    raise
                for length in range(len(spec[0]), 0, -1):
                    try:
                        target = locate(yaml_file, spec[0][:length], leaf + '（当前缺省；保存后写入）')
                        break
                    except ValueError:
                        continue
                else:
                    raise
            targets.append(target)
        result[key] = {'targets': targets, 'docs': DOCS[key]}
    for key, leaf in [('map_z_min', 'slice_z_min'), ('map_z_max', 'slice_z_max')]:
        result[key] = {'targets': [locate(height_file, (leaf,))], 'docs': DOCS[key]}
    for kind, key in [('global', 'global_planner_algorithm'), ('local', 'local_controller_algorithm')]:
        result[key] = {'targets': [locate(selected_file, (kind,))], 'docs': DOCS[key]}
    for key in ('pwm_compensation_m1', 'pwm_compensation_m2'):
        result[key] = {'targets': [locate(PWM_VIEW, (key,), '芯片参数回读（只读）')], 'docs': DOCS[key]}
    for key, local, global_ in [('costmap_radius', 'local_radius', 'global_radius'),
                               ('costmap_scaling', 'local_scaling', 'global_scaling'),
                               ('costmap_padding', 'local_padding', 'global_padding')]:
        result[key] = {'targets': [dict(result[local]['targets'][0], label='局部配置'),
                                  dict(result[global_]['targets'][0], label='全局配置')], 'docs': DOCS[key]}
    return result


def write_pwm_view(saved):
    values = {key: saved[key][key] for key in ('pwm_compensation_m1', 'pwm_compensation_m2')}
    text = '# STM32参数回读记录，实际参数保存在芯片Flash中。\n# 此文件只供查看；请在热参数面板中修改。\n' + yaml.safe_dump(values, sort_keys=False)
    if not PWM_VIEW.exists() or PWM_VIEW.read_text() != text:
        if PWM_VIEW.exists(): PWM_VIEW.chmod(0o644)
        PWM_VIEW.write_text(text)
        PWM_VIEW.chmod(0o444)


def open_target(catalog_, key, index=0, docs=False):
    if key not in catalog_ or type(index) is not int or index < 0:
        raise ValueError('不支持的参数链接')
    entry = catalog_[key]
    if docs:
        url = entry['docs']['url']
        args = ['/usr/bin/xdg-open', url]
        description = url
    else:
        if index >= len(entry['targets']): raise ValueError('配置位置不存在')
        target = entry['targets'][index]
        description = '{path}:{line}:{column}'.format(**target)
        args = ['/usr/bin/code', '--reuse-window', '--goto', description]
    env = os.environ.copy()
    env.update(DISPLAY=':0', XAUTHORITY='/run/user/1000/gdm/Xauthority',
               XDG_RUNTIME_DIR='/run/user/1000', DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus')
    process = subprocess.Popen(args, env=env, stdin=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    threading.Thread(target=process.wait, daemon=True).start()
    return description
