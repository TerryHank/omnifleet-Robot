from enum import Enum


class State(str, Enum):
    IDLE = "IDLE"
    STOPPING = "STOPPING"
    VERIFYING_STOP = "VERIFYING_STOP"
    STARTING = "STARTING"
    VERIFYING_START = "VERIFYING_START"
    RUNNING = "RUNNING"
    SAFE_BRINGUP = "SAFE_BRINGUP"


class InvalidTransition(RuntimeError):
    pass


class SwitchStateMachine:
    def __init__(self):
        self.state = State.IDLE
        self.transaction_id = ""
        self.zero_speed_locked = False
        self.message = ""

    def begin(self, transaction_id: str):
        if self.state not in {State.IDLE, State.RUNNING, State.SAFE_BRINGUP}:
            raise InvalidTransition(f"cannot begin from {self.state.value}")
        if not transaction_id:
            raise ValueError("必须提供 transaction_id")
        self.transaction_id = transaction_id
        self.zero_speed_locked = False
        self.message = ""
        self.state = State.STOPPING

    def lock_zero_speed(self):
        self._require(State.STOPPING)
        self.zero_speed_locked = True

    def old_backend_stopped(self):
        self._require(State.STOPPING)
        if not self.zero_speed_locked:
            raise InvalidTransition("zero-speed lock must be active before stopping")
        self.state = State.VERIFYING_STOP

    def old_tf_owners_absent(self):
        self._require(State.VERIFYING_STOP)
        if not self.zero_speed_locked:
            raise InvalidTransition("zero-speed lock was lost")
        self.state = State.STARTING

    def backend_started(self):
        self._require(State.STARTING)
        if not self.zero_speed_locked:
            raise InvalidTransition("cannot start a backend without zero-speed lock")
        self.state = State.VERIFYING_START

    def stop_complete(self):
        self._require(State.STARTING)
        if not self.zero_speed_locked:
            raise InvalidTransition("stop completed without zero-speed lock")
        self.state = State.IDLE

    def backend_healthy(self):
        self._require(State.VERIFYING_START)
        if not self.zero_speed_locked:
            raise InvalidTransition("cannot complete an unlocked switch")
        self.state = State.RUNNING

    def unlock_zero_speed(self):
        self._require(State.RUNNING)
        self.zero_speed_locked = False

    def fail(self, message: str):
        self.message = message
        self.zero_speed_locked = True
        self.state = State.SAFE_BRINGUP

    def reset_idle(self):
        if self.state not in {State.SAFE_BRINGUP, State.RUNNING, State.IDLE}:
            raise InvalidTransition(f"cannot reset from {self.state.value}")
        self.state = State.IDLE
        self.zero_speed_locked = True

    def _require(self, expected: State):
        if self.state is not expected:
            raise InvalidTransition(
                f"expected {expected.value}, current state is {self.state.value}"
            )
