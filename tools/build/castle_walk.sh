#!/usr/bin/env bash
# T-028: the walk bot through the castle approaches (no jumps): bonfire 7 -> the descent -> the causeway -> the pier (Cam carries the
# seal) -> the stair -> bonfire 8 -> the bridge -> the gate (k_down) and back (k_up); the sandy way out of the knock zone (k_sand).
# Needs the server and the dev client Cam; routes from python3 tools/build/castle_routes.py. Optional filter: a part of the route name.
# Summary -> server/build/walk/castle_walk.log.
set -uo pipefail
cd "$(dirname "$0")/../.."
R() { tools/server.sh rcon "$1" >/dev/null; }
LOG=server/build/walk/castle_walk.log; : > "$LOG"
DIFF=$(tools/server.sh rcon difficulty | awk '{print tolower($NF)}'); R "difficulty peaceful"; R "gamemode spectator Cam2"; R "time set noon"
R "execute as Cam run function last_ember:sleep/set_awake {ticks:0}"; R "gamemode survival Cam"; R "function last_ember:castle/reset"
R 'clear Cam *[minecraft:custom_data~{le_citem:"seal"}]'; R 'execute as Cam run function last_ember:cemetery/give {key:"seal"}'
walk() {
  n=$1; shift; [ "$n" = k_up ] && R "tag Cam add le.cpass"        # k_up starts at the gate: as one who came up the stair
  out=$(python3 tools/walkbot.py "server/build/walk/$n.json" --clear --out "server/build/walk/$n" "$@" 2>&1 | grep -E "PROBLEM|END")
  echo "$n :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  if echo "$out" | grep -q PROBLEM; then
    [ "$n" = k_up ] && R "tag Cam add le.cpass"
    out=$(python3 tools/walkbot.py "server/build/walk/$n.json" --clear --out "server/build/walk/$n" "$@" 2>&1 | grep -E "PROBLEM|END")
    echo "$n RETRY :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  fi
}
for n in k_down k_up; do
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  walk $n
done
R 'clear Cam *[minecraft:custom_data~{le_citem:"seal"}]'; R "function last_ember:cemetery/reset"
for n in k_sand; do
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  walk $n
done
R "function last_ember:castle/reset"; R "difficulty ${DIFF:-easy}"; R "gamemode survival Cam2"
