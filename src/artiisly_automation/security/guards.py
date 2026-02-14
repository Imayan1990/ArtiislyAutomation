from __future__ import annotations

import os
import time
from collections import defaultdict, deque

from fastapi import Header, HTTPException, status


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def validate(self, client_id: str) -> None:
        now = time.time()
        bucket = self._requests[client_id]

        while bucket and bucket[0] <= now - self.window_seconds:
            bucket.popleft()

        if len(bucket) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

        bucket.append(now)


limiter = SlidingWindowRateLimiter()


def verify_api_key(x_api_key: str | None = Header(default=None)) -> str:
    expected = os.getenv("ARTIISLY_AUTOMATION_API_KEY", "change-me-in-prod")
    if x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    limiter.validate(x_api_key)
    return x_api_key
