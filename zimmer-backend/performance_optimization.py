#!/usr/bin/env python3
"""
Performance Optimization Script for Zimmer AI Platform
Addresses database performance, query optimization, and caching
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, Index, func
from sqlalchemy.orm import sessionmaker
from database import Base, engine, SessionLocal

def create_performance_indexes():
    """Create additional indexes for frequently queried columns"""
    print("🔧 Creating performance indexes...")
    
    db = SessionLocal()
    try:
        # Create indexes for frequently queried columns
        indexes_to_create = [
            # User queries
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)",
            "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)",
            
            # UserAutomation queries
            "CREATE INDEX IF NOT EXISTS idx_user_automations_user_id ON user_automations(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_automations_automation_id ON user_automations(automation_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_automations_status ON user_automations(status)",
            "CREATE INDEX IF NOT EXISTS idx_user_automations_provisioned_at ON user_automations(provisioned_at)",
            "CREATE INDEX IF NOT EXISTS idx_user_automations_integration_status ON user_automations(integration_status)",
            
            # TokenUsage queries
            "CREATE INDEX IF NOT EXISTS idx_token_usage_user_id ON token_usage(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_token_usage_created_at ON token_usage(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_token_usage_user_automation_id ON token_usage(user_automation_id)",
            
            # Payment queries
            "CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)",
            "CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_payments_automation_id ON payments(automation_id)",
            
            # Ticket queries
            "CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON tickets(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)",
            "CREATE INDEX IF NOT EXISTS idx_tickets_importance ON tickets(importance)",
            "CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at)",
            
            # Automation queries
            "CREATE INDEX IF NOT EXISTS idx_automations_status ON automations(status)",
            "CREATE INDEX IF NOT EXISTS idx_automations_health_status ON automations(health_status)",
            "CREATE INDEX IF NOT EXISTS idx_automations_is_listed ON automations(is_listed)",
            "CREATE INDEX IF NOT EXISTS idx_automations_created_at ON automations(created_at)",
            
            # Session queries
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_revoked_at ON sessions(revoked_at)",
            
            # KB Status History queries
            "CREATE INDEX IF NOT EXISTS idx_kb_status_history_user_id ON kb_status_history(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_kb_status_history_automation_id ON kb_status_history(automation_id)",
            "CREATE INDEX IF NOT EXISTS idx_kb_status_history_timestamp ON kb_status_history(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_kb_status_history_kb_health ON kb_status_history(kb_health)",
            
            # Composite indexes for common query patterns
            "CREATE INDEX IF NOT EXISTS idx_user_automations_user_status ON user_automations(user_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_payments_user_status ON payments(user_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_token_usage_user_date ON token_usage(user_id, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_tickets_user_status ON tickets(user_id, status)",
        ]
        
        for index_sql in indexes_to_create:
            try:
                db.execute(text(index_sql))
                print(f"  ✅ Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
            except Exception as e:
                print(f"  ⚠️  Index creation warning: {e}")
        
        db.commit()
        print("✅ Performance indexes created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        db.rollback()
    finally:
        db.close()

def optimize_database_settings():
    """Optimize database settings for better performance"""
    print("🔧 Optimizing database settings...")
    
    db = SessionLocal()
    try:
        # SQLite specific optimizations
        if "sqlite" in str(engine.url):
            optimizations = [
                "PRAGMA journal_mode = WAL",  # Write-Ahead Logging
                "PRAGMA synchronous = NORMAL",  # Balance between safety and speed
                "PRAGMA cache_size = -64000",  # 64MB cache
                "PRAGMA temp_store = MEMORY",  # Store temp tables in memory
                "PRAGMA mmap_size = 268435456",  # 256MB memory mapping
                "PRAGMA optimize",  # Optimize the database
            ]
            
            for pragma in optimizations:
                try:
                    db.execute(text(pragma))
                    print(f"  ✅ Applied: {pragma}")
                except Exception as e:
                    print(f"  ⚠️  Pragma warning: {e}")
        
        db.commit()
        print("✅ Database settings optimized!")
        
    except Exception as e:
        print(f"❌ Error optimizing database: {e}")
        db.rollback()
    finally:
        db.close()

def analyze_query_performance():
    """Analyze current query performance"""
    print("📊 Analyzing query performance...")
    
    db = SessionLocal()
    try:
        # Check table sizes
        tables = [
            'users', 'user_automations', 'token_usage', 'payments', 
            'tickets', 'automations', 'sessions', 'kb_status_history'
        ]
        
        print("\n📈 Table Statistics:")
        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) as count FROM {table}"))
                count = result.scalar()
                print(f"  {table}: {count:,} records")
            except Exception as e:
                print(f"  {table}: Error - {e}")
        
        # Check index usage (SQLite specific)
        if "sqlite" in str(engine.url):
            print("\n🔍 Index Analysis:")
            try:
                result = db.execute(text("SELECT name, sql FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"))
                indexes = result.fetchall()
                print(f"  Found {len(indexes)} performance indexes")
                for name, sql in indexes:
                    print(f"    ✅ {name}")
            except Exception as e:
                print(f"  ⚠️  Index analysis error: {e}")
        
    except Exception as e:
        print(f"❌ Error analyzing performance: {e}")
    finally:
        db.close()

def create_caching_strategy():
    """Create caching configuration for frequently accessed data"""
    print("💾 Setting up caching strategy...")
    
    cache_config = """
