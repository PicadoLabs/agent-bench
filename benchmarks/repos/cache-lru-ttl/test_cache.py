import pytest
from lru_ttl_cache import LRUTTLCache


def test_basic_set_get():
    cache = LRUTTLCache(capacity=2)
    cache.set("a", 100, current_time=0.0)
    assert cache.get("a", current_time=0.0) == 100
    assert cache.get("nonexistent", current_time=0.0) is None


def test_ttl_expiration():
    cache = LRUTTLCache(capacity=2)
    cache.set("temp", "value", ttl_seconds=5.0, current_time=10.0)

    # Valid before expiration (t=14.9)
    assert cache.get("temp", current_time=14.9) == "value"

    # Expired at t=15.0 and beyond
    assert cache.get("temp", current_time=15.0) is None
    assert cache.size() == 0


def test_lru_eviction():
    cache = LRUTTLCache(capacity=2)
    cache.set("a", 1, current_time=0.0)
    cache.set("b", 2, current_time=0.0)

    # Access "a", making "b" the least recently used
    assert cache.get("a", current_time=0.0) == 1

    # Insert "c", which should evict "b"
    cache.set("c", 3, current_time=0.0)

    assert cache.get("a", current_time=0.0) == 1
    assert cache.get("c", current_time=0.0) == 3
    assert cache.get("b", current_time=0.0) is None
