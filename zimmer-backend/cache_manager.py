"""
Cache Manager for Zimmer AI Platform
Provides in-memory caching for frequently accessed data
"""

import time
import json
from typing import Any, Optional, Dict, Union
from functools import wraps
from datetime import datetime, timedelta

class CacheManager:
    """Simple in-memory cache manager"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = 300  # 5 minutes default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a cache entry with optional TTL"""
        ttl = ttl or self._default_ttl
        expires_at = time.time() + ttl
        
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': time.time()
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get a cache entry if it exists and hasn't expired"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Check if expired
        if time.time() > entry['expires_at']:
            del self._cache[key]
            return None
        
        return entry['value']
    
    def delete(self, key: str) -> bool:
        """Delete a cache entry"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count of removed entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        total_entries = len(self._cache)
        expired_entries = sum(
            1 for entry in self._cache.values()
            if current_time > entry['expires_at']
        )
        
        return {
            'total_entries': total_entries,
            'active_entries': total_entries - expired_entries,
            'expired_entries': expired_entries,
            'cache_size_mb': sum(
                len(str(entry['value']).encode('utf-8'))
                for entry in self._cache.values()
            ) / (1024 * 1024)
        }

# Global cache instance
cache = CacheManager()

def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def cache_user_data(user_id: int, data: Any, ttl: int = 300):
    """Cache user-specific data"""
    cache.set(f"user:{user_id}", data, ttl)

def get_cached_user_data(user_id: int) -> Optional[Any]:
    """Get cached user data"""
    return cache.get(f"user:{user_id}")

def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a user"""
    # This is a simple implementation - in production, you'd want more sophisticated invalidation
    cache.delete(f"user:{user_id}")

def cache_automation_data(automation_id: int, data: Any, ttl: int = 600):
    """Cache automation data"""
    cache.set(f"automation:{automation_id}", data, ttl)

def get_cached_automation_data(automation_id: int) -> Optional[Any]:
    """Get cached automation data"""
    return cache.get(f"automation:{automation_id}")

def cache_dashboard_data(user_id: int, data: Any, ttl: int = 120):
    """Cache dashboard data"""
    cache.set(f"dashboard:{user_id}", data, ttl)

def get_cached_dashboard_data(user_id: int) -> Optional[Any]:
    """Get cached dashboard data"""
    return cache.get(f"dashboard:{user_id}")

def cache_marketplace_data(data: Any, ttl: int = 600):
    """Cache marketplace data"""
    cache.set("marketplace:automations", data, ttl)

def get_cached_marketplace_data() -> Optional[Any]:
    """Get cached marketplace data"""
    return cache.get("marketplace:automations")

def cache_admin_stats(data: Any, ttl: int = 120):
    """Cache admin dashboard statistics"""
    cache.set("admin:stats", data, ttl)

def get_cached_admin_stats() -> Optional[Any]:
    """Get cached admin dashboard statistics"""
    return cache.get("admin:stats")

# Cache cleanup task
def cleanup_cache():
    """Cleanup expired cache entries"""
    removed_count = cache.cleanup_expired()
    if removed_count > 0:
        print(f"🧹 Cleaned up {removed_count} expired cache entries")
    return removed_count

# Cache statistics endpoint
def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics for monitoring"""
    return cache.get_stats()

# Create global cache manager instance
cache_manager = CacheManager()
