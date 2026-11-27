#!/usr/bin/env bash
# T-034: the Grotto of the Jelly onto the world (server STOPPED; a step of tools/build/r1_apply.sh right after the fens: its channel cuts
# the edge of the bowl, so `world_cache.py redo fens` redoes it too (DEPENDS); place name in the world cache: grotto). The box: the
# grotto's search area under the hill north of the bowl + 6, the channel, the water of the bowl it starts from.
set -euo pipefail
cd "$(dirname "$0")/../.."
SB="-500 150 -296 310"
tools/terrain.sh scan $SB server/build/r1/grotto_pre.bin | grep -v JAVA_TOOL
python3 tools/build/r1_grotto.py
python3 tools/gen_zones.py >/dev/null
python3 tools/gen_seer.py >/dev/null      # the fire zones of the staves read zones.txt
python3 tools/gen_loot.py >/dev/null      # the vault r1_grotto (treasury/vaults.txt)
python3 tools/build/validate.py server/build/r1/grotto.txt | tail -1
tools/blockwriter.sh apply server/build/r1/grotto.txt | grep -v JAVA_TOOL | tail -1
tools/terrain.sh scan $SB server/build/r1/grotto_post.bin | grep -v JAVA_TOOL
python3 tools/build/r1_check.py places grotto+fens
python3 tools/build/grotto_check.py
