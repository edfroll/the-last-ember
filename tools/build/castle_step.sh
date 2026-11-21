#!/usr/bin/env bash
# T-028: the approaches to the Enchanted Castle onto the world (server STOPPED; a step of tools/build/r1_apply.sh after the cemetery).
set -euo pipefail
cd "$(dirname "$0")/../.."
KB="324 -126 576 126"   # the place with its seam + 10 (checked by `places castle`)
tools/terrain.sh scan $KB server/build/r1/castle_pre.bin | grep -v JAVA_TOOL
python3 tools/build/r1_castle.py
python3 tools/gen_bonfires.py >/dev/null      # T-029: bonfire 11, the trap of the gaol, the Signet's source (castle_keep_dp wrote their lines)
python3 tools/gen_regions.py >/dev/null
python3 tools/gen_traps.py >/dev/null
python3 tools/gen_altars.py >/dev/null
python3 tools/gen_zones.py >/dev/null
python3 tools/gen_biomes.py >/dev/null
tools/terrain.sh apply server/build/r1/castle_terrain.bin | grep -v JAVA_TOOL
python3 tools/build/validate.py server/build/r1/castle.txt | tail -1
tools/blockwriter.sh apply server/build/r1/castle.txt | grep -v JAVA_TOOL | tail -1
tools/terrain.sh scan $KB server/build/r1/castle_post.bin | grep -v JAVA_TOOL
python3 tools/build/r1_check.py places castle
python3 tools/build/castle_check.py
