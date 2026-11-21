#!/usr/bin/env python3
"""T-028 checks of the built approaches on the scan after the build (server/build/r1/castle_post.bin, tools/build/castle_step.sh):
  edge    the sheer edge of the rock: every rock cell next to a cell outside the rock is >= 6 over its ground / water (the pier and the
          mouth of the stair excepted)
  knock   the knock zone 16 x 14: water >= 4 deep on every cell, the floor as planned (no stones, no piles)
  lake    the lake holds: every water column of the lake is at W, its neighbours are water or ground >= W; no other standing water above
          the lake in the place
  bfs     a walk with jumps (up 1 block, gaps of 2..4 at the same height or lower; swimming on the water surface; falls of any height)
          from the gorge, the plateau at bonfire 7, the north and east lowlands and the south ridge: with the stair walled up no cell of
          the rock is reached (the stair cells, the pier and the rest platform are walls: the tunnels are not in a height map)
Usage: python3 tools/build/castle_check.py [edge knock lake bfs]"""
import os, sys
from collections import deque
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, NONE
import castle_plan as P

def main(what):
    gr = P.grids(); rl = P.relief(gr); S = Scan(os.path.join(P.OUT, "castle_post.bin"))
    def sg(a): return a[gr["z1"] - S.z0:gr["z1"] - S.z0 + gr["X"].shape[0], gr["x1"] - S.x0:gr["x1"] - S.x0 + gr["X"].shape[1]].astype(np.int32)
    G, Wa, TOP = sg(S.ground), sg(S.water), sg(S.top)
    X, Z = gr["X"], gr["Z"]; rock = rl["rock"]; ok = True
    exc = P.rect((P.PIER[0] - 1, P.PIER[1] - 1, P.FACE_X + 15, P.PIER[3] + 1), X, Z)    # the pier and the stair's mouth
    exc |= P.rect((P.BRIDGE_X[0] - 1, P.RIFT[1] - 3, P.BRIDGE_X[1] + 1, P.RIFT[3] + 3), X, Z)   # the bridge (rock to rock over the rift)
    H = np.where((Wa != NONE) & (Wa > G), Wa, G)
    if "edge" in what:
        low = []; n = 0; worst = 999
        for i, j in zip(*np.nonzero(rock & ~exc)):
            for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p, r = i + a, j + c
                if rock[p, r] or exc[p, r]: continue
                d = int(G[i, j]) - int(H[p, r]); n += 1; worst = min(worst, d)
                if d < P.SHEER: low.append((int(X[i, j]), int(Z[i, j]), d))
        print(f"edge: {n} edge pairs of the rock, the lowest wall {worst} (>= {P.SHEER})" + (f"; low: {low[:10]}" if low else ""))
        ok &= not low
    if "knock" in what:
        kn = rl["knock"]; dep = (Wa - G)[kn]; fl = (G == rl["T"])[kn]
        print(f"knock: {int(kn.sum())} cells, water depth {int(dep.min())}..{int(dep.max())} (>= 4), floor as planned on {int(fl.sum())}")
        ok &= int(kn.sum()) == 224 and dep.min() >= 4 and fl.all()
    if "lake" in what:
        lk = rl["Wt"] != NONE; bad = []
        sand = np.zeros(lk.shape, bool)
        for (x, z) in rl["sand"]: sand[P.ix(gr, x, z)] = True
        for i, j in zip(*np.nonzero(lk & ~sand)):
            if Wa[i, j] != P.W and TOP[i, j] <= P.W: bad.append(("level", int(X[i, j]), int(Z[i, j]), int(Wa[i, j])))
            for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                p, r = i + a, j + c
                if lk[p, r] or Wa[p, r] == P.W: continue
                if G[p, r] < P.W: bad.append(("leak", int(X[p, r]), int(Z[p, r]), int(G[p, r])))
        pools = gr["place"] & ~lk & (Wa != NONE) & (Wa > G) & (Wa > P.W)
        print(f"lake: {int(lk.sum())} water columns at W {P.W}, problems {len(bad)} {bad[:6]}; standing water above the lake elsewhere in the place: {int(pools.sum())}"
              + (" e.g. %s" % [(int(X[i, j]), int(Z[i, j]), int(Wa[i, j])) for i, j in list(zip(*np.nonzero(pools)))[:6]] if pools.any() else ""))
        ok &= not bad and not pools.any()
    if "bfs" in what:
        seeds = [(381, -52), (356, -40), (440, -108), (548, 0), (450, 112), (360, 20)]
        stair = P.rect((P.PIER[0], P.PIER[1], P.FACE_X + 15, P.PIER[3]), X, Z) | P.rect((P.REST[0] - 1, P.REST[1] - 1, P.REST[2], P.REST[3] + 1), X, Z)
        for closed in (True,):
            blocked = stair if closed else np.zeros(X.shape, bool)
            seen = np.zeros(X.shape, bool); q = deque()
            for (x, z) in seeds:
                i, j = P.ix(gr, x, z); seen[i, j] = True; q.append((i, j))
            hh = H.copy(); n0, n1 = hh.shape
            while q:
                i, j = q.popleft(); h = hh[i, j]
                for a in (-1, 0, 1):
                    for c in (-1, 0, 1):
                        if not (a or c): continue
                        for k in (1, 2, 3, 4):
                            p, r = i + a * k, j + c * k
                            if not (0 <= p < n0 and 0 <= r < n1) or blocked[p, r] or not gr["place"][p, r] and k > 1: break
                            lim = h + 1 if k == 1 else h + (1 if k == 2 else 0)
                            if hh[p, r] <= lim and not seen[p, r]: seen[p, r] = True; q.append((p, r))
                            if k == 1 and hh[p, r] <= h: break                 # a gap jump only over lower ground
                            if hh[p, r] > h: break
            got = seen & rock
            tag = "stair walled up" if closed else "stair open"
            print(f"bfs ({tag}): {int(seen.sum())} columns reached, rock cells reached {int(got.sum())}"
                  + (" e.g. %s" % [(int(X[i, j]), int(Z[i, j]), int(H[i, j])) for i, j in list(zip(*np.nonzero(got)))[:6]] if got.any() else ""))
            near = int(seen[P.ix(gr, 414, -40)]) + int(seen[P.ix(gr, 400, -34)])
            print(f"     (the causeway's end and the knock zone reached: {near}/2 - the walk itself works)")
            ok &= not got.any() and near == 2
    print("OK" if ok else "CHECK"); return ok

if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1:] or ["edge", "knock", "lake", "bfs"]) else 1)
