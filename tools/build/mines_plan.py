"""T-033: the layout of the Iron Ore Mines (Шахты Железных Руд, Р1) on the place `mines` (rect 280 -60 60 50): the yard terrace (a search:
the least earth work for >= 30 x 22 inside the place, cut / fill <= 8), the levels (HQ T-033, 2: H1 = Y - 12, H2 = Y - 24, H3 = Y - 34,
floors; feet on floor + 1), the workings (drifts, the adit, the two inclines, the shaft), the cave-ins with their bypasses, the big
collapse and Bran's pocket, the ore strips (exact numbers of economy.md), the approach from the trail refuge -> causeway of T-022 (A* 2 wide
in half blocks). Read by tools/build/r1_mines.py (the blocks are mines_build.py); only planning here.

Everything is computed from the ground before the place (the first scan mines_pre.bin, kept in mines_before.npz) and the blocks under it
before the step (mines_under.npz: the vanilla caves, lava and gravel the step fills), the same on every run. The stop conditions of HQ
T-033, 2 raise SystemExit("STOP ...")."""
import hashlib, json, os, re, struct, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, NONE
from lib import h as hsh
import spiders_plan as SP          # astar / widen2 / trail_ok / steps / side / D (the trails of T-032: 2 wide, half blocks, level turns)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/r1")
PLACE = (250, -85, 310, -35)               # `mines rect 280 -60 60 50` (tools/build/r1_plots.txt)
MARGIN = 16
XMAX = 323                                 # the scan box of the castle (T-028) starts at x 324: never written
BOX = (PLACE[0] - MARGIN - 10, PLACE[1] - MARGIN - 10, PLACE[2] + MARGIN + 10, PLACE[3] + MARGIN + 10)   # 224 -111 336 -9
YARD_MIN = (30, 22)                        # HQ T-033, 2: the yard terrace >= 30 x 22
YARD_WORK = 8                              # stop: cut or fill over 8
WALL_AT = 3                                # a retaining wall where the edge differs by more than 3 (else 1:1 slopes)
WORK_PAD = 3                               # the workings keep 3 from the box of the place
COVER = 6                                  # rock over the workings (ground - ceiling); the portal of the adit excepted
TRAIL_CUT = 4                              # stop: the approach needs a cut or a fill over 4
FILL_BELOW = 6                             # the box is ours from H3 - 10 up to the ground - 6

ORE = {   # HQ T-033, 2 (economy.md, 22.10): horizon -> [(block, count, where)]
    1: [("coal_ore", 120, "all"), ("copper_ore", 15, "far")],
    2: [("coal_ore", 40, "near"), ("iron_ore", 40, "far"), ("copper_ore", 25, "mid")],
    3: [("iron_ore", 35, "all")],
    4: [("iron_ore", 25, "all"), ("lapis_ore", 12, "all")],    # 4 = Bran's pocket on H3 behind the big collapse
}

def in_rect(r, x, z): return (x >= r[0]) & (x <= r[2]) & (z >= r[1]) & (z <= r[3])
def in_place(x, z, m=MARGIN): return PLACE[0] - m <= x <= min(PLACE[2] + m, XMAX) and PLACE[1] - m <= z <= PLACE[3] + m
def ix(gr, x, z): return z - gr["z1"], x - gr["x1"]
def B4(gr, x, z): return int(gr["before"][ix(gr, x, z)])

def frame_trails():
    """the cells of the trails of T-022 near the place (refuge -> causeway, garden -> causeway) with 3 cells of their banks, and the
    centre line of refuge -> causeway (the approach starts beside it)"""
    d = json.load(open(os.path.join(OUT, "r1.json")))
    cells = set(); line = []
    for t in d["trails"]:
        if 7 not in (t["a"], t["b"]): continue
        for (x, z) in t["cells"]:
            if not in_place(x, z, MARGIN + 12): continue
            line.append((x, z))
            for a in range(-3, 4):
                for c in range(-3, 4): cells.add((x + a, z + c))
    return cells, sorted(set(line))

