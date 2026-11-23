#!/usr/bin/env bash
# T-032: the Spider Thicket onto the world (server STOPPED; a step of tools/build/r1_apply.sh after Heather; place name in the world
# cache: spiders).
set -euo pipefail
cd "$(dirname "$0")/../.."
SB="84 -366 216 -234"   # the place + its seam (16) + 10 (checked by `places spiders`)
tools/terrain.sh scan $SB server/build/r1/spiders_pre.bin | grep -v JAVA_TOOL
python3 tools/build/r1_spiders.py
python3 tools/gen_zones.py >/dev/null
python3 tools/gen_seer.py >/dev/null      # the fire zones of the staves read zones.txt
tools/terrain.sh apply server/build/r1/spiders_terrain.bin | grep -v JAVA_TOOL
python3 tools/build/validate.py server/build/r1/spiders.txt | tail -1
tools/blockwriter.sh apply server/build/r1/spiders.txt | grep -v JAVA_TOOL | tail -1
tools/terrain.sh scan $SB server/build/r1/spiders_post.bin | grep -v JAVA_TOOL
python3 tools/build/r1_check.py places spiders
python3 tools/build/spiders_check.py
