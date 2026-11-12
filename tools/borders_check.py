#!/usr/bin/env python3
"""T-021: no way through a border axis except its gaps (server STOPPED, after tools/borders.sh apply).

  python3 tools/borders_check.py holes [id...]
      every column of each axis (outside the gaps) must be closed from y -64 to 319 (full collision blocks + barrier);
      prints the passable cells left; exit 1 if any. Missing chunks are listed (not generated yet: apply again later).
  python3 tools/borders_check.py walk x1 z1 x2 z2 x,z x,z [x,z ...]
      flood fill over the columns of the area (4-neighbours; a column closed from -64 to 319 is a wall): each listed seed point
      must reach none of the others when the gaps of the borders are walled up, and the result with the gaps open is printed too.
      Used for the joints of two borders (a T: three regions)."""
import json, os, subprocess, sys
from collections import deque
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BS = os.path.join(ROOT, "tools/borders.sh")
TMP = os.path.join(ROOT, "server/build/borders"); os.makedirs(TMP, exist_ok=True)

def holes(ids):
    out = os.path.join(TMP, "holes.txt")
    subprocess.run([BS, "holes", out] + ids, check=True, capture_output=True)
    bad = 0
    for line in open(out):
        f = line.split()
        if f[0] == "missing": print("  missing chunk", f[1]); continue
        n = int(f[1]); bad += n
        print("  %-14s %s" % (f[0], "closed" if n == 0 else "%d passable columns:%s" % (n, " ".join(f[2:12]))))
    return bad

def walk(x1, z1, x2, z2, seeds):
    out = os.path.join(TMP, "wallmap.txt")
    subprocess.run([BS, "wallmap", str(x1), str(z1), str(x2), str(z2), out], check=True, capture_output=True)
    rows = open(out).read().split("\n")[1:]
    W = {(x1 + i, z1 + j): c == "1" for j, r in enumerate(rows) for i, c in enumerate(r)}
    borders = json.load(open(os.path.join(ROOT, "gates/borders.gen.json")))["borders"]
    gap = set()
    for b in borders:
        for g0, g1 in b["gaps"]:
            for t in range(g0, g1 + 1): gap.add((b["a"], t) if b["axis"] == "x" else (t, b["a"]))
    def fill(sx, sz, block_gaps):
        seen = {(sx, sz)}; q = deque([(sx, sz)])
        while q:
            x, z = q.popleft()
            for nx, nz in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if (nx, nz) in seen or (nx, nz) not in W or W[(nx, nz)] or (block_gaps and (nx, nz) in gap): continue
                seen.add((nx, nz)); q.append((nx, nz))
        return seen
    bad = 0
    for block in (True, False):
        print("  gaps %s:" % ("walled up" if block else "open"))
        for i, s in enumerate(seeds):
            reach = fill(*s, block)
            others = [t for j, t in enumerate(seeds) if j != i and t in reach]
            print("    from %s reaches %s" % (s, others or "none of the others"))
            if block and others: bad += 1
    return bad

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    if a[0] == "holes": sys.exit(1 if holes(a[1:]) else 0)
    if a[0] == "walk":
        x1, z1, x2, z2 = map(int, a[1:5]); seeds = [tuple(map(int, s.split(","))) for s in a[5:]]
        sys.exit(1 if walk(x1, z1, x2, z2, seeds) else 0)
