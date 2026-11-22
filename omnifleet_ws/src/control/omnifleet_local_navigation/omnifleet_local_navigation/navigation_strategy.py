"""Persist the strategy selected for the next onboard navigation task."""
import json
import os
from pathlib import Path

STRATEGIES = ('sequential', 'through_poses')
STRATEGY_FILE = Path.home()/'.local/share/omnifleet_t2/navigation-strategy.json'


def navigation_strategy(path=STRATEGY_FILE):
    if not path.exists():
        return 'sequential'
    value = json.loads(path.read_text())['strategy']
    if value not in STRATEGIES:
        raise ValueError('导航策略无效')
    return value


def save_navigation_strategy(value, path=STRATEGY_FILE):
    if value not in STRATEGIES:
        raise ValueError('导航策略只能是 sequential 或 through_poses')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name+f'.tmp-{os.getpid()}')
    temporary.write_text(json.dumps({'strategy': value})+'\n')
    temporary.replace(path)
    return {'strategy': navigation_strategy(path), 'applies_to': 'next_task'}
