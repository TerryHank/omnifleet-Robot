import json
from pathlib import Path

import pytest

root = Path(__file__).resolve().parent


from omnifleet_rmf_adapter.alignment_validation import independently_corroborated


def recorded():
    fixture=json.loads((root/'data/partial-registration-reboot.json').read_text())
    return fixture['best'],fixture['margin'],fixture['grid']


def test_reboot_partial_map_is_corroborated_in_the_navigation_plane():
    best,margin,grid=recorded()
    assert best['overlap_region']['reverse_fitness']<.6
    assert independently_corroborated(best,margin,grid)


@pytest.mark.parametrize('failure', ['translation', 'yaw', 'cloud_ambiguity', 'grid_ambiguity',
                                    'cloud_match', 'cloud_residual', 'planar_match', 'planar_residual',
                                    'planar_region', 'grid_region', 'grid_source'])
def test_partial_map_still_requires_complete_independent_evidence(failure):
    best, margin, grid = recorded()
    if failure == 'translation': grid['best']['transform'][0] += .3
    elif failure == 'yaw': grid['best']['transform'][2] += .2
    elif failure == 'cloud_ambiguity': margin = .01
    elif failure == 'grid_ambiguity':
        grid['distinct_candidate_margin'] = .01
        grid['best']['overlap_region_margin'] = .01
    elif failure == 'cloud_match': best['fitness'] = .5
    elif failure == 'cloud_residual': best['inlier_rmse_m'] = .12
    elif failure == 'planar_match': best['planar_xy']['fitness'] = .7
    elif failure == 'planar_residual': best['planar_xy']['inlier_rmse_m'] = .12
    elif failure == 'planar_region': best['planar_xy']['overlap_region']['reverse_fitness'] = .3
    elif failure == 'grid_region': grid['best']['overlap_region']['reverse_fitness'] = .3
    elif failure == 'grid_source': grid['best']['source_overlap'] = .3
    result=independently_corroborated(best, margin, grid)
    assert type(result) is bool
    assert json.loads(json.dumps({'validated': result})) == {'validated': False}
