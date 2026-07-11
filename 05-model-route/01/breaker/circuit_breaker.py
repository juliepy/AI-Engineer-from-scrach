import time
from dataclasses import dataclass

from .state import State


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    success_threshold: int = 2  # 半开阶段连续成功次数
    open_seconds: float = 30.0
    half_open_max_calls: int = 3

    def __post_init__(self):
        self.state = State.CLOSED
        self.failures = 0
        self.successes_half = 0
        self.open_until = 0.0
        self.half_open_inflight = 0

    def _trip(self):
        self.state = State.OPEN
        self.open_until = time.time() + self.open_seconds
        self.failures = 0
        self.successes_half = 0
        self.half_open_inflight = 0

    def allow(self) -> bool:
        now = time.time()
        if self.state == State.OPEN:
            if now >= self.open_until:
                self.state = State.HALF_OPEN
                self.successes_half = 0
                self.half_open_inflight = 0
            else:
                return False
        if self.state == State.HALF_OPEN:
            return self.half_open_inflight < self.half_open_max_calls
        return True

    def before_call(self):
        if self.state == State.HALF_OPEN:
            self.half_open_inflight += 1

    def on_success(self):
        if self.state == State.HALF_OPEN:
            self.successes_half += 1
            if self.successes_half >= self.success_threshold:
                self.state = State.CLOSED
                self.successes_half = 0
        else:
            self.failures = 0
        if self.state == State.HALF_OPEN:
            self.half_open_inflight = max(0, self.half_open_inflight - 1)

    def on_failure(self):
        self.failures += 1
        if self.state == State.HALF_OPEN or self.failures >= self.failure_threshold:
            self._trip()
        if self.state == State.HALF_OPEN:
            self.half_open_inflight = max(0, self.half_open_inflight - 1)
