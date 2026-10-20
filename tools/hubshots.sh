#!/usr/bin/env bash
# Hub-hill screenshots for a seed: tools/hubshots.sh <seed> <x> <y> <z> <outDir>   (fresh world with the datapack; looks N, E, S)
set -euo pipefail
cd "$(dirname "$0")/.."
SEED=$1; X=$2; Y=$3; Z=$4; OUT=$5
pkill -f "net.minecraft.client.main.Main" || true; python3 -I tools/rcon.py stop >/dev/null 2>&1 || true; sleep 6; pkill -f server-26.3 || true; sleep 2
rm -rf server/world; mkdir -p server/world/datapacks
sed -i '' "s/^level-seed=.*/level-seed=$SEED/" server/server.properties
(nohup tools/server.sh start > server/console.out 2>&1 &)
for i in $(seq 1 90); do grep -q "RCON running" server/console.out && break; sleep 2; done
python3 -I tools/rcon.py "execute in minecraft:overworld run forceload add $((X-160)) $((Z-160)) $((X+159)) $((Z+159))" >/dev/null
sleep 40
python3 -I tools/client_launch.py >/dev/null; sleep 60
cat > /tmp/hub_$SEED.json <<J
{"time":"noon","weather":"clear","shots":[
 {"name":"seed_${SEED}_hub_north","x":$X,"y":$((Y+4)),"z":$Z,"yaw":180,"pitch":5,"settle":10},
 {"name":"seed_${SEED}_hub_east","x":$X,"y":$((Y+4)),"z":$Z,"yaw":-90,"pitch":5,"settle":4},
 {"name":"seed_${SEED}_hub_south","x":$X,"y":$((Y+4)),"z":$Z,"yaw":0,"pitch":5,"settle":4}]}
J
python3 -I tools/screenshot.py /tmp/hub_$SEED.json --out "$OUT"
