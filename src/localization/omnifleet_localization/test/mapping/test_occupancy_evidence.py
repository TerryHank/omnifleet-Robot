from omnifleet_localization.occupancy_evidence import (
    OccupancyEvidence,
    bresenham_free_cells,
)


def test_obstacle_requires_two_independent_windows():
    evidence = OccupancyEvidence(hit_threshold=2)
    evidence.observe({(4, 2)}, set(), 0.0)
    assert (4, 2) not in evidence.confirmed
    evidence.observe({(4, 2)}, set(), 1.0)
    assert (4, 2) in evidence.confirmed


def test_neighboring_hit_confirms_without_drawing_inflation():
    evidence = OccupancyEvidence(hit_threshold=2, hit_tolerance_cells=1)
    evidence.observe({(4, 2)}, set(), 0.0)
    evidence.observe({(5, 2)}, set(), 1.0)
    assert evidence.confirmed == {(4, 2), (5, 2)}


def test_neighboring_wall_cells_are_not_collapsed_to_one_coordinate():
    evidence = OccupancyEvidence(hit_threshold=2, hit_tolerance_cells=1)
    evidence.observe({(4, 2), (5, 2), (6, 2)}, set(), 0.0)
    evidence.observe({(4, 2), (5, 2), (6, 2)}, set(), 1.0)
    assert evidence.confirmed == {(4, 2), (5, 2), (6, 2)}


def test_large_history_keeps_neighbor_confirmation_semantics():
    evidence = OccupancyEvidence(
        hit_threshold=3,
        hit_window_size=4,
        hit_tolerance_cells=1,
    )
    noise = {(x, 50) for x in range(2000)}
    evidence.observe(noise | {(10, 10)}, set(), 0.0)
    evidence.observe(noise | {(11, 10)}, set(), 1.0)
    evidence.observe(noise | {(10, 11)}, set(), 2.0)
    assert {(10, 10), (11, 10), (10, 11)} <= evidence.confirmed


def test_low_quality_endpoint_needs_persistent_kn_support():
    evidence = OccupancyEvidence(
        hit_threshold=5,
        hit_window_size=10,
        persistent_hit_threshold=8,
        persistent_hit_window_size=12,
    )
    for index in range(7):
        evidence.observe({(2, 2)}, set(), float(index), quality_cells=set())
    assert (2, 2) not in evidence.confirmed
    evidence.observe({(2, 2)}, set(), 7.0, quality_cells=set())
    assert (2, 2) in evidence.confirmed


def test_strong_structure_uses_faster_three_of_four_policy():
    evidence = OccupancyEvidence(
        hit_threshold=5,
        strong_hit_threshold=3,
        strong_hit_window_size=4,
    )
    for index in range(2):
        evidence.observe(
            {(8, 8)}, set(), float(index), strong_cells={(8, 8)}, quality_cells=set()
        )
    assert (8, 8) not in evidence.confirmed
    evidence.observe(
        {(8, 8)}, set(), 2.0, strong_cells={(8, 8)}, quality_cells=set()
    )
    assert (8, 8) in evidence.confirmed


def test_hits_outside_bounded_window_do_not_accumulate_forever():
    evidence = OccupancyEvidence(hit_threshold=3, hit_window_size=4)
    evidence.observe({(1, 1)}, set(), 0.0)
    for index in range(1, 5):
        evidence.observe(set(), set(), float(index))
    evidence.observe({(1, 1)}, set(), 5.0)
    evidence.observe({(1, 1)}, set(), 6.0)
    assert (1, 1) not in evidence.confirmed


def test_single_scan_obstacle_candidate_expires():
    evidence = OccupancyEvidence(candidate_ttl=2.0)
    evidence.observe({(1, 1)}, set(), 0.0)
    evidence.observe(set(), set(), 2.1)
    assert (1, 1) not in evidence.candidates


def test_unknown_cell_needs_three_free_windows():
    evidence = OccupancyEvidence(free_threshold=3)
    evidence.observe(set(), {(2, 3)}, 0.0)
    evidence.observe(set(), {(2, 3)}, 0.5)
    assert (2, 3) not in evidence.known_free
    evidence.observe(set(), {(2, 3)}, 1.0)
    assert (2, 3) in evidence.known_free


def test_single_free_candidate_expires_without_clearing_unknown():
    evidence = OccupancyEvidence(free_threshold=3, free_candidate_ttl=1.0)
    evidence.observe(set(), {(8, 9)}, 0.0)
    evidence.observe(set(), set(), 1.1)
    assert (8, 9) not in evidence.free_candidates
    assert (8, 9) not in evidence.known_free


def test_confirmed_obstacle_needs_three_free_rays_to_clear():
    evidence = OccupancyEvidence(
        hit_threshold=1, miss_threshold=3, free_threshold=3
    )
    evidence.observe({(1, 1)}, set(), 0.0)
    evidence.observe(set(), {(1, 1)}, 1.0)
    evidence.observe(set(), {(1, 1)}, 2.0)
    assert (1, 1) in evidence.confirmed
    evidence.observe(set(), {(1, 1)}, 3.0)
    assert (1, 1) not in evidence.confirmed
    assert (1, 1) in evidence.known_free


def test_obstacle_wins_same_window_conflict():
    evidence = OccupancyEvidence(hit_threshold=1, free_threshold=1)
    evidence.observe({(3, 3)}, {(3, 3)}, 0.0)
    assert (3, 3) in evidence.confirmed
    assert (3, 3) not in evidence.known_free


def test_confirmed_wall_does_not_decay_when_unobserved():
    evidence = OccupancyEvidence(hit_threshold=1, candidate_ttl=2.0)
    evidence.observe({(7, 8)}, set(), 0.0)
    evidence.observe(set(), set(), 20.0)
    assert (7, 8) in evidence.confirmed


def test_stale_confirmed_wall_stays_drawn_but_stops_guarding_rays():
    evidence = OccupancyEvidence(hit_threshold=1)
    evidence.observe({(7, 8)}, set(), 0.0)
    assert evidence.active_wall_guards(1.0, 3.0) == {(7, 8)}
    assert evidence.active_wall_guards(4.0, 3.0) == set()
    assert (7, 8) in evidence.confirmed


def test_unconfirmed_candidate_does_not_erase_confirmed_free_cell():
    evidence = OccupancyEvidence(hit_threshold=5, free_threshold=1)
    evidence.observe(set(), {(3, 4)}, 0.0)
    evidence.observe({(3, 4)}, set(), 1.0, quality_cells=set())
    assert (3, 4) in evidence.known_free
    assert (3, 4) not in evidence.confirmed


def test_raytrace_excludes_obstacle_endpoint():
    assert bresenham_free_cells((0, 0), (3, 0)) == [(0, 0), (1, 0), (2, 0)]
