#!/usr/bin/env python3
"""
Simple endpoint test to isolate performance issues
"""

from fastapi import FastAPI
import time

app = FastAPI()

@app.get("/test-simple")
async def test_simple():
    """Simple endpoint with no database or complex operations"""
    return {
        "message": "Simple test endpoint",
        "timestamp": time.time()
    }

@app.get("/test-cache")
async def test_cache():
    """Test endpoint with caching"""
    from cache_manager import cache as cache_manager
    
    cache_key = "test_cache"
    cached_data = cache_manager.get(cache_key)
    
    if cached_data:
        return {"message": "Cached response", "data": cached_data}
    
    data = {
        "message": "Fresh response",
        "timestamp": time.time(),
        "computed_value": sum(range(1000))  # Some computation
    }
    
    cache_manager.set(cache_key, data, ttl=60)
    return {"message": "Fresh response", "data": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
