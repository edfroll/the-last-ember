#!/usr/bin/env bash
# T-034: the walk bot through the treasuries of R1 (routes from tools/build/treasury_routes.py): o_approach (the trail -> the chain of
# bones -> the oak: natural hill ground, --jump: the bot jumps where it is stuck, the count reported) and back, o_in / o_in_b (the stair,
# no jumps), g_in / g_in_b (the stepping stones, no jumps), t_ledges / t_ledges_b (3 jumps over the gaps, the seal of the colossi on Cam).
# Peaceful (no owners), --clear. Needs the server and the dev client Cam. Optional filter: a part of the route name.
# Summary -> server/build/walk/treasury_walk.log.
set -uo pipefail
cd "$(dirname "$0")/../.."
R() { tools/server.sh rcon "$1" >/dev/null; }
LOG=server/build/walk/treasury_walk.log; : > "$LOG"
DIFF=$(tools/server.sh rcon difficulty | awk '{print tolower($NF)}'); R "difficulty peaceful"; R "gamemode spectator Cam2"; R "time set noon"
R "execute as Cam run function last_ember:sleep/set_awake {ticks:0}"
R 'execute as Cam run function last_ember:cemetery/give {key:"seal"}'; R "tag Cam add le.cpass"
walk() {
  n=$1; shift; out=$(python3 tools/walkbot.py "server/build/walk/$n.json" --clear --out "server/build/walk/$n" "$@" 2>&1 | grep -E "PROBLEM|END")
  echo "$n :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  if echo "$out" | grep -q PROBLEM; then
    out=$(python3 tools/walkbot.py "server/build/walk/$n.json" --clear --out "server/build/walk/$n" "$@" 2>&1 | grep -E "PROBLEM|END")
    echo "$n RETRY :: $(echo "$out" | tr '\n' ' ')" | tee -a "$LOG"
  fi
}
for n in o_approach o_in o_in_b o_approach_b g_in g_in_b t_ledges t_ledges_b; do
  [ -n "${1:-}" ] && [[ "$n" != *$1* ]] && continue
  case "$n" in
    o_approach*) walk $n --jump ;;
    t_*) R "tag Cam add le.cpass"; walk $n ;;     # the pass of the colossi (in the game from the bridge); it lapses after 5 s off the rock
    *) walk $n ;;
  esac
done
R "difficulty ${DIFF:-easy}"; R "gamemode survival Cam2"
