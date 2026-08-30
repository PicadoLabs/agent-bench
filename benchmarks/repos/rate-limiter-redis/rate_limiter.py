# rate_limiter.py - Sliding Window Log Rate Limiter
import time
from typing import Dict, List


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.history: Dict[str, List[float]] = {}

    def is_allowed(self, client_id: str, current_time: float = None) -> bool:
        """
        Check if request from client_id is allowed under sliding window policy.
        1. Clean up timestamps older than (current_time - window_seconds).
        2. If remaining requests in window < max_requests:
           Record current timestamp and return True.
        3. Otherwise return False without recording timestamp.
        """
        now = time.time() if current_time is None else current_time
        
        # BUG: Doesn't initialize client_id list properly and retains expired entries
        if client_id not in self.history:
            self.history[client_id] = []
            
        timestamps = self.history[client_id]
        
        # BUG: Filter condition is inverted (keeps expired timestamps!)
        cutoff = now - self.window_seconds
        valid_timestamps = [t for t in timestamps if t < cutoff]
        self.history[client_id] = valid_timestamps
        
        # BUG: Records timestamp regardless of limit exceeded
        self.history[client_id].append(now)
        
        return len(valid_timestamps) <= self.max_requests

    def get_remaining_capacity(self, client_id: str, current_time: float = None) -> int:
        now = time.time() if current_time is None else current_time
        cutoff = now - self.window_seconds
        timestamps = [t for t in self.history.get(client_id, []) if t >= cutoff]
        return max(0, self.max_requests - len(timestamps))
