#!/usr/bin/env bash
# T-034: the Ogre's Den onto the world (server STOPPED; the last place step of tools/build/r1_apply.sh, after the mines; place name in the
# world cache: ogre). The box: the place + seam + 10, the cave + 6 under the hill north of it, the chain of bones to the trail refuge ->
# bonfire 2 (its skulls and ribs outside the place are excused by `places`: ogre_deco.json).
set -euo pipefail
cd "$(dirname "$0")/../.."
SB="55 112 300 282"
tools/terrain.sh scan $SB server/build/r1/ogre_pre.bin | grep -v JAVA_TOOL
python3 tools/build/r1_ogre.py
python3 tools/gen_zones.py >/dev/null
python3 tools/gen_seer.py >/dev/null      # the fire zones of the staves read zones.txt
python3 tools/gen_loot.py >/dev/null      # the vault r1_ogre (treasury/vaults.txt)
python3 tools/build/validate.py server/build/r1/ogre.txt | tail -1
tools/blockwriter.sh apply server/build/r1/ogre.txt | grep -v JAVA_TOOL | tail -1
tools/terrain.sh scan $SB server/build/r1/ogre_post.bin | grep -v JAVA_TOOL
python3 tools/build/r1_check.py places ogre+ogre_den
python3 tools/build/ogre_check.py
