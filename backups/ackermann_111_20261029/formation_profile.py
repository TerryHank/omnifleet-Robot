"""Read the selected controller's effective limits and footprint; never changes parameters."""
import json,math,time
from rcl_interfaces.srv import GetParameters

def value(parameter):
    return {1:parameter.bool_value,2:parameter.integer_value,3:parameter.double_value,
            4:parameter.string_value}.get(parameter.type)

class FormationProfile:
    def __init__(self,node):
        self.node=node;self.last=-10.;self.pending=None
        self.clients={key:node.create_client(GetParameters,path) for key,path in {
            'controller':'/controller_server/get_parameters',
            'geometry':'/local_costmap/local_costmap/get_parameters',
            'planner':'/planner_server/get_parameters'}.items()}

    def tick(self):
        now=time.monotonic();selected=self.node.selected_algorithms
        if self.pending:
            pending=self.pending
            if now-pending['started']>2.:
                for key,future in pending['futures'].items():
                    if not future.done():self.clients[key].remove_pending_request(future)
                self.pending=None;return
            if not all(f.done() for f in pending['futures'].values()):return
            self.pending=None
            try:
                results={key:{name:value(p) for name,p in zip(pending['names'][key],future.result().values)}
                         for key,future in pending['futures'].items()}
                controller=pending['controller'];raw=results['controller'];prefix=controller+'.'
                geometry=results['geometry'];footprint=json.loads(geometry['footprint'])
                # The initial supported tracking backend is the existing MPPI controller.
                limits={key:raw.get(prefix+param) for key,param in
                        {'forward':'vx_max','reverse':'vx_min','angular':'wz_max','accel':'ax_max','decel':'ax_min','angular_accel':'az_max'}.items()}
                if selected.get('controller')!=controller:return
                if not all(type(v) in (int,float) and math.isfinite(v) for v in limits.values()):return
                limits['reverse']=max(0.,-limits['reverse']);limits['decel']=abs(limits['decel'])
                if min(limits[k] for k in ['forward','angular','accel','decel','angular_accel'])<=0:return
                self.node.record('formation_profile',{'controller':controller,'motion_model':raw.get(prefix+'motion_model'),
                    'footprint':footprint,'padding':geometry['footprint_padding'],'robot_radius':geometry['robot_radius'],
                    'limits':limits,'allow_unknown':results['planner'].get(pending['planner']+'.allow_unknown',False),
                    'planning_seconds':results['planner'].get(pending['planner']+'.max_planning_time') or 3.})
            except (ValueError,TypeError,AttributeError,KeyError):pass
            return
        if now-self.last<2. or not all(c.service_is_ready() for c in self.clients.values()):return
        controller,planner=selected.get('controller'),selected.get('planner')
        if not controller or not planner:return
        names={'controller':[controller+'.'+n for n in ['vx_max','vx_min','wz_max','ax_max','ax_min','az_max','motion_model']],
               'geometry':['footprint','footprint_padding','robot_radius'],
               'planner':[planner+'.allow_unknown',planner+'.max_planning_time']}
        self.last=now;self.pending={'started':now,'controller':controller,'planner':planner,'names':names,
            'futures':{k:self.clients[k].call_async(GetParameters.Request(names=v)) for k,v in names.items()}}
