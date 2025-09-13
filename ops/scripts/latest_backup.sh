#!/usr/bin/env bash
set -euo pipefail

dir="${1:-ops/backup/archives}"
latest="$(ls -1t "$dir"/zimmer-*.dump 2>/dev/null | head -n1 || true)"

if [ -z "$latest" ]; then
  echo "No backups found in $dir" >&2
  exit 1
fi

echo "$latest"
