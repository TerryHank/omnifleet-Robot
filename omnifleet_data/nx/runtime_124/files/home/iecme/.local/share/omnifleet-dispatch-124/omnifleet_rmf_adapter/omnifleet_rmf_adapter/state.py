def summarize(payload, now, stale_after):
    ipc_age = now - payload['sample_monotonic']
    fresh = {
        key: 0 <= sample['age_seconds'] + ipc_age <= stale_after
        for key, sample in payload['samples'].items()
    }
    return {
        **payload,
        'ipc_age_seconds': ipc_age,
        'fresh': fresh,
        'transport_connected': 0 <= ipc_age <= stale_after and all(fresh.get(k, False) for k in ('navigation', 'control')),
        'online': 0 <= ipc_age <= stale_after and all(fresh.get(k, False) for k in ('pose', 'navigation', 'control')),
        'dispatch_enabled': False,
        'rmf_registered': False,
        'blockers': ['read_only_bootstrap', 'map_registration_not_validated',
                     'onboard_fleet_lease_not_implemented'],
    }


def connection_states(report):
    """Resolve public status entries to stable transport/cache connection IDs."""
    return {state.get("connection_id", key): state
            for key, state in report["robots"].items()}
