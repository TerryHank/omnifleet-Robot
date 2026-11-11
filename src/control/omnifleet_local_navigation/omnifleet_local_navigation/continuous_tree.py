"""Adapt the single-goal navigation policy for continuous waypoint tracking."""
import xml.etree.ElementTree as ET


def continuous_tree(template, frame_id, base_frame, pass_radius):
    root = ET.fromstring(template)
    pipeline = root.find('.//PipelineSequence')
    replanning = pipeline.find('ReplanningControl')
    replanning.attrib.pop('goal')
    replanning.set('goals', '{goals}')
    replanning.set('path', '{path}')
    planner = replanning.find('.//ComputePathToPose')
    planner.tag = 'ComputePathThroughPoses'
    planner.attrib.pop('goal')
    planner.set('goals', '{goals}')
    # Check progress even when periodic replanning is disabled. A changed
    # remaining-goal list causes the shared policy to plan the new segment.
    passed = ET.Element('RemovePassedGoals', {
        'input_goals': '{goals}', 'output_goals': '{goals}',
        'radius': str(pass_radius), 'global_frame': frame_id,
        'robot_base_frame': base_frame,
    })
    pipeline.insert(list(pipeline).index(replanning), passed)
    following = pipeline.find('RecoveryNode')
    pipeline.insert(list(pipeline).index(following), ET.Element('PublishNativeWaypointProgress', {'goals': '{goals}', 'path': '{path}'}))
    following.find('FollowPath').set('goal_checker_id', 'native_continuous_goal_checker')
    return ET.tostring(root, encoding='unicode')
