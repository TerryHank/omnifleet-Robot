"""Construct map-related TF messages; publishers remain owned by existing nodes."""
import math
from geometry_msgs.msg import TransformStamped


def planar_transform(parent_frame, child_frame, pose, stamp):
    message = TransformStamped()
    message.header.frame_id = parent_frame
    message.child_frame_id = child_frame
    message.header.stamp = stamp
    message.transform.translation.x = pose[0]
    message.transform.translation.y = pose[1]
    message.transform.rotation.z = math.sin(pose[2] / 2)
    message.transform.rotation.w = math.cos(pose[2] / 2)
    return message
