#!/usr/bin/env pwsh
# PowerShell version of roundtrip_sqlite.sh

$env:DATABASE_URL = if ($env:TEST_SQLITE_URL) { $env:TEST_SQLITE_URL } else { "sqlite:///./_test_roundtrip.db" }

Write-Host ">>> Removing any previous test DB"
if (Test-Path "./_test_roundtrip.db") {
    Remove-Item "./_test_roundtrip.db" -Force
}

Write-Host ">>> Alembic downgrade to base (fresh)"
alembic -c alembic.ini downgrade base

Write-Host ">>> Alembic upgrade to head"
alembic -c alembic.ini upgrade head

Write-Host ">>> Alembic downgrade back to base"
alembic -c alembic.ini downgrade base

Write-Host ">>> Alembic upgrade to head again (idempotency check)"
alembic -c alembic.ini upgrade head

Write-Host ">>> Roundtrip complete."
