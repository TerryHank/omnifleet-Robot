import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional


class TrafficDecision(Enum):
    NONE = "none"
    STOP = "stop"
    GO = "go"


@dataclass(frozen=True)
class TrafficTransition:
    decision: TrafficDecision
    signal: str
    stopped: bool
    consecutive_count: int


def parse_confirmed_signal(payload: Any) -> Optional[str]:
    """Return a confirmed cascade signal, ignoring malformed/partial results."""

    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except (TypeError, ValueError):
            return None
    if not isinstance(payload, Mapping):
        return None
    if payload.get("fusion_status") != "cascade_confirmed":
        return None
    signal = str(payload.get("fused_state", "")).strip().lower()
    return signal if signal in {"red", "yellow", "green"} else None


class TrafficLightPolicy:
    """Debounce red/yellow stop and green resume decisions."""

    def __init__(self, stop_confirmations: int = 2, go_confirmations: int = 3):
        if stop_confirmations < 1 or go_confirmations < 1:
            raise ValueError("traffic-light confirmation counts must be positive")
        self.stop_confirmations = int(stop_confirmations)
        self.go_confirmations = int(go_confirmations)
        self.stopped = False
        self._candidate = ""
        self._candidate_count = 0

    def observe(self, payload: Any) -> TrafficTransition:
        signal = parse_confirmed_signal(payload)
        candidate = "stop" if signal in {"red", "yellow"} else signal
        if candidate not in {"stop", "green"}:
            self._candidate = ""
            self._candidate_count = 0
            return TrafficTransition(TrafficDecision.NONE, "unknown", self.stopped, 0)

        if candidate == self._candidate:
            self._candidate_count += 1
        else:
            self._candidate = candidate
            self._candidate_count = 1

        decision = TrafficDecision.NONE
        if not self.stopped and candidate == "stop":
            if self._candidate_count >= self.stop_confirmations:
                self.stopped = True
                decision = TrafficDecision.STOP
        elif self.stopped and candidate == "green":
            if self._candidate_count >= self.go_confirmations:
                self.stopped = False
                decision = TrafficDecision.GO

        return TrafficTransition(
            decision,
            signal or "unknown",
            self.stopped,
            self._candidate_count,
        )
