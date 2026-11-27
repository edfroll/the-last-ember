"""T-034: the layout of the Ogre's Den (Нора Людоеда, Р1, card 5.1) on the place `ogre_den` (rect 250 180 40 30: x 230..270, z 165..195).

HQ T-034, 2 (by the seed not as on the card): the cave is a search under the hill north of the place (30 x 24 either way round, air 8 over
the floor, >= 8 of rock over the roof and >= 6 to the surface on every side); the stair (2 wide, flights of <= 10 stairs with 3 x 3
landings, turns on landings, <= 40 stairs, 3 of headroom) comes up from a wall of the cave to a mouth inside the place, by the old oak;
a fallen trunk lies across the trench of the mouth. The chain of bones (the tale of Toivo, T-032) goes from the trail refuge -> bonfire 2
(T-022) to the oak along the easiest way over the ground before the step (A* over the heights: up <= 1, down <= 3, dry).

Everything is computed from the ground before the step (the first scan ogre_pre.bin, kept in ogre_before.npz) and the blocks of the box of
the cave before the step (ogre_under.npz: the vanilla caves, water, lava the step fills with rock), the same on every run.
Only planning here; the blocks are tools/build/r1_ogre.py. Stop conditions raise SystemExit("STOP ...")."""
import hashlib, heapq, json, math, os, re, struct, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, NONE

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/r1")
PLACE = (230, 165, 270, 195)              # `ogre_den rect 250 180 40 30` (tools/build/r1_plots.txt)
MARGIN = 16
BOX = (55, 112, 300, 282)                 # the scan box of the step: the place + seam + 10, the cave + 6, the chain of bones to the trail
CAVE_WD = (30, 24)                        # HQ: 30 x 24, either way round
AIR = 8                                   # air over the floor: floor F, air F+1 .. F+8, roof F+9
COVER_UP, COVER_SIDE = 8, 6               # rock over the roof, rock to the surface on every side
CAVE_AREA = (196, 118, 296, 224)          # where the search puts the cave (the hill north of the place, under the seam and beyond)
FLIGHT = (3, 10)                          # stairs in a flight
STAIRS_MAX = 40
HEAD = 3                                  # air over every stair and landing block
SIGNS = (12, 20); GAP = (8, 12)           # the chain: 12..20 signs 8..12 apart

DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]         # east, south, west, north
FACE = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}
def right(d): return (-d[1], d[0])
def left(d): return (d[1], -d[0])
def in_rect(r, x, z): return r[0] <= x <= r[2] and r[1] <= z <= r[3]


# ---------------------------------------------------------------- inputs
class Ground:
    def __init__(self):
        pre_path = os.path.join(OUT, "ogre_pre.bin")
        if not os.path.exists(pre_path): raise SystemExit("no %s: tools/terrain.sh scan %d %d %d %d %s" % ((pre_path,) + BOX + (pre_path,)))
        pre = Scan(pre_path)
        x1, z1, x2, z2 = BOX
        assert (pre.x0, pre.z0, pre.w, pre.h) == (x1, z1, x2 - x1 + 1, z2 - z1 + 1), "ogre_pre.bin is not the box %s" % (BOX,)
        key = hashlib.sha1(open(os.path.join(OUT, "terrain.bin"), "rb").read() + open(os.path.join(OUT, "base.bin"), "rb").read()).hexdigest()
        cp = os.path.join(OUT, "ogre_before.npz")
        if os.path.exists(cp) and str(np.load(cp)["key"]) == key:
            d = np.load(cp); self.G = d["ground"].astype(np.int32); self.top = d["top"].astype(np.int32); self.W = d["water"].astype(np.int32)
        else:
            self.G, self.top, self.W = pre.ground.copy(), pre.top.copy(), pre.water.copy()
            np.savez_compressed(cp, ground=self.G, top=self.top, water=self.W, key=key)
        self.key = key; self.x1, self.z1 = x1, z1
    def g(self, x, z): return int(self.G[z - self.z1, x - self.x1])
    def t(self, x, z): return int(self.top[z - self.z1, x - self.x1])
    def wet(self, x, z): return int(self.W[z - self.z1, x - self.x1]) > int(self.G[z - self.z1, x - self.x1])
    def sub(self, x1, z1, x2, z2): return self.G[z1 - self.z1:z2 - self.z1 + 1, x1 - self.x1:x2 - self.x1 + 1]


