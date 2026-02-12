#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ISSUE_DATE="${ISSUE_DATE:-$(date -u +%F)}"
X_MODE="${X_MODE:-mock}"
X_LOCAL_DIR="${X_LOCAL_DIR:-$HOME/.openclaw/local/ai-daily/x-snapshots}"
SYNC_X_TO_ISSUES="${SYNC_X_TO_ISSUES:-1}"


echo "[1/4] Fetch HF daily data (placeholder hook for OpenClaw source ingest)"
echo "HF fetch placeholder: integrate existing Hugging Face fetch flow here."

echo "[2/4] Fetch X snapshot (mode=$X_MODE, date=$ISSUE_DATE, sync=$SYNC_X_TO_ISSUES)"
if [[ "$SYNC_X_TO_ISSUES" == "1" ]]; then
  python3 scripts/fetch-x-snapshot.py --mode "$X_MODE" --date "$ISSUE_DATE" --local-dir "$X_LOCAL_DIR" --sync-to-issues
else
  python3 scripts/fetch-x-snapshot.py --mode "$X_MODE" --date "$ISSUE_DATE" --local-dir "$X_LOCAL_DIR"
fi

echo "[3/4] Fetch paper images with fallback strategy"
python3 scripts/fetch-paper-images.py --date "$ISSUE_DATE"

echo "[4/4] Build issue adapter data for frontend"
python3 scripts/build-issue-data.py --date "$ISSUE_DATE"

echo "OpenClaw pipeline completed for $ISSUE_DATE"
