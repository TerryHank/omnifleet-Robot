"""Receiver-clock control lease, independent of any coordinator implementation."""
import uuid


class FleetLease:
    def __init__(self, timeout=0.8):
        self.timeout=timeout;self.revoke()

    def revoke(self):
        self.epoch='';self.received=None;self.sequence=-1;self.task_id='';self.revision=0

    def fresh(self, now):
        return bool(self.epoch) and self.received is not None and 0<=now-self.received<=self.timeout

    def acquire(self, now):
        if self.fresh(now):return None
        self.revoke();self.epoch=uuid.uuid4().hex;self.received=now
        return self.epoch

    def renew(self, message, now):
        if not isinstance(message,dict) or not self.fresh(now) or message.get('epoch')!=self.epoch:return False
        seq=message.get('sequence');rev=message.get('revision');task=message.get('task_id')
        if type(seq) is not int or seq<=self.sequence or type(rev) is not int or rev<self.revision:return False
        if not isinstance(task,str) or len(task)>160 or (rev>0 and not task):return False
        if rev==self.revision and task!=self.task_id:return False
        self.sequence=seq;self.revision=rev;self.task_id=task;self.received=now
        return True

    def matches(self, ticket, now):
        return (self.fresh(now) and ticket.command_epoch==self.epoch and
                ticket.task_id==self.task_id and ticket.revision==self.revision and self.revision>0)
