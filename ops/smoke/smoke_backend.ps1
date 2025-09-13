$ErrorActionPreference = "Stop"

Write-Host "== Zimmer Backend Smoke =="
Push-Location ../../zimmer-backend

# 0) Python env sanity
python -V; pip -V

# 1) Install minimal deps to run tests & alembic
pip install -q -r requirements.txt
if (Test-Path requirements-dev.txt) { pip install -q -r requirements-dev.txt }

# 2) SQLite safe DB for smoke
$env:DATABASE_URL = "sqlite:///./_smoke.db"

# 3) Migrations
alembic -c alembic.ini upgrade head

# 4) Drift guard (exit code 0 = ok, 2 = drift)
try {
  python scripts/check_migration_drift.py
} catch { Write-Host "Drift check threw; investigate scripts/check_migration_drift.py output" }

# 5) Constraint validator (should print all good or failures)
try {
  python scripts/validate_constraints.py
} catch { Write-Host "Constraint validation failed"; throw }

# 6) Core pytest subset (adjust paths if different)
$tests = @(
  "tests/test_health.py",
  "tests/test_auth_flow.py",
  "tests/test_user_profile_password.py",
  "tests/test_payments_sandbox.py",
  "tests/test_notifications.py",
  "tests/test_admin_notifications.py",
  "tests/test_migrations_guard.py",
  "tests/test_discounts.py",
  "tests/test_admin_discounts.py",
  "tests/test_2fa.py",
  "tests/test_email_verification.py"
) | Where-Object { Test-Path $_ }

if ($tests.Count -eq 0) {
  Write-Host "No tests found, skipping pytest";
} else {
  pytest -q $tests
}

Pop-Location
Write-Host "== Backend smoke done =="
