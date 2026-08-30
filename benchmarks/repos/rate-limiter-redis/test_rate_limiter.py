import pytest
from rate_limiter import SlidingWindowRateLimiter


def test_basic_rate_limiting():
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=10.0)
    
    # 3 requests allowed at t=100
    assert limiter.is_allowed("user-1", current_time=100.0) is True
    assert limiter.is_allowed("user-1", current_time=100.1) is True
    assert limiter.is_allowed("user-1", current_time=100.2) is True
    
    # 4th request within window rejected
    assert limiter.is_allowed("user-1", current_time=100.5) is False
    assert limiter.get_remaining_capacity("user-1", current_time=100.5) == 0


def test_sliding_window_expiration():
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=5.0)
    
    assert limiter.is_allowed("user-1", current_time=10.0) is True
    assert limiter.is_allowed("user-1", current_time=12.0) is True
    assert limiter.is_allowed("user-1", current_time=13.0) is False
    
    # At t=15.1, the request from t=10.0 expired (window: 10.1 to 15.1)
    assert limiter.is_allowed("user-1", current_time=15.1) is True
    assert limiter.is_allowed("user-1", current_time=15.2) is False


def test_multiple_clients_isolated():
    limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=10.0)
    
    assert limiter.is_allowed("user-a", current_time=10.0) is True
    assert limiter.is_allowed("user-a", current_time=11.0) is False
    
    # user-b is unaffected by user-a
    assert limiter.is_allowed("user-b", current_time=11.0) is True
    assert limiter.is_allowed("user-b", current_time=12.0) is False
