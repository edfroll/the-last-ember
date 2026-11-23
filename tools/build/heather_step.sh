#!/usr/bin/env bash
# T-031: the Village of Heather and the Dragon Ridge onto the world (server STOPPED; a step of tools/build/r1_apply.sh after the grove;
# both places in one step, like cemetery+lodge; place name in the world cache: heather).
set -euo pipefail
cd "$(dirname "$0")/../.."
HB="-36 -606 176 -399"   # both places + their seams (16) + 10 (checked by `places heather+dragon_ridge`)
tools/terrain.sh scan $HB server/build/r1/heather_pre.bin | grep -v JAVA_TOOL
python3 tools/build/r1_heather.py
python3 tools/gen_zones.py >/dev/null
python3 tools/gen_seer.py >/dev/null      # the fire zones of the staves read zones.txt
tools/terrain.sh apply server/build/r1/heather_terrain.bin | grep -v JAVA_TOOL
python3 tools/build/validate.py server/build/r1/heather.txt | tail -1
tools/blockwriter.sh apply server/build/r1/heather.txt | grep -v JAVA_TOOL | tail -1
tools/terrain.sh scan $HB server/build/r1/heather_post.bin | grep -v JAVA_TOOL
python3 tools/build/r1_check.py places heather+dragon_ridge
python3 tools/build/heather_check.py