def grids():
    x1, z1, x2, z2 = BOX; X, Z = np.meshgrid(np.arange(x1, x2 + 1), np.arange(z1, z2 + 1))
    def grid(s, a): return a[z1 - s.z0:z2 - s.z0 + 1, x1 - s.x0:x2 - s.x0 + 1].astype(np.int32)
    base = Scan(os.path.join(OUT, "base.bin"))
    gr = dict(X=X, Z=Z, x1=x1, z1=z1, nat=grid(base, base.ground),
              place=in_rect((PLACE[0] - MARGIN, PLACE[1] - MARGIN, min(PLACE[2] + MARGIN, XMAX), PLACE[3] + MARGIN), X, Z), inner=in_rect(PLACE, X, Z))
    d = open(os.path.join(OUT, "terrain.bin"), "rb").read(); assert d[:4] == b"LETA"
    tx0, tz0, tw, th = struct.unpack("<4i", d[4:20]); TH = np.frombuffer(d, "<i2", tw * th, 20).reshape(th, tw).astype(np.int32)
    gr["frame"] = TH[z1 - tz0:z2 - tz0 + 1, x1 - tx0:x2 - tx0 + 1] != NONE
    pre_path = os.path.join(OUT, "mines_pre.bin")
    if not os.path.exists(pre_path): raise SystemExit("no %s: tools/terrain.sh scan %d %d %d %d %s" % ((pre_path,) + BOX + (pre_path,)))
    pre = Scan(pre_path); gr.update(live=grid(pre, pre.ground), top=grid(pre, pre.top), lwater=grid(pre, pre.water))
    key = hashlib.sha1(open(os.path.join(OUT, "terrain.bin"), "rb").read() + open(os.path.join(OUT, "base.bin"), "rb").read()).hexdigest()
    cp = os.path.join(OUT, "mines_before.npz")
    if os.path.exists(cp) and str(np.load(cp)["key"]) == key:
        dd = np.load(cp); gr["before"] = dd["before"].astype(np.int32); gr["btop"] = dd["top"].astype(np.int32); gr["bwat"] = dd["water"].astype(np.int32)
    else:
        gr["before"] = gr["live"].copy(); gr["btop"] = gr["top"].copy(); gr["bwat"] = gr["lwater"].copy()
        np.savez_compressed(cp, before=gr["before"], top=gr["btop"], water=gr["bwat"], key=key)
    gr["under"] = under_blocks(key)
    ft, fline = frame_trails()
    m = np.zeros(X.shape, bool)
    for (x, z) in ft:
        if x1 <= x <= x2 and z1 <= z <= z2: m[z - z1, x - x1] = True
    gr["ftrail"] = m | gr["frame"]; gr["fline"] = fline
    gr["wet"] = gr["bwat"] > gr["before"]
    return gr

ROCK_OK = re.compile(r"minecraft:(stone|andesite|diorite|granite|tuff|deepslate|dirt|coarse_dirt|calcite|grass_block)$")
def under_blocks(key):
    """the blocks of the box of the place that are not plain rock (air, cave air, water, lava, gravel, infested stone, ores...), read from
    the world before the step (the first run), kept in mines_under.npz: {(x, y, z): name}"""
    cp = os.path.join(OUT, "mines_under.npz")
    if os.path.exists(cp):
        dd = np.load(cp, allow_pickle=True)
        if str(dd["key"]) == key: return {tuple(int(t) for t in k): str(n) for k, n in zip(dd["pos"], dd["name"])}
    import fens_scan
    old = fens_scan.BAN; fens_scan.BAN = re.compile(r"(?!%s).*" % ROCK_OK.pattern)
    try: found = fens_scan.scan(os.path.join(ROOT, "server/world"), box=PLACE)
    finally: fens_scan.BAN = old
    found = [(x, y, z, n) for (x, y, z, n) in found if y < 170 and not (n == "minecraft:air" and y > 95)]
    np.savez_compressed(cp, pos=np.array([[x, y, z] for (x, y, z, n) in found] or np.zeros((0, 3)), np.int32),
                        name=np.array([n for (x, y, z, n) in found], object), key=key)
    return {(x, y, z): n for (x, y, z, n) in found}

