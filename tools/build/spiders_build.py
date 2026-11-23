"""T-032: the blocks of the Spider Thicket (Паучья чаща, Р1): the forest of the edge (poplars of three colours and dark oaks, white bands,
rare web, small cocoons), the deep (dark oak and oak trunks, a canopy of dark oak leaves with layers of web inside: mushroom stem and
cobweb), the web by density, the hanging cocoons on chains, the 3 cocoons with remains (a barrel inside), the live cocoon, the trails,
the trip wires, the fallen giant with the butt's root plate, the nest (the pit under a web lid, the drop, the burrow of roots).
Called by tools/build/r1_spiders.py; `ctx` holds the grids, the relief and the plan."""
import math
import numpy as np
from lib import B, Mix, h as hsh, slab, stairs
import spiders_plan as P

LEAF = "minecraft:dark_oak_leaves[distance=1,persistent=true,waterlogged=false]"
POPLAR_LEAVES = Mix({"yellow_poplar_leaves[distance=1,persistent=true,waterlogged=false]": 40, "orange_poplar_leaves[distance=1,persistent=true,waterlogged=false]": 35,
                     "red_poplar_leaves[distance=1,persistent=true,waterlogged=false]": 25}, 3201)
DLOG = "minecraft:dark_oak_log[axis=y]"
OLOG = "minecraft:oak_log[axis=y]"
PLOG = "minecraft:poplar_log[axis=y]"
WEB = "minecraft:cobweb"
STEM = "minecraft:mushroom_stem[down=true,east=true,north=true,south=true,up=true,west=true]"
WOOL = "minecraft:white_wool"
COCOON = Mix({STEM: 60, WOOL: 30, WEB: 10}, 3202)
GROUND_DEEP = Mix({"podzol[snowy=false]": 35, "coarse_dirt": 30, "rooted_dirt": 30, "bone_block[axis=y]": 5}, 3203)
GROUND_MID = Mix({"podzol[snowy=false]": 35, "coarse_dirt": 25, "grass_block[snowy=false]": 30, "rooted_dirt": 10}, 3204)
GROUND_EDGE = Mix({"grass_block[snowy=false]": 70, "podzol[snowy=false]": 20, "coarse_dirt": 10}, 3205)
STEEP = Mix({"tuff": 40, "coarse_dirt": 35, "stone": 25}, 3206)
TRAIL = Mix({"coarse_dirt": 55, "dirt_path": 25, "rooted_dirt": 20}, 3207)             # the trail of the victims: trodden earth
ANIMAL = Mix({"coarse_dirt": 60, "dirt_path": 25, "podzol[snowy=false]": 15}, 3208)     # the animal trail (HQ T-032: coarse dirt, path in patches)
ROOT_SLAB = "minecraft:dark_oak_slab[type=bottom,waterlogged=false]"   # the half steps: root steps
ROOTS = "minecraft:mangrove_roots[waterlogged=false]"
WALL = Mix({"rooted_dirt": 55, "tuff": 45}, 3209)
FLOOR = Mix({"rooted_dirt": 45, "tuff": 25, "coarse_dirt": 20, "bone_block[axis=y]": 10}, 3210)
LID = Mix({STEM: 55, WOOL: 30, "rooted_dirt": 15}, 3211)
GIANT = Mix({"dark_oak_wood[axis=z]": 80, "stripped_dark_oak_wood[axis=z]": 20}, 3212)
LITTER = ["minecraft:leaf_litter[facing=%s,segment_amount=%d]" % (f, n) for f in ("north", "east", "south", "west") for n in (1, 2, 3, 4)]
CHAIN = "minecraft:iron_chain[axis=y,waterlogged=false]"
ROT = ["north", "east", "south", "west"]
DXZ = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}

class Ctx:
    def __init__(self, gr, rl, pl):
        self.gr, self.rl, self.pl = gr, rl, pl; self.T = rl["T"]
        self.keep = set()        # cells (x, z) where nothing grows and no web lies on the walking height: trails, clearings, nest, giant
        self.walk = {}           # (x, z) -> surface height in half blocks: the trails and the clearings (feet = v / 2 + 1)
    def g(self, x, z): return int(self.T[P.ix(self.gr, x, z)])
    def ed(self, x, z): return P.edge_dist(x, z)
    def inner(self, x, z): return P.in_place(x, z, 0)

