"""T-034: the layout of the Grotto of the Jelly (Грот Студня, Р1, card 5.4) under the north cliff of the bowl of the Crooked Fens (T-026).

HQ T-034, 3 (by the seed not as on the card): the levels from W = 134 (fens.json): the water of the grotto at W (sources), waist deep
(the floor W - 1), the dry ledge in the middle at W + 1 (feet W + 2), the roof at W + 10; >= 8 of rock over the roof and >= 6 to the
surface on every side; 30 x 26 either way round. The side channel (new): from the nearest water of the bowl that a boat reaches from the
hut's pier (a channel or shallows; not the pools of the heads P1..P5 nor their ring of shallows) to the mouth of the grotto: 3 wide,
water W, the bed W - 2, no flowing water over an edge; open first (a cut into the hill with sheer walls of the cliff's palette), the last
<= 12 cells a low tunnel (roof W + 3). The boardwalk, the climb from bonfire 5 and the zone of the hut are not crossed.

`places grotto+fens` checks the columns outside both places: the open cut stays inside the place of the fens or of `grotto` (each + 16 of
seam); the tunnel and the grotto are under the rock (their columns keep their tops).

Stop conditions of HQ (SystemExit("STOP ...")): the channel longer than 70 cells; a cut deeper than 20; no grotto with the cover of 8 / 6.
Everything from the ground and water before the step (grotto_pre.bin, kept in grotto_before.npz). Only planning here."""
import hashlib, heapq, json, math, os, sys
from collections import deque
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, NONE

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/r1")
BOX = (-500, 150, -296, 310)               # the scan box of the step (the grotto's search area + 6, the channel, the water of the bowl)
GROTTO_WD = (30, 26)
UP, SIDE = 8, 6
CH_MAX, CUT_MAX, TUNNEL_MAX = 70, 20, 12
HUT_R = 24 + 2                             # fens_hut: cylinder r 24 round the hut's centre (+ 2)
PLOTS = {"fens": (-490, 240, -270, 420), "grotto": (-348, 220, -312, 252)}    # r1_plots.txt rects (x1 z1 x2 z2)
SEAM = 16
SEARCH = (-480, 160, -310, 250)            # where the grotto may lie (under the hill north of the bowl)
DIRS = [(1, 0), (0, 1), (-1, 0), (0, -1)]


def in_rect(r, x, z, m=0): return r[0] - m <= x <= r[2] + m and r[1] - m <= z <= r[3] + m
def in_places(x, z): return any(in_rect(r, x, z, SEAM) for r in PLOTS.values())


class Ground:
    def __init__(self):
        p = os.path.join(OUT, "grotto_pre.bin")
        if not os.path.exists(p): raise SystemExit("no %s: tools/terrain.sh scan %d %d %d %d %s" % ((p,) + BOX + (p,)))
        s = Scan(p); x1, z1, x2, z2 = BOX
        assert (s.x0, s.z0, s.w, s.h) == (x1, z1, x2 - x1 + 1, z2 - z1 + 1), "grotto_pre.bin is not the box %s" % (BOX,)
        F = json.load(open(os.path.join(OUT, "fens.json")))
        self.Wl = F["W"]
        key = hashlib.sha1(open(os.path.join(OUT, "fens.txt"), "rb").read() + open(os.path.join(OUT, "base.bin"), "rb").read()).hexdigest()
        cp = os.path.join(OUT, "grotto_before.npz")
        if os.path.exists(cp) and str(np.load(cp)["key"]) == key:
            d = np.load(cp); self.G = d["ground"].astype(np.int32); self.T = d["top"].astype(np.int32); self.Wt = d["water"].astype(np.int32)
        else:
            self.G, self.T, self.Wt = s.ground.copy(), s.top.copy(), s.water.copy()
            np.savez_compressed(cp, ground=self.G, top=self.T, water=self.Wt, key=key)
        self.key = key; self.x1, self.z1 = x1, z1; self.F = F
    def g(self, x, z): return int(self.G[z - self.z1, x - self.x1])
    def w(self, x, z): return int(self.Wt[z - self.z1, x - self.x1])
    def wet(self, x, z): return self.w(x, z) > self.g(x, z)
    def sub(self, x1, z1, x2, z2): return self.G[z1 - self.z1:z2 - self.z1 + 1, x1 - self.x1:x2 - self.x1 + 1]
    def inbox(self, x, z, m=1): return BOX[0] + m <= x <= BOX[2] - m and BOX[1] + m <= z <= BOX[3] - m


