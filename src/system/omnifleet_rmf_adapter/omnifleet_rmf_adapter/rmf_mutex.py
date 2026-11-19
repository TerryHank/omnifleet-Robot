"""Bridge application corridor IDs to Open-RMF's native mutex supervisor."""
import time

from rclpy.qos import DurabilityPolicy, QoSProfile
from rmf_fleet_msgs.msg import MutexGroupRequest, MutexGroupStates
from rmf_traffic_msgs.msg import Participants


class RmfMutex:
    def __init__(self, node):
        self.node = node
        self.ids = {}
        self.assignments = {}
        self.claims = {}
        self.last_state = self.last_heartbeat = 0.
        qos = QoSProfile(depth=100, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.requests = node.create_publisher(MutexGroupRequest, '/mutex_group_request', qos)
        node.create_subscription(MutexGroupStates, '/mutex_group_states', self.states, qos)
        node.create_subscription(Participants, '/rmf_traffic/participants', self.participants, qos)

    def participants(self, message):
        owners = {'omnifleet_'+robot: robot for robot in self.node.maps.names}
        self.ids = {owners[p.description.owner]:p.id for p in message.participants
                    if p.description.owner in owners}

    def states(self, message):
        self.assignments = {a.group:a for a in message.assignments}
        self.last_state = time.monotonic()

    def connected(self):
        return self.requests.get_subscription_count() > 0 and time.monotonic()-self.last_state < 6

    def claim(self, group, robot):
        participant = self.ids.get(robot)
        if participant is None or not self.connected():
            return False
        key = (group, robot)
        request = self.claims.get(key)
        if request is None or request.claimant != participant:
            request = MutexGroupRequest(group=group, claimant=participant,
                        claim_time=self.node.get_clock().now().to_msg(), mode=MutexGroupRequest.MODE_LOCK)
            self.claims[key] = request
            self.requests.publish(request)
        reply = self.assignments.get(group)
        return bool(reply and reply.claimant == participant and reply.claim_time == request.claim_time)

    def tick(self, traffic):
        now = time.monotonic()
        for group, lock in traffic.saved['locks'].items():
            self.claim(group, lock['robot'])
        for key, request in list(self.claims.items()):
            group, robot = key
            job = traffic.owner.jobs.get(robot, {})
            held = traffic.saved['locks'].get(group, {}).get('robot') == robot
            waiting = (job.get('phase') in ('PLANNING','YIELDING','ARMING','BLOCKED')
                       and group in job.get('resources', []))
            if not (held or waiting):
                request.mode = MutexGroupRequest.MODE_RELEASE
                self.requests.publish(request)
                del self.claims[key]
            elif now-self.last_heartbeat >= 1:
                self.requests.publish(request)
        if now-self.last_heartbeat >= 1:
            self.last_heartbeat = now

    def holder(self, group):
        assignment = self.assignments.get(group)
        if not assignment or assignment.claimant == (1 << 64)-1:
            return None
        return next((r for r,p in self.ids.items() if p == assignment.claimant),
                    str(assignment.claimant))
