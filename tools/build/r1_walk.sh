#!/usr/bin/env bash
# T-022: the walk bot over every R1 trail (no jumps) and every pad walk to the hearth (no jumps; causeway -> bridge is the castle stairs: --jump).
# Needs the server and the dev client Cam; routes from python3 tools/build/r1_routes.py. Summary -> server/build/walk/r1_walk.log
set -uo pipefail
cd "$(dirname "$0")/../.."
LOG=server/build/walk/r1_walk.log; : > "$LOG"
tools/server.sh rcon 'function last_ember:gate/open {id:"west_pass"}' >/dev/null; sleep 2     # the gorge route goes through the rubble
for f in server/build/walk/r1_*.json; do
  n=$(basename "$f" .json); j=""; case "$n" in r1_gate_*) continue;; *causeway_r1_bridge_stub) j="--jump";; esac   # gates: r1_gates_test.py
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  out=$(python3 tools/walkbot.py "$f" $j --out "server/build/walk/$n" 2>&1 | grep -E "PROBLEM|END")
  echo "$n $j :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
done
tools/server.sh rcon 'function last_ember:gate/close {id:"west_pass"}' >/dev/null
