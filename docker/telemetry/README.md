# Claude Code telemetry

Local OpenTelemetry sink for Claude Code cost and token metrics. No extra model calls or tokens:
Claude Code exports the usage numbers it already receives from the API.

```bash
docker compose up -d   # from this directory
```

- Grafana dashboard: http://127.0.0.1:3001/d/claude-code-cost (anonymous admin, localhost only)
- Prometheus: http://127.0.0.1:9090 (90-day / 1 GB retention)
- OTLP receiver: `localhost:4317` (gRPC) and `localhost:4318` (HTTP)

The exporter env vars (`CLAUDE_CODE_ENABLE_TELEMETRY`, `OTEL_*`) live in `claude/settings.json`.
Memory limits: collector 128m, Prometheus 256m, Grafana 256m.

When the stack is down, Claude Code keeps working and simply drops the metrics.

Cost panels sum `max_over_time` of each session's cumulative counter, so a session that started
before the selected range is counted in full.
