#!/usr/bin/env bash
# T-033: the walk bot through the Iron Ore Mines (no jumps): n_in (from the trail refuge -> causeway to the yard, the adit, H1, the
# inclines, H2, H3, the water, the big collapse; n_in_b back) with the cave-ins kept from falling (their scores set down, the blocks
# standing: the bot walks through the zones), n_bypass1..3 round the cave-ins down (they fall first), n_approach (the trail of T-022 along
# the place, n_approach_b). Then the mines are reset. Needs the server and the dev client Cam; routes from tools/build/mines_routes.py.
# Optional filter: a part of the route name. Summary -> server/build/walk/mines_walk.log.
set -uo pipefail
cd "$(dirname "$0")/../.."
R() { tools/server.sh rcon "$1" >/dev/null; }
LOG=server/build/walk/mines_walk.log; : > "$LOG"
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
R "function last_ember:mines/reset"
for f in server/build/walk/n_*.json; do
  n=$(basename "$f" .json)
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  case "$n" in
    n_bypass*) R "function last_ember:mines/gen/fall_1"; R "function last_ember:mines/gen/fall_2"; R "function last_ember:mines/gen/fall_3" ;;
    *) R "function last_ember:mines/reset"; for k in 1 2 3; do R "scoreboard players set #c$k le.mn 1"; done ;;
  esac
  walk $n
done
R "function last_ember:mines/reset"
R "difficulty ${DIFF:-easy}"; R "gamemode survival Cam2"
