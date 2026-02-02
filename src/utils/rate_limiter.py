"""
Rate limiter for controlling request frequency
"""

import asyncio
from datetime import datetime, timedelta
from collections import deque
from typing import Optional

from .config import settings
from .logger import logger


class RateLimiter:
    def __init__(self, requests_per_minute: Optional[int] = None):
        self.requests_per_minute = requests_per_minute or settings.requests_per_minute
        self.request_times: deque = deque()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = datetime.now()
            one_minute_ago = now - timedelta(minutes=1)

            while self.request_times and self.request_times[0] < one_minute_ago:
                self.request_times.popleft()

            if len(self.request_times) >= self.requests_per_minute:
                oldest_request = self.request_times[0]
                wait_until = oldest_request + timedelta(minutes=1)
                wait_seconds = (wait_until - now).total_seconds()

                if wait_seconds > 0:
                    logger.debug(
                        f"Rate limit reached. Waiting {wait_seconds:.2f} seconds..."
                    )
                    await asyncio.sleep(wait_seconds)

                    now = datetime.now()
                    one_minute_ago = now - timedelta(minutes=1)
                    while self.request_times and self.request_times[0] < one_minute_ago:
                        self.request_times.popleft()

            self.request_times.append(datetime.now())

    def reset(self):
        self.request_times.clear()
        logger.debug("Rate limiter reset")

    @property
    def current_rate(self) -> int:
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        return sum(1 for req_time in self.request_times if req_time >= one_minute_ago)


rate_limiter = RateLimiter()
