#!/usr/bin/env bash
# why: backs /telemetry — toggles Claude Code OTel export (settings env) and the local Grafana stack together.
# hazard: settings.json is a symlink into this repo; write through it (redirect), never mv over it.
set -euo pipefail
settings="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json"
compose="$(cd "$(dirname "$0")/.." && pwd)/docker/telemetry/docker-compose.yml"

set_flag() {
  local json
  json=$(jq --arg v "$1" '.env.CLAUDE_CODE_ENABLE_TELEMETRY = $v' "$settings")
  printf '%s\n' "$json" >"$settings"
}

case "${1:-status}" in
  on)
    set_flag 1
    docker compose -f "$compose" up -d
    echo "telemetry: ON (export starts next session) — http://127.0.0.1:3001/d/claude-code-cost"
    ;;
  off)
    set_flag 0
    docker compose -f "$compose" stop
    echo "telemetry: OFF (next session; history kept)"
    ;;
  status)
    flag=$(jq -r '.env.CLAUDE_CODE_ENABLE_TELEMETRY // "0"' "$settings")
    [ "$flag" = 1 ] && echo "telemetry: ON" || echo "telemetry: OFF"
    docker compose -f "$compose" ps --format '{{.Service}} {{.State}}'
    echo "dashboard: http://127.0.0.1:3001/d/claude-code-cost"
    ;;
  *)
    echo "usage: telemetry.sh [on|off|status]" >&2
    exit 2
    ;;
esac