def banned(gr):
    """cells the channel may not take: the pools of the heads and their ring of shallows (+ 1), the boardwalk and the climb (+ 2), the
    zone of the hut, the decks"""
    F = gr.F; out = set()
    for p in F["pools"]:
        r = p["r"] + 2 + 1
        for a in range(-r, r + 1):
            for c in range(-r, r + 1): out.add((p["x"] + a, p["z"] + c))
    pts = [tuple(c) for c in F["board"]] + [(c[0], c[2]) for c in F["climb"]] + [tuple(c) for c in F["cpath"]]
    for pair in F["deck"]: pts += [tuple(c) for c in pair]
    for (x, z) in pts:
        for a in range(-2, 3):
            for c in range(-2, 3): out.add((x + a, z + c))
    hx, hz = F["hut_centre"]
    for a in range(-HUT_R, HUT_R + 1):
        for c in range(-HUT_R, HUT_R + 1):
            if a * a + c * c <= HUT_R * HUT_R: out.add((hx + a, hz + c))
    return out


def boat_water(gr, ban):
    """the water at W a boat reaches from the hut's pier (fens.json boats 3 and 4): 3 x 3 open water round the boat (fens_boat.py)"""
    W = gr.Wl
    def water(x, z): return gr.inbox(x, z, 0) and gr.w(x, z) == W and gr.g(x, z) < W
    def boat(x, z): return all(water(x + a, z + b) for a in (-1, 0, 1) for b in (-1, 0, 1))
    seeds = []
    for (bx, by, bz) in gr.F["boats"]:
        for a in range(-3, 4):
            for c in range(-3, 4):
                if boat(bx + a, bz + c): seeds.append((bx + a, bz + c))
    seen = set(seeds); q = deque(seeds)
    while q:
        x, z = q.popleft()
        for (dx, dz) in DIRS:
            n = (x + dx, z + dz)
            if n not in seen and boat(*n): seen.add(n); q.append(n)
    return seen


def grotto_sites(gr):
    """every rect 30 x 26 (either way) in SEARCH with the cover: over the footprint ground >= W + 10 + 8, round it within 6 ground >=
    W + 10 (the air W + 1 .. W + 9 has rock to the side at every level)"""
    W = gr.Wl; out = []
    for (w, d) in (GROTTO_WD, GROTTO_WD[::-1]):
        for x1 in range(SEARCH[0], SEARCH[2] - w + 2):
            for z1 in range(SEARCH[1], SEARCH[3] - d + 2):
                x2, z2 = x1 + w - 1, z1 + d - 1
                if not (gr.inbox(x1 - SIDE, z1 - SIDE) and gr.inbox(x2 + SIDE, z2 + SIDE)): continue
                if gr.sub(x1, z1, x2, z2).min() < W + 10 + UP: continue
                if gr.sub(x1 - SIDE, z1 - SIDE, x2 + SIDE, z2 + SIDE).min() < W + 10: continue
                out.append((x1, z1, x2, z2))
    return out