# Caching Strategy for Zimmer AI Platform

## 1. Database Query Caching
- Cache user profile data (5 minutes)
- Cache automation listings (10 minutes)
- Cache dashboard statistics (2 minutes)
- Cache health status (1 minute)

## 2. API Response Caching
- GET /api/me - 5 minutes
- GET /api/automations/marketplace - 10 minutes
- GET /api/user/dashboard - 2 minutes
- GET /api/admin/dashboard - 2 minutes

## 3. Frontend Caching
- Static assets: 1 year
- API responses: 5 minutes
- User data: 2 minutes

## 4. Database Connection Pooling
- Pool size: 20 connections
- Max overflow: 30 connections
- Pool recycle: 1 hour
- Pool pre-ping: enabled
"""
    
    with open("CACHING_STRATEGY.md", "w") as f:
        f.write(cache_config)
    
    print("✅ Caching strategy documented!")

def optimize_queries():
    """Create optimized query examples"""
    print("🔍 Creating optimized query examples...")
    
    optimized_queries = """
# Optimized Query Examples

## 1. User Dashboard Query (Optimized)
```python
def get_user_dashboard_optimized(db: Session, user_id: int):
    # Use single query with proper joins
    query = db.query(
        UserAutomation,
        Automation.name,
        Automation.description,
        Automation.pricing_type,
        Automation.price_per_token,
        Automation.status
    ).join(
        Automation, UserAutomation.automation_id == Automation.id
    ).filter(
        UserAutomation.user_id == user_id
    ).options(
        # Use eager loading to prevent N+1 queries
        joinedload(UserAutomation.automation)
    )
    
    return query.all()
```

## 2. Token Usage Query (Optimized)
```python
def get_weekly_usage_optimized(db: Session, user_id: int):
    # Use indexed columns and proper date functions
    six_days_ago = datetime.utcnow() - timedelta(days=6)
    
    query = db.query(
        func.date(TokenUsage.created_at).label('day'),
        func.sum(TokenUsage.tokens_used).label('tokens'),
        func.count(TokenUsage.id).label('sessions')
    ).filter(
        TokenUsage.user_id == user_id,
        TokenUsage.created_at >= six_days_ago
    ).group_by(
        func.date(TokenUsage.created_at)
    ).order_by('day')
    
    return query.all()
```

## 3. Admin Dashboard Query (Optimized)
```python
def get_admin_dashboard_optimized(db: Session):
    # Use subqueries for better performance
    stats = db.query(
        func.count(User.id).label('total_users'),
        func.count(Automation.id).label('total_automations'),
        func.count(Ticket.id).label('total_tickets'),
        func.count(UserAutomation.id).label('active_automations')
    ).first()
    
    return stats
```
"""
    
    with open("OPTIMIZED_QUERIES.md", "w") as f:
        f.write(optimized_queries)
    
    print("✅ Optimized query examples created!")

def main():
    """Main optimization function"""
    print("🚀 Starting Zimmer AI Platform Performance Optimization")
    print("=" * 60)
    
    try:
        # Step 1: Create performance indexes
        create_performance_indexes()
        print()
        
        # Step 2: Optimize database settings
        optimize_database_settings()
        print()
        
        # Step 3: Analyze current performance
        analyze_query_performance()
        print()
        
        # Step 4: Create caching strategy
        create_caching_strategy()
        print()
        
        # Step 5: Create optimized query examples
        optimize_queries()
        print()
        
        print("🎉 Performance optimization completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Restart the backend server to apply database optimizations")
        print("2. Implement caching in the application code")
        print("3. Update queries to use the optimized patterns")
        print("4. Monitor performance improvements")
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
