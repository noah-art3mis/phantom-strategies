"""Single-process admission limits; all accepted attempts consume quota."""

import math
import time
from collections import deque
from contextlib import contextmanager
from threading import Lock

from fastapi import HTTPException


class Admission:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.history = deque()
        self.active = 0
        self.lock = Lock()

    @contextmanager
    def slot(self, visitor):
        with self.lock:
            now = self.clock()
            while self.history and self.history[0][0] <= now - 3600:
                self.history.popleft()
            personal = [t for t, ip in self.history if ip == visitor]
            minute = [t for t in personal if t > now - 60]
            global_minute = [t for t, _ in self.history if t > now - 60]
            waits = []
            for timestamps, limit, window in (
                (minute, 3, 60),
                (personal, 20, 3600),
                (global_minute, 30, 60),
            ):
                if len(timestamps) >= limit:
                    waits.append(timestamps[-limit] + window - now)
            if self.active >= 2:
                waits.append(5)
            if waits:
                retry = max(1, math.ceil(max(waits)))
                raise HTTPException(
                    429,
                    f"Too many requests. Try again in {retry} seconds.",
                    headers={"Retry-After": str(retry)},
                )
            self.history.append((now, visitor))
            self.active += 1
        try:
            yield
        finally:
            with self.lock:
                self.active -= 1
