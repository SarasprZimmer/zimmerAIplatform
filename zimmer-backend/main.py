from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from database import Base, engine
import os
import time
import psutil
import gc
from asyncio import Semaphore
from dotenv import load_dotenv
from cache_manager import cache as cache_manager

# Load environment variables
load_dotenv()

# Import security middleware
from utils.security_headers import SecurityHeadersMiddleware, configure_cors
from utils.csrf import CSRFMiddleware
from utils.rate_limit import RateLimitMiddleware

# Import auth dependencies
from models.user import User
from utils.auth_dependency import get_current_user as get_current_user_dependency

# Initialize FastAPI app
app = FastAPI(
    title="Zimmer Internal Management Dashboard",
    description="Backend API for Zimmer's internal management and automation tracking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add security middleware in order (last added = first executed)
# 1. Security headers (adds headers to all responses)
app.add_middleware(SecurityHeadersMiddleware)

# 2. Rate limiting (checks limits before processing)
# TEMPORARILY DISABLED FOR DEBUGGING
# app.add_middleware(RateLimitMiddleware)

# 3. CSRF protection (checks CSRF tokens for unsafe methods)
app.add_middleware(CSRFMiddleware)

# 4. Trusted host middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Configure appropriately for production

# Configure CORS with tight security settings
configure_cors(app, allowed_origins=[
    "http://localhost:3000",  # User panel dev
    "http://127.0.0.1:3000", 
    "http://localhost:3001",  # Admin panel dev (legacy)
    "http://127.0.0.1:3001", 
    "http://localhost:4000",  # Admin panel dev (new)
    "http://127.0.0.1:4000", 
    "http://localhost:8000",  # Backend dev (localhost)
    "http://127.0.0.1:8000",  # Backend dev (127.0.0.1)
    "http://193.162.129.243:3000",  # User panel production
    "http://193.162.129.243:4000",  # Admin panel production
    "http://173.234.25.122:4000",  # Admin panel external access
    "https://zimmerai.com",   # Production
    "https://admin.zimmerai.com",  # Production admin (legacy)
    "https://panel.zimmerai.com",  # Production user panel
    "https://manager.zimmerai.com",  # Production admin panel
])

@app.get("/test-cors")
async def test_cors():
    return {"message": "CORS test successful", "timestamp": "2025-07-07"}

@app.get("/health")
async def health_check():
    """Simple health check endpoint with caching"""
    # Check cache first
    cache_key = "health_check"
    cached_health = cache_manager.get(cache_key)
    
    if cached_health:
        print(f"✅ Cache HIT for {cache_key}")
        return cached_health
    
    print(f"❌ Cache MISS for {cache_key}")
    
    # Generate health data
    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "memory_percent": psutil.virtual_memory().percent,
        "cpu_percent": psutil.cpu_percent()
    }
    
    # Cache for 30 seconds
    cache_manager.set(cache_key, health_data, ttl=30)
    print(f"💾 Cached {cache_key} for 30 seconds")
    
    return health_data

@app.get("/circuit-breaker/stats")
async def get_circuit_breaker_stats():
    """Get circuit breaker statistics"""
    from utils.circuit_breaker import get_circuit_breaker_stats
    return get_circuit_breaker_stats()

# Auth optimization middleware (MUST be first)
auth_semaphore = Semaphore(5)  # Limit auth requests to 5 concurrent

@app.middleware("http")
async def auth_optimization_middleware(request: Request, call_next):
    """Optimize authentication for public endpoints - FIRST MIDDLEWARE"""
    # Skip auth middleware for public endpoints
    public_endpoints = [
        "/api/automations/marketplace",
        "/api/optimized/automations/marketplace",
        "/api/optimized/cache/stats",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json"
    ]
    
    if request.url.path in public_endpoints:
        response = await call_next(request)
        return response
    
    # For auth endpoints, use limited concurrency
    if request.url.path.startswith("/api/auth/"):
        async with auth_semaphore:
            response = await call_next(request)
            return response
    
    # For other endpoints, proceed normally
    response = await call_next(request)
    return response

# Performance optimization middleware (SECOND)
request_semaphore = Semaphore(10)  # Max 10 concurrent requests

