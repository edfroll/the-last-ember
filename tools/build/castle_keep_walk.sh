#!/usr/bin/env bash
# T-029: the walk bot through the castle (no jumps): c_tour (the gate -> the court -> the wings -> the galleries -> the vestibule -> the
# throne hall -> its gallery -> back), c_dungeon (the library -> the gaol -> the crypt -> back; the gaol door open), c_secret (the
# reliquary -> the spiral -> the tunnel -> the pier door -> the pier; the doors open). Needs the server and the dev client Cam; routes
# from python3 tools/build/castle_keep_routes.py. Optional filter: a part of the route name. Summary -> server/build/walk/castle_keep_walk.log.
set -uo pipefail
cd "$(dirname "$0")/../.."
R() { tools/server.sh rcon "$1" >/dev/null; }
LOG=server/build/walk/castle_keep_walk.log; : > "$LOG"
DIFF=$(tools/server.sh rcon difficulty | awk '{print tolower($NF)}'); R "difficulty peaceful"; R "gamemode spectator Cam2"; R "time set noon"
R "execute as Cam run function last_ember:sleep/set_awake {ticks:0}"; R "gamemode survival Cam"; R "forceload add 400 -40 490 95"
R "function last_ember:castle/kg/t_gate_open"; R "function last_ember:castle/kg/t_gaol_door_open"; R "function last_ember:castle/kg/t_reliq_door_open"
R "function last_ember:castle/kg/t_pier_door_open"
walk() {
  n=$1; shift; R "tag Cam add le.cpass"
  out=$(python3 tools/walkbot.py "server/build/walk/$n.json" --clear --out "server/build/walk/$n" "$@" 2>&1 | grep -E "PROBLEM|END")
  echo "$n :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  if echo "$out" | grep -q PROBLEM; then
    R "tag Cam add le.cpass"
    out=$(python3 tools/walkbot.py "server/build/walk/$n.json" --clear --out "server/build/walk/$n" "$@" 2>&1 | grep -E "PROBLEM|END")
    echo "$n RETRY :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  fi
}
for n in c_tour c_dungeon c_secret; do
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  walk $n
done
R "function last_ember:castle/kg/reset_all"; R "difficulty ${DIFF:-easy}"; R "gamemode survival Cam2"; R "forceload remove 400 -40 490 95"
