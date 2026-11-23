#!/usr/bin/env bash
# T-031: the walk bot through the Village of Heather and the Dragon Ridge (no jumps): bonfire 9 -> the bridge -> the street -> the
# square -> the church -> up the bell tower to the ringer and back (h_in, h_in_b); into every house and back (h_house<N>: the window,
# the cellar, the outer stair, the ladder onto the roof, the door in the hearth); the church -> the trail -> the mouth and back
# (h_ridge, h_ridge_b); the approaches of T-022 to the pad (h_approach, h_approach_b). Needs the server and the dev client Cam;
# routes from python3 tools/build/heather_routes.py. Optional filter: a part of the route name. Summary -> server/build/walk/heather_walk.log.
set -uo pipefail
cd "$(dirname "$0")/../.."
R() { tools/server.sh rcon "$1" >/dev/null; }
LOG=server/build/walk/heather_walk.log; : > "$LOG"
DIFF=$(tools/server.sh rcon difficulty | awk '{print tolower($NF)}'); R "difficulty peaceful"; R "gamemode spectator Cam2"; R "time set noon"
R "execute as Cam run function last_ember:sleep/set_awake {ticks:0}"
walk() {
  n=$1; shift; out=$(python3 tools/walkbot.py "server/build/walk/$n.json" --clear --out "server/build/walk/$n" "$@" 2>&1 | grep -E "PROBLEM|END")
  echo "$n :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  if echo "$out" | grep -q PROBLEM; then
    out=$(python3 tools/walkbot.py "server/build/walk/$n.json" --clear --out "server/build/walk/$n" "$@" 2>&1 | grep -E "PROBLEM|END")
    echo "$n RETRY :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  fi
}
for f in server/build/walk/h_*.json; do
  n=$(basename "$f" .json)
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  walk $n
done
R "difficulty ${DIFF:-easy}"; R "gamemode survival Cam2"
