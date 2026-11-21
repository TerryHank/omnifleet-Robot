"""Compact current configuration while preserving JSON evidence paths."""
import copy,json

def compact_snapshot(snapshot):
    compact=copy.deepcopy(snapshot)
    details=snapshot.get('parameter_details',{})
    active={key for key,item in details.items() if item.get('applicable') is True}
    # Preserve evidence for combined controls without sending duplicated controls.
    saved_keys=set(active)
    for key in active:
        for path in snapshot.get('parameter_evidence_paths',{}).get(key,[]):
            if path.startswith('/saved_parameters/'):
                saved_keys.add(path.split('/')[2].replace('~1','/').replace('~0','~'))
    for key,pair in {'costmap_radius':['local_radius','global_radius'],
                     'costmap_scaling':['local_scaling','global_scaling'],
                     'costmap_padding':['local_padding','global_padding']}.items():
        if key in active:saved_keys.update(pair)
    for field in ('parameter_catalog','parameter_details','parameter_evidence_paths'):
        compact[field]={k:v for k,v in compact.get(field,{}).items() if k in active}
    compact['saved_parameters']={k:v for k,v in compact.get('saved_parameters',{}).items() if k in saved_keys}
    allowed=set()
    for key in active:
        item=details[key]
        for name in item.get('ros_parameters',[]):allowed.add((item.get('node'),name))
        for pointer in snapshot.get('parameter_evidence_paths',{}).get(key,[]):
            parts=pointer.split('/')
            if len(parts)==4 and parts[1]=='live_parameters':
                allowed.add(tuple(part.replace('~1','/').replace('~0','~') for part in parts[2:]))
    # Drop only runtime values belonging to registered inactive controls; keep
    # extra runtime conditions and sensor/TF diagnostics used for reasoning.
    inactive=set()
    for key,item in details.items():
        if key not in active:
            inactive.update((item.get('node'),name) for name in item.get('ros_parameters',[]))
    for node,values in compact.get('live_parameters',{}).items():
        compact['live_parameters'][node]={k:v for k,v in values.items() if (node,k) not in inactive or (node,k) in allowed}
    compact.pop('foxglove',None)  # duplicate topic inventory already in visible_topics
    # Parameter descriptions live in the registry; names need not be repeated.
    for item in compact['parameter_details'].values():item.pop('label',None)
    raw=json.dumps(snapshot,ensure_ascii=False,separators=(',',':'),allow_nan=False)
    encoded=json.dumps(compact,ensure_ascii=False,separators=(',',':'),allow_nan=False)
    return compact,{'snapshot_bytes_before':len(raw.encode()),'snapshot_bytes_after':len(encoded.encode()),'active_parameter_count':len(active)}