HD = {}
def channel(gr, rect, ban, bw):
    """A* for the centre line of the channel from a door cell in a wall of the grotto (its middle third) out to a cell next to boat water:
    4 neighbours; the band of 3 across the line must be free of `ban`; while the line is under rock (ground over the band >= W + 4) it
    is the tunnel (only the first TUNNEL_MAX cells from the door); once open it stays open: every cell of the band inside the places
    (+ seam), its ground <= W + CUT_MAX. Cost: a cell 1, a turn 3, the cut depth / 4. Returns (line from the grotto out, cost) or None"""
    W = gr.Wl; x1, z1, x2, z2 = rect
    doors = []
    w3 = (x2 - x1) // 3; d3 = (z2 - z1) // 3
    for x in range(x1 + w3, x2 - w3 + 1): doors += [((x, z2 + 1), (0, 1)), ((x, z1 - 1), (0, -1))]
    for z in range(z1 + d3, z2 - d3 + 1): doors += [((x2 + 1, z), (1, 0)), ((x1 - 1, z), (-1, 0))]
    def band(c, d):
        p = (-d[1], d[0]); return [(c[0] + k * p[0], c[1] + k * p[1]) for k in (-1, 0, 1)]
    def in_grotto(x, z): return x1 <= x <= x2 and z1 <= z <= z2
    def under(cells): return all(gr.g(*c) >= W + 4 for c in cells)
    goal_near = set()
    for (x, z) in bw:
        for (dx, dz) in DIRS: goal_near.add((x + dx, z + dz))
    hdist = HD.get(id(bw))
    if hdist is None:                       # manhattan distance to the boat water (a BFS over the box, no obstacles)
        hdist = {c: 0 for c in bw}; qq = deque(bw)
        while qq:
            x, z = qq.popleft()
            for (dx, dz) in DIRS:
                n = (x + dx, z + dz)
                if n not in hdist and gr.inbox(*n, 0): hdist[n] = hdist[(x, z)] + 1; qq.append(n)
        HD[id(bw)] = hdist
    q = []; cost = {}; prev = {}
    for (c, d) in doors:
        b = band(c, d)
        if any(x in ban for x in b) or not under(b): continue
        st = (c, d, 1, True)
        cost[st] = 0; prev[st] = None; heapq.heappush(q, (0, 0, st))
    end = None
    while q:
        _, cc, st = heapq.heappop(q)
        if cc > cost[st]: continue
        c, d, n, tun = st
        if c in bw or (not tun and (c[0] + d[0], c[1] + d[1]) in bw):      # the boat goes on along d into the water of the bowl
            end = st; break
        if n >= CH_MAX: continue
        for nd in DIRS:
            if nd == (-d[0], -d[1]): continue
            nc = (c[0] + nd[0], c[1] + nd[1])
            if not gr.inbox(*nc, 3): continue
            b = band(nc, nd)
            if nd != d: b = b + band(c, nd)
            if any(x in ban or in_grotto(*x) for x in b): continue
            ntun = tun and under(b)
            if ntun and n + 1 > TUNNEL_MAX: continue
            if not ntun:
                if any(not in_places(*x) for x in b): continue
                if any(gr.g(*x) > W + CUT_MAX for x in b): continue
            depth = max(0, max(gr.g(*x) for x in b) - W)
            ncost = cc + 1 + (3 if nd != d else 0) + depth / 4.0
            ns = (nc, nd, n + 1, ntun)
            if ns not in cost or ncost < cost[ns]:
                cost[ns] = ncost; prev[ns] = st
                heapq.heappush(q, (ncost + hdist.get(nc, 999), ncost, ns))
    if end is None: return None
    line = []; s = end
    while s: line.append((s[0], s[1], s[3])); s = prev[s]
    return line[::-1], cost[end]


