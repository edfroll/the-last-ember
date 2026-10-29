#!/usr/bin/env bash
# T-003 pipeline on a fresh world: tools/sculpt_test.sh <seed> <spec.json> <profiles.csv>
# generate footprint+seam chunks (forceload) -> stop -> backup -> sculpt apply -> verify. (server left stopped)
set -euo pipefail
cd "$(dirname "$0")/.."
. tools/env.sh
SEED=$1; SPEC=$2; PROF=$3
pkill -f "net.minecraft.client.main.Main" || true; python3 -I tools/rcon.py stop >/dev/null 2>&1 || true; sleep 6; pkill -f server-26.3 || true; sleep 2
rm -rf server/world server/world-pre-sculpt; mkdir -p server/world/datapacks
sedi "s/^level-seed=.*/level-seed=$SEED/" server/server.properties
(nohup tools/server.sh start > server/console.out 2>&1 &)
for i in $(seq 1 90); do grep -q "RCON running" server/console.out && break; sleep 2; done
python3 -I - <<'P'
import importlib.util
spec=importlib.util.spec_from_file_location('rcon','tools/rcon.py');rc=importlib.util.module_from_spec(spec);spec.loader.exec_module(rc)
for cx1,cx2 in [(-77,-62),(-61,-46),(-45,-38)]:
    for cz1,cz2 in [(-25,-10),(-9,6),(7,14)]:
        rc.run(f"execute in minecraft:overworld run forceload add {cx1*16} {cz1*16} {cx2*16+15} {cz2*16+15}")
P
sleep 170
python3 -I tools/rcon.py "forceload remove all" >/dev/null; python3 -I tools/rcon.py "save-all flush" >/dev/null; python3 -I tools/rcon.py stop >/dev/null; sleep 8
cp -R server/world server/world-pre-sculpt
tools/sculpt.sh apply "$SPEC"
tools/sculpt.sh verify "$SPEC" "$PROF"
