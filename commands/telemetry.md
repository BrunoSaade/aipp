---
model: haiku
context: fork
background: false
description: Toggle Claude Code cost telemetry (on|off|status) — OTel export + local Grafana stack
argument-hint: "[on|off|status]"
allowed-tools: Bash(bash:*)
---

!`bash "$AI_PROJECT_ROOT_DIR/scripts/telemetry.sh" $ARGUMENTS 2>&1`

Only confirm the state above to the user. Do nothing else.