# ---------------------------------------------------------------- the yard
def yard_site(gr):
    """HQ T-033, 2: the terrace >= 30 x 22 (either way round) inside the place with WALL_AT of room for its slopes, the least earth work
    sum |Y - ground|; cut and fill <= 8 (stop otherwise). Returns the rect and the level Y (the top block of the yard)"""
    best = None
    for (w, d) in (YARD_MIN, YARD_MIN[::-1]):
        for x1 in range(PLACE[0] + WORK_PAD, PLACE[2] - WORK_PAD - w + 2):
            for z1 in range(PLACE[1] + WORK_PAD, PLACE[3] - WORK_PAD - d + 2):
                i1, j1 = ix(gr, x1, z1); a = gr["before"][i1:i1 + d, j1:j1 + w]
                for Y in range(int(a.min()), int(a.max()) + 1):
                    cut, fill = int((a - Y).max()), int((Y - a).max())
                    if max(cut, fill) > YARD_WORK: continue
                    c = (int(np.abs(a - Y).sum()), cut + fill, x1, z1, w, d, Y, cut, fill)
                    if best is None or c < best: best = c
    if best is None: raise SystemExit("STOP (HQ T-033, 2): no yard %d x %d with cut and fill <= %d" % (YARD_MIN + (YARD_WORK,)))
    work, _, x1, z1, w, d, Y, cut, fill = best
    return dict(r=(x1, z1, x1 + w - 1, z1 + d - 1), Y=Y, cut=cut, fill=fill, work=work)

# ---------------------------------------------------------------- the workings
# Drawn for the yard the search finds on seed 10845 (x 253..282, z -82..-61, Y 111): HQ T-033, 2 fixes the depths from Y; the plan in
# plan view is ours. Rects are floor cells (x1, z1, x2, z2), inclusive.
YARD_EXPECT = (253, -82, 282, -61)
SHAFT = (272, -74, 276, -70)               # the shaft 5 x 5 (inside), under the headframe 7 x 7
HEADFRAME = (271, -75, 277, -69)
LADDER_Z = -74                             # the ladders on the north wall, columns alternating
LADDER_X = (273, 275)
# horizon -> [(name, rect, width)]; H1 drifts 3 x 3, H2 2 wide x 3 high (HQ T-033, 2: «уже»), H3 main 3 wide, side 2
DRIFTS = {
    1: [("A1", (298, -80, 300, -40)), ("A2", (262, -42, 297, -40)), ("A3", (258, -73, 297, -71))],
    2: [("B1", (263, -72, 264, -58)), ("B1b", (265, -71, 271, -70)), ("B2a", (277, -71, 282, -70)), ("B2b", (281, -69, 282, -61)),
        ("B2c", (281, -60, 306, -59)), ("B2d", (305, -58, 306, -44)),
        ("K1a", (287, -62, 288, -61)), ("K1b", (287, -64, 297, -63)), ("K1c", (296, -62, 297, -61)),          # the bypass of cave-in 1
        ("K2a", (301, -58, 304, -57)), ("K2b", (301, -56, 302, -52)), ("K2c", (301, -51, 304, -50))],         # the bypass of cave-in 2
    3: [("D1a", (263, -46, 291, -44)), ("D1b", (263, -61, 265, -47)), ("D2", (274, -69, 275, -47)),
        ("K3a", (271, -43, 272, -42)), ("K3b", (263, -41, 272, -40)), ("K3c", (263, -43, 264, -42))],         # the bypass of cave-in 3
    4: [("P", (260, -75, 267, -70))],          # Bran's pocket (H3)
}
# the inclines: (name, from horizon, lanes rect, direction of descent (dx, dz), number of stairs per flight, rail lane or None)
INCLINES = [("adit", 0, (283, -66, 297, -64), (1, 0), (6, 6), -66),
            ("I12", 1, (262, -57, 264, -43), (0, -1), (6, 6), None),
            ("I23", 2, (292, -46, 304, -44), (-1, 0), (6, 4), None)]
