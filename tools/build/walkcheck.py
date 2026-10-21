"""Walkability check for a built piece: BFS over standing positions (4-neighbour moves, no jumps: step-up <= 0.5 block,
or +1 onto a stair block entered from its low side). Usage: from walkcheck import reach; reach(b, start, goal_pred, box)"""
import math
PASS = ("air", "ladder", "potted", "candle", "carpet", "torch", "rail", "button", "pressure_plate", "sign", "flower", "short_grass")
def kind(s):
    if s is None: return "air"
    n = s.replace("minecraft:", "")
    if n == "air" or any(n.startswith(p) or p in n.split("[")[0] for p in PASS if p != "air"): return "air"
    if "_slab" in n and "type=bottom" in n: return "lowslab"
    if "_stairs" in n and "half=bottom" in n: return "stair:" + n.split("facing=")[1].split(",")[0].split("]")[0]
    if "fence" in n or "_wall" in n and "sign" not in n: return "tall"
    return "solid"
DIRS = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}
def surfaces(get, x, z, y1, y2):
    out = []
    for y in range(y1, y2 + 1):
        k = kind(get(x, y, z))
        if k in ("air", "tall"): continue
        s = y + (0.5 if k == "lowslab" else 1.0)
        # head room: blocks at floor(s) .. floor(s+1.8) must be passable
        if all(kind(get(x, yy, z)) == "air" for yy in range(math.floor(s) if s != int(s) else int(s), math.floor(s + 1.8) + 1) if yy != y):
            out.append((s, k))
    return out
def reach(get, start, box, y1, y2):
    x1, z1, x2, z2 = box
    seen = {start}; q = [start]
    while q:
        x, z, s = q.pop()
        for (dx, dz), face in DIRS.items():
            nx, nz = x + dx, z + dz
            if not (x1 <= nx <= x2 and z1 <= nz <= z2): continue
            for ns, k in surfaces(get, nx, nz, max(y1, int(s) - 4), min(y2, int(s) + 2)):
                up = ns - s
                ok = up <= 0.5 + 1e-9 or (up <= 1.0 + 1e-9 and k == "stair:" + face)
                if up < -3: ok = False
                if ok and (nx, nz, ns) not in seen: seen.add((nx, nz, ns)); q.append((nx, nz, ns))
    return seen
