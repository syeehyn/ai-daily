#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_DIR="$ROOT_DIR/apps/web"

if [[ ! -d "$WEB_DIR/node_modules" ]]; then
  echo "Installing web dependencies..."
  (cd "$WEB_DIR" && npm install)
fi

if [[ "${MODE:-dev}" == "build" ]]; then
  (cd "$WEB_DIR" && npm run typecheck && npm run build)
else
  (cd "$WEB_DIR" && npm run dev)
fi
