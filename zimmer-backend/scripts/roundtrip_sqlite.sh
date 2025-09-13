#!/usr/bin/env bash
set -euo pipefail

export DATABASE_URL=${TEST_SQLITE_URL:-sqlite:///./_test_roundtrip.db}

echo ">>> Removing any previous test DB"
rm -f ./_test_roundtrip.db || true

echo ">>> Alembic downgrade to base (fresh)"
alembic -c alembic.ini downgrade base

echo ">>> Alembic upgrade to head"
alembic -c alembic.ini upgrade head

echo ">>> Alembic downgrade back to base"
alembic -c alembic.ini downgrade base

echo ">>> Alembic upgrade to head again (idempotency check)"
alembic -c alembic.ini upgrade head

echo ">>> Roundtrip complete."
