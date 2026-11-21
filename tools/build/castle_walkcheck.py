"""T-029: tools/build/walkcheck.reach with one more rule for the castle's stairwells and holes: a step down (or up) also needs the air
of the target column from the lower surface up to 1.8 over the higher one (walkcheck.reach lets a walker drop through a floor or a wall
into a stairwell under it)."""
import math
from walkcheck import DIRS, surfaces, kind


def clear(get, x, z, lo, hi):
    return all(kind(get(x, y, z)) == "air" for y in range(math.floor(lo), math.floor(hi + 1.8) + 1) if not (y == math.floor(lo) and lo != int(lo)))


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
                if ok and up < 0 and not clear(get, nx, nz, ns, s): ok = False
                if ok and up > 0 and not clear(get, x, z, s, ns): ok = False
                if ok and (nx, nz, ns) not in seen: seen.add((nx, nz, ns)); q.append((nx, nz, ns))
    return seen
