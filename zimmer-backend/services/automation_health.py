import httpx
from datetime import datetime, timezone

DEFAULT_TIMEOUT = 5.0
RETRIES = 2

EXPECTED_FIELDS = {"status", "version", "uptime"}  # customize as needed

async def probe(url: str) -> dict:
    """
    Probe an automation's health check URL
    
    Args:
        url: Health check URL to probe
        
    Returns:
        dict with probe results
    """
    if not url:
        return {"ok": False, "error": "no_health_check_url"}
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        last_exc = None
        for _ in range(RETRIES+1):
            try:
                r = await client.get(url)
                if r.status_code != 200:
                    return {"ok": False, "error": f"http_{r.status_code}"}
                
                js = r.json()
                missing = [k for k in EXPECTED_FIELDS if k not in js]
                if missing:
                    return {"ok": False, "error": "schema_mismatch", "missing": missing, "body": js}
                
                # Optionally check version compatibility
                return {"ok": True, "body": js}
            except Exception as e:
                last_exc = str(e)
        
        return {"ok": False, "error": "exception", "detail": last_exc}

def classify(result: dict) -> str:
    """
    Classify health check result into status
    
    Args:
        result: Probe result from probe() function
        
    Returns:
        Health status: 'healthy', 'degraded', or 'unhealthy'
    """
    if not result.get("ok"):
        return "unhealthy"
    
    body = result.get("body") or {}
    # You can implement real heuristics here
    return "healthy" if body.get("status") in ("ok", "healthy", "up") else "degraded"
