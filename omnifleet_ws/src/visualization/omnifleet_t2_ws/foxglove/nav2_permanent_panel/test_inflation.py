import sys
from pathlib import Path
import yaml

sys.path.insert(0,str(Path(__file__).parent))
from test_geometry_fields import config,save,model,store

def test_point_model_keeps_identity_when_inflation_changes(config):
 model.save_mode('point',config,config.parent/'backup',navigation_active=False,state_age=.1,motion_age=3)
 before=model.profile_path(config).read_bytes()
 save(config,{'geometry_local_inflation_radius':.3,'geometry_global_inflation_radius':.3})
 assert model.state(config)['mode']=='point'
 assert model.profile_path(config).read_bytes()==before
 data=yaml.safe_load(config.read_text())
 for scope in ('local','global'):
  params=data[scope+'_costmap'][scope+'_costmap']['ros__parameters']
  assert params['robot_radius']==.01 and params['footprint']=='[]'
  assert params['inflation_layer']['inflation_radius']==.3

def test_body_model_keeps_identity_when_only_inflation_changes(config):
 model.capture_body(yaml.safe_load(config.read_text()),config)
 save(config,{'geometry_local_inflation_radius':.6,'geometry_global_inflation_radius':.6})
 assert model.state(config)['mode']=='body'

def test_only_inflation_geometry_supports_live_apply():
 hot={'geometry_local_inflation_radius','geometry_global_inflation_radius'}
 assert store.GEOMETRY_IDS-store.RESTART_ONLY==hot
