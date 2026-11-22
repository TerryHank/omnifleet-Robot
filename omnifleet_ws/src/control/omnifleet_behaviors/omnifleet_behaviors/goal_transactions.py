from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Tuple
from uuid import uuid4


class Decision(Enum):
    START = "start"
    CANCEL = "cancel"
    WAIT = "wait"


@dataclass(frozen=True)
class GoalTransaction:
    transaction_id: str
    kind: str
    payload: Any


class GoalTransactions:
    """Serialize action goals so replacements wait for the prior result."""

    def __init__(self):
        self.current: Optional[GoalTransaction] = None
        self.pending: Optional[GoalTransaction] = None
        self.state = "idle"

    def submit(self, kind: str, payload: Any) -> Tuple[GoalTransaction, Decision]:
        transaction = GoalTransaction(uuid4().hex, kind, payload)
        if self.current is None:
            self.current = transaction
            self.state = "starting"
            return transaction, Decision.START

        self.pending = transaction
        if self.state == "active":
            self.state = "cancelling"
            return transaction, Decision.CANCEL
        return transaction, Decision.WAIT

    def goal_response(self, transaction_id: str, accepted: bool) -> Decision:
        if not accepted:
            _, decision = self.goal_rejected(transaction_id)
            return decision
        if self.current is None or self.current.transaction_id != transaction_id:
            return Decision.WAIT
        self.state = "active"
        if self.pending is not None:
            self.state = "cancelling"
            return Decision.CANCEL
        return Decision.WAIT

    def cancel_response(self, transaction_id: str) -> Decision:
        if self.current is None or self.current.transaction_id != transaction_id:
            return Decision.WAIT
        return Decision.WAIT

    def request_cancel(self) -> Decision:
        self.pending = None
        if self.current is None or self.state not in {"active", "cancelling"}:
            return Decision.WAIT
        self.state = "cancelling"
        return Decision.CANCEL

    def goal_rejected(
        self, transaction_id: str
    ) -> Tuple[Optional[GoalTransaction], Decision]:
        return self.result(transaction_id)

    def result(
        self, transaction_id: str
    ) -> Tuple[Optional[GoalTransaction], Decision]:
        if self.current is None or self.current.transaction_id != transaction_id:
            return None, Decision.WAIT
        self.current = None
        self.state = "idle"
        if self.pending is None:
            return None, Decision.WAIT
        promoted = self.pending
        self.pending = None
        self.current = promoted
        self.state = "starting"
        return promoted, Decision.START
