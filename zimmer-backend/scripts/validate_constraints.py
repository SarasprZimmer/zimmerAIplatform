"""
Validates core DB constraints (UNIQUE, FK, NOT NULL, Enum-like checks).
Uses DATABASE_URL from env; for SQLite ensures foreign_keys=ON.
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, ProgrammingError

DB_URL = os.getenv("DATABASE_URL", "sqlite:///./_test_roundtrip.db")
engine = create_engine(DB_URL, future=True)

# Ensure FK ON for SQLite
with engine.connect() as conn:
    try:
        conn.exec_driver_sql("PRAGMA foreign_keys=ON")
    except Exception:
        pass

def must_fail(stmt, desc):
    try:
        with engine.begin() as conn:
            conn.execute(text(stmt))
    except Exception as e:
        print(f"✅ Expected fail [{desc}]:", type(e).__name__)
        return True
    print(f"❌ Should have failed but succeeded [{desc}]")
    return False

def must_pass(stmt, desc):
    try:
        with engine.begin() as conn:
            conn.execute(text(stmt))
        print(f"✅ Passed [{desc}]")
        return True
    except Exception as e:
        print(f"❌ Unexpected fail [{desc}]: {type(e).__name__} {e}")
        return False

def cleanup_test_data():
    """Clean up any test data from previous runs"""
    with engine.begin() as conn:
        try:
            # Delete test data in reverse dependency order
            conn.execute(text("DELETE FROM payments WHERE transaction_id LIKE 'tx%'"))
            conn.execute(text("DELETE FROM user_automations WHERE telegram_bot_token LIKE '%ABC%'"))
            conn.execute(text("DELETE FROM automations WHERE name = 'Travel AI'"))
            conn.execute(text("DELETE FROM users WHERE email = 'admin@test.local'"))
            print("🧹 Cleaned up previous test data")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

# Minimal smoke based on your models; adjust table/columns to match actual schema.
# Assumptions: users(id PK, email UNIQUE NOT NULL, role, password_hash NOT NULL)
#              sessions(user_id FK users.id)
#              automations(id PK, name, pricing_type, health_status NOT NULL, is_listed NOT NULL)
#              user_automations(user_id FK, automation_id FK, telegram_bot_token UNIQUE, tokens_remaining NOT NULL)
#              payments(user_id FK, automation_id FK, amount NOT NULL)

tests = [
    # Clean up first
    ("", "cleanup", "cleanup"),
    
    # Insert a valid user
    ("INSERT INTO users (name, email, password_hash, role, is_active, created_at) "
     "VALUES ('Admin','admin@test.local','x', 'manager', 1, CURRENT_TIMESTAMP)",
     "insert valid user"),

    # UNIQUE email constraint check
    ("INSERT INTO users (name, email, password_hash, role, is_active, created_at) "
     "VALUES ('Dup','admin@test.local','x', 'manager', 1, CURRENT_TIMESTAMP)",
     "unique email duplicate (should fail)", True),

    # NOT NULL check (password_hash)
    ("INSERT INTO users (name, email, role, is_active, created_at) "
     "VALUES ('NoPass','nopass@test.local','support_staff', 1, CURRENT_TIMESTAMP)",
     "missing password_hash (should fail)", True),

    # Valid automation with required health_status and is_listed fields
    ("INSERT INTO automations (name, description, pricing_type, price_per_token, status, api_endpoint, service_token_hash, health_status, is_listed, created_at) "
     "VALUES ('Travel AI','desc','token_per_session', 10.0, 1, '/x','hash', 'unknown', 0, CURRENT_TIMESTAMP)",
     "insert automation"),

    # Valid FK pair (user_automations)
    ("INSERT INTO user_automations (user_id, automation_id, telegram_bot_token, tokens_remaining, demo_tokens, is_demo_active, demo_expired, status, provisioned_at, integration_status) "
     "VALUES (1, 1, '123:ABC', 5, 5, 1, 0, 'active', CURRENT_TIMESTAMP, 'ok')",
     "insert user_automation valid"),

    # UNIQUE telegram_bot_token
    ("INSERT INTO user_automations (user_id, automation_id, telegram_bot_token, tokens_remaining, demo_tokens, is_demo_active, demo_expired, status, provisioned_at, integration_status) "
     "VALUES (1, 1, '123:ABC', 5, 5, 1, 0, 'active', CURRENT_TIMESTAMP, 'ok')",
     "duplicate telegram_bot_token (should fail)", True),

    # FK violation: non-existent user_id
    ("INSERT INTO user_automations (user_id, automation_id, telegram_bot_token, tokens_remaining, demo_tokens, is_demo_active, demo_expired, status, provisioned_at, integration_status) "
     "VALUES (999, 1, 'NOUSER', 5, 5, 1, 0, 'active', CURRENT_TIMESTAMP, 'ok')",
     "FK violation user_id (should fail)", True),

    # Payment valid
    ("INSERT INTO payments (user_id, automation_id, amount, tokens_purchased, method, gateway, transaction_id, ref_id, status, created_at) "
     "VALUES (1, 1, 100000, 100, 'online', 'zarinpal', 'tx1', 'ref1', 'paid', CURRENT_TIMESTAMP)",
     "insert payment valid"),

    # Payment FK violation
    ("INSERT INTO payments (user_id, automation_id, amount, tokens_purchased, method, gateway, transaction_id, ref_id, status, created_at) "
     "VALUES (999, 1, 100000, 100, 'online', 'zarinpal', 'tx2', 'ref2', 'paid', CURRENT_TIMESTAMP)",
     "payment FK violation user_id (should fail)", True),
]

all_ok = True
for stmt, desc, *should_fail in tests:
    if desc == "cleanup":
        cleanup_test_data()
        continue
        
    if should_fail:
        ok = must_fail(stmt, desc)
    else:
        ok = must_pass(stmt, desc)
    all_ok = all_ok and ok

if all_ok:
    print("\n🎉 All constraint validations passed!")
else:
    print("\n❌ Some constraint validations failed!")
    exit(1)
