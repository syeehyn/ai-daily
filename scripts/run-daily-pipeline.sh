#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ISSUE_DATE="${ISSUE_DATE:-$(date -u +%F)}"
X_MODE="${X_MODE:-mock}"
X_LOCAL_DIR="${X_LOCAL_DIR:-$HOME/.openclaw/local/ai-daily/x-snapshots}"
SYNC_X_TO_ISSUES="${SYNC_X_TO_ISSUES:-0}"

echo "[1/3] Fetch HF daily data (placeholder)"
echo "HF fetch placeholder: integrate existing Hugging Face fetch flow here."

echo "[2/3] Fetch X snapshot (mode=$X_MODE, date=$ISSUE_DATE, local=$X_LOCAL_DIR, sync=$SYNC_X_TO_ISSUES)"
if [[ "$SYNC_X_TO_ISSUES" == "1" ]]; then
  python3 scripts/fetch-x-snapshot.py --mode "$X_MODE" --date "$ISSUE_DATE" --local-dir "$X_LOCAL_DIR" --sync-to-issues
else
  python3 scripts/fetch-x-snapshot.py --mode "$X_MODE" --date "$ISSUE_DATE" --local-dir "$X_LOCAL_DIR"
fi

echo "[3/3] Build static site"
python3 scripts/build-site.py

echo "Pipeline completed for $ISSUE_DATE"
