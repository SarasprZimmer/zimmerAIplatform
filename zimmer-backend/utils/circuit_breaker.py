"""
Circuit Breaker Implementation for Zimmer AI Platform
Provides failure detection and automatic recovery for auth endpoints
"""

import time
from enum import Enum
from typing import Callable, Any
import asyncio
from functools import wraps

class CircuitState(Enum):
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Circuit is open, requests fail fast
    HALF_OPEN = "HALF_OPEN"  # Testing if service is back

class CircuitBreaker:
    """
    Circuit breaker implementation for auth endpoints
    """
    
    def __init__(
        self,
        failure_threshold: int = 3,
        timeout: int = 30,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
        # Statistics
        self.total_requests = 0
        self.total_failures = 0
        self.total_successes = 0
        
    def __call__(self, func: Callable) -> Callable:
        """Decorator for circuit breaker"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        return wrapper
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        self.total_requests += 1
        
        # Check circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception(f"Circuit breaker is OPEN for {self.timeout} seconds")
        
        try:
            # Execute the function
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
        except Exception as e:
            # For unexpected exceptions, don't count as circuit breaker failure
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.timeout
    
    def _on_success(self):
        """Handle successful request"""
        self.total_successes += 1
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed request"""
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"Circuit breaker OPENED after {self.failure_count} failures")
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics"""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "total_requests": self.total_requests,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "failure_rate": (self.total_failures / self.total_requests * 100) if self.total_requests > 0 else 0,
            "last_failure_time": self.last_failure_time,
            "time_since_last_failure": time.time() - self.last_failure_time if self.last_failure_time else None
        }
    
    def reset(self):
        """Manually reset circuit breaker"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        print("Circuit breaker manually reset")

# Global circuit breakers for different auth endpoints
auth_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    timeout=30,
    expected_exception=Exception
)

login_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=60,
    expected_exception=Exception
)

user_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    timeout=30,
    expected_exception=Exception
)

def get_circuit_breaker_stats() -> dict:
    """Get statistics for all circuit breakers"""
    return {
        "auth": auth_circuit_breaker.get_stats(),
        "login": login_circuit_breaker.get_stats(),
        "user": user_circuit_breaker.get_stats()
    }

def reset_all_circuit_breakers():
    """Reset all circuit breakers"""
    auth_circuit_breaker.reset()
    login_circuit_breaker.reset()
    user_circuit_breaker.reset()
    print("All circuit breakers reset")
