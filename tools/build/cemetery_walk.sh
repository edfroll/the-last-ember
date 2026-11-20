#!/usr/bin/env bash
# T-027: the walk bot through the Cemetery and the Lodge (no jumps): bonfire 2 -> the lodge door and back (c_lodge, c_lodge_b); bonfire 2
# -> the gate -> the descent -> the crypt door -> the top of the hill (c_down) and back up (c_up); the crypt from the door through the
# corridor and the hall out by its exit (c_crypt: the door opened, the Magister laid to rest first); each barrow in by the dromos and out
# over the top of its mound (c_barrow_N). Needs the server and the dev client Cam; routes from python3 tools/build/cemetery_routes.py.
# Optional filter: a part of the route name. Summary -> server/build/walk/cemetery_walk.log; the cemetery is reset at the end.
set -uo pipefail
cd "$(dirname "$0")/../.."
R() { tools/server.sh rcon "$1" >/dev/null; }
LOG=server/build/walk/cemetery_walk.log; : > "$LOG"
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
for n in c_lodge c_lodge_b c_spy c_down c_up; do
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  walk $n
done
R "scoreboard players set #door le.cem 1"; R "scoreboard players set #q le.cem 3"; R "function last_ember:cemetery/mag_rest"
for n in c_crypt c_barrow_1 c_barrow_2 c_barrow_3 c_barrow_4 c_barrow_5; do
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  walk $n
done
R "function last_ember:cemetery/reset"; R "difficulty ${DIFF:-easy}"; R "gamemode survival Cam2"
