"""Hold safety output for RMF while retaining the current Nav2 action."""
import json
import time


def receive_pause(node, message):
    try:
        value=json.loads(message.data);job=node.current_job
        if (not job or job.source!='FLEET' or node.mode!='FLEET' or node.policy.canceling
                or not node.fleet_lease.matches(job.ticket,time.monotonic())
                or value.get('task_id')!=job.ticket.task_id
                or value.get('epoch')!=job.ticket.command_epoch
                or value.get('revision')!=job.ticket.revision
                or type(value.get('paused')) is not bool
                or type(value.get('sequence')) is not int
                or value['sequence']<=node.traffic_sequence):return
        node.traffic_sequence=value['sequence']
        paused=value['paused']
        if paused and not node.execution.active and not node.traffic_suspended:return
        if paused==node.traffic_paused:return
        node.traffic_paused=paused
        node.get_logger().info('traffic_pause '+json.dumps(value,ensure_ascii=False))
        if paused:
            node.traffic_suspended=True;node.inhibit_output()
            # Keep the existing backend action; traffic_suspended already blocks output.
    except (ValueError,TypeError,KeyError):
        return


def update_pause(node):
    if not node.traffic_suspended:return False
    job=node.current_job
    if (not job or job.source!='FLEET' or node.mode!='FLEET' or node.policy.canceling
            or node.estop or node.fleet_hold or getattr(node.execution,'failed',False)
            or not node.fleet_lease.matches(job.ticket,time.monotonic())):
        node.traffic_paused=node.traffic_suspended=False
        return False
    if node.execution.phase=='cancel_unconfirmed':
        node.traffic_paused=node.traffic_suspended=False
        node.stop_owned('交通暂停的内部导航取消尚未确认')
        return False
    if not node.stationary():return True
    node.navigation_active=True
    if node.traffic_paused:
        node.message='交通等待；保留本车任务，等待RMF放行'
        node.publish_catalog()
        return True
    node.traffic_suspended=False;node.inhibited=False
    node.armed=False;node.nav=[0.,0.];node.nav_time=0.
    if node.execution.active:node.arm_navigation_output()
    node.get_logger().info('traffic_resume task_id='+job.ticket.task_id+'；继续同一车端任务')
    return True
