#!/usr/bin/env bash
# why: tlc-exec is external to this repo; mirror its output into the shared external hook log.
# hazard: pipefail keeps tlc-exec's exit code (exit 2 = block) instead of tee's always-0.
set -o pipefail
mkdir -p "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/logs"
# why: tlc needs Node >= 24, but Claude inherits whatever nvm node the launching shell had active;
#      prefer nvm's NODE_VERSION (set in settings.json env), fall back to PATH node.
node=$HOME/.nvm/versions/node/v${NODE_VERSION}/bin/node
[ -n "$NODE_VERSION" ] && [ -x "$node" ] || node=node
"$node" $HOME/.tlc/harness/bin/tlc-exec.mjs "$@" 2>&1 | bash "$(dirname "$0")/ext-log.sh" "TlcExec-$1"