# cave-ins: (n, horizon, zone rect (floor cells), axis of the drift)
CAVES = [(1, 2, (290, -60, 294, -59), "x"), (2, 2, (305, -56, 306, -52), "z"), (3, 3, (266, -46, 270, -44), "x")]
BIG = dict(rect=(263, -69, 265, -62), front=-62, lane=(264, 265))   # the big collapse at the end of D1b (north); Bran's crawl: x 264..265
WATER = (277, 288)                         # D1a: x 278..287 water, 277 and 288 the waterlogged slab steps
DRIPS = [(279, -45), (282, -46), (285, -44), (287, -45)]      # pointed dripstone under the ceiling over the water

def levels(Y):
    return {0: Y, 1: Y - 12, 2: Y - 24, 3: Y - 34, 4: Y - 34}

def incline_cells(inc, lv):
    """{(x, z): (kind, y)}: kind 'stair' (stair block at y, facing the ascent), 'land' (floor block y), 'rail' (rail at y on a block y - 1);
    a flight starts with a stair level with the floor above it (its top = that floor's surface), the landing is 1 under the last stair"""
    name, hfrom, r, (dx, dz), (n1, n2), rail = inc
    top = lv[hfrom]
    lanes = [(x, z) for x in range(r[0], r[2] + 1) for z in range(r[1], r[3] + 1)]
    along = (lambda q: (q[0] - r[0]) if dx > 0 else (r[2] - q[0])) if dx else (lambda q: (q[1] - r[1]) if dz > 0 else (r[3] - q[1]))
    seq = [("stair", top - k) for k in range(n1)] + [("land", top - n1)] * 3 + [("stair", top - n1 - k) for k in range(n2)]
    out = {}
    for q in lanes:
        k = along(q); kind, y = seq[k]
        lane = q[1] if dx else q[0]
        if rail is not None and lane == rail:
            if kind == "stair": out[q] = ("rail_up", y)          # the rail at y (the stair's level), its block y - 1
            else: out[q] = ("rail", y + 1)
        else: out[q] = (kind, y)
    face = {(1, 0): "west", (-1, 0): "east", (0, 1): "north", (0, -1): "south"}[(dx, dz)]
    return out, face

def workings(Y):
    """the excavation: floor cells per horizon {(x, z): floor}, the incline cells, the shaft; air {(x, y, z)}; walls (the rock cells
    beside the drifts' air, with their horizon) for the ore; stops when the workings leave the box of the place minus WORK_PAD"""
    lv = levels(Y)
    floor = {}; horizon = {}; seg_of = {}
    for h, segs in DRIFTS.items():
        for name, r in segs:
            for x in range(r[0], r[2] + 1):
                for z in range(r[1], r[3] + 1):
                    if in_rect(SHAFT, x, z): continue
                    floor[(x, z, h)] = lv[h]; seg_of[(x, z, h)] = name
    inc = {}
    for I in INCLINES:
        cells, face = incline_cells(I, lv)
        inc[I[0]] = dict(cells=cells, face=face)
    air = set()
    for (x, z, h), f in floor.items():
        for y in range(f + 1, f + 4): air.add((x, y, z))
    for nm, d in inc.items():
        for (x, z), (kind, y) in d["cells"].items():
            lo, hi = (y + 1, y + 3) if kind in ("stair", "land") else (y, y + 3) if kind == "rail_up" else (y, y + 2)
            for yy in range(lo, hi + 1): air.add((x, yy, z))        # rail: the rail at y on its block y - 1
    # the shaft: air from H3's floor + 1 to the deck (the platforms are solid, set by the build)
    plats = shaft_platforms(lv)
    for x in range(SHAFT[0], SHAFT[2] + 1):
        for z in range(SHAFT[1], SHAFT[3] + 1):
            for y in range(lv[3] + 1, lv[0]):
                if y not in plats: air.add((x, y, z))
    # the water steps and pool of D1a: the floor 1 lower there
    f3 = lv[3]
    for x in range(WATER[0], WATER[1] + 1):
        for z in range(-46, -43): air.add((x, f3, z))
    out = [q for q in air if not (PLACE[0] + WORK_PAD <= q[0] <= PLACE[2] - WORK_PAD and PLACE[1] + WORK_PAD <= q[2] <= PLACE[3] - WORK_PAD)]
    if out: raise SystemExit("STOP (HQ T-033, 2): the workings leave the box of the place minus %d: %s" % (WORK_PAD, sorted(out)[:5]))
    return dict(lv=lv, floor=floor, seg=seg_of, inc=inc, air=air, plats=plats)

