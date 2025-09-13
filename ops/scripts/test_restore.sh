#!/usr/bin/env bash
set -euo pipefail

# 1) Pick latest backup
LATEST="$(ops/scripts/latest_backup.sh)"
echo ">>> Using latest backup: $LATEST"

# 2) Restore into fresh postgres-restore
bash ops/scripts/restore_db.sh "$LATEST"

# 3) Run Alembic migrations (idempotent) against restored DB
echo ">>> Running alembic upgrade head against restored DB"
pushd zimmer-backend >/dev/null
export DATABASE_URL="postgresql+psycopg2://zimmer:zimmer@localhost:5433/zimmer_restore"
alembic -c alembic.ini upgrade head

# 4) Run constraint checks against restored DB
echo ">>> Running constraint validation"
python scripts/validate_constraints.py
popd >/dev/null

echo "🎉 Restore test passed: backup can be restored and schema is consistent."