# ---------------------------------------------------------------- ground, trails
def ground(b, c):
    """the top block of every column of the place (not the pit, not the trails): the card's palette by band; steep: tuff and coarse dirt"""
    T = c.T; gr = c.gr
    for i, j in zip(*np.nonzero(gr["inner"] & ~c.rl["pit"] & ~c.rl["flatm"])):
        x, z = j + gr["x1"], i + gr["z1"]; y = int(T[i, j])
        if b.get(x, y, z) is not None: continue
        nb = [T[i + a, j + d] for a, d in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        steep = max(abs(v - y) for v in nb) >= 3
        e = c.ed(x, z)
        if steep: s = STEEP
        elif e <= 4: s = GROUND_EDGE
        elif e <= P.EDGE: s = GROUND_MID
        else: s = GROUND_DEEP
        # bone patches in the deep (noise 3 x 3 clumps)
        if e > P.EDGE + 2 and not steep and hsh(x // 3, 7, z // 3, 3213) < 0.12: b.set(x, y, z, "minecraft:bone_block[axis=y]")
        else: b.set(x, y, z, s)
        if e <= 6 and not steep and b.get(x, y + 1, z) is None and hsh(x, 1, z, 3214) < 0.35 - e * 0.04:
            b.set(x, y + 1, z, LITTER[int(hsh(x, 2, z, 3215) * len(LITTER))])

def trails(b, c, meta):
    """the trail of the victims and the walk to the burrow (coarse dirt, path patches, rooted dirt; the half steps are dark oak slabs:
    root steps), the animal trail (coarse dirt, path in patches): the top block at T, a slab over it on an odd level"""
    for part, pal in (("ta", ANIMAL), ("tv", TRAIL), ("ts", TRAIL)):
        for (x, z), v in c.pl[part].items():
            y = v // 2
            b.set(x, y, z, pal)
            if v % 2: b.set(x, y + 1, z, ROOT_SLAB)
            for yy in range(y + 1 + v % 2, y + 4):
                if b.get(x, yy, z) is None: b.set(x, yy, z, "minecraft:air")
            c.walk[(x, z)] = v
    meta["trails"] = dict(victims=len(c.pl["tv"]), animal=len(c.pl["ta"]), spur=len(c.pl["ts"]))

# ---------------------------------------------------------------- trees
def white_band(b, x, y, z, salt, p):
    if hsh(x, y // 3, z, salt) < p: b.set(x, y, z, WOOL if hsh(x, y, z, salt + 1) < 0.5 else STEM)

def poplar(b, x, gy, z, hh, salt, lo):
    """a poplar of the edge (grove_build.poplar with three leaf colours, no shelf mushrooms), white bands on the trunk"""
    for y in range(lo - 1, gy + hh): b.set(x, y, z, PLOG)
    for y in range(gy + 1, gy + hh - 1): white_band(b, x, y, z, salt, 0.35)
    y0 = gy + int(hh * 0.33); y1 = gy + hh + 2; mid = gy + hh * 0.58
    for y in range(y0, y1 + 1):
        t = (y - mid) / ((y1 - y0) / 2 + 0.5)
        rr = 2.3 * math.sqrt(max(0.0, 1 - t * t)) + 0.3
        for a in range(-3, 4):
            for cc in range(-3, 4):
                if (a or cc) and math.hypot(a, cc) <= rr and hsh(x + a, y, z + cc, salt) < 0.92 and b.get(x + a, y, z + cc) is None: b.set(x + a, y, z + cc, POPLAR_LEAVES)
        if y >= gy + hh: b.set(x, y, z, POPLAR_LEAVES)
    return dict(x=x, z=z, h=hh, kind="poplar")

def dark_oak(b, x, gy, z, hh, salt, lo, band=0.3, crown=True):
    """a dark oak 2 x 2 (x..x+1, z..z+1), white bands; the crown (edge) is a flat wide disc; in the deep the canopy is the crown"""
    for a in (0, 1):
        for cc in (0, 1):
            for y in range(lo - 1, gy + hh): b.set(x + a, y, z + cc, DLOG)
            for y in range(gy + 1, gy + hh - 2): white_band(b, x + a, y, z + cc, salt + a * 2 + cc, band)
    if crown:
        for y in range(gy + hh - 2, gy + hh + 2):
            rr = 3.4 if y < gy + hh + 1 else 2.2
            for a in range(-4, 6):
                for cc in range(-4, 6):
                    if math.hypot(a - 0.5, cc - 0.5) <= rr and b.get(x + a, y, z + cc) is None and hsh(x + a, y, z + cc, salt + 1) < 0.9:
                        b.set(x + a, y, z + cc, LEAF)
    return dict(x=x, z=z, h=hh, kind="dark_oak")

def free_spot(b, c, x, z, r=1, up=6):
    if not all(c.inner(x + a, z + cc) for a in range(-r, r + 2) for cc in range(-r, r + 2)): return False
    for a in range(-r, r + 2):
        for cc in range(-r, r + 2):
            q = (x + a, z + cc)
            if q in c.keep or q in c.walk: return False
    gy = c.g(x, z)
    return not any(b.get(x + a, gy + yy, z + cc) is not None for a in (-1, 0, 1, 2) for cc in (-1, 0, 1, 2) for yy in range(1, up))

def canopy_base(c):
    """the canopy's bottom per column: the highest ground within 2 + 8, never under the ground + 8 nor over + 14; smoothed (HQ T-032:
    the crowns grow into a canopy 8..14 over the ground along the slope)"""
    T = np.where(c.rl["pit"], c.gr["before"], c.T).astype(float); m = T.copy()       # over the pit: its lid (the natural ground)
    for _ in range(2):
        p = np.pad(m, 1, mode="edge"); m = np.maximum.reduce([m, p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]])
    base = m + 8
    for _ in range(3):
        p = np.pad(base, 1, mode="edge"); base = (base * 4 + p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]) / 8
    base = np.clip(np.round(base), T + 8, T + 14).astype(np.int32)
    return base

CANOPY_FROM = 6          # the continuous canopy covers the place from 6 inside the outline (the edge's inner half under the crowns)
CANOPY_T = 4             # its thickness (dark oak leaves; poplar leaves in the edge band)
def forest(b, c, meta):
    """the trees and the canopy: edge band (0..EDGE): poplars and dark oaks half and half on a jittered grid, their crowns; from
    CANOPY_FROM inward the canopy (CANOPY_T thick, its mid layer has mushroom stem patches: the web inside the canopy; poplar leaves in
    the edge band, dark oak leaves in the deep); deep trunks (dark oak 2 x 2 and oak 1 x 1) on a jittered grid of 5 reach into it"""
    gr = c.gr; T = c.T; cb = canopy_base(c); c.cb = cb
    trees = []
    xs = range(P.PLACE[0] + 1, P.PLACE[2], 5); zs = range(P.PLACE[1] + 1, P.PLACE[3], 5)
    for gx in xs:
        for gz in zs:
            x = gx + int(hsh(gx, 1, gz, 3220) * 4) - 1; z = gz + int(hsh(gx, 2, gz, 3221) * 4) - 1
            if not c.inner(x, z) or not c.inner(x + 1, z + 1): continue
            e = c.ed(x, z)
            if not free_spot(b, c, x, z, 0 if e > P.EDGE else 1, 4): continue
            sub = T[P.ix(gr, x, z)[0]:P.ix(gr, x, z)[0] + 2, P.ix(gr, x, z)[1]:P.ix(gr, x, z)[1] + 2]
            lo, gy = int(sub.min()), int(sub.max())
            if gy - lo > 3: continue
            k = len(trees)
            if e <= P.EDGE:
                if hsh(x, 3, z, 3222) < 0.6: trees.append(dark_oak(b, x, gy, z, 6 + int(hsh(x, 4, z, 3223) * 3), 3300 + k, lo, 0.3, crown=e < CANOPY_FROM))
                else: trees.append(poplar(b, x, gy, z, 11 + int(hsh(x, 5, z, 3224) * 5), 3300 + k, lo))
                if e >= CANOPY_FROM and trees[-1]["kind"] == "dark_oak":       # the trunk reaches the canopy
                    top = int(cb[P.ix(gr, x, z)]) + 1
                    for a in (0, 1):
                        for cc in (0, 1):
                            for y in range(gy, top): b.set(x + a, y, z + cc, DLOG)
            else:
                top = int(cb[P.ix(gr, x, z)]) + 1
                if hsh(x, 6, z, 3225) < 0.55:
                    for a in (0, 1):
                        for cc in (0, 1):
                            for y in range(lo - 1, top + 1): b.set(x + a, y, z + cc, DLOG)
                            for y in range(gy + 1, top - 1): white_band(b, x + a, y, z + cc, 3400 + k, 0.55)
                    trees.append(dict(x=x, z=z, kind="deep_dark_oak", top=top))
                else:
                    for y in range(c.g(x, z) - 1, top + 1): b.set(x, y, z, OLOG)
                    for y in range(c.g(x, z) + 1, top - 1): white_band(b, x, y, z, 3400 + k, 0.55)
                    trees.append(dict(x=x, z=z, kind="deep_oak", top=top))
    # the canopy
    nleaf = nstem = 0
    for i, j in zip(*np.nonzero(gr["inner"])):
        x, z = j + gr["x1"], i + gr["z1"]; e = c.ed(x, z)
        if e < CANOPY_FROM: continue
        y0 = int(cb[i, j])
        th = CANOPY_T if e > P.EDGE else CANOPY_T - 1
        for k in range(th):
            y = y0 + k
            if b.get(x, y, z) is not None and "leaves" not in b.get(x, y, z): continue
            if e > P.EDGE + 1 and k == 1 and hsh(x // 2, y, z // 2, 3226) < 0.45: b.set(x, y, z, STEM if hsh(x, y, z, 3227) < 0.7 else WOOL); nstem += 1
            else: b.set(x, y, z, LEAF if e > P.EDGE - 1 or hsh(x, y, z, 3228) < 0.35 else POPLAR_LEAVES); nleaf += 1
        # the web over the canopy (seen from the hills round: a grey-white shroud over the deep, thinning to the edge)
        yt = y0 + th; r = hsh(x, yt, z, 3229); pw = min(0.45, 0.05 + max(0, e - CANOPY_FROM) * 0.03)
        if b.get(x, yt, z) is None and b.get(x, yt - 1, z) is not None and "leaves" in b.get(x, yt - 1, z):
            if r < pw * 0.6: b.set(x, yt, z, WEB); nstem += 0
            elif r < pw: b.set(x, yt - 1, z, WOOL if hsh(x, 1, z, 3230) < 0.5 else STEM)
    meta["forest"] = dict(edge_poplars=sum(1 for t in trees if t["kind"] == "poplar"), edge_dark_oaks=sum(1 for t in trees if t["kind"] == "dark_oak"),
                          deep_dark_oaks=sum(1 for t in trees if t["kind"] == "deep_dark_oak"), deep_oaks=sum(1 for t in trees if t["kind"] == "deep_oak"),
                          canopy_leaves=nleaf, canopy_stem=nstem)
    return trees

def web(b, c, meta, trees):
    """cobweb by density from the edge to the centre: on the ground (feet level), between the trunks (strings at 2..5), under the canopy
    (hanging 1..2 under it); never on the walks and their head room (the bot); the small cocoons of the edge under the crowns"""
    gr = c.gr; n = dict(ground=0, mid=0, under=0, small=0)
    def dens(e): return 0.01 if e < 4 else 0.03 if e <= P.EDGE else min(0.16, 0.05 + (e - P.EDGE) * 0.006)
    def clear(x, z): return (x, z) not in c.keep and (x, z) not in c.walk
    for i, j in zip(*np.nonzero(gr["inner"] & ~c.rl["pit"])):
        x, z = j + gr["x1"], i + gr["z1"]; e = c.ed(x, z); gy = c.g(x, z)
        if not clear(x, z): continue
        d = dens(e)
        if hsh(x, 11, z, 3230) < d and b.get(x, gy + 1, z) in (None,) + tuple(LITTER): b.set(x, gy + 1, z, WEB); n["ground"] += 1
        if e > P.EDGE and hsh(x, 12, z, 3231) < d * 0.8:
            y = gy + 2 + int(hsh(x, 13, z, 3232) * 3)
            if b.get(x, y, z) is None: b.set(x, y, z, WEB); n["mid"] += 1
        if e >= CANOPY_FROM:
            y = int(c.cb[i, j]) - 1
            if hsh(x, 14, z, 3233) < d * 2.2 and b.get(x, y, z) is None and y > gy + 3:
                b.set(x, y, z, WEB); n["under"] += 1
                if hsh(x, 15, z, 3234) < 0.4 and b.get(x, y - 1, z) is None and y - 1 > gy + 3: b.set(x, y - 1, z, WEB)
    for t in trees:              # the small cocoons of the edge: a bundle 1 x 2 (wool over stem) stuck to the side of an edge tree's trunk
        if t["kind"] not in ("poplar", "dark_oak") or hsh(t["x"], 16, t["z"], 3235) > 0.5: continue
        w = 2 if t["kind"] == "dark_oak" else 1
        for (x, z) in ((t["x"] + w, t["z"]), (t["x"] - 1, t["z"]), (t["x"], t["z"] + w), (t["x"], t["z"] - 1)):
            if (x, z) in c.walk or (x, z) in c.keep or not c.inner(x, z): continue
            y = c.g(x, z) + 2 + int(hsh(x, 17, z, 3236) * 2)
            if b.get(x, y, z) is None and b.get(x, y + 1, z) is None:
                b.set(x, y, z, STEM); b.set(x, y + 1, z, WOOL); n["small"] += 1; break
    meta["web"] = n

# ---------------------------------------------------------------- cocoons
def cocoon_shape(kind):
    """cells (dx, dy, dz) of the 3 cocoon templates (2..3 high), dy from the bottom; the top cell is under the chain"""
    if kind == "a": return [(0, 0, 0), (0, 1, 0), (1, 1, 0), (0, 1, 1), (0, 2, 0)]                      # a spindle with a bulge
    if kind == "b": return [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (0, 0, 1), (0, 1, 1), (1, 1, 1), (0, 2, 0)]   # a sack
    return [(0, 0, 0), (0, 1, 0), (0, 2, 0), (1, 1, 0)]                                                   # c: a long one
def rot(dx, dz, r):
    for _ in range(r): dx, dz = -dz, dx
    return dx, dz
def hanging(b, c, meta):
    """15..20 cocoons on chains in the deep: bottom at ground + 3 (a player walks under), the chain up to the canopy; not over the walks;
    3 templates, turned 4 ways"""
    gr = c.gr; out = []
    cand = []
    for i, j in zip(*np.nonzero(gr["inner"] & ~c.rl["pit"])):
        x, z = j + gr["x1"], i + gr["z1"]
        if c.ed(x, z) < P.EDGE + 2 or (x, z) in c.walk: continue
        cand.append((hsh(x, 20, z, 3240), x, z))
    cand.sort()
    for _, x, z in cand:
        if len(out) >= 18: break
        if any(max(abs(x - o["x"]), abs(z - o["z"])) < 8 for o in out): continue
        kind = "abc"[len(out) % 3]; r = int(hsh(x, 21, z, 3241) * 4)
        cells = [(x + rot(dx, dz, r)[0], dy, z + rot(dx, dz, r)[1]) for (dx, dy, dz) in cocoon_shape(kind)]
        if any((cx, cz) in c.walk or (cx, cz) in c.keep or not c.inner(cx, cz) for (cx, dy, cz) in cells): continue
        gy = max(c.g(cx, cz) for (cx, dy, cz) in cells); y0 = gy + 3
        top = int(c.cb[P.ix(gr, x, z)]) - 1
        if top - (y0 + 2) < 1: continue
        if any(b.get(cx, y0 + dy, cz) not in (None, WEB) for (cx, dy, cz) in cells): continue
        for (cx, dy, cz) in cells: b.set(cx, y0 + dy, cz, COCOON)
        for y in range(y0 + 3, top + 1): b.set(x, y, z, CHAIN)
        out.append(dict(x=x, z=z, y=y0, kind=kind, rot=r))
    meta["cocoons"] = out
    return out

def remains(b, c, meta):
    """3 cocoons with remains lying on the ground by the trail of the victims (their chain broke): a shell 4 x 3 x 3 opened toward the
    trail (2 wide, 2 high), inside a barrel (loot r1/common, T-019) and a stand with leather rags (the datapack: spiders/gen/props); the
    cavity's floor at the trail's level"""
    pv = c.pl["pv"]; out = []
    picks = [int(len(pv) * f) for f in (0.2, 0.45, 0.7)]
    used = set()
    for n0 in picks:
        done = False
        for dn in sorted(range(-len(pv), len(pv)), key=abs):
            n = n0 + dn
            if not 2 <= n < len(pv) - 3 or done: continue
            x, z, v = pv[n]
            if v % 2: continue
            k = P.D.index((pv[n + 1][0] - x, pv[n + 1][1] - z))
            if P.D.index((x - pv[n - 1][0], z - pv[n - 1][1])) != k: continue
            # the side of the trail opposite to its second lane: the shell's mouth faces the trail
            sx, sz = P.side(k)
            if (x + sx, z + sz) not in c.walk: sx, sz = -sx, -sz
            fx, fz = P.D[k]
            y = v // 2
            for (lx, lz, off) in ((-sx, -sz, 0), (sx, sz, 1)):          # either side of the trail (off: past the second lane)
                shell = {}
                for a in (-1, 0, 1, 2):            # along the trail
                    for w in (1, 2, 3):            # away from the trail
                        shell[(a, w)] = (x + fx * a + lx * (w + off), z + fz * a + lz * (w + off))
                cells = list(shell.values())
                if any((q in c.walk) or (q in c.keep) or not c.inner(*q) or q in used for q in cells): continue
                hollow = [shell[(a, w)] for a in (0, 1) for w in (1, 2)]
                if any(c.g(*q) > y for q in hollow) or any(c.g(*q) > y + 2 or c.g(*q) < y - 4 for q in cells): continue
                if any(b.get(q[0], y + dy, q[1]) is not None for q in cells for dy in (1, 2, 3)): continue
                break
            else: continue
            for (a, w), (cx, cz) in shell.items():
                if c.g(cx, cz) <= y: b.set(cx, y, cz, "minecraft:rooted_dirt")
                for yy in range(c.g(cx, cz) + 1, y): b.set(cx, yy, cz, "minecraft:rooted_dirt")
                for dy in (1, 2, 3):
                    inside = a in (0, 1) and w == 2 and dy in (1, 2)
                    mouth = a in (0, 1) and w == 1 and dy in (1, 2)
                    if inside or mouth: b.set(cx, y + dy, cz, "minecraft:air"); continue
                    if y + dy <= c.g(cx, cz): continue                                                     # in the bank: the ground is the shell
                    if dy == 3 and (a in (-1, 2) or w in (1, 3)) and hsh(cx, y, cz, 3250) < 0.4: continue    # ragged top
                    b.set(cx, y + dy, cz, COCOON)
            bx, bz = shell[(1, 2)]; sxx, szz = shell[(0, 2)]
            b.set(bx, y + 1, bz, "minecraft:barrel[facing=%s,open=false]{LootTable:\"last_ember:chests/r1/common\"}" % ROT[(ROT.index(["east", "west", "south", "north"][k]) + 2) % 4] if False else
                  "minecraft:barrel[facing=up,open=false]{LootTable:\"last_ember:chests/r1/common\"}")
            b.set(bx, y + 2, bz, "minecraft:air")
            # a broken chain end on the top and bones by the mouth
            tx_, tz_ = shell[(0, 3)]
            b.set(tx_, y + 4, tz_, CHAIN)
            mx_, mz_ = shell[(2, 1)]
            if b.get(mx_, y + 1, mz_) in (None, "minecraft:air"): pass
            face = ["west", "east", "north", "south"][k]                 # the stand looks out of the mouth (toward the trail)
            yaw = {"south": 0, "west": 90, "north": 180, "east": -90}[{(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}[(-lx, -lz)]]
            out.append(dict(barrel=[bx, y + 1, bz], stand=[sxx, y + 1, szz], yaw=yaw, front=[x, z], v=v, n=n))
            used |= set(cells) | {(q[0] + a, q[1] + cc) for q in cells for a in (-3, 0, 3) for cc in (-3, 0, 3)}
            for q in cells: c.keep.add(q)
            done = True
        if not done: raise SystemExit("no place for a cocoon with remains near trail cell %d" % n0)
    meta["remains"] = out
    return out

def live_cocoon(b, c, meta):
    """the live cocoon at the pit's south wall, east of the trunk: lower than the others (its bottom at the eyes of one standing in the
    clearing), a light grey wool patch, on a chain to the canopy; the templates cocoon_live_closed | open (the datapack swaps them);
    Toivo's bow lies in the clearing (item_display, datapack)"""
    cx, cz = c.pl["cocoon"]; ex, ez = c.pl["pv"][-1][0], c.pl["pv"][-1][1]; v = c.pl["pv"][-1][2]
    feet = v // 2 + 1
    y0 = feet + 1
    closed, opened = {}, {}
    shape = [(0, 0, 0), (0, 1, 0), (0, 2, 0), (1, 0, 0), (1, 1, 0), (1, 2, 0), (0, 0, -1), (1, 1, -1), (0, 1, -1), (0, 3, 0), (1, 3, 0)]
    for (dx, dy, dz) in shape:
        q = (cx + dx, y0 + dy, cz + dz)
        s = COCOON.at(*q)
        if (dx, dy, dz) in ((0, 1, 0), (1, 2, 0)): s = "minecraft:light_gray_wool"          # the patch on the face toward the clearing
        if s == WEB: s = STEM
        closed[q] = s
        opened[q] = WEB if (dz == 0 and dy in (0, 1, 2) and hsh(*q, 3251) < 0.5) else ("minecraft:air" if dz == 0 and dy in (0, 1, 2) else s)
    for q, s in closed.items(): b.set(*q, s)
    top = int(c.cb[P.ix(c.gr, cx, cz)]) - 1
    for y in range(y0 + 4, max(top, y0 + 6) + 1): b.set(cx, y, cz, CHAIN)
    # the space under it: air down to the ground (the rim of the pit)
    for (dx, dz) in ((0, 0), (1, 0), (0, -1), (1, -1)):
        for y in range(c.g(cx + dx, cz + dz) + 1, y0):
            if b.get(cx + dx, y, cz + dz) is None: b.set(cx + dx, y, cz + dz, "minecraft:air")
    for q in ((cx, cz), (cx + 1, cz), (cx, cz - 1), (cx + 1, cz - 1)): c.keep.add(q)
    origin = (cx, y0, cz - 1)
    meta["live"] = dict(cells=[list(q) for q in closed], origin=list(origin), size=[2, 4, 2], clearing=[ex, feet, ez], bottom=y0,
                        bow=[cx + 0.5, feet + 0.03, cz + 1.6], toivo=[cx + 0.5, feet, cz + 1.5])
    return closed, opened, origin

# ---------------------------------------------------------------- the trip wires
def tripwires(b, c, meta):
    """3 places on the trail of the victims, out of the nest's zone (adventure there: shears could not cut them): a straight level
    stretch, the hooks on the two cells beside the trail on dark oak posts (their trunks go up into the canopy), the wire across both
    lanes at the feet; a fresh scratch (stripped dark oak) on the post; spread along the allowed part of the trail, >= 6 cells apart"""
    pv = c.pl["pv"]; out = []
    nx1, nz1, nx2, nz2 = c.pl["nest"]["r"]; gi = c.pl["giant"]
    cands = []
    for n in range(2, len(pv) - 2):
        x, z, v = pv[n]
        if v % 2: continue
        if nx1 - 10 <= x <= nx2 + 10 and z <= gi["zb"] + 9: continue
        k = P.D.index((pv[n + 1][0] - x, pv[n + 1][1] - z))
        if P.D.index((x - pv[n - 1][0], z - pv[n - 1][1])) != k: continue
        sx, sz = P.side(k)
        if (x + sx, z + sz) not in c.walk: sx, sz = -sx, -sz                  # the second lane (widened in the search's order)
        lanes = [(x, z), (x + sx, z + sz)]
        if any(c.walk.get(q) != v for q in lanes): continue
        h1 = (x - sx, z - sz); h2 = (x + 2 * sx, z + 2 * sz); p1 = (x - 2 * sx, z - 2 * sz); p2 = (x + 3 * sx, z + 3 * sz)
        y = v // 2 + 1
        if any(q in c.walk or q in c.keep or not c.inner(*q) for q in (h1, h2, p1, p2)): continue
        if any(c.g(*q) > v // 2 + 1 for q in (h1, h2)) or any(c.g(*q) > v // 2 + 2 for q in (p1, p2)): continue   # a hook may sit in the bank's top block
        if any(b.get(q[0], yy, q[1]) is not None for q in (h1, h2, p1, p2) for yy in range(y, y + 3)): continue
        if c.cb[P.ix(c.gr, *p1)] - y < 3: continue
        cands.append((n, x, z, v, sx, sz, lanes, h1, h2, p1, p2, y))
    if len(cands) < 3: raise SystemExit("only %d straight level stretches for the trip wires out of the nest's zone" % len(cands))
    lo, hi = cands[0][0], cands[-1][0]; picks = []
    for f in (0.1, 0.5, 0.9):
        t = lo + (hi - lo) * f
        for cd in sorted(cands, key=lambda q: abs(q[0] - t)):
            if all(abs(cd[0] - o[0]) >= 6 for o in picks) and all(max(abs(cd[1] - o[1]), abs(cd[2] - o[2])) >= 5 for o in picks): picks.append(cd); break
    if len(picks) < 3: raise SystemExit("the trip wires cannot be spread 6 cells apart (%d)" % len(picks))
    for (n, x, z, v, sx, sz, lanes, h1, h2, p1, p2, y) in sorted(picks):
        dir1 = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}[(sx, sz)]
        dir2 = {"east": "west", "west": "east", "south": "north", "north": "south"}[dir1]
        top = int(c.cb[P.ix(c.gr, *p1)]) + 1
        for (px, pz) in (p1, p2):
            for yy in range(min(c.g(px, pz) + 1, y), top + 1): b.set(px, yy, pz, DLOG)          # the post: from the ground (or the hook's level in the bank) up into the canopy
        for (hx, hz) in (h1, h2):
            for yy in range(c.g(hx, hz) + 1, y): b.set(hx, yy, hz, "minecraft:rooted_dirt")      # the hooks' cells raised to the trail
        b.set(p1[0], y, p1[1], "minecraft:stripped_dark_oak_log[axis=y]")                    # the scratch at the hook
        b.set(p1[0], y + 1, p1[1], "minecraft:stripped_dark_oak_log[axis=y]")
        b.set(h1[0], y, h1[1], "minecraft:tripwire_hook[attached=true,facing=%s,powered=false]" % dir1)
        b.set(h2[0], y, h2[1], "minecraft:tripwire_hook[attached=true,facing=%s,powered=false]" % dir2)
        ax = "east=true,west=true,north=false,south=false" if sx else "east=false,west=false,north=true,south=true"
        for (lx, lz) in lanes: b.set(lx, y, lz, "minecraft:tripwire[attached=true,disarmed=false,%s,powered=false]" % ax)
        for q in (h1, h2, p1, p2): c.keep.add(q)
        out.append(dict(n=n, hooks=[[h1[0], y, h1[1]], [h2[0], y, h2[1]]], wire=[[lx, y, lz] for (lx, lz) in lanes], f1=dir1, f2=dir2, ax=ax))
    meta["trips"] = out
    return out

# ---------------------------------------------------------------- the fallen giant and the nest
def giant(b, c, meta):
    """the fallen giant: a trunk 5 x 5 (disc r 2.5 across, dark oak wood with stripped patches) along z from the crown end (broken
    branches) to the butt; the butt's root plate (mangrove roots, rooted dirt clods) stands up across the trunk's end"""
    gi = c.pl["giant"]; cx = gi["x"]; cells = {}
    for z in range(gi["za"], gi["zb"] + 1):
        yc = P.trunk_y(gi, z)
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if (dx * dx + (dy + (yc - math.floor(yc)) - 0.5) ** 2) <= TR2:
                    cells[(cx + dx, int(math.floor(yc)) + dy, z)] = GIANT.at(cx + dx, int(math.floor(yc)) + dy, z)
    for q, s in cells.items(): b.set(*q, s)
    # the crown end: broken limbs
    yz = P.trunk_y(gi, gi["za"])
    for k, (dx, dy, dz, n) in enumerate(((-1, 2, -1, 5), (2, 1, -2, 4), (0, 3, 0, 4), (-3, 0, -1, 3))):
        for t in range(n):
            q = (cx + dx * (1 + t // 2) // 1, int(yz) + dy + t // 3, gi["za"] - 1 - t + dz)
            b.set(*q, "minecraft:dark_oak_log[axis=z]")
    # the root plate: a disc r 6 across the trunk at the butt (x-y plane, 2 thick), ragged, roots dangle under it
    yb = P.trunk_y(gi, gi["zb"]); zb = gi["zb"]
    for dx in range(-6, 7):
        for dy in range(-6, 7):
            d = math.hypot(dx, dy)
            if d > 6.2 or hsh(cx + dx, dy, zb, 3260) < (d - 4.5) * 0.35: continue
            y = int(yb) + dy
            if y <= c.g(cx + dx, zb): continue
            for z in (zb, zb + 1):
                if d < 2.6 and z == zb: continue
                b.set(cx + dx, y, z, ROOTS if hsh(cx + dx, y, z, 3261) < 0.65 else "minecraft:rooted_dirt")
    for dx in range(-6, 7, 2):
        n = 2 + int(hsh(cx + dx, 1, zb, 3262) * 3)
        for t in range(n):
            y = int(yb) - 6 + int(abs(dx) * 0.4) - t
            if y > c.g(cx + dx, zb + 2) + 2 and b.get(cx + dx, y, zb + 2) is None: b.set(cx + dx, y, zb + 2, ROOTS)
    meta["giant"] = dict(gi, cells=len(cells), yb=round(yb, 1))
TR2 = 2.5 ** 2 + 0.6

def nest(b, c, meta):
    """the pit: floor (T) of rooted dirt, tuff, coarse dirt, bone; walls (the ring 2 thick from the floor to the ground) rooted dirt and
    tuff with web; the web lid at the natural ground (mushroom stem, wool, rooted dirt) under the trunk, cobweb hanging under it; the
    drop 3 x 3 open, 3 layers of cobweb at its foot; clutches (turtle eggs, frogspawn: decor on the dry floor), bones, the Mistress's lair
    in the middle; the burrow of roots: a ledge along the north, west and south walls from the floor up to the exit by the live cocoon
    (its body rooted dirt and roots, dark oak slabs on the half steps, a railing of roots where it is 2 over the floor, the lid lifted
    over it into a hump of roots where the head room needs it)"""
    gr = c.gr; x1, z1, x2, z2 = c.pl["nest"]["r"]; F = c.pl["nest"]["floor"]; hole = c.pl["hole"]
    B4 = lambda x, z: P.B4(gr, x, z)
    def in_hole(x, z): return hole[0] <= x <= hole[2] and hole[1] <= z <= hole[3]
    lanes = P.lair_lanes(c.pl["lair"])
    ramp = {q: v for q, v in lanes.items() if x1 <= q[0] <= x2 and z1 <= q[1] <= z2}
    for x in range(x1 - 2, x2 + 3):
        for z in range(z1 - 2, z2 + 3):
            inside = x1 <= x <= x2 and z1 <= z <= z2
            if not inside:
                if (x, z) in lanes or (x, z) in c.walk: continue
                for y in range(F - 2, B4(x, z)): b.set(x, y, z, WALL)
                continue
            for y in range(F - 2, F + 1): b.set(x, y, z, FLOOR)
            top = B4(x, z)
            if (x, z) in ramp:
                v = ramp[(x, z)]; y = v // 2
                for yy in range(F + 1, y + 1): b.set(x, yy, z, "minecraft:rooted_dirt" if (x + yy + z) % 3 else ROOTS)
                if v % 2: b.set(x, y + 1, z, ROOT_SLAB)
                feet = y + 1 + (v % 2) * 0.5
                ceil = int(math.ceil(feet + LAIR_ROOM))
                for yy in range(y + 1 + v % 2, max(top, ceil)): b.set(x, yy, z, "minecraft:air")
                if ceil > top:                                    # the hump of roots over the ledge (the lid is too low there)
                    for yy in range(max(top, y + 1 + v % 2), ceil): b.set(x, yy, z, "minecraft:air")
                    b.set(x, ceil, z, ROOTS)
                    if hsh(x, ceil, z, 3271) < 0.5: b.set(x, ceil + 1, z, ROOTS)
                else: b.set(x, top, z, ROOTS if hsh(x, top, z, 3271) < 0.6 else LID)
                continue
            if in_hole(x, z):
                for yy in range(F + 1, top + 1): b.set(x, yy, z, "minecraft:air")
            else:
                for yy in range(F + 1, top): b.set(x, yy, z, "minecraft:air")
                b.set(x, top, z, LID)
                if hsh(x, 30, z, 3272) < 0.25 and top - 1 > F + 7: b.set(x, top - 1, z, WEB)
    # the railing of roots on the ledge's open side, 1 high, where the ledge is 2 over the floor
    for (x, z), v in ramp.items():
        if v - 2 * F < 4: continue
        for (a, cc) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + a, z + cc)
            if q in ramp or not (x1 <= q[0] <= x2 and z1 <= q[1] <= z2) or in_hole(*q): continue
            b.set(x, v // 2 + 1 + (v % 2), z, ROOTS) if False else b.set(q[0], v // 2 + 1, q[1], ROOTS)
            for yy in range(F + 1, v // 2 + 1):
                if b.get(q[0], yy, q[1]) in (None, "minecraft:air") and hsh(q[0], yy, q[1], 3277) < 0.3: b.set(q[0], yy, q[1], ROOTS)   # roots hanging off the ledge
    # the web on the walls (inside face) and in the corners
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            if (x, z) in ramp or in_hole(x, z): continue
            if x in (x1, x2) or z in (z1, z2) or any(q in ramp for q in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1))):
                for y in range(F + 2, B4(x, z) - 1):
                    if b.get(x, y, z) in (None, "minecraft:air") and hsh(x, y, z, 3273) < 0.15: b.set(x, y, z, WEB)
    # the cobweb at the foot of the drop: 3 layers
    for x in range(hole[0], hole[2] + 1):
        for z in range(hole[1], hole[3] + 1):
            for y in (F + 1, F + 2, F + 3): b.set(x, y, z, WEB)
            b.set(x, F, z, "minecraft:rooted_dirt")
    # the lair of the Mistress (the middle, west of the drop): a mat of wool and stem
    mx, mz = (x1 + x2) // 2 - 1, (z1 + z2) // 2
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            if not in_hole(mx + dx, mz + dz) and (mx + dx, mz + dz) not in ramp:
                b.set(mx + dx, F, mz + dz, WOOL if abs(dx) + abs(dz) <= 2 else STEM)
    # clutches and bones by the walls; the floor in the middle stays clear for the fight
    n_e = 0
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            if (x, z) in ramp or in_hole(x, z) or abs(x - mx) <= 3 and abs(z - mz) <= 3: continue
            near_wall = min(x - x1, x2 - x, z - z1, z2 - z) <= 1 or any(q in ramp for q in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)))
            r = hsh(x, 40, z, 3274)
            if b.get(x, F + 1, z) not in (None, "minecraft:air"): continue
            if near_wall and r < 0.12: b.set(x, F + 1, z, "minecraft:turtle_egg[eggs=%d,hatch=0]" % (1 + int(hsh(x, 41, z, 3275) * 4))); n_e += 1
            elif near_wall and r < 0.18: b.set(x, F + 1, z, "minecraft:frogspawn"); n_e += 1
            elif r < 0.24: b.set(x, F, z, "minecraft:bone_block[axis=%s]" % "xyz"[int(hsh(x, 42, z, 3276) * 3)])
            elif r < 0.27 and not near_wall: b.set(x, F + 1, z, WEB)
    meta["nest"] = dict(r=[x1, z1, x2, z2], floor=F, hole=list(hole), lair_mid=[mx, F + 1, mz], clutches=n_e, ramp=len(ramp))
    return ramp
LAIR_ROOM = 3

def burrow(b, c, meta):
    """the burrow's mouth outside the pit's south wall (T at the ledge's level there): rooted dirt, an arch of roots over it (the posts
    at its sides, the lintel at feet + 3)"""
    gr = c.gr; la = c.pl["lair"]; x1, z1, x2, z2 = c.pl["nest"]["r"]
    lanes = P.lair_lanes(la)
    out = [(q, v) for q, v in lanes.items() if not (x1 <= q[0] <= x2 and z1 <= q[1] <= z2)]
    for (x, z), v in out:
        y = v // 2; b.set(x, y, z, "minecraft:rooted_dirt")
        if v % 2: b.set(x, y + 1, z, ROOT_SLAB)
        for yy in range(y + 1 + v % 2, y + 4): b.set(x, yy, z, "minecraft:air")
        c.walk[(x, z)] = v
    ex, ez = la["exit"]; y = la["ve"] // 2
    for px in (ex - 1, ex + 2):
        if (px, ez) in c.walk: continue
        for yy in range(c.g(px, ez) + 1, y + 4): b.set(px, yy, ez, ROOTS)
    for x in range(ex - 1, ex + 3): b.set(x, y + 4, ez, ROOTS); b.set(x, y + 4, ez - 1, ROOTS)
    meta["burrow"] = dict(exit=[ex, ez], cut=la["cut"], cells=len(la["path"]), ledge_top=la["ve"] / 2 + 1)
