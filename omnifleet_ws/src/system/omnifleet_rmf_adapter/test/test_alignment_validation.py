import math

import numpy as np

from omnifleet_rmf_adapter.alignment_validation import validate_projection


def fit(matrix):
    return {'full_transform':matrix.tolist(),'transform':[matrix[0,3],matrix[1,3],math.atan2(matrix[1,0],matrix[0,0])]}


def cloud():
    return np.random.default_rng(17).uniform([-3.,-4.,-.7],[4.,3.,2.6],(800,3))


def test_independent_height_origins_do_not_invalidate_correct_horizontal_navigation():
    source=cloud();matrix=np.eye(4);matrix[:3,3]=[.9,-.3,-.185]
    target=source+matrix[:3,3]
    best,margin,valid=validate_projection(source,target,[fit(matrix)])
    assert valid and margin>.08 and best['fitness']==best['planar_xy']['fitness']==1.
    assert best['inlier_rmse_m']<1e-10 and best['planar_xy']['inlier_rmse_m']<1e-10


def test_bad_three_dimensional_alignment_cannot_pass_on_dense_xy_overlap():
    source=cloud();target=source+[0.,0.,1.]
    best,_,valid=validate_projection(source,target,[fit(np.eye(4))])
    assert best['planar_xy']['fitness']==1. and not valid


def test_full_alignment_with_bad_planar_projection_is_rejected():
    source=cloud()[:80];source[:,:2]*=3;source[:,2]=2.5
    matrix=np.eye(4);angle=.25
    matrix[0,0]=matrix[2,2]=math.cos(angle);matrix[0,2]=math.sin(angle);matrix[2,0]=-math.sin(angle)
    target=source@matrix[:3,:3].T
    best,_,valid=validate_projection(source,target,[fit(matrix)])
    assert best['fitness']==1. and not valid


def test_ambiguity_uses_the_same_three_dimensional_score_for_every_candidate():
    source=cloud();matrix=np.eye(4);matrix[2,3]=-.185
    wrong=matrix.copy();wrong[0,3]=1.
    best,margin,valid=validate_projection(source,source+matrix[:3,3],[fit(wrong),fit(matrix)])
    assert valid and margin>.08 and best['transform'][0]==0.


def test_indistinguishable_candidates_still_fail_the_ambiguity_gate():
    source=cloud();identity=fit(np.eye(4))
    _,margin,valid=validate_projection(source,source,[identity,identity])
    assert margin==0. and not valid