def shaft_platforms(lv):
    """the platforms of the shaft (HQ T-033, 2: never more than 6 apart): the deck at Y, H1, H2 and H3 (its floor), one between each"""
    Y, f1, f2, f3 = lv[0], lv[1], lv[2], lv[3]
    ps = sorted({Y, (Y + f1) // 2, f1, (f1 + f2) // 2, f2, (f2 + f3) // 2, f3}, reverse=True)
    assert all(a - b <= 6 for a, b in zip(ps, ps[1:])), ps
    return ps

def ladder_x(k): return LADDER_X[k % 2]

def walls(W, skip):
    """the rock cells beside the air of the drifts (and the pocket) at the feet .. head rows (floor + 1 .. + 3), by horizon:
    {h: [(x, y, z, (nx, nz) normal into the drift, segment, along)]}; skip(x, y, z) drops crib posts, cave-ins and junctions"""
    out = {1: [], 2: [], 3: [], 4: []}; seen = set()
    for (x, z, h), f in sorted(W["floor"].items()):
        for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            wx, wz = x + dx, z + dz
            for y in range(f + 1, f + 4):
                if (wx, y, wz) in W["air"] or (wx, y, wz) in seen or skip(wx, y, wz): continue
                seen.add((wx, y, wz))
                nm = W["seg"][(x, z, h)]
                out[h].append((wx, y, wz, (-dx, -dz), nm, x if abs(dz) else z))
    return out

def strips(cands, n, salt, order):
    """n ore cells in strips along the walls (HQ T-033, 2: bands 1..3 high along the drifts; the rest stone): candidates sorted by
    order(c) are walked wall by wall (same segment and normal); a strip runs 2..6 cells along, 1..3 rows high from the floor row, gaps 2..7;
    repeated with shorter gaps until n are placed (exactly n: the last strip is cut)"""
    from collections import defaultdict
    faces = defaultdict(list)
    for c in cands: faces[(c[4], c[3])].append(c)
    keys = sorted(faces, key=lambda k: min(order(c) for c in faces[k]))
    picked = []; got = set()
    for rnd in range(6):
        for k in keys:
            cs = faces[k]
            rows = defaultdict(dict)
            for c in cs: rows[c[5]][c[1]] = c
            along = sorted(rows)
            i = int(hsh(len(along), rnd, salt, 7) * 3)
            while i < len(along) and len(picked) < n:
                a0 = along[i]; L = 2 + int(hsh(a0, rnd, salt, 11) * 5); hgt = 1 + int(hsh(a0, rnd, salt, 13) * 3)
                ys = sorted(rows[a0]); y0 = ys[0] + int(hsh(a0, rnd, salt, 17) * max(1, len(ys) - hgt + 1))
                for a in along[i:i + L]:
                    if a - a0 >= L: break
                    for y in range(y0, y0 + hgt):
                        c = rows[a].get(y)
                        if c and (c[0], c[1], c[2]) not in got and len(picked) < n: got.add((c[0], c[1], c[2])); picked.append(c)
                i += L + max(1, int((2 + hsh(a0, rnd, salt, 19) * 6) / (1 + rnd)))
            if len(picked) >= n: break
        if len(picked) >= n: break
    return picked

# ---------------------------------------------------------------- the approach
def approach(gr, yard, keep):
    """HQ T-033, 2: from the trail refuge -> causeway (just north of its banks, z of the place's south seam) to the yard's south edge: 2
    wide, half a block per cell, no jumps, in the place and its seam only, cut / fill <= 4 (stop otherwise)"""
    x1, z1, x2, z2 = yard["r"]; Y = yard["Y"]
    inside = lambda x, z: in_place(x, z) and x >= PLACE[0] - 6
    ok = SP.trail_ok(gr, keep, TRAIL_CUT, inside)
    cost = lambda x, z, v: 0.12 * abs(v / 2 - B4(gr, x, z))
    gx = (x1 + 2, x1 + 16)                     # the yard's south edge, its west half (the east half is cut 6..8 into the hill)
    goal = lambda x, z, v: gx[0] <= x <= gx[1] and z == z2 + 1 and v == 2 * Y
    hh = lambda x, z, v: max(0, gx[0] - x, x - gx[1]) + abs(z - z2 - 1) + abs(v - 2 * Y) * 0.5
    starts = []
    for (fx, fz) in gr["fline"]:
        if not (PLACE[0] <= fx <= PLACE[0] + 30): continue
        sz = fz - 4                            # just north of the banks (3) of the trail
        if any((fx, zz) in gr["fline"] for zz in range(sz - 3, sz + 1)) or not inside(fx, sz) or gr["ftrail"][ix(gr, fx, sz)]: continue
        starts.append((abs(fx - sum(gx) // 2), fx, sz))
    for _, fx, sz in sorted(starts):
        v0 = 2 * B4(gr, fx, sz)
        if not ok(fx, sz, v0, 3): continue
        p = SP.astar((fx, sz, v0), goal, hh, ok, cost, turn=0.4, run=2)
        if p: return p[::-1]                   # yard -> trail (widened in the search order below)
    raise SystemExit("STOP (HQ T-033, 2): the approach needs a cut or a fill over %d or columns outside the place and its seam" % TRAIL_CUT)

# ---------------------------------------------------------------- relief
def relief(gr, yard, ta):
    """T (the ground per column as the step writes it): the yard at Y; round it 1:1 slopes where the edge differs by <= WALL_AT, a
    retaining wall otherwise (cut: the wall stands in the first ring outside, its top the natural ground; fill: the yard's edge column is
    the wall); the approach (half blocks, banks <= 3 cells like the trails of T-032)"""
    T = gr["before"].copy(); bf = gr["before"]
    x1, z1, x2, z2 = yard["r"]; Y = yard["Y"]
    yd = in_rect(yard["r"], gr["X"], gr["Z"])
    T[yd] = Y
    walls = dict(cut=set(), fill=set())
    for z in range(z1 - 3, z2 + 4):
        for x in range(x1 - 3, x2 + 4):
            if x1 <= x <= x2 and z1 <= z <= z2: continue
            if not in_place(x, z, 0): continue
            ex, ez = min(max(x, x1), x2), min(max(z, z1), z2)          # the nearest yard cell
            d = max(abs(x - ex), abs(z - ez))
            e1 = (ex + int(np.sign(x - ex)), ez + int(np.sign(z - ez)))   # the first ring cell toward it
            de = B4(gr, *e1) - Y
            if abs(de) > WALL_AT:
                if d == 1: (walls["cut"] if de > 0 else walls["fill"]).add((x, z) if de > 0 else (ex, ez))
                continue
            b = B4(gr, x, z)
            T[ix(gr, x, z)] = min(max(b, Y - d), Y + d)
    # the approach: its cells at v // 2, banks as T-032
    flat = dict(ta)
    src = np.full(T.shape, -999); srcu = np.full(T.shape, 9999)
    for (x, z), v in flat.items(): srcu[ix(gr, x, z)] = v // 2; src[ix(gr, x, z)] = v // 2
    up, low = srcu.copy(), src.copy()
    for k in range(3):
        pu = np.pad(up, 1, constant_values=9999); pl = np.pad(low, 1, constant_values=-999); mu = up.copy(); ml = low.copy()
        for dz in (0, 1, 2):
            for dx in (0, 1, 2):
                if dz != 1 and dx != 1: continue
                mu = np.minimum(mu, pu[dz:dz + T.shape[0], dx:dx + T.shape[1]] + 1)
                ml = np.maximum(ml, pl[dz:dz + T.shape[0], dx:dx + T.shape[1]] - 1)
        up, low = mu, ml
    fm = np.zeros(T.shape, bool)
    for q in flat: fm[ix(gr, *q)] = True
    near_yard = in_rect((x1 - 4, z1 - 4, x2 + 4, z2 + 4), gr["X"], gr["Z"])
    cone = gr["place"] & ~fm & ~near_yard & ~gr["ftrail"]
    T = np.where(cone, bf + np.clip(np.clip(bf, low, up) - bf, -TRAIL_CUT, TRAIL_CUT), T)
    for (x, z), v in flat.items(): T[ix(gr, x, z)] = v // 2
    return dict(T=T, walls=walls, flat=flat, flatm=fm, yard=yd)

# ---------------------------------------------------------------- the plan
def plan(gr):
    """cached in server/build/r1/mines_plan.pkl (the A* of the approach), keyed by the ground before and the sources"""
    import pickle
    src = open(os.path.abspath(__file__), "rb").read() + open(SP.__file__.replace(".pyc", ".py"), "rb").read()
    key = hashlib.sha1(gr["before"].tobytes() + gr["ftrail"].tobytes() + src).hexdigest()
    cp = os.path.join(OUT, "mines_plan.pkl")
    if os.path.exists(cp):
        d = pickle.load(open(cp, "rb"))
        if d.get("key") == key: return d["plan"]
    pl = plan_now(gr)
    pickle.dump(dict(key=key, plan=pl), open(cp, "wb"))
    return pl

def plan_now(gr):
    yard = yard_site(gr)
    if yard["r"] != YARD_EXPECT: raise SystemExit("the yard search gives %s, the workings are drawn for %s: redraw DRIFTS" % (yard["r"], YARD_EXPECT))
    x1, z1, x2, z2 = yard["r"]
    keep = {(x, z) for x in range(x1 - 1, x2 + 2) for z in range(z1 - 1, z2 + 1)}
    pa = approach(gr, yard, keep)
    ta = SP.widen2(pa[::-1])                 # widened in the search order (trail -> yard): its lanes are the ones the search checked
    return dict(yard=yard, pa=pa, ta=ta)

def checks(gr, yard, rl, W, ta):
    """the numbers of the plan and the stop conditions (the yard's and the approach's work, the cover over the workings)"""
    T, bf = rl["T"], gr["before"]
    info = dict(yard=list(yard["r"]), Y=yard["Y"], yard_cut=yard["cut"], yard_fill=yard["fill"], levels=W["lv"],
                approach_len=len(ta), approach_cut=max([B4(gr, *q) - v / 2 for q, v in ta.items()] + [0]),
                approach_fill=max([v / 2 - B4(gr, *q) for q, v in ta.items()] + [0]), approach_step=SP.steps(ta))
    if info["approach_step"] > 1: raise SystemExit("the approach steps more than half a block: %s" % info)
    for k in ("approach_cut", "approach_fill"):
        if info[k] > TRAIL_CUT: raise SystemExit("STOP (HQ T-033, 2): %s %.1f > %d" % (k, info[k], TRAIL_CUT))
    out = [q for q in ta if not in_place(*q)]
    if out: raise SystemExit("STOP (HQ T-033, 2): approach cells outside the place and its seam: %s" % out[:5])
    if (T != bf)[gr["ftrail"]].any(): raise SystemExit("the trails of T-022 would change")
    # the cover: ground (after the step) - the top air of the workings >= COVER except the adit's first cells (the portal)
    top = {}
    for (x, y, z) in W["air"]: top[(x, z)] = max(top.get((x, z), -999), y)
    portal = {q for q, (k, y) in W["inc"]["adit"]["cells"].items() if q[0] <= INCLINES[0][2][0] + 4}
    thin = [(x, z, int(T[ix(gr, x, z)]) - y) for (x, z), y in top.items() if (x, z) not in portal and not in_rect(SHAFT, x, z)
            and int(T[ix(gr, x, z)]) - y < COVER]
    info["cover_min"] = min(int(T[ix(gr, x, z)]) - y for (x, z), y in top.items() if (x, z) not in portal and not in_rect(SHAFT, x, z))
    if thin: raise SystemExit("STOP: the rock over the workings is thinner than %d at %s" % (COVER, sorted(thin)[:6]))
    info["lowest"] = min(y for (x, y, z) in W["air"]) - 1
    if info["lowest"] < 30: raise SystemExit("STOP (framework): the workings go under y 30")
    info["changed"] = int(((T != bf) & gr["place"]).sum())
    return info
