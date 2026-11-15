#!/usr/bin/env bash
# T-022: the R1 frame onto the world (server STOPPED). Needs server/build/r1/nat.bin and base.bin (tools/build/rebuild.sh makes them
# on a fresh world and they are kept: a re-run gives the same result). Writes only the frame's own columns and blocks: the places of
# locations (tools/build/r1_plots.txt) are never touched, so locations built later stay.
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 tools/build/r1.py
python3 tools/gen_bonfires.py >/dev/null && python3 tools/gen_gates.py >/dev/null && python3 tools/gen_zones.py >/dev/null
tools/terrain.sh apply server/build/r1/terrain.bin | grep -v JAVA_TOOL
python3 tools/build/validate.py server/build/r1/r1.txt | tail -1
tools/blockwriter.sh apply server/build/r1/r1.txt | grep -v JAVA_TOOL | tail -1
# T-023: the Circle of the Weepers on its place (only inside it; the statues and the core of the tree are placed by the datapack)
WB="-476 -236 -364 -124"
tools/terrain.sh scan $WB server/build/r1/weepers_pre.bin | grep -v JAVA_TOOL
python3 tools/build/r1_weepers.py && python3 tools/gen_altars.py >/dev/null && python3 tools/gen_zones.py >/dev/null
tools/terrain.sh apply server/build/r1/weepers_terrain.bin | grep -v JAVA_TOOL
python3 tools/build/validate.py server/build/r1/weepers.txt | tail -1
tools/blockwriter.sh apply server/build/r1/weepers.txt | grep -v JAVA_TOOL | tail -1
tools/terrain.sh scan $WB server/build/r1/weepers_post.bin | grep -v JAVA_TOOL
python3 tools/build/r1_check.py places weepers
# T-024: the Enchanted Maze with its terrace (only inside its place; movable cells, exit and guard statues are templates of the datapack)
MB="-236 -516 -64 -344"   # the place with its seam margin + 10 around (checked by `places`)
tools/terrain.sh scan $MB server/build/r1/maze_pre.bin | grep -v JAVA_TOOL
python3 tools/build/r1_maze.py && python3 tools/gen_altars.py >/dev/null && python3 tools/gen_zones.py >/dev/null && python3 tools/gen_biomes.py >/dev/null
tools/terrain.sh apply server/build/r1/maze_terrain.bin | grep -v JAVA_TOOL
python3 tools/build/validate.py server/build/r1/maze.txt | tail -1
tools/blockwriter.sh apply server/build/r1/maze.txt | grep -v JAVA_TOOL | tail -1
tools/terrain.sh scan $MB server/build/r1/maze_post.bin | grep -v JAVA_TOOL
python3 tools/build/r1_check.py places maze
tools/biomepaint.sh | grep -v JAVA_TOOL | head -1
tools/borders.sh apply | grep -v JAVA_TOOL | tail -3
tools/server.sh sync
