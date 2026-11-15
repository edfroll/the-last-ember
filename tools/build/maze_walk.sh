#!/usr/bin/env bash
# T-024: the walk bot through the maze (no jumps): bonfire 3 -> the gate -> the court of the sanctum with all movable cells in variant
# 1, 2, 3 (routes m_in_N), and the sanctum -> the open secret exit -> the band on the terrace west of the outer wall -> bonfire 3 (m_exit).
# Needs the server and the dev client Cam; routes from python3 tools/build/maze_routes.py. Summary -> server/build/walk/maze_walk.log
set -uo pipefail
cd "$(dirname "$0")/../.."
R() { tools/server.sh rcon "$1" >/dev/null; }
LOG=server/build/walk/maze_walk.log; : > "$LOG"
DIFF=$(tools/server.sh rcon difficulty | awk '{print tolower($NF)}'); R "difficulty peaceful"; R "gamemode spectator Cam2"
EXIT0=$(tools/server.sh rcon "scoreboard players get #exit le.mz" | grep -o 'has [0-9]*' | awk '{print $2}')
walk() {
  n=$1; out=$(python3 tools/walkbot.py "server/build/walk/$n.json" --clear --out "server/build/walk/$n" 2>&1 | grep -E "PROBLEM|END")
  echo "$n :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  if echo "$out" | grep -q PROBLEM; then
    out=$(python3 tools/walkbot.py "server/build/walk/$n.json" --clear --out "server/build/walk/$n" 2>&1 | grep -E "PROBLEM|END")
    echo "$n RETRY :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  fi
}
for v in 1 2 3; do
  [ -n "${1:-}" ] && [[ "m_in_$v" != *$1* ]] && continue
  for k in 1 2 3 4 5 6; do R "function last_ember:maze/set {cell:$k,var:$v}"; done
  R "scoreboard players set #shuf le.mz -100000"; R "scoreboard players set #gcd le.mz 2147483000"    # no rebuild under the bot
  walk m_in_$v
done
if [ -z "${1:-}" ] || [[ "m_exit" == *$1* ]]; then
  R "scoreboard players set #exit le.mz 1"; R "data modify storage last_ember:maze exit set value 1"; R "execute in minecraft:overworld run function last_ember:maze/gen/sync_exit"
  walk m_exit
  R "scoreboard players set #exit le.mz ${EXIT0:-0}"; R "data modify storage last_ember:maze exit set value ${EXIT0:-0}"; R "execute in minecraft:overworld run function last_ember:maze/gen/sync_exit"
fi
R "scoreboard players set #shuf le.mz 0"; R "scoreboard players set #gcd le.mz 0"; R "difficulty ${DIFF:-normal}"; R "gamemode survival Cam2"
