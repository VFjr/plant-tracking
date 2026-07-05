#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$ROOT/backups}"
STAMP="$(date +%F-%H%M%S)"
ARCHIVE="$BACKUP_DIR/plant-tracking-$STAMP.tar.gz"

if [[ ! -d "$ROOT/data" ]]; then
  echo "No data directory at $ROOT/data — nothing to back up." >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
tar -czf "$ARCHIVE" -C "$ROOT" data/

echo "Backup written to $ARCHIVE"
