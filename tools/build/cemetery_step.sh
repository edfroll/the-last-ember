#!/usr/bin/env bash
# T-027: the Cemetery of the Fallen Knights and the Keeper's Lodge onto the world (server STOPPED; a step of tools/build/r1_apply.sh).
set -euo pipefail
cd "$(dirname "$0")/../.."
CB="58 348 302 552"     # both places with their seam + 10 (checked by `places cemetery+lodge`)
tools/terrain.sh scan $CB server/build/r1/cemetery_pre.bin | grep -v JAVA_TOOL
python3 tools/build/r1_cemetery.py && python3 tools/gen_zones.py >/dev/null && python3 tools/gen_traps.py >/dev/null
tools/terrain.sh apply server/build/r1/cemetery_terrain.bin | grep -v JAVA_TOOL
python3 tools/build/validate.py server/build/r1/cemetery.txt | tail -1
tools/blockwriter.sh apply server/build/r1/cemetery.txt | grep -v JAVA_TOOL | tail -1
tools/terrain.sh scan $CB server/build/r1/cemetery_post.bin | grep -v JAVA_TOOL
python3 tools/build/r1_check.py places cemetery+lodge
