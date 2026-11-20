#!/usr/bin/env python3
"""T-027 (review): the falls of the lodge stream in the running world. A player is put on the yard (the cemetery loop runs only with
someone near), the datapack starts the flow; then every water block in a box round the stream is read over RCON:
  python3 tools/build/lodge_stream_check.py      -> the flowing water cells; FAIL when one is outside the stream channel (x 111..112,
                                                    z 427..441), on the footbridge, the road, the curb or the yard; the falls present
Needs the server with the world after tools/build/rebuild.sh and the player Cam online."""
import json, os, socket, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools")); import rcon as RC
M = json.load(open(os.path.join(ROOT, "server/build/r1/cemetery.json")))
p = RC.props(); s = socket.create_connection(("127.0.0.1", int(p.get("rcon.port", 25575))), timeout=30)
RC.pkt(s, 1, 3, p["rcon.password"]); RC.read(s)
def R(c): return RC.exchange(s, c)
def isb(x, y, z, b): return "passed" in R(f"execute if block {x} {y} {z} {b}")
R("tp Cam 105.5 197 433.5"); time.sleep(6)                      # the yard; >= 1 s for the loop, then the flow settles
falls = M["lodge"]["falls"]
bad, flow, src = [], [], 0
for x in range(108, 119):
    for z in range(424, 447):
        for y in range(186, 201):
            if not isb(x, y, z, "minecraft:water"): continue
            if isb(x, y, z, "minecraft:water[level=0]"): src += 1; continue
            flow.append((x, y, z))
            if not (111 <= x <= 112 and 427 <= z <= 441): bad.append((x, y, z))
ok_falls = all(isb(*f[1], "minecraft:water") and not isb(*f[1], "minecraft:water[level=0]") for f in falls)
print("source blocks %d, flowing %d: %s" % (src, len(flow), flow))
print("falls over the %d lips: %s" % (len(falls), "all there" if ok_falls else "MISSING"))
print("flowing water outside the channel: %s" % (bad or "none"))
print("OK" if ok_falls and not bad else "FAIL"); sys.exit(0 if ok_falls and not bad else 1)
