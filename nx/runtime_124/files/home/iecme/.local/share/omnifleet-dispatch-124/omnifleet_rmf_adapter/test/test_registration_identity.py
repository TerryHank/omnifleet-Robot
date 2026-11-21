from omnifleet_rmf_adapter.state import connection_states


def test_renamed_public_ids_keep_registration_epochs_bound_to_physical_connections():
    states = {
        'car1': {'robot_id': 'car1', 'connection_id': 'robot_113',
                 'samples': {'navigation': {'value': {'localization_epoch': 'session113'}}}},
        'lead_2': {'robot_id': 'lead_2', 'connection_id': 'robot_104',
                   'samples': {'navigation': {'value': {'localization_epoch': 'session104'}}}},
    }
    connections = connection_states({'robots': states})
    assert connections['robot_113'] is states['car1']
    assert connections['robot_104'] is states['lead_2']
    epochs = {r: s['samples']['navigation']['value']['localization_epoch']
              for r, s in connections.items()}
    assert epochs == {'robot_113': 'session113', 'robot_104': 'session104'}
    assert set(states) == {'car1', 'lead_2'}


def test_legacy_reports_without_connection_id_remain_readable():
    state = {'robot_id': 'robot_113'}
    assert connection_states({'robots': {'robot_113': state}}) == {'robot_113': state}
