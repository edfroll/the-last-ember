#!/usr/bin/env bash
# T-026: the walk bot through the Crooked Fens: bonfire 5 -> the climb -> the outer pier (f_climb, no jumps); the outer pier -> the
# boardwalk (over the tussocks, round the dark gap by the piles) -> the hut's porch -> the hall (f_board, jumps); and back (f_back).
# Needs the server and the dev client Cam; routes from python3 tools/build/fens_routes.py. Optional filter: a part of the route name.
# A fall into the water is a problem (the route expects the feet on the boardwalk). Summary -> server/build/walk/fens_walk.log
set -uo pipefail
cd "$(dirname "$0")/../.."
R() { tools/server.sh rcon "$1" >/dev/null; }
LOG=server/build/walk/fens_walk.log; : > "$LOG"
DIFF=$(tools/server.sh rcon difficulty | awk '{print tolower($NF)}'); R "difficulty peaceful"; R "gamemode spectator Cam2"; R "time set noon"
R "scoreboard players set #ms le.fn 3"; R "execute store result score #mt le.fn run time query gametime"; R "scoreboard players add #mt le.fn 72000"   # the Master stays down
walk() {
  n=$1; shift; out=$(python3 tools/walkbot.py "server/build/walk/$n.json" --clear --out "server/build/walk/$n" "$@" 2>&1 | grep -E "PROBLEM|END")
  echo "$n :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  if echo "$out" | grep -q PROBLEM; then
    out=$(python3 tools/walkbot.py "server/build/walk/$n.json" --clear --out "server/build/walk/$n" "$@" 2>&1 | grep -E "PROBLEM|END")
    echo "$n RETRY :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  fi
}
for n in f_climb; do
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  walk $n
done
for n in f_board f_back; do
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  walk $n --jump
done
R "scoreboard players set #ms le.fn 0"; R "difficulty ${DIFF:-easy}"; R "gamemode survival Cam2"
