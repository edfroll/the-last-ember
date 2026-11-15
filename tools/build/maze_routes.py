#!/usr/bin/env python3
"""T-024: walk-bot routes of the Enchanted Maze -> server/build/walk/m_*.json (tools/walkbot.py, no jumps):
  m_in_1, m_in_2, m_in_3   bonfire 3 -> the gate -> the shortest way through the maze -> the court of the sanctum, with all the movable
                           cells in variant 1 / 2 / 3 (set them first: function last_ember:maze/set {cell:k,var:v} for k 1..6)
  m_exit                   the sanctum -> the secret exit (open: after the key) -> along the band on the terrace west of the outer wall
                           -> the band south of it -> bonfire 3
The ways are shortest paths on the block grid of the plan (r1_maze.walk_grid), reduced to their turns."""
import json, os, sys
from collections import deque
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools/build"))
import r1_maze as RM
OUT = os.path.join(ROOT, "server/build/walk"); os.makedirs(OUT, exist_ok=True)
Y = RM.G + 1
def bfs(W, a, b):
    prev = {a: None}; dq = deque([a])
    while dq:
        p = dq.popleft()
        if p == b: break
        for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (p[0] + dz, p[1] + dx)
            if 0 <= q[0] < W.shape[0] and 0 <= q[1] < W.shape[1] and W[q] and q not in prev: prev[q] = p; dq.append(q)
    if b not in prev: raise SystemExit("no way %s -> %s" % (a, b))
    out = [b]
    while prev[out[-1]] is not None: out.append(prev[out[-1]])
    return out[::-1]
def turns(cells):
    """(z, x) grid cells -> world points at the turns (block centres)"""
    pts = [cells[0]]
    for i in range(1, len(cells) - 1):
        d1 = (cells[i][0] - cells[i - 1][0], cells[i][1] - cells[i - 1][1]); d2 = (cells[i + 1][0] - cells[i][0], cells[i + 1][1] - cells[i][1])
        if d1 != d2: pts.append(cells[i])
    pts.append(cells[-1])
    return [[RM.OX1 + x + 0.5, RM.OZ1 + z + 0.5, Y] for z, x in pts]
def save(name, start, pts):
    json.dump({"start": start, "points": pts}, open(os.path.join(OUT, name + ".json"), "w")); print(name, len(pts), "points")
cells = RM.plan()
GATE = (RM.OZ2 - RM.OZ1, -150 - RM.OX1)                      # the gate cell of the outer ring
COURT = (RM.CZ - 7 - RM.OZ1, RM.CX - RM.OX1)                 # the court of the sanctum north of the fountain, and south of it
COURT_S = (RM.CZ + 7 - RM.OZ1, RM.CX - RM.OX1)
APPROACH = [[-149.5, -360.5, Y], [-149.5, -366.5, Y]]        # the pad of bonfire 3 -> in front of the gate
for v in (1, 2, 3):
    W = RM.walk_grid(cells, {c: v - 1 for c in RM.MOVABLE})
    save("m_in_%d" % v, [-149.5, Y + 0.2, -358.5], APPROACH + turns(bfs(W, GATE, COURT_S)))
# the exit: from the court north of the fountain straight north through the exit lane, then the terrace band west and south
W = RM.walk_grid(cells, {c: 0 for c in RM.MOVABLE}, exit_open=True)
inside = turns(bfs(W, COURT, (0, RM.EXIT_X[0] + 1 - RM.OX1)))
xo = RM.EXIT_X[0] + 1.5
import math
def mid(a, b): return math.floor((a + b) / 2.0) + 0.5           # the middle of a band (terrace edge .. outer wall), a block centre
band_w = mid(RM.TX1, RM.OX1); band_n = mid(RM.TZ1, RM.OZ1); band_s = mid(RM.TZ2, RM.OZ2)
out = [[xo, band_n, Y], [band_w, band_n, Y], [band_w, band_s, Y], [-157.5, band_s, Y], [-149.5, -360.5, Y]]
save("m_exit", [RM.CX + 0.5, Y + 0.2, RM.CZ - 6.5], inside + out)
