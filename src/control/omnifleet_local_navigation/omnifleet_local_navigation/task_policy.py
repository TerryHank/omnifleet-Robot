"""Source ownership is independent of coordinator availability."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Ticket:
    task_id: str
    source: str
    revision: int = 0
    command_epoch: str = ''

class TaskPolicy:
    def __init__(self):
        self.current=None
        self.pending=None
        self.local_override=False
        self.canceling=False

    def request(self,ticket):
        if ticket.source not in ('LOCAL','FLEET'):return 'INVALID_SOURCE'
        if ticket.source=='FLEET' and self.local_override:return 'LOCAL_OVERRIDE'
        if self.pending:return 'BUSY_CANCELING'
        if self.current:
            if (ticket.source==self.current.source and ticket.command_epoch==self.current.command_epoch and
                ticket.task_id==self.current.task_id and ticket.revision<=self.current.revision):return 'DUPLICATE'
            if ticket.source=='FLEET':return 'BUSY'
            self.local_override=True
            self.pending=ticket;self.canceling=True
            return 'CANCEL_THEN_TAKEOVER'
        self.current=ticket
        if ticket.source=='LOCAL':self.local_override=True
        return 'START'

    def canceled_and_stopped(self):
        if not self.canceling:return None
        self.current=self.pending;self.pending=None;self.canceling=False
        return self.current

    def update_fleet(self,ticket,stop_first):
        if (self.local_override or self.canceling or not self.current or
            self.current.source!='FLEET' or ticket.source!='FLEET' or
            ticket.task_id!=self.current.task_id or ticket.command_epoch!=self.current.command_epoch or ticket.revision<=self.current.revision):return False
        if stop_first:self.pending=ticket;self.canceling=True
        else:self.current=ticket
        return True

    def finish(self,ticket):
        if ticket!=self.current:return False
        if self.canceling:return False
        self.current=None
        return True

    def cancel(self):
        self.pending=None
        if self.current:self.canceling=True

    def release_to_fleet(self,stopped):
        if self.current or self.pending or self.canceling or not stopped:return False
        self.local_override=False
        return True

    def fleet_lost(self):
        if self.current and self.current.source=='FLEET':
            self.canceling=True
            return True
        return False
