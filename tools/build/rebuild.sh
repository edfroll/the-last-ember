#!/usr/bin/env bash
# T-008: rebuild the Refuge in the test world from scratch (world copy before T-008 in /tmp/world-before-t008), restart, rebuild runtime pieces.
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 tools/build/refuge.py && python3 tools/build/validate.py server/build/refuge/refuge.txt
pkill -f "net.minecraft.client.main.Main" || true; tools/server.sh stop >/dev/null 2>&1 || true
for i in $(seq 1 30); do pgrep -f server-26.3.jar >/dev/null || break; sleep 1; done
rm -rf server/world && cp -c -r /tmp/world-before-t008 server/world
tools/sculpt.sh apply server/build/refuge/terrain.json | tail -1
tools/blockwriter.sh apply server/build/refuge/refuge.txt | tail -1
tools/biomepaint.sh | head -1
(tools/server.sh start > server/console.out 2>&1 &)
for i in $(seq 1 60); do grep -q "RCON running" server/console.out 2>/dev/null && break; sleep 2; done
for c in "data remove storage last_ember:bonfires by" "data remove storage last_ember:ash urns" "data remove storage last_ember:ash t" "data remove storage last_ember:ember carrier" "reload" "defaultgamemode survival" "time set 1000" "weather clear" "forceload add -16 -16 15 15"; do tools/server.sh rcon "$c" >/dev/null; done
sleep 5; tools/server.sh rcon "forceload remove all" >/dev/null
for attempt in 1 2 3; do
  (python3 -I tools/client_launch.py > server/client.out 2>&1 &)
  for i in $(seq 1 40); do tools/server.sh rcon list | grep -q Cam && break 2; sleep 3; done
  pkill -f "net.minecraft.client.main.Main" || true; sleep 3
done
tools/server.sh rcon list
