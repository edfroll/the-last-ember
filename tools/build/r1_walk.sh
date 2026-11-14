#!/usr/bin/env bash
# T-022: the walk bot over every R1 trail (no jumps) and every pad walk to the hearth (no jumps; causeway -> bridge is the castle stairs: --jump).
# Needs the server and the dev client Cam; routes from python3 tools/build/r1_routes.py. Summary -> server/build/walk/r1_walk.log
set -uo pipefail
cd "$(dirname "$0")/../.."
LOG=server/build/walk/r1_walk.log; : > "$LOG"
tools/server.sh rcon 'function last_ember:gate/open {id:"west_pass"}' >/dev/null; sleep 2
DIFF=$(tools/server.sh rcon difficulty | awk '{print tolower($NF)}'); tools/server.sh rcon "difficulty peaceful" >/dev/null   # no skeletons shooting the bot; restored at the end     # the gorge route goes through the rubble
for f in server/build/walk/r1_*.json; do
  n=$(basename "$f" .json); j=""; case "$n" in r1_gate_*) continue;; *causeway_r1_bridge_stub) j="--jump";; esac   # gates: r1_gates_test.py
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  out=$(python3 tools/walkbot.py "$f" $j --clear --out "server/build/walk/$n" 2>&1 | grep -E "PROBLEM|END")
  echo "$n $j :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  if echo "$out" | grep -q PROBLEM; then      # once more: a mob in the way or a lag spike of the cloud client is not the trail's fault
    out=$(python3 tools/walkbot.py "$f" $j --clear --out "server/build/walk/$n" 2>&1 | grep -E "PROBLEM|END")
    echo "$n $j RETRY :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  fi
done
tools/server.sh rcon 'function last_ember:gate/close {id:"west_pass"}' >/dev/null; tools/server.sh rcon "difficulty ${DIFF:-normal}" >/dev/null
