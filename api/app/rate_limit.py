from collections import defaultdict, deque
from time import monotonic


class RateLimiter:
    def __init__(self, per_minute: int, per_hour: int) -> None:
        self.per_minute = per_minute
        self.per_hour = per_hour
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = monotonic()
        bucket = self._hits[key]

        while bucket and now - bucket[0] > 3600:
            bucket.popleft()

        minute_count = sum(1 for timestamp in bucket if now - timestamp <= 60)
        if minute_count >= self.per_minute or len(bucket) >= self.per_hour:
            return False

        bucket.append(now)
        return True
