#!/usr/bin/env python3
"""T-029: walk-bot routes through the castle -> server/build/walk/c_*.json (tools/walkbot.py, no jumps): the shortest ways on the block
model (castle_walkcheck rules: steps up <= 0.5 or onto a stair from its low side, no dropping through floors) between the places of the
task, cut to the points where the way turns:
  c_tour     the gate of the barbican -> the court -> the chapel -> the library -> the kitchens -> the armoury -> the galleries -> the
             vestibule (bonfire 11) -> the throne hall -> its gallery (by the corner stair) -> back to the gate
  c_dungeon  the library -> the gaol -> the crypt -> back to the library (the gaol door open)
  c_secret   the reliquary -> the spiral -> the tunnel -> the pier door -> the pier (the reliquary door and the pier door open)
  python3 tools/build/castle_keep_routes.py    (needs server/build/r1/castle_pre.bin of the place, as r1_castle.py)"""
import collections, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import castle_plan as P
import castle_layout as L
import castle_walkcheck as CW
from walkcheck import DIRS, surfaces
import r1_castle as R1

ROOT = P.ROOT; OUT = os.path.join(ROOT, "server/build/walk")


def model():
    gr = P.grids(); rl = P.relief(gr); b, meta = R1.build(gr, rl)
    T = rl["Tw"]; tpl = meta["keep_tpl"]
    def mk(states):
        over = {}
        for s in states: over.update(tpl[s])
        def get(x, y, z):
            if (x, y, z) in over: return over[(x, y, z)]
            s = b.get(x, y, z)
            if s is not None: return s
            i, j = z - gr["z1"], x - gr["x1"]
            return "minecraft:stone" if 0 <= i < T.shape[0] and 0 <= j < T.shape[1] and y <= T[i, j] else None
        return get
    return mk


def path(get, a, goal, box=(400, -40, 490, 96), y1=90, y2=262):
    """BFS (castle_walkcheck moves) from a = (x, z, feet) to the cell goal = (x, z, feet +- 0.6); the cells of the way"""
    x1, z1, x2, z2 = box
    par = {a: None}; q = collections.deque([a])
    while q:
        c = q.popleft(); x, z, s = c
        if (x, z) == goal[:2] and abs(s - goal[2]) < 0.6:
            out = []
            while c: out.append(c); c = par[c]
            return out[::-1]
        for (dx, dz), face in DIRS.items():
            nx, nz = x + dx, z + dz
            if not (x1 <= nx <= x2 and z1 <= nz <= z2): continue
            for ns, k in surfaces(get, nx, nz, max(y1, int(s) - 4), min(y2, int(s) + 2)):
                up = ns - s
                ok = up <= 0.5 + 1e-9 or (up <= 1.0 + 1e-9 and k == "stair:" + face)
                if up < -3: ok = False
                if ok and up < 0 and not CW.clear(get, nx, nz, ns, s): ok = False
                if ok and up > 0 and not CW.clear(get, x, z, s, ns): ok = False
                n = (nx, nz, ns)
                if ok and n not in par: par[n] = c; q.append(n)
    raise SystemExit("no way from %s to %s" % (a, goal))


def points(cells):
    """the turning points (block centres, feet) of a way of cells"""
    pts = [cells[0]]
    for i in range(1, len(cells) - 1):
        d0 = (cells[i][0] - cells[i - 1][0], cells[i][1] - cells[i - 1][1]); d1 = (cells[i + 1][0] - cells[i][0], cells[i + 1][1] - cells[i][1])
        if d0 != d1: pts.append(cells[i])
    pts.append(cells[-1])
    return [[x + 0.5, z + 0.5, float(s)] for (x, z, s) in pts]


def route(get, stops, box=(400, -40, 490, 96)):
    cells = []
    for a, b_ in zip(stops, stops[1:]):
        w = path(get, a, b_, box)
        cells += w if not cells else w[1:]
    return cells


def main():
    os.makedirs(OUT, exist_ok=True)
    mk = model(); Pp = L.P; G = L.GAL; HY = L.HALL_Y
    gate = (451, 33, 163.0)
    tour = [gate, (450, 47, Pp + 1.0), (420, 46, Pp + 1.0), (414, 75, Pp + 1.0), (450, 47, Pp + 1.0), (473, 49, Pp + 1.0), (476, 62, Pp + 1.0),
            (473, 49, Pp + 1.0), (468, 45, G + 1.0), (450, 56, G + 1.0), (424, 64, G + 1.0), (446, 73, Pp + 1.0), (444, 74, HY + 1.0),
            (450, 60, HY + L.HG + 1.0), (444, 74, HY + 1.0), (446, 73, Pp + 1.0), (450, 47, Pp + 1.0), gate]
    dungeon = [(414, 70, Pp + 1.0), (414, 78, L.GAOL_Y + 1.0), (420, 47, L.CRYPT_Y + 1.0), (414, 78, L.GAOL_Y + 1.0), (414, 70, Pp + 1.0)]
    secret = [(466, 75, HY + 1.0), (475, 79, L.TUN_Y + 1.0), (434, -32, L.DOOR_Y + 1.0), (428, -32, L.DOOR_Y + 1.0)]
    out = {}
    for name, stops, states in (("c_tour", tour, ["gate_open"]), ("c_dungeon", dungeon, ["gaol_door_open"]),
                                ("c_secret", secret, ["reliq_door_open", "pier_door_open"])):
        cells = route(mk(states), stops)
        pts = points(cells)
        s0 = cells[0]
        json.dump({"start": [s0[0] + 0.5, s0[2], s0[1] + 0.5], "points": pts}, open(os.path.join(OUT, name + ".json"), "w"))
        out[name] = (len(cells), len(pts))
    print("castle routes: " + ", ".join("%s %d cells %d points" % (k, a, b_) for k, (a, b_) in out.items()))


if __name__ == "__main__":
    main()
