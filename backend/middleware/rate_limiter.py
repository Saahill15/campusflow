import time
from collections import defaultdict
from typing import Optional


class RateLimiter:
    """Simple in-memory rate limiter using token bucket algorithm."""
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the time window.
            window_seconds: Time window in seconds.
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)
    
    def is_allowed(self, key: str) -> bool:
        """
        Check if a request is allowed for the given key.
        
        Args:
            key: Identifier (e.g., IP address, email).
            
        Returns:
            True if request is allowed, False if rate limit exceeded.
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Remove old requests outside the window
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > window_start]
        
        # Check if limit is exceeded
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        # Record this request
        self.requests[key].append(now)
        return True


# Global instance for registration endpoint
# Allow 5 registration attempts per email/IP per 1 hour
registration_limiter = RateLimiter(max_requests=5, window_seconds=3600)
