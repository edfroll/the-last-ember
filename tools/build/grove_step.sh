#!/usr/bin/env bash
# T-030: the Mushroom Grove of the Advisor onto the world (server STOPPED; a step of tools/build/r1_apply.sh after the castle).
set -euo pipefail
cd "$(dirname "$0")/../.."
GB="-491 -11 -349 131"   # the place (circle r 45 + 16 of seam) + 10 (checked by `places grove`)
tools/terrain.sh scan $GB server/build/r1/grove_pre.bin | grep -v JAVA_TOOL
python3 tools/build/r1_grove.py
python3 tools/gen_zones.py >/dev/null
python3 tools/gen_seer.py >/dev/null      # the fire zones of the staves read zones.txt (the zone grove)
tools/terrain.sh apply server/build/r1/grove_terrain.bin | grep -v JAVA_TOOL
python3 tools/build/validate.py server/build/r1/grove.txt | tail -1
tools/blockwriter.sh apply server/build/r1/grove.txt | grep -v JAVA_TOOL | tail -1
tools/terrain.sh scan $GB server/build/r1/grove_post.bin | grep -v JAVA_TOOL
python3 tools/build/r1_check.py places grove
python3 tools/build/grove_check.py