def plan():
    gr = Ground()
    src = hashlib.sha1(open(os.path.abspath(__file__), "rb").read().split(b"\ndef plan_png")[0]).hexdigest()
    cp = os.path.join(OUT, "grotto_plan.json")
    if os.path.exists(cp):
        d = json.load(open(cp))
        if d.get("key") == gr.key + src: return gr, d
    ban = banned(gr); bw = boat_water(gr, ban)
    bw = {c for c in bw if c not in ban}
    sites = grotto_sites(gr)
    if not sites: raise SystemExit("STOP (HQ T-034, 3): no grotto 30 x 26 under the hill with %d of rock over the roof and %d to the sides" % (UP, SIDE))
    # the grottoes nearest to the boat water first; the channel searched for each until one is found, then 40 more and the cheapest kept
    bwl = list(bw)[:: max(1, len(bw) // 300)]
    def dist(r): return min(max(r[0] - x, 0, x - r[2]) + max(r[1] - z, 0, z - r[3]) for (x, z) in bwl)
    sites.sort(key=dist)
    best = None; tried = 0
    for r in sites:
        if dist(r) > CH_MAX: break
        res = channel(gr, r, ban, bw)
        tried += 1
        if res:
            line, c = res
            k = (c + 0.0, r)
            if best is None or k < best[0]: best = (k, r, line)
        if best and tried > 60: break
    if best is None: raise SystemExit("STOP (HQ T-034, 3): no channel <= %d cells (cut <= %d, tunnel <= %d) from the water of the bowl to a grotto" % (CH_MAX, CUT_MAX, TUNNEL_MAX))
    _, rect, line = best
    W = gr.Wl
    cut = max(gr.g(x, z) - W for (x, z), d, tun in [((c[0], c[1]), dd, t) for (c, dd, t) in line] if not tun)
    out = dict(key=gr.key + src, W=W, rect=list(rect), line=[[c[0], c[1], d[0], d[1], int(t)] for (c, d, t) in line],
               length=len(line), tunnel=sum(1 for l in line if l[2]), cut=int(cut), sites=len(sites), tried=tried)
    json.dump(out, open(cp, "w"))
    return gr, out


if __name__ == "__main__":
    gr, p = plan()
    print("grotto", p["rect"], "channel", p["length"], "tunnel", p["tunnel"], "cut", p["cut"], "sites", p["sites"], "tried", p["tried"])
    print("from", p["line"][0], "to", p["line"][-1])


def plan_png(gr, p, path):
    """the plan for HQ: the ground (shade), the water of the bowl (blue; the boat water brighter), the banned cells (red: pools and their
    rings, the boardwalk, the climb, the hut), the places + seam (outline), the grotto (its rect, the ledge), the channel (open: cyan,
    tunnel: violet), the numbers"""
    from PIL import Image, ImageDraw
    ban = banned(gr); bw = boat_water(gr, ban)
    S = 4; x1, z1, x2, z2 = BOX
    img = Image.new("RGB", ((x2 - x1 + 1) * S, (z2 - z1 + 1) * S + 90), (20, 20, 24)); d = ImageDraw.Draw(img)
    W = gr.Wl
    for z in range(z1, z2 + 1):
        for x in range(x1, x2 + 1):
            y = gr.g(x, z); v = int(np.clip(40 + (y - W + 10) * 4, 25, 235)); col = (v, v, v - 10 if v > 10 else v)
            if gr.wet(x, z) and gr.w(x, z) <= W: col = (60, 110, 210) if (x, z) in bw else (40, 70, 140)
            if (x, z) in ban: col = (min(255, col[0] // 2 + 120), col[1] // 2, col[2] // 2)
            if not in_places(x, z): col = tuple(int(c * 0.7) for c in col)
            d.rectangle([(x - x1) * S, (z - z1) * S, (x - x1) * S + S - 1, (z - z1) * S + S - 1], fill=col)
    for k, r in PLOTS.items():
        d.rectangle([(r[0] - x1) * S, (r[1] - z1) * S, (r[2] - x1 + 1) * S, (r[3] - z1 + 1) * S], outline=(240, 200, 60))
        d.rectangle([(r[0] - SEAM - x1) * S, (r[1] - SEAM - z1) * S, (r[2] + SEAM - x1 + 1) * S, (r[3] + SEAM - z1 + 1) * S], outline=(150, 120, 40))
        d.text(((r[0] - x1) * S + 3, (r[1] - z1) * S + 3), k, fill=(240, 200, 60))
    gx1, gz1, gx2, gz2 = p["rect"]
    d.rectangle([(gx1 - x1) * S, (gz1 - z1) * S, (gx2 - x1 + 1) * S, (gz2 - z1 + 1) * S], outline=(120, 255, 120), width=2)
    if "ledge" in p:
        lx1, lz1, lx2, lz2 = p["ledge"]
        d.rectangle([(lx1 - x1) * S, (lz1 - z1) * S, (lx2 - x1 + 1) * S, (lz2 - z1 + 1) * S], fill=(150, 200, 120))
    for (x, z, dx, dz, t) in p["line"]:
        px, pz = -dz, dx
        for k in (-1, 0, 1):
            cx, cz = x + k * px, z + k * pz
            d.rectangle([(cx - x1) * S, (cz - z1) * S, (cx - x1) * S + S - 1, (cz - z1) * S + S - 1], fill=(170, 90, 230) if t else (60, 220, 230))
    txt = ("Grotto of the Jelly (T-034): grotto %s (green), W %d, ledge %s; channel %d cells (open cyan, tunnel %d violet), cut <= %d;"
           % (p["rect"], W, p.get("ledge"), p["length"], p["tunnel"], p["cut"]))
    d.text((6, (z2 - z1 + 1) * S + 6), txt, fill=(230, 230, 230))
    d.text((6, (z2 - z1 + 1) * S + 24), "blue: water of the bowl (bright: a boat reaches it from the hut's pier); red: banned (heads' pools + rings, boardwalk, climb, hut);", fill=(200, 200, 200))
    d.text((6, (z2 - z1 + 1) * S + 42), "yellow: places fens / grotto (+16 seam, dark outside: the open cut stays inside). Stop: channel > %d, cut > %d, no grotto 8/6." % (CH_MAX, CUT_MAX), fill=(200, 200, 200))
    os.makedirs(os.path.dirname(path), exist_ok=True); img.save(path)
