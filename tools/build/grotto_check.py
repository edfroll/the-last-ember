#!/usr/bin/env python3
"""T-034: checks of the built Grotto of the Jelly (after tools/build/grotto_step.sh; the region files are read, the server stopped):
  - the cover of HQ T-034, 3: >= 8 solid over the roof of every column of the grotto, >= 6 to the first air on every side at every level
    of its air (the tunnel excepted);
  - water: no flowing water in the box of the grotto and the channel (every water block a source or waterlogged);
  - light: no block light but the glow lichen on the roof (light 7 at most: monsters may spawn);
  - one chest on the ledge with its lock (a slime block) over it;
  - no jumps both ways (tools/build/walkcheck.py rules, water as air): from the water at the foot of the stepping stones up to the chest;
  - a boat from the hut's pier to the stones and back (tools/build/fens_boat.py grotto).
Exit 1 on a failure."""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worldblocks
from walkcheck import surfaces, DIRS
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
M = json.load(open(os.path.join(ROOT, "server/build/r1/grotto.json")))
ok = True
def fail(msg):
    global ok; ok = False; print("FAIL", msg)
W = M["W"]; x1, z1, x2, z2 = M["rect"]
cx = [c[0] for c in M["chan"]]; cz = [c[1] for c in M["chan"]]
WB = worldblocks.World(min(x1, min(cx)) - 10, min(z1, min(cz)) - 10, max(x2, max(cx)) + 10, max(z2, max(cz)) + 10, W - 10, W + 50)
AIRY = re.compile(r"minecraft:(air|cave_air|water|lava|snow|short_grass|tall_grass|fern|hanging_roots|vine|glow_lichen|pointed_dripstone)$")
def airy(s): return s is None or bool(AIRY.match(s.split("[")[0]))
def get(x, y, z):
    s = WB.get(x, y, z)
    if s and (s.startswith("minecraft:water") or s.startswith("minecraft:glow_lichen") or s.startswith("minecraft:hanging_roots")): return "minecraft:air"
    return s
ceil = {tuple(int(v) for v in k.split(",")): c for k, c in M["ceil"].items()}
tunnel = set()
for (x, z, o) in M["chan"]:
    if not o:
        for a in range(-1, 2):
            for c in range(-1, 2): tunnel.add((x + a, z + c))
wu = 99; ws = 99; where = None
for (x, z), c in ceil.items():
    n = 0; y = c + 1
    while not airy(WB.get(x, y, z)) and n < 40: n += 1; y += 1
    if n < wu: wu = n; where = (x, z)
if wu < 8: fail("rock over the roof: %d at %s" % (wu, where))
for (x, z), c in ceil.items():
    for (dx, dz) in DIRS:
        if (x + dx, z + dz) in ceil: continue
        for y in range(W, c + 1):
            n = 0
            while n < 12:
                q = (x + dx * (n + 1), z + dz * (n + 1))
                if q in tunnel or q in ceil or airy(WB.get(q[0], y, q[1])): break
                n += 1
            q = (x + dx * (n + 1), z + dz * (n + 1))
            if q in tunnel or q in ceil: continue
            if n < ws: ws = n; where = (x, y, z, dx, dz)
if ws < 6: fail("rock to the side: %d at %s" % (ws, where))
print("grotto check: rock over the roof >= %d, to the sides >= %d" % (wu, ws))
flow = []; lit = []; chests = 0; slimes_floor = 0
bx1, bz1, bx2, bz2 = min(x1, min(cx)) - 2, min(z1, min(cz)) - 2, max(x2, max(cx)) + 2, max(z2, max(cz)) + 2
for x in range(bx1, bx2 + 1):
    for z in range(bz1, bz2 + 1):
        for y in range(W - 3, W + 12):
            s = WB.get(x, y, z) or ""
            if s.startswith("minecraft:water") and "level=0" not in s: flow.append((x, y, z, s))
            if re.search(r"torch|lantern|glowstone|shroomlight|froglight|lava|sea_lantern|lit=true|magma|redstone_lamp", s): lit.append((x, y, z, s))
            if s.startswith("minecraft:chest") and x1 <= x <= x2 and z1 <= z <= z2: chests += 1
if flow: fail("flowing water: %d, e.g. %s" % (len(flow), flow[:3]))
if lit: fail("light other than the lichen: %s" % lit[:3])
chx, chy, chz = M["chest"]
if chests != 1 or WB.get(chx, chy + 1, chz) != "minecraft:slime_block": fail("chests %d, over it %s" % (chests, WB.get(chx, chy + 1, chz)))
print("grotto check: flowing water 0: %s; light only the lichen: %s; chest %d, lock %s" % (not flow, not lit, chests, WB.get(chx, chy + 1, chz)))
OPP = {"east": "west", "west": "east", "north": "south", "south": "north"}
fx, fy, fz = M["water_foot"]; start = None
for s, k in surfaces(get, int(fx // 1), int(fz // 1), W - 2, W + 1): start = (int(fx // 1), int(fz // 1), s); break
seen = {start: "solid"}; q = [start]
while q:
    x, z, s = q.pop()
    for (dx, dz), face in DIRS.items():
        nx, nz = x + dx, z + dz
        if not (x1 - 1 <= nx <= x2 + 1 and z1 - 1 <= nz <= z2 + 1): continue
        for ns, k in surfaces(get, nx, nz, int(s) - 3, int(s) + 2):
            up = ns - s
            fwd = up <= 0.5 + 1e-9 or (up <= 1.0 + 1e-9 and k == "stair:" + face)
            back = -up <= 0.5 + 1e-9 or (-up <= 1.0 + 1e-9 and seen[(x, z, s)] == "stair:" + OPP[face])
            if fwd and back and (nx, nz, ns) not in seen: seen[(nx, nz, ns)] = k; q.append((nx, nz, ns))
face = {"south": (0, 1), "north": (0, -1), "east": (1, 0), "west": (-1, 0)}[M["chest_facing"]]
front = (chx + face[0], chz + face[1])
got = [k for k in seen if (k[0], k[1]) == front and abs(k[2] - (W + 2)) < 0.01]
print("grotto check: walk (no jumps, both ways) the water at the stones %s -> the front of the chest %s: %s" % (start, front, "OK" if got else "NO"))
if not got: fail("no way without jumps from the water to the chest")
r = subprocess.run([sys.executable, os.path.join(ROOT, "tools/build/fens_boat.py"), "grotto"], capture_output=True, text=True)
print(r.stdout.strip())
if r.returncode: fail("no way for a boat")
print("grotto check: %s" % ("OK" if ok else "FAIL"))
sys.exit(0 if ok else 1)
