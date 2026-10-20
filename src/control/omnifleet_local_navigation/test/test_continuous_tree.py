from pathlib import Path
import xml.etree.ElementTree as ET
from ament_index_python.packages import get_package_share_directory
from omnifleet_local_navigation.continuous_tree import continuous_tree


def trees(frame='map', base='base_link'):
    template = (Path(get_package_share_directory('omnifleet_planner')) /
                'behavior_trees/navigate_to_pose_with_selectors.xml').read_text()
    return ET.fromstring(template), ET.fromstring(continuous_tree(template, frame, base, .25))


def test_same_algorithms_controller_goal_checker_and_recovery_rules():
    single, continuous = trees()
    for tag in ['PlannerSelector', 'ControllerSelector',
                'RecoveryAllowed', 'RoundRobin', 'Spin', 'Wait', 'BackUp']:
        assert [ET.tostring(x) for x in single.iter(tag)] == [ET.tostring(x) for x in continuous.iter(tag)]
    assert len(list(continuous.iter('RecoveryAllowed'))) == 3
    assert not list(continuous.iter('RateController'))
    single_follow = dict(single.find('.//FollowPath').attrib)
    single_follow['goal_checker_id'] = 'native_continuous_goal_checker'
    assert continuous.find('.//FollowPath').attrib == single_follow


def test_remaining_goals_use_the_shared_replanning_policy():
    single, continuous = trees()
    policy = continuous.find('.//ReplanningControl')
    expected = dict(single.find('.//ReplanningControl').attrib)
    expected.pop('goal')
    expected['goals'] = '{goals}'
    expected['path'] = '{path}'
    assert policy.attrib == expected
    planner = policy.find('.//ComputePathThroughPoses')
    assert planner.attrib == {'goals': '{goals}', 'path': '{path}', 'planner_id': '{selected_planner}'}
    assert not list(continuous.iter('ComputePathToPose'))


def test_progress_updates_outside_periodic_planning_without_final_stop_changes():
    _, continuous = trees('robot_113/map', 'robot_113/base_link')
    pipeline = continuous.find('.//PipelineSequence')
    tags = [node.tag for node in pipeline]
    assert tags.index('RemovePassedGoals') + 1 == tags.index('ReplanningControl')
    passed = pipeline.find('RemovePassedGoals')
    assert passed.attrib == {'input_goals': '{goals}', 'output_goals': '{goals}',
                             'radius': '0.25', 'global_frame': 'robot_113/map',
                             'robot_base_frame': 'robot_113/base_link'}
    assert continuous.find('.//FollowPath').get('goal_checker_id') == 'native_continuous_goal_checker'
    assert tags.index('PublishNativeWaypointProgress') + 1 == tags.index('RecoveryNode')
    assert pipeline.find('PublishNativeWaypointProgress').attrib == {'goals': '{goals}', 'path': '{path}'}


def test_single_goal_policy_changes_are_inherited():
    template = '<root><PipelineSequence><ReplanningControl goal="{goal}" planner_id="{p}"><ComputePathToPose goal="{goal}" path="{path}" planner_id="{p}"/></ReplanningControl><RecoveryNode><FollowPath path="{path}"/><RecoveryAllowed><Wait wait_duration="12"/></RecoveryAllowed></RecoveryNode></PipelineSequence></root>'
    continuous = ET.fromstring(continuous_tree(template, 'map', 'base_link', .3))
    assert continuous.find('.//Wait').get('wait_duration') == '12'
    assert continuous.find('.//ComputePathThroughPoses').get('planner_id') == '{p}'
