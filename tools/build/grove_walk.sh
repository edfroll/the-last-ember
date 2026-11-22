#!/usr/bin/env bash
# T-030: the walk bot through the Mushroom Grove (no jumps): bonfire 10 -> the path -> the door -> both storeys -> the observatory (v_in)
# and back (v_out); the garden and its bench (v_garden); the approaches of T-022 through the grove to the pad and back (v_approach,
# v_approach_b). Needs the server and the dev client Cam; routes from python3 tools/build/grove_routes.py. Optional filter: a part of the
# route name. Summary -> server/build/walk/grove_walk.log.
set -uo pipefail
cd "$(dirname "$0")/../.."
R() { tools/server.sh rcon "$1" >/dev/null; }
LOG=server/build/walk/grove_walk.log; : > "$LOG"
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
for n in v_in v_out v_garden v_approach v_approach_b; do
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  walk $n
done
R "difficulty ${DIFF:-easy}"; R "gamemode survival Cam2"
