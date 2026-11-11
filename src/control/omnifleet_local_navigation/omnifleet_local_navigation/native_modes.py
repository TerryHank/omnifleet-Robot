"""Native Nav2 execution inside the existing FLEET navigation owner."""
import hashlib
import math
from pathlib import Path
from tempfile import NamedTemporaryFile

from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.task import Future

from .scope import topic

NATIVE_BACKENDS = ('nav2_single', 'nav2_dynamic', 'nav2_waypoints')


def native_tree(planner, dynamic=False, *, goal_checker=None):
    # Use the same selectors, goal checker and recovery tree as local Fox.
    from ament_index_python.packages import get_package_share_directory
    import xml.etree.ElementTree as ET
    template=(Path(get_package_share_directory('omnifleet_planner')) /
              'behavior_trees/navigate_to_pose_with_selectors.xml').read_text()
    tree=ET.fromstring(template)
    tree.find('.//PlannerSelector').set('default_planner',planner)
    if goal_checker is not None:
        tree.find('.//FollowPath').set('goal_checker_id',goal_checker)
    if dynamic:
        compute=tree.find('.//ComputePathToPose');compute.set('goal','{updated_goal}')
        parent=next(node for node in tree.iter() if compute in list(node))
        index=list(parent).index(compute);parent.remove(compute)
        updater=ET.Element('GoalUpdater',input_goal='{goal}',output_goal='{updated_goal}')
        updater.append(compute);parent.insert(index,updater)
    text=ET.tostring(tree,encoding='unicode')
    folder = Path.home()/'.local/share/omnifleet_t2/native-modes'
    folder.mkdir(parents=True, exist_ok=True)
    path = folder/(hashlib.sha256(text.encode()).hexdigest()[:16]+'.xml')
    if not path.is_file():
        with NamedTemporaryFile(mode='w',encoding='utf-8',dir=folder,delete=False) as output:
            output.write(text)
        Path(output.name).replace(path)
    return str(path)


