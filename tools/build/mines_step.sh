#!/usr/bin/env bash
# T-033: the Iron Ore Mines onto the world (server STOPPED; a step of tools/build/r1_apply.sh after the Spider Thicket; place name in the
# world cache: mines).
set -euo pipefail
cd "$(dirname "$0")/../.."
SB="224 -111 336 -9"   # the place + its seam (16) + 10 (checked by `places mines`)
tools/terrain.sh scan $SB server/build/r1/mines_pre.bin | grep -v JAVA_TOOL
python3 tools/build/r1_mines.py
python3 tools/gen_zones.py >/dev/null
python3 tools/gen_loot.py >/dev/null
python3 tools/gen_traders.py >/dev/null
tools/terrain.sh apply server/build/r1/mines_terrain.bin | grep -v JAVA_TOOL
python3 tools/build/validate.py server/build/r1/mines.txt | tail -1
tools/blockwriter.sh apply server/build/r1/mines.txt | grep -v JAVA_TOOL | tail -1
tools/terrain.sh scan $SB server/build/r1/mines_post.bin | grep -v JAVA_TOOL
python3 tools/build/r1_check.py places mines
python3 tools/build/mines_check.py
