import time
from datetime import datetime
from collections import deque


class RateLimiter:
    def __init__(self, max_calls: int = 60, per_seconds: int = 60):
        self.max_calls = max_calls
        self.per_seconds = per_seconds
        self.call_times: deque = deque()

    def wait_if_needed(self):
        now = time.time()

        while self.call_times and self.call_times[0] < now - self.per_seconds:
            self.call_times.popleft()

        if len(self.call_times) >= self.max_calls:
            sleep_time = self.call_times[0] + self.per_seconds - now
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.call_times.append(time.time())

    def daily_budget_remaining(self, daily_limit: int = 1000) -> int:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        calls_today = sum(1 for t in self.call_times if t >= today_start.timestamp())
        return daily_limit - calls_today