def in_place(x, z, m=MARGIN):
    return PLACE[0] - m <= x <= PLACE[2] + m and PLACE[1] - m <= z <= PLACE[3] + m


# ---------------------------------------------------------------- the cave
def cave_site(gr):
    """the highest floor F with the cover of HQ (over the footprint ground >= F + 9 + 8, round it within 6 ground >= F + 9: every level
    of the air has 6 of rock to the surface); ties: the cave nearest to the place"""
    best = None
    for (w, d) in (CAVE_WD, CAVE_WD[::-1]):
        for x1 in range(CAVE_AREA[0] + COVER_SIDE, CAVE_AREA[2] - COVER_SIDE - w + 2):
            for z1 in range(CAVE_AREA[1] + COVER_SIDE, CAVE_AREA[3] - COVER_SIDE - d + 2):
                x2, z2 = x1 + w - 1, z1 + d - 1
                fp = int(gr.sub(x1, z1, x2, z2).min()); ring = int(gr.sub(x1 - COVER_SIDE, z1 - COVER_SIDE, x2 + COVER_SIDE, z2 + COVER_SIDE).min())
                F = min(fp - AIR - 1 - COVER_UP, ring - AIR - 1)
                dist = max(PLACE[0] - x2, 0, x1 - PLACE[2]) + max(PLACE[1] - z2, 0, z1 - PLACE[3])
                c = (-F, dist, x1, z1, w, d)
                if best is None or c < best: best = c
    F = -best[0]; x1, z1, w, d = best[2], best[3], best[4], best[5]
    if F < 30: raise SystemExit("STOP (HQ T-034, 2): no cave with the cover above y 30")
    return dict(r=(x1, z1, x1 + w - 1, z1 + d - 1), F=F)


# ---------------------------------------------------------------- the stair
def flight_cells(a, d, n, s):
    """the stairs of a flight going up along d from the cell a (lanes a, a + right(d)), the feet before it at s:
    [(x, z, block y, 'stair', d)]"""
    p = right(d); out = []
    for i in range(n):
        for w in (0, 1): out.append((a[0] + i * d[0] + w * p[0], a[1] + i * d[1] + w * p[1], s + i, "stair", d))
    return out

def landing_cells(a, d, n, side, y):
    """the 3 x 3 landing after a flight of n from a along d (block level y): 3 long, 3 wide (the lanes + one to `side`: 1 right, -1 left)"""
    p = right(d); ws = (0, 1, 2) if side >= 0 else (-1, 0, 1); out = []
    for i in range(n, n + 3):
        for w in ws: out.append((a[0] + i * d[0] + w * p[0], a[1] + i * d[1] + w * p[1], y, "land", d))
    return out

