#!/usr/bin/env bash
# The test world from scratch (T-008 Refuge + T-022 frame of the Vale), no manual steps:
#   fresh world (seed 10845, the datapack is in place before the world is created) -> chunks of the hub, the Vale with its borders,
#   the Ring Mountain and the Wall map (forceload) -> natural ground scan -> Refuge (T-008) -> Ring Mountain (T-003 tool)
#   -> R1 frame (tools/build/r1.py: border relief, the Wall, the rift and the bridge, the gorge, bonfire pads, trails, forests)
#   -> biomes -> barriers on the border axes -> start + dev client Cam.
# Usage: tools/build/rebuild.sh [--no-client] [--cache | --start-only]      (Linux cloud or Mac; ~17 min from scratch)
#   --cache       take the generated chunks from the world cache (tools/world_cache.py, branch world-cache) when its key matches (~12 min)
#   --start-only  only the first start + client, after `tools/world_cache.py restore final` or `redo` (the world is already built)
# Snapshots for the cache are written on the way (server/cache/gen.tar.gz, final.tar.gz); upload with tools/world_cache.py push.
# Re-run of the R1 step over an existing world (locations built later are kept): tools/build/r1_apply.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
T0=$(date +%s); say() { echo "[$(( $(date +%s) - T0 ))s] $*"; }
CLIENT=1; MODE=scratch
for a in "$@"; do case "$a" in --no-client) CLIENT=0 ;; --cache) MODE=cache ;; --start-only) MODE=start ;; *) echo "unknown option $a"; exit 1 ;; esac; done
pkill -f "net.minecraft.client.main.Main" || true; tools/server.sh stop >/dev/null 2>&1 || true
for i in $(seq 1 30); do pgrep -f server-26.3.jar >/dev/null || break; sleep 1; done
[ $MODE = start ] || { rm -rf server/world server/build/r1/nat.bin server/build/r1/base.bin; mkdir -p server/build/r1 server/build/refuge; }
grep -q '^level-seed=10845' server/server.properties || { echo "server.properties: level-seed must be 10845"; exit 1; }
start_server() {
  (tools/server.sh start > server/console.out 2>&1 &)
  for i in $(seq 1 90); do grep -q "RCON running" server/console.out 2>/dev/null && return 0; sleep 2; done; echo "server did not start"; exit 1
}
stop_server() { tools/server.sh stop >/dev/null; for i in $(seq 1 60); do pgrep -f server-26.3.jar >/dev/null || return 0; sleep 1; done; }
if [ $MODE = cache ] && [ "$(python3 tools/world_cache.py key)" = "$(python3 -c 'import json;print(json.load(open("server/cache/manifest.json"))["gen"]["key"])' 2>/dev/null)" ]; then
  say "generated chunks from the cache"; mkdir -p server/world; python3 tools/world_cache.py restore gen
elif [ $MODE != start ]; then
[ $MODE = cache ] && say "the cache has no generated chunks for these inputs: generating"
say "generating chunks"; start_server
# frozen while the chunks are generated (review T-025, 6): no datapack functions (it would build bonfires, gates, traders at the
# positions of the previous build into the "natural" ground the scans read), no flowing water, no freezing, no falling blocks
tools/server.sh rcon "tick freeze" >/dev/null
python3 tools/build/pregen.py -736 -1024 751 751  -1232 -400 -737 239  -1504 -1024 -737 -592 | tail -1
stop_server
say "natural ground"; tools/terrain.sh scan -1504 -1024 751 751 server/build/r1/nat.bin | grep -v JAVA_TOOL
python3 tools/world_cache.py save gen
fi
if [ $MODE != start ]; then
say "Refuge (T-008)"
tools/blockwriter.sh heights -210 -210 210 210 server/build/refuge/heights.txt | grep -v JAVA_TOOL
python3 tools/build/refuge.py && python3 tools/build/validate.py server/build/refuge/refuge.txt
tools/sculpt.sh apply server/build/refuge/terrain.json | grep -v JAVA_TOOL | tail -1
tools/blockwriter.sh apply server/build/refuge/refuge.txt | grep -v JAVA_TOOL | tail -1
say "Ring Mountain (T-003)"; tools/sculpt.sh apply tools/sculpt_specs/ring_mountain.json | grep -v JAVA_TOOL | tail -1
tools/terrain.sh scan -1504 -1024 751 751 server/build/r1/base.bin | grep -v JAVA_TOOL
say "R1 frame (T-022)"; rm -rf server/cache/snap; LE_SNAPDIR="$PWD/server/cache/snap" tools/build/r1_apply.sh
python3 tools/world_cache.py save final
fi
say "start"; start_server
for c in "tick unfreeze" "data remove storage last_ember:bonfires by" "data remove storage last_ember:ash urns" "data remove storage last_ember:ash t" "data remove storage last_ember:ember carrier" "reload" "defaultgamemode survival" "time set 1000" "weather clear" "forceload add -16 -16 15 15"; do tools/server.sh rcon "$c" >/dev/null; done
sleep 5; tools/server.sh rcon "forceload remove all" >/dev/null
say "world ready"
[ $CLIENT = 0 ] && exit 0
for attempt in 1 2 3; do
  (python3 -I tools/client_launch.py > server/client.out 2>&1 &)
  for i in $(seq 1 40); do tools/server.sh rcon list | grep -q Cam && break 2; sleep 3; done
  pkill -f "net.minecraft.client.main.Main" || true; sleep 3
done
tools/server.sh rcon list; say "done"
