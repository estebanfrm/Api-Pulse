"""Single-process admission control for the one-worker public demo."""

from collections import deque
from contextlib import contextmanager
from threading import Lock
from time import monotonic
from typing import Iterator

from fastapi import HTTPException

from app.config import settings


class DemoLimiter:
    def __init__(self) -> None:
        self._lock = Lock()
        self._by_client: dict[str, deque[float]] = {}
        self._global: deque[float] = deque()
        self._active_by_client: dict[str, int] = {}
        self._active_global = 0
        self._last_sweep = 0.0

    @contextmanager
    def admit(self, client_key: str) -> Iterator[None]:
        now = monotonic()
        with self._lock:
            if now - self._last_sweep >= 60:
                for key, events in list(self._by_client.items()):
                    while events and events[0] <= now - 60:
                        events.popleft()
                    if not events and self._active_by_client.get(key, 0) == 0:
                        del self._by_client[key]
                        self._active_by_client.pop(key, None)
                self._last_sweep = now
            while self._global and self._global[0] <= now - 60:
                self._global.popleft()
            if len(self._global) >= settings.demo_requests_per_minute_global:
                raise HTTPException(status_code=429, detail="Demo request limit reached. Try again later.")
            recent = self._by_client.get(client_key)
            if recent is not None:
                while recent and recent[0] <= now - 60:
                    recent.popleft()
            if recent is not None and len(recent) >= settings.demo_requests_per_minute_ip:
                raise HTTPException(status_code=429, detail="Demo request limit reached. Try again later.")
            if self._active_by_client.get(client_key, 0) >= settings.demo_concurrent_ip or self._active_global >= settings.demo_concurrent_global:
                raise HTTPException(status_code=429, detail="Demo is busy. Try again shortly.")
            if recent is None:
                recent = deque()
                self._by_client[client_key] = recent
            recent.append(now)
            self._global.append(now)
            self._active_by_client[client_key] = self._active_by_client.get(client_key, 0) + 1
            self._active_global += 1
        try:
            yield
        finally:
            with self._lock:
                self._active_by_client[client_key] -= 1
                self._active_global -= 1


demo_limiter = DemoLimiter()
