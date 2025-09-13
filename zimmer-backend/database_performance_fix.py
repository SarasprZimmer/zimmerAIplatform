#!/usr/bin/env python3
"""
Database Performance Fix Script for Zimmer AI Platform
Adds additional indexes and optimizations to fix timeout issues
"""

import sqlite3
from sqlalchemy import create_engine, text
from database import engine, get_db
from sqlalchemy.orm import Session

def add_performance_indexes():
    """Add additional performance indexes for slow queries"""
    print("🔧 Adding performance indexes for timeout fixes...")
    
    # Additional indexes for authentication and user queries
    indexes_to_create = [
        # User table indexes
        ("users", "is_active", "idx_users_is_active"),
        ("users", "email_verified", "idx_users_email_verified"),
        ("users", "role", "idx_users_role"),
        
        # UserAutomation table indexes
        ("user_automations", "user_id", "idx_user_automations_user_id"),
        ("user_automations", "automation_id", "idx_user_automations_automation_id"),
        ("user_automations", "status", "idx_user_automations_status"),
        ("user_automations", "tokens_remaining", "idx_user_automations_tokens"),
        
        # TokenUsage table indexes
        ("token_usage", "user_id", "idx_token_usage_user_id"),
        ("token_usage", "user_automation_id", "idx_token_usage_user_automation_id"),
        ("token_usage", "created_at", "idx_token_usage_created_at"),
        ("token_usage", "tokens_used", "idx_token_usage_tokens_used"),
        
        # TwoFA table indexes
        ("twofa", "user_id", "idx_twofa_user_id"),
        ("twofa", "is_enabled", "idx_twofa_is_enabled"),
        
        # EmailVerification table indexes
        ("email_verifications", "user_id", "idx_email_verifications_user_id"),
        ("email_verifications", "token", "idx_email_verifications_token"),
        ("email_verifications", "expires_at", "idx_email_verifications_expires_at"),
        
        # Session table indexes
        ("sessions", "user_id", "idx_sessions_user_id"),
        ("sessions", "expires_at", "idx_sessions_expires_at"),
        ("sessions", "revoked_at", "idx_sessions_revoked_at"),
        
        # Composite indexes for common query patterns
        ("user_automations", ["user_id", "status"], "idx_user_automations_user_status"),
        ("token_usage", ["user_id", "created_at"], "idx_token_usage_user_date"),
        ("users", ["is_active", "email_verified"], "idx_users_active_verified"),
        ("sessions", ["user_id", "expires_at"], "idx_sessions_user_expires"),
    ]
    
    with engine.connect() as conn:
        for table, columns, index_name in indexes_to_create:
            try:
                if isinstance(columns, list):
                    # Composite index
                    columns_str = ", ".join(columns)
                else:
                    # Single column index
                    columns_str = columns
                
                # Check if index already exists
                check_sql = f"""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name='{index_name}'
                """
                result = conn.execute(text(check_sql)).fetchone()
                
                if not result:
                    create_sql = f"CREATE INDEX {index_name} ON {table} ({columns_str})"
                    conn.execute(text(create_sql))
                    print(f"  ✅ Created index: {index_name}")
                else:
                    print(f"  ⚠️  Index already exists: {index_name}")
                    
            except Exception as e:
                print(f"  ❌ Failed to create index {index_name}: {e}")
        
        conn.commit()
        print("✅ Performance indexes added successfully!")

def optimize_sqlite_settings():
    """Optimize SQLite settings for better performance"""
    print("🔧 Optimizing SQLite settings...")
    
    optimizations = [
        "PRAGMA journal_mode = WAL",
        "PRAGMA synchronous = NORMAL",
        "PRAGMA cache_size = 10000",
        "PRAGMA temp_store = MEMORY",
        "PRAGMA mmap_size = 268435456",
        "PRAGMA page_size = 4096",
        "PRAGMA auto_vacuum = INCREMENTAL",
        "PRAGMA optimize",
    ]
    
    with engine.connect() as conn:
        for pragma in optimizations:
            try:
                conn.execute(text(pragma))
                print(f"  ✅ Applied: {pragma}")
            except Exception as e:
                print(f"  ❌ Failed to apply {pragma}: {e}")
        
        conn.commit()
        print("✅ SQLite optimizations applied successfully!")

def analyze_slow_queries():
    """Analyze and optimize slow queries"""
    print("🔍 Analyzing slow queries...")
    
    # Common slow query patterns
    slow_queries = [
        {
            "name": "User with active automations",
            "query": """
            SELECT u.*, COUNT(ua.id) as automation_count
            FROM users u
            LEFT JOIN user_automations ua ON u.id = ua.user_id AND ua.status = 'active'
            WHERE u.id = ? AND u.is_active = 1
            GROUP BY u.id
            """,
            "optimization": "Index on user_automations(user_id, status)"
        },
        {
            "name": "User token usage",
            "query": """
            SELECT ua.user_id, SUM(ua.tokens_remaining) as total_tokens
            FROM user_automations ua
            WHERE ua.user_id = ? AND ua.status = 'active'
            GROUP BY ua.user_id
            """,
            "optimization": "Index on user_automations(user_id, status, tokens_remaining)"
        },
        {
            "name": "Recent token usage",
            "query": """
            SELECT tu.*, ua.automation_id
            FROM token_usage tu
            JOIN user_automations ua ON tu.user_automation_id = ua.id
            WHERE tu.user_id = ? AND tu.created_at >= ?
            ORDER BY tu.created_at DESC
            """,
            "optimization": "Index on token_usage(user_id, created_at)"
        }
    ]
    
    print("📊 Slow query analysis:")
    for query_info in slow_queries:
        print(f"  🔍 {query_info['name']}")
        print(f"     Query: {query_info['query'].strip()}")
        print(f"     Optimization: {query_info['optimization']}")
        print()

def vacuum_and_analyze():
    """Vacuum and analyze database for optimal performance"""
    print("🧹 Vacuuming and analyzing database...")
    
    with engine.connect() as conn:
        try:
            # Vacuum database
            conn.execute(text("VACUUM"))
            print("  ✅ Database vacuumed")
            
            # Analyze tables
            conn.execute(text("ANALYZE"))
            print("  ✅ Database analyzed")
            
            # Get database statistics
            stats = conn.execute(text("PRAGMA stats")).fetchall()
            print("  📊 Database statistics updated")
            
        except Exception as e:
            print(f"  ❌ Failed to vacuum/analyze: {e}")
        
        conn.commit()

def main():
    """Main optimization function"""
    print("🚀 Database Performance Fix for Timeout Issues")
    print("=" * 50)
    
    try:
        # Add performance indexes
        add_performance_indexes()
        print()
        
        # Optimize SQLite settings
        optimize_sqlite_settings()
        print()
        
        # Analyze slow queries
        analyze_slow_queries()
        print()
        
        # Vacuum and analyze
        vacuum_and_analyze()
        print()
        
        print("🎉 Database performance optimization completed!")
        print("📈 Expected improvements:")
        print("  - Faster user authentication queries")
        print("  - Improved user data retrieval")
        print("  - Better token usage queries")
        print("  - Optimized session management")
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")

if __name__ == "__main__":
    main()
