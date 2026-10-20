"""Validate model-selected links against the live parameter registry, never select answers."""
import json
import re

_MISSING = object()


def resolve_pointer(snapshot, path):
    if not isinstance(path, str) or not path.startswith('/') or len(path) > 512:
        return _MISSING
    value = snapshot
    try:
        for part in path.split('/')[1:]:
            part = part.replace('~1', '/').replace('~0', '~')
            value = value[int(part)] if isinstance(value, list) else value[part]
        return value if value is not None else _MISSING
    except (KeyError, TypeError, ValueError, IndexError):
        return _MISSING


def build_parameter_details(source, snapshot, specs, algorithms):
    """Use the panel's own help and YAML/plugin bindings as the model's registry."""
    help_text = {}
    for literal in re.findall(r'(?:const parameterHelp = |Object\.assign\(parameterHelp, )(\{[^\n]*\})', source):
        help_text.update(json.loads(literal))
    for key, quote, value in re.findall(r'parameterHelp\.(\w+)\s*=\s*([\"\'])(.*?)\2;', source):
        help_text[key] = value
    selected = snapshot.get('saved_algorithms', {}).copy()
    for kind, topic in [('local', '/controller_selector'), ('global', '/planner_selector')]:
        observed = snapshot.get('observations', {}).get(topic, {}).get('value')
        if observed:
            selected[kind] = next((key for key, option in algorithms[kind].items() if option[2] == observed), None)
    details = {}
    for key, label in snapshot['parameter_catalog'].items():
        entry = {'label': label, 'description': help_text.get(key, ''), 'scope': 'shared', 'applicable': True}
        spec = specs.get(key)
        if spec:
            entry.update(node=spec[2], ros_parameters=[spec[3]+leaf for leaf in spec[1]],
                         minimum=spec[4], maximum=spec[5], type=spec[6] if len(spec)>6 else 'double')
            for kind, options in algorithms.items():
                for algorithm, option in options.items():
                    if option[2] in spec[0]:
                        entry.update(scope=kind, algorithm=algorithm,
                                     applicable=selected.get(kind)==algorithm,
                                     selected_algorithm=selected.get(kind))
        details[key] = entry
    return details


def accepted_parameter_actions(result, question, snapshot):
    catalog = snapshot.get('parameter_catalog', {})
    details = snapshot.get('parameter_details', {})
    bindings = snapshot.get('parameter_evidence_paths', {})
    actions = result.get('parameter_actions', [])
    accepted = []
    if not isinstance(actions, list):
        return accepted
    for action in actions:
        if not isinstance(action, dict):
            continue
        key, intent, reason = action.get('id'), action.get('intent'), action.get('reason')
        if (not isinstance(key, str) or key not in catalog or key not in details
                or details[key].get('applicable') is not True
                or intent not in ('inspect', 'adjust')
                or not isinstance(reason, str) or len(reason.strip()) < 8):
            continue
        refs = action.get('evidence_refs', [])
        if not isinstance(refs, list) or not refs or any(resolve_pointer(snapshot, ref) is _MISSING for ref in refs):
            continue
        own = [ref for ref in refs if ref in bindings.get(key, [])]
        if not own:
            continue
        if intent == 'adjust':
            if not any(ref.startswith('/live_parameters/') for ref in own):
                continue
            if not any(ref.startswith(('/motion_window/', '/observations/', '/reported_error/', '/recent_errors/')) for ref in refs):
                continue
        if any(item['id'] == key for item in accepted):
            continue
        accepted.append({'id': key, 'intent': intent, 'reason': reason.strip()[:400], 'evidence_refs': refs[:6]})
        if len(accepted) >= 6:
            break
    return accepted
