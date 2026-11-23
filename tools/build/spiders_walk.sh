#!/usr/bin/env bash
# T-032: the walk bot through the Spider Thicket (no jumps): s_in (from the trail Heather -> Garden by the animal trail and the trail of
# the victims to the live cocoon and back, s_in_b), s_roots (from the cocoon down the burrow of roots to the floor of the nest and back),
# s_barrels (to the 3 cocoons with remains and back), s_approach (the approach of T-022 to bonfire 4, s_approach_b). Needs the server
# and the dev client Cam;
# routes from python3 tools/build/spiders_routes.py. Optional filter: a part of the route name. Summary -> server/build/walk/spiders_walk.log.
set -uo pipefail
cd "$(dirname "$0")/../.."
R() { tools/server.sh rcon "$1" >/dev/null; }
LOG=server/build/walk/spiders_walk.log; : > "$LOG"
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
for f in server/build/walk/s_*.json; do
  n=$(basename "$f" .json)
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  walk $n
done
R "difficulty ${DIFF:-easy}"; R "gamemode survival Cam2"