def stair_search(gr, cave):
    """flights from a wall of the cave up to a mouth in the place: the first flight starts at the wall (its first stair on the floor of
    the cave + 1), turns on 3 x 3 landings (straight, left, right), the top stair's feet = the ground of the 2 exit cells + 1 (cut or
    fill <= 1 there), 2 more cells of ground beyond within 1 of it. Headroom HEAD over every block; the roof is rock where the ground
    before is >= block + HEAD + 1, else the cell is open (a trench: only the last 4 stairs). Every cell >= 2 off the cave but the first
    flight's, inside the box. Cost: stairs, trench cells, earth work at the mouth; the mouth nearest to the place's middle"""
    x1, z1, x2, z2 = cave["r"]; F = cave["F"]
    starts = []
    for x in range(x1 + 2, x2 - 2):
        starts.append(((x, z2 + 1), (0, 1))); starts.append(((x + 1, z1 - 1), (0, -1)))
    for z in range(z1 + 2, z2 - 2):
        starts.append(((x2 + 1, z + 1), (1, 0))); starts.append(((x1 - 1, z), (-1, 0)))
    def near_cave(x, z): return x1 - 2 <= x <= x2 + 2 and z1 - 2 <= z <= z2 + 2
    best = None
    pmx, pmz = (PLACE[0] + PLACE[2]) / 2, (PLACE[1] + PLACE[3]) / 2

    def finish(cells, a, d, n, s, nst):
        # the mouth: the exit cells a + n*d (two lanes) and 2 beyond
        p = right(d); top = s + n
        ex = [(a[0] + (n + k) * d[0] + w * p[0], a[1] + (n + k) * d[1] + w * p[1]) for k in range(3) for w in (0, 1)]
        if not all(in_rect(PLACE, x, z) for (x, z) in ex): return None
        work = 0
        for k, (x, z) in enumerate(ex):
            gy = gr.g(x, z); dd = abs(gy - (top - 1))
            if gr.wet(x, z) or dd > 1: return None
            if k < 2: work += dd
        trench = 0; last = len(cells) - 1
        for k, (x, z, y, kind, _) in enumerate(cells):
            if gr.g(x, z) < y + HEAD + 1:
                trench += 1
                if kind != "stair" or (len(cells) - k) > 8: return None      # only the last 4 stairs (2 lanes) are open
        mx, mz = ex[0]
        return (nst + 2 * trench + 3 * work + 0.05 * math.hypot(mx - pmx, mz - pmz), cells, ex, top, work, trench)

    gmin = int(gr.sub(*PLACE).min())
    def grow(cells, a, d, s, nst, nfl):
        nonlocal best
        left_st = STAIRS_MAX - nst
        reach = left_st + 3 * (3 - nfl) + 4
        if max(PLACE[0] - a[0], 0, a[0] - PLACE[2]) + max(PLACE[1] - a[1], 0, a[1] - PLACE[3]) > reach: return
        if s + left_st < gmin + 1: return
        occ0 = {(x, z) for (x, z, *_) in cells}
        for n in range(FLIGHT[0], FLIGHT[1] + 1):
            if nst + n > STAIRS_MAX: break
            fc = flight_cells(a, d, n, s)
            if not all(BOX[0] + 2 <= x <= BOX[2] - 2 and BOX[1] + 2 <= z <= BOX[3] - 2 for (x, z, *_) in fc): break
            if nfl > 0 and any(near_cave(x, z) for (x, z, *_) in fc): break
            if any(gr.wet(x, z) for (x, z, *_) in fc) or any((x, z) in occ0 for (x, z, *_) in fc): break
            cc = cells + fc
            r = finish(cc, a, d, n, s, nst + n)
            if r and (best is None or r[0] < best[0]): best = r
            if nfl >= 3: continue
            y = s + n - 1
            for turn in ("straight", "left", "right"):
                side = -1 if turn == "left" else 1
                lc = landing_cells(a, d, n, side, y)
                if any(near_cave(x, z) for (x, z, *_) in lc) or any(gr.wet(x, z) for (x, z, *_) in lc): continue
                if turn == "straight": na, nd = (a[0] + (n + 3) * d[0], a[1] + (n + 3) * d[1]), d
                elif turn == "right":
                    p = right(d); na = (a[0] + (n + 2) * d[0] + 3 * p[0], a[1] + (n + 2) * d[1] + 3 * p[1]); nd = p
                else:
                    p = right(d); na = (a[0] + (n + 1) * d[0] - 2 * p[0], a[1] + (n + 1) * d[1] - 2 * p[1]); nd = left(d)
                occ = {(x, z) for (x, z, *_) in cc}
                if any((x, z) in occ for (x, z, *_) in lc): continue
                grow(cc + lc, na, nd, s + n, nst + n, nfl + 1)

    for (a, d) in starts:
        grow([], a, d, F + 1, 0, 0)
    if best is None: raise SystemExit("STOP (HQ T-034, 2): no stair of <= %d stairs from the cave to a mouth in the place" % STAIRS_MAX)
    cost, cells, ex, top, work, trench = best
    return dict(cells=cells, exit=ex, top=top, work=work, trench=trench, stairs=sum(1 for c in cells if c[3] == "stair") // 2)


# ---------------------------------------------------------------- the chain of bones
def trail_cells():
    d = json.load(open(os.path.join(OUT, "r1.json")))
    t = [t for t in d["trails"] if 2 in (t["a"], t["b"]) and "R" in (t["a"], t["b"])][0]
    return [tuple(c) for c in t["cells"]]

def chain_way(gr, goal):
    """the easiest way on the ground before the step from the trail refuge -> bonfire 2 to the goal (the cell before the oak): A* over the
    columns, up <= 1, down <= 3, dry; cost 1 a cell + 1 for a climb of 1 (it needs a jump); the trail cells and their 3 cells of banks
    are not walked but for the start"""
    tr = trail_cells(); trs = set(tr); bank = set()
    for (x, z) in tr:
        for a in range(-3, 4):
            for c in range(-3, 4): bank.add((x + a, z + c))
    starts = [c for c in tr if BOX[0] <= c[0] <= BOX[2] and BOX[1] <= c[1] <= BOX[3]]
    if not starts: raise SystemExit("STOP: the trail refuge -> bonfire 2 does not pass the box of the step")
    near = min(starts, key=lambda c: math.dist(c, goal))
    hh = lambda c: math.dist(c, goal)
    q = [(hh(near), 0.0, near)]; cost = {near: 0.0}; prev = {near: None}; end = None
    while q:
        _, cc, cur = heapq.heappop(q)
        if cc > cost[cur]: continue
        if cur == goal: end = cur; break
        y0 = gr.g(*cur)
        for d in DIRS + [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            n = (cur[0] + d[0], cur[1] + d[1])
            if not (BOX[0] + 1 <= n[0] <= BOX[2] - 1 and BOX[1] + 1 <= n[1] <= BOX[3] - 1): continue
            if n in trs: continue
            if gr.wet(*n): continue
            up = gr.g(*n) - y0
            if up > 1 or up < -3: continue
            if d[0] and d[1] and (gr.g(cur[0] + d[0], cur[1]) - y0 > 1 or gr.g(cur[0], cur[1] + d[1]) - y0 > 1): continue
            nc = cc + math.hypot(*d) + (1 if up == 1 else 0) + 0.2 * abs(up)
            if n not in cost or nc < cost[n]: cost[n] = nc; prev[n] = cur; heapq.heappush(q, (nc + hh(n), nc, n))
    if end is None: raise SystemExit("STOP: no way on the ground from the trail to the oak")
    way = []
    while end: way.append(end); end = prev[end]
    return way[::-1], near, bank

def chain_signs(gr, way, oak_cells, bank):
    """12..20 signs along the way, 8..12 apart in a straight line (the way bends round the hills): the first one >= 9 from the trail
    off its banks (seen from it), then greedily the farthest cell of the way (anywhere ahead: the bends are cut) within G of the last sign (G = 12, then less), the last
    within 15 of the mouth (the oak stands there); the kinds in turn: a skull (block), ribs (bone_block, 1 or 2), a bone (item_display), a skull, ribs: [(x, y, z, kind)], y the
    ground before + 1"""
    L = [0.0]
    for a, b in zip(way, way[1:]): L.append(L[-1] + math.dist(a, b))
    k0 = next(k for k in range(len(way)) if L[k] >= 9.0 and way[k] not in bank)
    best = None
    for G in (12.0, 11.5, 11.0, 10.5, 10.0):
        pts = [k0]
        while True:
            k = pts[-1]; cand = None
            for j in range(k + 1, len(way)):
                dj = math.dist(way[j], way[k])
                if dj <= G and way[j] not in bank and way[j] not in oak_cells: cand = j
            if cand is None or math.dist(way[k], way[-1]) <= 15: break      # the last sign within 15 of the mouth: the oak (14..18 high) is seen from it
            pts.append(cand)
        cells = [way[k] for k in pts]
        gaps = [math.dist(a, b) for a, b in zip(cells, cells[1:])]
        print("  chain G %.1f: %d signs, gaps %.1f..%.1f, the last %.1f from the mouth" % (G, len(cells), min(gaps), max(gaps), math.dist(cells[-1], way[-1])))
        if SIGNS[0] <= len(cells) <= SIGNS[1] and all(GAP[0] <= q <= GAP[1] for q in gaps) and math.dist(cells[-1], way[-1]) <= 15:
            best = cells; break
    if best is None:
        raise SystemExit("STOP (HQ T-034, 2): the way to the oak (%.0f long, %.0f straight) takes no %d..%d signs %d..%d apart"
                         % (L[-1], math.dist(way[0], way[-1]), SIGNS[0], SIGNS[1], GAP[0], GAP[1]))
    kinds = ["skull", "ribs", "bone", "skull", "ribs"]        # the first two blocks (seen from the trail); bones (item_displays) 1 in 5
    return [(x, gr.g(x, z) + 1, z, kinds[i % 5]) for i, (x, z) in enumerate(best)], L[-1]


# ---------------------------------------------------------------- the whole plan (cached by its inputs)
def plan():
    gr = Ground()
    src = hashlib.sha1(open(os.path.abspath(__file__), "rb").read()).hexdigest()
    cp = os.path.join(OUT, "ogre_plan.json")
    if os.path.exists(cp):
        d = json.load(open(cp))
        if d.get("key") == gr.key + src: return gr, d
    sp = os.path.join(OUT, "ogre_stair.json")      # the stair search is slow (~2 min): kept by its own inputs
    sk = gr.key + hashlib.sha1(open(os.path.abspath(__file__), "rb").read().split(b"# ---------------------------------------------------------------- the chain")[0]).hexdigest()
    if os.path.exists(sp) and json.load(open(sp)).get("key") == sk: d0 = json.load(open(sp)); cave, st = d0["cave"], d0["stair"]
    else:
        cave = cave_site(gr); st = stair_search(gr, cave); json.dump(dict(key=sk, cave=cave, stair=st), open(sp, "w"))
        cave, st = json.loads(json.dumps(cave)), json.loads(json.dumps(st))
    st["exit"] = [tuple(c) for c in st["exit"]]; st["cells"] = [(c[0], c[1], c[2], c[3], tuple(c[4])) for c in st["cells"]]
    # the oak: a 2 x 2 trunk beside the open part of the stair, on the side away from the cave, its cells on the ground within 1 of the
    # mouth's; the way of the chain ends at the exit
    ex = st["exit"]; d = tuple(st["cells"][-1][4]); p = right(d)
    top_cells = [c for c in st["cells"] if c[3] == "stair"][-8:]
    occ = {(x, z) for (x, z, *_) in st["cells"]} | set(ex)
    oak = None
    for side, off in ((1, 2), (-1, -1)):
        for back in (0, 1, 2, 3):
            ax = ex[0][0] - back * d[0] + (off if side > 0 else off - 1) * p[0]
            az = ex[0][1] - back * d[1] + (off if side > 0 else off - 1) * p[1]
            cells = [(ax + i * p[0] + j * d[0], az + i * p[1] + j * d[1]) for i in (0, 1) for j in (0, 1)]
            if any(c in occ for c in cells) or not all(in_rect(PLACE, *c) for c in cells): continue
            gys = [gr.g(*c) for c in cells]
            if max(gys) - min(gys) > 2: continue
            oak = dict(cells=cells, y=min(gys) + 1, side=side); break
        if oak: break
    if oak is None: raise SystemExit("STOP: no room for the oak by the mouth")
    goal = (ex[4][0] + 2 * d[0], ex[4][1] + 2 * d[1])
    way, start, bank = chain_way(gr, goal)
    signs, total = chain_signs(gr, way, set(oak["cells"]) | occ, bank)
    out = dict(key=gr.key + src, cave=cave, stair=st, oak=oak, way=way, trail_start=start, signs=signs, way_len=total)
    json.dump(out, open(cp, "w"))
    return gr, out


if __name__ == "__main__":
    gr, p = plan()
    st = p["stair"]
    print("cave", p["cave"], "stairs", st["stairs"], "top", st["top"], "exit", st["exit"][:2], "work", st["work"], "trench", st["trench"])
    print("flights:", [(c[0], c[1], c[2], c[3], c[4]) for c in st["cells"] if c[3] == "land"][::9])
    print("oak", p["oak"], "way", len(p["way"]), "%.0f" % p["way_len"], "from", p["trail_start"], "signs", len(p["signs"]))