@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Performance optimization middleware - SECOND MIDDLEWARE"""
    start_time = time.time()
    
    # Check memory usage and cleanup if needed
    memory_percent = psutil.virtual_memory().percent
    if memory_percent > 80:
        gc.collect()  # Force garbage collection
        print(f"High memory usage: {memory_percent}% - forced GC")
    
    # Rate limiting with semaphore (but not for auth endpoints - they have their own)
    if not request.url.path.startswith("/api/auth/"):
        async with request_semaphore:
            try:
                response = await call_next(request)
                
                # Log slow requests
                process_time = time.time() - start_time
                if process_time > 1.0:
                    print(f"Slow request: {request.url.path} - {process_time:.2f}s")
                
                return response
                
            except Exception as e:
                process_time = time.time() - start_time
                print(f"Request error: {request.url.path} - {process_time:.2f}s - {str(e)}")
                raise e
    else:
        # For auth endpoints, just proceed without additional semaphore
        try:
            response = await call_next(request)
            
            # Log slow requests
            process_time = time.time() - start_time
            if process_time > 1.0:
                print(f"Slow auth request: {request.url.path} - {process_time:.2f}s")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            print(f"Auth request error: {request.url.path} - {process_time:.2f}s - {str(e)}")
            raise e

# Import and include routers
from routers import users, admin, fallback, knowledge, telegram, ticket, ticket_message, auth
app.include_router(auth.router, tags=["auth"])

# Import and include Google OAuth router
from routers.auth_google import router as auth_google_router
app.include_router(auth_google_router, tags=["auth-google"])
app.include_router(users.router, prefix="/api", tags=["users"])

# Import and include auth sessions router
from routers.auth_sessions import router as auth_sessions_router
app.include_router(auth_sessions_router, prefix="/api/auth", tags=["auth-sessions"])

# Import and include email verification router
from routers.email_verify import router as email_verify_router
app.include_router(email_verify_router, tags=["email-verification"])

# Import and include 2FA router
from routers.twofa import router as twofa_router
app.include_router(twofa_router, tags=["twofa"])
from routers.admin import router as admin_router
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(fallback.router, prefix="/api/admin", tags=["fallback"])
app.include_router(knowledge.router, prefix="/api", tags=["knowledge"])
app.include_router(ticket.router, prefix="/api", tags=["tickets"])
app.include_router(ticket_message.router, prefix="/api", tags=["ticket-messages"])
app.include_router(telegram.router)
from routers.password_reset import router as password_reset_router
app.include_router(password_reset_router, prefix="/api", tags=["password-reset"])
from routers.admin.automation import router as admin_automation_router
app.include_router(admin_automation_router, prefix="/api/admin", tags=["automation"])
from routers.admin.kb_monitoring import router as kb_monitoring_router
app.include_router(kb_monitoring_router, prefix="/api/admin", tags=["kb-monitoring"])
from routers.admin.kb_monitoring_simple import router as kb_monitoring_simple_router
app.include_router(kb_monitoring_simple_router, prefix="/api/admin", tags=["kb-monitoring-simple"])
from routers.admin.kb_history import router as kb_history_router
app.include_router(kb_history_router, prefix="/api/admin", tags=["kb-history"])
from routers.admin.backups import router as backups_router
app.include_router(backups_router, prefix="/api/admin", tags=["backups"])
from routers.admin.kb_templates import router as kb_templates_router
app.include_router(kb_templates_router, prefix="/api/admin", tags=["kb-templates"])
from routers.admin.automation_integrations import router as automation_integrations_router
app.include_router(automation_integrations_router, prefix="/api/admin", tags=["automation-integrations"])
from routers.automations import router as automations_router
app.include_router(automations_router, prefix="/api", tags=["automations"])
from routers.automation_usage import router as automation_usage_router
app.include_router(automation_usage_router, prefix="/api", tags=["automation-usage"])

# Import optimized endpoints
from optimized_endpoints import router as optimized_router
app.include_router(optimized_router, tags=["optimized"])

# Import production monitoring
from production_monitoring import router as monitoring_router, start_monitoring
app.include_router(monitoring_router, tags=["monitoring"])

# Import new routers
from routers.payments import router as payments_router
app.include_router(payments_router, tags=["payments"])

from routers.notifications_extended import router as notifications_extended_router
app.include_router(notifications_extended_router, tags=["notifications-extended"])

from routers.support import router as support_router
app.include_router(support_router, tags=["support"])

# Import optimized routers for timeout fixes
from routers.auth_optimized import router as auth_optimized_router
app.include_router(auth_optimized_router, tags=["auth-optimized"])

from routers.users_optimized import router as users_optimized_router
app.include_router(users_optimized_router, tags=["users-optimized"])

# Import admin discounts router (MUST be before openai_keys to avoid routing conflict)
from routers.admin_discounts import router as admin_discounts_router
app.include_router(admin_discounts_router, prefix="/api/admin", tags=["admin-discounts"])

# Import public discounts router
from routers.discounts import router as discounts_router
app.include_router(discounts_router, prefix="/api", tags=["discounts"])

from routers.admin.openai_keys import router as openai_keys_router
app.include_router(openai_keys_router, prefix="/api/admin", tags=["openai-keys"])
from routers.admin.user_management import router as user_management_router
app.include_router(user_management_router, prefix="/api/admin", tags=["user-management"])

# Import system status router
from routers.admin.system_status import router as system_status_router
app.include_router(system_status_router, prefix="/api/admin/system", tags=["system-status"])

# Import payment router
from routers.payments_zarinpal import router as payments_zarinpal_router
app.include_router(payments_zarinpal_router, prefix="/api/payments", tags=["payments"])

# Import token adjustments router
from routers.admin.token_adjustments import router as token_adjustments_router
app.include_router(token_adjustments_router, prefix="/api/admin/tokens", tags=["token-adjustments"])

# Import notifications router
from routers.notifications import router as notifications_router
app.include_router(notifications_router, tags=["notifications"])

# Import user usage router
from routers.user_usage import router as user_usage_router
app.include_router(user_usage_router)

# Import user billing router
from routers.user_billing import router as user_billing_router
app.include_router(user_billing_router)

# Import admin notifications router
from routers.admin_notifications import router as admin_notifications_router
app.include_router(admin_notifications_router, tags=["admin:notifications"])

# Import admin automation health router
from routers.admin_automation_health import router as admin_automation_health_router
app.include_router(admin_automation_health_router, tags=["admin:automation-health"])

# Import admin dashboard router
from routers.admin_dashboard import router as admin_dashboard_router
app.include_router(admin_dashboard_router, prefix="/api", tags=["admin-dashboard"])

# Import missing admin endpoints router
from routers.admin_missing_endpoints import router as admin_missing_router
app.include_router(admin_missing_router, tags=["admin-missing"])

# Import all models to ensure they're registered with Base
from models.user import User
from models.automation import Automation
from models.ticket import Ticket
from models.ticket_message import TicketMessage
from models.payment import Payment
from models.knowledge import KnowledgeEntry
from models.kb_template import KBTemplate
from models.kb_status_history import KBStatusHistory
from models.openai_key import OpenAIKey
from models.openai_key_usage import OpenAIKeyUsage
from models.password_reset_token import PasswordResetToken
from models.backup import BackupLog
from models.fallback_log import FallbackLog
from models.token_usage import TokenUsage
from models.user_automation import UserAutomation
from models.token_adjustment import TokenAdjustment
from models.session import Session
from models.notification import Notification
from models.discount import DiscountCode, DiscountCodeAutomation, DiscountRedemption

# Note: Database tables are now managed by Alembic migrations
# Run 'alembic upgrade head' to create/update tables

# Import backup scheduler (will be started in startup event)
# from scheduler import backup_scheduler

# Temporarily disabled startup/shutdown events to fix backend issues
# @app.on_event("startup")
# async def startup_event():
#     """Startup event handler"""
#     pass

# @app.on_event("shutdown")
# async def shutdown_event():
#     """Shutdown event handler"""
#     pass

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Zimmer Internal Management Dashboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "zimmer-dashboard"}



@app.post("/dev/seed")
async def seed_data():
    """Development endpoint to seed sample data"""
    try:
        from utils.seeder import seed_sample_data
        seed_sample_data()
        return {"message": "Sample data seeded successfully"}
    except Exception as e:
        return {"error": f"Failed to seed data: {str(e)}"}

from pydantic import BaseModel

class TestGPTRequest(BaseModel):
    message: str

@app.post("/dev/test-gpt")
async def test_gpt(request: TestGPTRequest):
    """Development endpoint to test GPT service"""
    try:
        from services.gpt import generate_gpt_response, count_tokens, get_response_cost
        
        # Generate response
        response = generate_gpt_response(None, request.message)
        
        if response is None:
            return {
                "message": "Fallback triggered",
                "reason": "Complex keywords or long message detected",
                "input_message": request.message,
                "word_count": len(request.message.split())
            }
        else:
            tokens = count_tokens(response)
            cost = get_response_cost(tokens)
            return {
                "message": "GPT response generated",
                "response": response,
                "tokens_used": tokens,
                "estimated_cost": f"${cost:.4f}",
                "input_message": request.message,
                "word_count": len(request.message.split())
            }
    except Exception as e:
        return {"error": f"GPT test failed: {str(e)}"} 

@app.get("/api/auth/me")
async def get_current_user(current_user: User = Depends(get_current_user_dependency)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "is_admin": current_user.is_admin
    }


@app.get("/api/admin/list")
async def list_api_keys(current_user: User = Depends(get_current_user_dependency)):
    """List API keys for admin"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Return a simple response for now
    return {
        "keys": [],
        "total": 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


