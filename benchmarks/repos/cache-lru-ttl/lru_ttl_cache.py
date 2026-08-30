# lru_ttl_cache.py - In-memory LRU Cache with TTL Expiration
import time
from collections import OrderedDict
from typing import Any, Optional


class CacheEntry:
    def __init__(self, value: Any, expires_at: Optional[float]):
        self.value = value
        self.expires_at = expires_at

    def is_expired(self, current_time: float) -> bool:
        if self.expires_at is None:
            return False
        return current_time >= self.expires_at


class LRUTTLCache:
    def __init__(self, capacity: int = 100):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()

    def get(self, key: str, current_time: Optional[float] = None) -> Optional[Any]:
        """
        Get value for key if present and not expired.
        - If key exists and is expired: delete entry and return None.
        - If key exists and valid: move to most recently used end (MRU) and return value.
        - If not found: return None.
        """
        now = time.time() if current_time is None else current_time
        if key not in self.cache:
            return None

        entry = self.cache[key]
        
        # BUG: Expiry check condition is inverted (treats valid items as expired!)
        if not entry.is_expired(now):
            # BUG: Deletes valid entries
            del self.cache[key]
            return None

        # BUG: Doesn't move accessed key to MRU (end of OrderedDict)
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None, current_time: Optional[float] = None) -> None:
        """
        Set key-value pair with optional TTL.
        - If key already exists: update entry and move to MRU.
        - If capacity is exceeded: evict Least Recently Used (first entry in OrderedDict).
        """
        now = time.time() if current_time is None else current_time
        expires_at = (now + ttl_seconds) if ttl_seconds is not None else None

        if key in self.cache:
            self.cache.move_to_end(key)
        
        self.cache[key] = CacheEntry(value, expires_at)

        # Evict LRU if over capacity
        if len(self.cache) > self.capacity:
            # BUG: Pops from end (MRU) instead of beginning (LRU: last=False)
            self.cache.popitem(last=True)

    def size(self) -> int:
        return len(self.cache)
