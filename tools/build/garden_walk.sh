#!/usr/bin/env bash
# T-025: the walk bot through the Garden of Silence: bonfire 4 -> the gardener's house -> the path -> the orangery -> the pedestal (g_in)
# and back (g_out), no jumps; from the path to each of the 6 hearts with jumps (g_heart_N). Needs the server and the dev client Cam;
# routes from python3 tools/build/garden_routes.py. Optional filter: a part of the route name. Summary -> server/build/walk/garden_walk.log
set -uo pipefail
cd "$(dirname "$0")/../.."
R() { tools/server.sh rcon "$1" >/dev/null; }
LOG=server/build/walk/garden_walk.log; : > "$LOG"
DIFF=$(tools/server.sh rcon difficulty | awk '{print tolower($NF)}'); R "difficulty peaceful"; R "gamemode spectator Cam2"; R "time set noon"
walk() {
  n=$1; shift; out=$(python3 tools/walkbot.py "server/build/walk/$n.json" --clear --out "server/build/walk/$n" "$@" 2>&1 | grep -E "PROBLEM|END")
  echo "$n :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  if echo "$out" | grep -q PROBLEM; then
    out=$(python3 tools/walkbot.py "server/build/walk/$n.json" --clear --out "server/build/walk/$n" "$@" 2>&1 | grep -E "PROBLEM|END")
    echo "$n RETRY :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  fi
}
for n in g_in g_out; do
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  walk $n
done
for k in 1 2 3 4 5 6; do
  [ -n "${1:-}" ] && [[ "g_heart_$k" != *$1* ]] && continue
  walk g_heart_$k --jump
done
R "difficulty ${DIFF:-normal}"; R "gamemode survival Cam2"
