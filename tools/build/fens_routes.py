#!/usr/bin/env python3
"""T-026: walk-bot routes of the Crooked Fens -> server/build/walk/f_*.json (tools/walkbot.py), from server/build/r1/fens.json:
  f_climb   the pad of bonfire 5 -> the graded climb (half blocks) -> the outer pier (no jumps)
  f_board   the outer pier -> the boardwalk (over the tussocks of 4 gaps, round the dark gap by the piles beside it) -> the stairs of the
            hut's porch -> the hall (with jumps: tools/walkbot.py --jump)
  f_back    the hall -> the boardwalk -> the outer pier -> down the climb -> the pad of bonfire 5 (with jumps)
The points are the centres of the cells of the ways the generator laid (the climb's cells with their feet levels, the boardwalk's line),
reduced to the turns (a straight run is one point)."""
import json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B = os.path.join(ROOT, "server/build/r1"); OUT = os.path.join(ROOT, "server/build/walk"); os.makedirs(OUT, exist_ok=True)
M = json.load(open(os.path.join(B, "fens.json")))
W = M["W"]; FL = M["floor"]
def simplify(pts):
    """keep the first, the last and every point where the direction or the level changes"""
    if len(pts) <= 2: return pts
    out = [pts[0]]
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        d1 = (b[0] - a[0], b[1] - a[1]); d2 = (c[0] - b[0], c[1] - b[1])
        if d1 != d2 or abs(b[2] - a[2]) > 0.01 and abs(c[2] - b[2]) > 0.01 and False: out.append(b)
    out.append(pts[-1]); return out
# the climb: cells with the feet level (s2 / 2)
climb = [[c[0] + 0.5, c[1] + 0.5, s2 / 2.0] for c, s2 in zip(M["cpath"], M["cprof"])]
hx, hy, hz = M["hearth"]
cp_ = M["climb_pad"]; pad = [cp_[0] + 0.5, cp_[1] + 0.5, hy * 1.0]       # the cell of the pad next to the first cell of the climb
pier_end = [M["pier_out"][0] - 0.5 + 0.5, M["pier_out"][2] + 0.5, W + 2.0]
# the boardwalk: the line of the way (the first cell of each 2-wide row), feet W+2; the gaps: over the tussock (the middle row of the
# gap), the dark gap: by the two piles beside it
deck = M["deck"]; gaps = {g["k"]: g for g in M["gaps"]}
board = []; skip = set()
for k, (a, b) in enumerate(deck):
    if k in skip: continue
    g = gaps.get(k + 2)
    if g and g["dark"]:                  # deck k -> the row of piles beside the gap (one jump over its middle) -> the deck after the gap
        p0, p1, p2, p3 = M["dark_posts"]; e = deck[k + 4][0]
        board += [[a[0] + 0.5, a[1] + 0.5, W + 2.0], [p0[0] + 0.5, p0[2] + 0.5, p0[1] + 1.0], [p1[0] + 0.5, p1[2] + 0.5, p1[1] + 1.0],
                  [p2[0] + 0.5, p2[2] + 0.5, p2[1] + 1.0, 1], [p3[0] + 0.5, p3[2] + 0.5, p3[1] + 1.0], [e[0] + 0.5, e[1] + 0.5, W + 2.0]]
        skip.update({k + 1, k + 2, k + 3, k + 4}); continue
    if g:                                # deck k -> jump onto the tussock (the gap's middle row) -> jump onto the deck after the gap
        t = deck[k + 2][0]; n = deck[k + 4][0]
        board += [[a[0] + 0.5, a[1] + 0.5, W + 2.0], [t[0] + 0.5, t[1] + 0.5, W + 2.0, 1], [n[0] + 0.5, n[1] + 0.5, W + 2.0, 1]]
        skip.update({k + 1, k + 2, k + 3, k + 4}); continue
    board.append([a[0] + 0.5, a[1] + 0.5, W + 2.0])
board = [b for b in board]
porch = M["hut"]["porch"]          # the boardwalk's end at the stairs (x, W+1, z): stairs up west to the platform, then into the hall
px = porch[0]                      # the lowest stair (W+2), then W+3, then the stair at the platform's edge (FL), the platform, the hall door (x -384)
hut_in = [[px + 1.5, porch[2] + 0.5, W + 2.0], [px + 0.5, porch[2] + 0.5, W + 3.0], [px - 0.5, porch[2] + 0.5, W + 4.0],
          [px - 1.5, porch[2] + 0.5, FL + 1.0], [px - 5.5, porch[2] + 0.5, FL + 1.0], [-385.5, porch[2] + 0.5, FL + 1.0], [-387.5, porch[2] + 0.5, FL + 1.0]]
cl = simplify(climb)
def back(pts):
    """the way back: the jump marks move to the point after each gap seen from the other side"""
    r = [p[:3] for p in pts[::-1]]
    for i, p in enumerate(pts):
        if len(p) > 3: r[len(pts) - i] = r[len(pts) - i] + [1] if len(pts) - i < len(r) else r[-1]
    return r
routes = {
    "f_climb": dict(start=[pad[0], pad[2], pad[1]], points=[[p[0], p[1], p[2]] for p in [[pad[0], pad[1], pad[2]]] + cl] + [[pier_end[0], pier_end[1], pier_end[2]]]),
    "f_board": dict(start=[pier_end[0], pier_end[2], pier_end[1]], points=board + hut_in),
    "f_back": dict(start=[hut_in[-1][0], hut_in[-1][2], hut_in[-1][1]], points=hut_in[::-1][1:] + back(board) + [pier_end] + cl[::-1] + [[pad[0], pad[1], pad[2]]]),
}
for n, r in routes.items():
    json.dump(r, open(os.path.join(OUT, n + ".json"), "w"))
    L = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(r["points"], r["points"][1:]))
    print(f"{n}: {len(r['points'])} points, {L:.0f} blocks")
