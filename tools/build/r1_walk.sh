#!/usr/bin/env bash
# T-022: the walk bot over every R1 trail (no jumps) and every stub over the natural ground of a place (--jump).
# Needs the server and the dev client Cam; routes from python3 tools/build/r1_routes.py. Summary -> server/build/walk/r1_walk.log
set -uo pipefail
cd "$(dirname "$0")/../.."
LOG=server/build/walk/r1_walk.log; : > "$LOG"
for f in server/build/walk/r1_*.json; do
  n=$(basename "$f" .json); j=""; case "$n" in *_stub) j="--jump";; esac
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  out=$(python3 tools/walkbot.py "$f" $j --out "server/build/walk/$n" 2>&1 | grep -E "PROBLEM|END")
  echo "$n $j :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
done
