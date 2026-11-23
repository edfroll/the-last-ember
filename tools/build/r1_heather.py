#!/usr/bin/env python3
"""T-031: the Village of Heather (Деревня Вереск) and the Dragon Ridge (Р1) on the places `heather` and `dragon_ridge` (+ their seams).

  python3 tools/build/r1_heather.py         -> server/build/r1/heather_terrain.bin (tools/terrain.sh apply), heather.txt (tools/blockwriter.sh
                                               apply), heather.json (points for the tests, the bot and the datapack), docs/reports/T-031/
                                               heather_plan.png, structure/heather/head.nbt, sword_lo.nbt, sword_hi.nbt, datapack
                                               function/heather/gen/* and dialog/heather/* (tools/build/heather_dp.py), the zone lines
  python3 tools/build/r1_heather.py plan    only the plan (needs server/build/r1/heather_pre.bin: the scan of the places now)
Inputs: server/build/r1/base.bin, terrain.bin (the frame), heather_pre.bin (scan of the places now; the first one is kept as the ground
before the places in heather_before.npz).

Layout (HQ T-031, 1): the village on the natural shelf over the brook (the brook stays), the bridge from the pad of bonfire 9, the street
(3 wide, half a block per step, a cut <= 4, a fill on walls <= 8) to the square and up to the church terrace (the highest, on the slope
under the ridge); house terraces, the mill, the gardens on <= 8 of cut/fill with 1:1 banks or retaining walls; the ridge follows the
massif (a crest with vertebrae on top), the head-cliff on its east end on a mound, the trail from the church along the seams to the
mouth. Re-run: the same places, 0 columns changed."""
import json, math, os, re, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, write_grid, NONE
from lib import B, Mix, h as hsh, stairs, slab, lantern
import heather_plan as P
import heather_build as HB
import heather_ridge as HR
from heather_plan import ix

ROOT = P.ROOT; OUT = P.OUT
DP = os.path.join(ROOT, "datapack/data/last_ember")
STR = os.path.join(DP, "structure/heather")
S_GRASS, S_FOREST, S_ROCK = 1, 2, 10
R_STONE = 0
WALL_AT = 3                    # a flat whose neighbour lies more than this lower gets a retaining wall (else a 1:1 fill, at most 4 cells)
FILL_REACH = 4
TRAIL = Mix({"coarse_dirt": 40, "gravel": 20, "tuff": 25, "cobblestone": 15}, 3401)
SQUARE = Mix({"cobblestone": 45, "gravel": 25, "mossy_cobblestone": 15, "coarse_dirt": 15}, 3402)

# ---------------------------------------------------------------- relief
def relief(gr, pl):
    """T: the ground top per column after the places; flats {(x, z): v (half blocks)}: the church terrace, the square, the houses, the
    plain terraces, the street, the trail; the head mound; 1:1 banks round the flats (cuts full, fills <= FILL_REACH cells) or a
    retaining wall where the ground beside a flat lies more than WALL_AT lower"""
    bf = gr["before"]; T = bf.copy()
    flat = {}; kind = {}
    def rect(r, v, k):
        for x in range(r[0], r[2] + 1):
            for z in range(r[1], r[3] + 1): flat[(x, z)] = v; kind[(x, z)] = k
    rect(pl["church"], 2 * pl["cL"], "church"); rect(pl["square"], 2 * pl["sL"], "square")
    for h_ in pl["houses"]:
        rect(h_["r"], 2 * h_["L"], "house")
        for q in h_.get("apron", []):
            if q not in flat: flat[q] = 2 * h_["L"]; kind[q] = "apron"
    for k, q in pl["plain"].items():
        if q["L"] is not None: rect(q["r"], 2 * q["L"], k)
    for q, v in pl["surf"].items(): flat[q] = v; kind[q] = "street"
    for q, v in pl["tsurf"].items():
        if q not in flat: flat[q] = v; kind[q] = "trail"
    for (x, z), v in flat.items(): T[ix(gr, x, z)] = v // 2
    # the head mound (its own 1:1 banks)
    mound = np.zeros(T.shape, bool)
    for (x, z), t in pl["mound"].items():
        if (x, z) in flat: continue
        T[ix(gr, x, z)] = t; mound[ix(gr, x, z)] = True
    # retaining walls
    wall = {}; walled = set()
    for (x, z), v in flat.items():
        for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + a, z + c)
            if q in flat or P.on_pad(*q) or not P.in_place(*q) or gr["wet"][ix(gr, *q)] or (q[0], q[1]) in pl["deck"]: continue
            if mound[ix(gr, *q)]: continue
            if P.B4(gr, *q) < v // 2 - WALL_AT: walled.add((x, z)); wall[q] = max(wall.get(q, -999), v // 2)
    for q, y in wall.items(): T[ix(gr, *q)] = y
    src = np.full(T.shape, -999); srcu = np.full(T.shape, 9999)
    for (x, z), v in flat.items():
        srcu[ix(gr, x, z)] = (v + 1) // 2
        if (x, z) not in walled: src[ix(gr, x, z)] = v // 2
    for q, y in wall.items(): srcu[ix(gr, *q)] = y
    up, low = srcu.copy(), src.copy()
    for k in range(16):
        pu = np.pad(up, 1, constant_values=9999); pl_ = np.pad(low, 1, constant_values=-999); mu = up.copy(); ml = low.copy()
        for dz in (0, 1, 2):
            for dx in (0, 1, 2):
                mu = np.minimum(mu, pu[dz:dz + T.shape[0], dx:dx + T.shape[1]] + 1)
                if k < FILL_REACH: ml = np.maximum(ml, pl_[dz:dz + T.shape[0], dx:dx + T.shape[1]] - 1)
        up, low = mu, ml
    fl = np.zeros(T.shape, bool)
    for (x, z) in flat: fl[ix(gr, x, z)] = True
    wm = np.zeros(T.shape, bool)
    for q in wall: wm[ix(gr, *q)] = True
    deckm = np.zeros(T.shape, bool)
    for q in pl["deck"]: deckm[ix(gr, *q)] = True
    cone = gr["place"] & ~fl & ~gr["pad"] & ~wm & ~mound & ~gr["wet"] & ~deckm
    T = np.where(cone, np.clip(T, low, up), T)
    T = np.where(gr["pad"], bf, T)
    return dict(T=T, flat=flat, kind=kind, flatm=fl, wall=wall, wallm=wm, mound=mound)

def checks(gr, pl, rl):
    """HQ T-031, 1: the stop conditions and the numbers for the report"""
    T, bf = rl["T"], gr["before"]
    out = {}
    def mx(cells): return int(max(abs(int(T[ix(gr, *q)]) - int(bf[ix(gr, *q)])) for q in cells)) if cells else 0
    def rc(r): return [(x, z) for x in range(r[0], r[2] + 1) for z in range(r[1], r[3] + 1)]
    out["church"] = mx(rc(pl["church"])); out["square"] = mx(rc(pl["square"]))
    out["houses"] = max(mx(rc(h_["r"])) for h_ in pl["houses"])
    out["plain"] = max(mx(rc(q["r"])) for q in pl["plain"].values() if q["L"] is not None)
    for k in ("church", "square", "houses", "plain"):
        if out[k] > P.MAX_EARTH: raise SystemExit("STOP (HQ T-031, 1): %s cut/fill %d > %d" % (k, out[k], P.MAX_EARTH))
    st = [(v / 2 - int(bf[ix(gr, *q)])) for q, v in pl["surf"].items()]          # the walked surface (a slab: +0.5) to the ground
    out["street_cut"] = -min(st); out["street_fill"] = max(st)
    if out["street_cut"] > P.STREET_CUT: raise SystemExit("STOP (HQ T-031, 1): the street cuts %.1f" % out["street_cut"])
    hd = [t - P.B4(gr, x, z) for (x, z), t in pl["mound"].items() if P.in_rect(P.HEAD, x, z)]
    out["head_fill_mound"] = max(hd) if hd else 0
    _, hm = HR.skull_cells()
    out["head_fill_top"] = max(y - P.B4(gr, x, z) for (x, z), y in hm["body"].items())   # the body of the head (mound + skull, not the horns and fins) over the natural ground
    if out["head_fill_top"] > 50: raise SystemExit("STOP (HQ T-031, 1): the head needs %d of fill" % out["head_fill_top"])
    hx1, hz1, hx2, hz2 = P.HEAD
    if hx1 < P.RIDGE[0] + 3 or hx2 > P.RIDGE[2] - 3 or hz1 < P.RIDGE[1] + 3 or hz2 > P.RIDGE[3] - 3 + 9:
        raise SystemExit("STOP (HQ T-031, 1): the head does not fit the place dragon_ridge with 3 to spare")
    tr = [(v / 2 - int(bf[ix(gr, *q)])) for q, v in pl["tsurf"].items()]
    out["trail_cut"] = -min(tr); out["trail_fill"] = max(tr)
    if out["trail_cut"] > 8: raise SystemExit("STOP (HQ T-031, 1): the trail cuts the massif %d" % out["trail_cut"])
    bad = [q for q in pl["tsurf"] if not P.in_place(*q)]
    if bad: raise SystemExit("STOP (HQ T-031, 1): the trail needs columns outside both places and their seams: %s" % bad[:5])
    out["street_len"] = len(pl["street"]); out["trail_len"] = len(pl["trail"]); out["bridge"] = len(pl["deck"]) // 3
    out["changed"] = int(((T != bf) & gr["place"]).sum())
    return out

# ---------------------------------------------------------------- the bridge, the street, the square, the trail
def bridge(b, gr, pl, meta):
    """the deck (spruce planks, spruce slabs on the half steps) on dark oak beams x 68 / 72 with rails of dark oak fence, piers of dark
    oak logs down to the bed every 4 rows; the sign «Вереск» at the south end, two lanterns on the end posts"""
    zs = sorted({z for (x, z) in pl["deck"]}, reverse=True)
    for z in zs:
        v = pl["deck"][(70, z)]; y = v // 2
        for x in range(P.BRIDGE_X[0], P.BRIDGE_X[1] + 1):
            b.set(x, y, z, "minecraft:spruce_planks")
            if v % 2: b.set(x, y + 1, z, "minecraft:spruce_slab[type=bottom,waterlogged=false]")
            for yy in range(y + 1 + (v % 2), y + 5): b.set(x, yy, z, "minecraft:air")
        top = y + (1 if v % 2 else 0)
        for x in (P.BRIDGE_X[0] - 1, P.BRIDGE_X[1] + 1):
            b.set(x, top, z, "minecraft:dark_oak_log[axis=z]")
            b.set(x, top + 1, z, "minecraft:dark_oak_fence")
            if (z - zs[0]) % 4 == 0 or z == zs[-1]:
                lo = int(gr["before"][ix(gr, x, z)])
                for yy in range(lo, top): b.set(x, yy, z, "minecraft:dark_oak_log[axis=y]")
                b.set(x, top + 1, z, "minecraft:dark_oak_log[axis=y]"); b.set(x, top + 2, z, "minecraft:dark_oak_fence")
    z0 = zs[0]; y0 = pl["deck"][(70, z0)] // 2 + (pl["deck"][(70, z0)] % 2)
    b.set(P.BRIDGE_X[1] + 1, y0 + 3, z0, "minecraft:dark_oak_fence")
    b.set(P.BRIDGE_X[1] + 1, y0 + 4, z0, lantern())
    # the sign standing on the west end post, facing south (to the pad); the pad itself is never written
    b.set(P.BRIDGE_X[0] - 1, y0 + 2, z0, 'minecraft:dark_oak_sign[rotation=0,waterlogged=false]' + HB.sign_nbt(["", "Вереск", "", ""]))
    meta["bridge"] = dict(z=[zs[-1], zs[0]], sign=[P.BRIDGE_X[0] - 1, y0 + 2, z0], north=[70, zs[-1]], south_y=y0)

def surface_walks(b, gr, pl, rl, meta):
    """the street (gravel, coarse dirt, cobble; cobblestone slabs on the half steps), the square (cobble), the trail (coarse dirt, tuff;
    tuff slabs), the terraces' tops, the retaining walls with parapets; 3 of air over every walked cell"""
    T = rl["T"]
    for (x, z), v in rl["flat"].items():
        k = rl["kind"][(x, z)]; y = v // 2
        if k in ("house", "church"): continue
        if k == "street": b.set(x, y, z, HB.STREET)
        elif k == "square": b.set(x, y, z, SQUARE)
        elif k == "trail": b.set(x, y, z, TRAIL)
        elif k in ("mill", "miller", "apron"): b.set(x, y, z, "minecraft:coarse_dirt" if hsh(x, 1, z, 3403) < 0.5 else "minecraft:grass_block[snowy=false]")
        if v % 2: b.set(x, y + 1, z, slab("tuff_slab" if k == "trail" else "cobblestone_slab"))
        for yy in range(y + 1 + v % 2, y + 4):
            if b.get(x, yy, z) is None: b.set(x, yy, z, "minecraft:air")
    for (x, z), y in rl["wall"].items():
        lo = min(int(gr["before"][ix(gr, x, z)]), int(gr["live"][ix(gr, x, z)]))
        for yy in range(lo - 2, y + 1): b.set(x, yy, z, HB.WALLB)
        b.set(x, y + 1, z, "minecraft:cobblestone_wall" if hsh(x, 2, z, 3404) < 0.6 else "minecraft:mossy_cobblestone_wall")
    meta["walls"] = len(rl["wall"])

# ---------------------------------------------------------------- the trees, the snow, the springs, the old trees
VANILLA_TREE = re.compile(r"minecraft:(oak|birch|spruce|dark_oak|jungle|acacia|mangrove|cherry|pale_oak|azalea|flowering_azalea)_(log|leaves|wood)$|minecraft:(vine|pale_moss_carpet|pale_hanging_moss|cocoa|bee_nest)$")
SNOW = re.compile(r"minecraft:(snow|snow_block|powder_snow)$")
WATER = re.compile(r"minecraft:water$")
PLANTS = re.compile(r"minecraft:(short_grass|tall_grass|fern|large_fern|dandelion|poppy|azure_bluet|oxeye_daisy|cornflower|bush|firefly_bush|leaf_litter|wildflowers|sweet_berry_bush|.*_tulip|.*mushroom)$")
def world_scan(regex, inside):
    import fens_scan
    old = fens_scan.BAN; fens_scan.BAN = regex
    try: return fens_scan.scan(os.path.join(ROOT, "server/world"), box=P.BOX, inside=inside)
    finally: fens_scan.BAN = old

def in_vbox(x, z): return P.in_village(x, z)
def untree(b, gr, pl, rl, meta):
    """HQ T-031, 1: no vanilla trees in the village box (logs, leaves; leaves of crowns hanging in from outside too, when no trunk outside
    is within 4), nor on the walks of the ridge (the trail, the head, the spine); snow (none expected): grass/dirt/stone; springs on
    the slopes (water over the ground above the brook's level that can run off) go until only closed pools stay (T-028, T-030)"""
    T = rl["T"]; n = 0
    def clear_zone(x, z):
        if in_vbox(x, z): return True
        return any(abs(x - a) <= 3 and abs(z - c) <= 3 for (a, c) in []) or (x, z) in meta["_ridge_keep"]
    tr = world_scan(VANILLA_TREE, lambda x, z: P.in_village(x, z, 8) or (x, z) in meta["_ridge_keep"])
    logs_out = [(x, y, z) for (x, y, z, nm) in tr if ("_log" in nm or "_wood" in nm) and not clear_zone(x, z)]
    lo = {}
    for (x, y, z) in logs_out:
        for a in range(-4, 5):
            for c in range(-4, 5): lo.setdefault((x + a, z + c), []).append(y)
    for (x, y, z, nm) in tr:
        if b.get(x, y, z) is not None: continue
        if clear_zone(x, z):
            g = int(T[ix(gr, x, z)])
            b.set(x, y, z, "minecraft:air" if y > g else ("minecraft:grass_block[snowy=false]" if y == g else "minecraft:dirt")); n += 1
            continue
        if "leaves" in nm and P.in_village(x, z, 8) and not any(abs(y - yy) <= 4 for yy in lo.get((x, z), [])): b.set(x, y, z, "minecraft:air"); n += 1
    ns = 0
    for (x, y, z, nm) in world_scan(SNOW, lambda x, z: P.in_village(x, z) or P.in_ridge(x, z)):
        g = int(T[ix(gr, x, z)])
        if b.get(x, y, z) not in (None, "minecraft:air"): continue
        b.set(x, y, z, ("minecraft:grass_block[snowy=false]" if y == g else "minecraft:dirt") if g - 3 <= y <= g else ("minecraft:stone" if y < g else "minecraft:air"))
        ns += 1
    wat = {(x, y, z) for (x, y, z, nm) in world_scan(WATER, lambda x, z: P.in_place(x, z)) if y > 62}
    wat = {c for c in wat if c[1] > int(T[ix(gr, c[0], c[2])]) and b.get(*c) is None}
    nw = 0
    while True:
        gone = set()
        for (x, y, z) in wat:
            for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)):
                q = (x + a, y - (1 if (a, c) == (0, 0) else 0), z + c)
                i, j = ix(gr, q[0], q[2])
                if q in wat: continue
                if not (0 <= i < T.shape[0] and 0 <= j < T.shape[1]) or int(T[i, j]) < q[1]: gone.add((x, y, z)); break
        if not gone: break
        for c in gone: b.set(*c, "minecraft:air"); nw += 1
        wat -= gone
    # the plants over changed columns (they would float or stand in the walks)
    npl = 0
    for (x, y, z, nm) in world_scan(PLANTS, lambda x, z: P.in_village(x, z) or (x, z) in meta["_ridge_keep"]):
        i, j = ix(gr, x, z)
        if b.get(x, y, z) is not None: continue
        if y <= int(T[i, j]): continue                 # under the new ground: the terrain write takes it (air here would cut the ground)
        if T[i, j] != gr["live"][i, j] or y != int(T[i, j]) + 1 or (x, z) in rl["flat"] or rl["wallm"][i, j]: b.set(x, y, z, "minecraft:air"); npl += 1
    meta["removed"] = dict(tree_blocks=n, snow=ns, springs=nw, plants=npl)

def keepout(gr, pl, rl):
    """cells where no tree grows: the flats, the walls, the deck, the gardens, the pasture, the mill's yard and the wood of the contract
    (east plain: x >= 90), 2 round them"""
    m = rl["flatm"] | rl["wallm"] | gr["pad"] | gr["wet"]
    m = m | P.in_rect((88, -515, 120, -440), gr["X"], gr["Z"])
    out = m.copy()
    for _ in range(3):
        p = np.pad(out, 1); out = out | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    return out

def dark_oak(b, x, gy, z, lo, salt):
    """a dark oak: 2 x 2 trunk 5..7, a flat wide crown (dark oak leaves, persistent)"""
    hh = 5 + int(hsh(x, 1, z, salt) * 3)
    for a in (0, 1):
        for c in (0, 1):
            for y in range(lo - 1, gy + hh): b.set(x + a, y, z + c, "minecraft:dark_oak_log[axis=y]")
    for y in range(gy + hh - 2, gy + hh + 2):
        rr = 3.2 if y < gy + hh + 1 else 2.0
        for a in range(-4, 6):
            for c in range(-4, 6):
                if math.hypot(a - 0.5, c - 0.5) <= rr and b.get(x + a, y, z + c) is None and hsh(x + a, y, z + c, salt + 1) < 0.9:
                    b.set(x + a, y, z + c, "minecraft:dark_oak_leaves[distance=1,persistent=true,waterlogged=false]")
    return dict(x=x, z=z, h=hh, kind="dark_oak")

def trees(b, gr, pl, rl, meta):
    """HQ T-031, 1: on the places of the old trees of the village (base.bin: canopy >= 5) poplars of three colours (as the grove of
    T-030) and rare dark oaks; none on the gardens, the pasture, the walks, the east plain; leaves never into the ground uphill"""
    import grove_build as GB
    T = rl["T"]; ko = keepout(gr, pl, rl); out = []
    spots = []
    for i, j in zip(*np.nonzero(gr["village"] & (gr["trees"] >= 5) & ~ko)):
        x, z = int(gr["X"][i, j]), int(gr["Z"][i, j])
        if not P.in_village(x, z, -3): continue
        spots.append((x, z))
    spots.sort(key=lambda c: hsh(c[0], 3, c[1], 3410))
    taken = []
    for (x, z) in spots:
        if any(max(abs(x - a), abs(z - c)) < 6 for (a, c) in taken): continue
        sub = T[ix(gr, x, z)[0] - 1:ix(gr, x, z)[0] + 3, ix(gr, x, z)[1] - 1:ix(gr, x, z)[1] + 3]
        if sub.max() - sub.min() > 3: continue
        gy = int(T[ix(gr, x, z)])
        if any(b.get(x + a, gy + yy, z + c) is not None for a in (-2, -1, 0, 1, 2) for c in (-2, -1, 0, 1, 2) for yy in range(1, 8)): continue
        if len(taken) % 6 == 5: out.append(dark_oak(b, x, gy, z, int(sub.min()), 3420 + len(taken)))
        else: out.append(GB.poplar(b, x, gy, z, 10 + int(hsh(x, 6, z, 3421) * 6), 3430 + (x * 7 + z) % 37))
        taken.append((x, z))
        if len(taken) >= 34: break
    for (x, y, z) in [k for k, s in b.v.items() if re.search(r"leaves|shelf_mushroom", s)]:
        i, j = ix(gr, x, z)
        if y <= int(T[i, j]) or (x, z) in rl["flat"] or rl["wallm"][i, j] and y <= int(T[i, j]) + 3: del b.v[(x, y, z)]
    meta["trees"] = dict(poplars=sum(1 for t in out if t.get("kind") != "dark_oak"), dark_oaks=sum(1 for t in out if t.get("kind") == "dark_oak"))
    return out

# ---------------------------------------------------------------- the terrain write, the templates, the zones
def write_terrain(gr, rl, b):
    import r1_fens as RF
    T = rl["T"]; Wt = np.full(T.shape, NONE, np.int32)
    now, nw = gr["live"], gr["lwater"]
    cols = {}
    for (x, y, z), s_ in b.v.items(): cols.setdefault((x, z), {})[y] = s_
    act = gr["place"] & ~gr["pad"] & ~gr["wet"]
    cand = act & ((T != gr["before"]) | (T != now))
    touch = np.zeros(T.shape, bool)
    for i, j in zip(*np.nonzero(cand)):
        x, z = j + gr["x1"], i + gr["z1"]
        eg, ew = RF.expected_scan(T, Wt, cols, x, z, i, j)
        if now[i, j] != eg or (nw[i, j] != ew and ew != NONE): touch[i, j] = True
    H = np.where(touch, T, NONE).astype(np.int32)
    lo = T.copy()
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): lo = np.minimum(lo, np.roll(np.roll(lo, dz, 0), dx, 1))
    F = np.minimum(np.minimum(T, now), lo) - 4
    slope = np.zeros(T.shape, np.int32)
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): slope = np.maximum(slope, np.abs(T - np.roll(np.roll(T, dz, 0), dx, 1)))
    S = np.where(gr["ridge"] | (slope >= 3), S_ROCK, S_GRASS).astype(np.uint8)      # grass in the village, rock on the ridge and steep banks
    write_grid(os.path.join(OUT, "heather_terrain.bin"), gr["x1"], gr["z1"], H, F, np.full(T.shape, NONE, np.int32), S, np.full(T.shape, R_STONE, np.uint8), np.zeros(T.shape, np.uint8))
    return int(touch.sum())

def nbt(name, cells, origin):
    os.makedirs(STR, exist_ok=True)
    p = os.path.join(OUT, "tpl_heather_%s.txt" % name)
    with open(p, "w") as f:
        for (x, y, z), s in sorted(cells.items()): f.write("%d %d %d %s\n" % (x, y, z, s))
    r = subprocess.run([os.path.join(ROOT, "tools/blockwriter.sh"), "nbt", p, str(origin[0]), str(origin[1]), str(origin[2]), os.path.join(STR, name + ".nbt")], capture_output=True, text=True)
    if r.returncode or "nbt:" not in r.stdout: raise SystemExit(r.stdout + r.stderr)

def zone_lines(gr, rl, b, meta):
    from r1 import replace_lines
    T = rl["T"]
    lo = int(T[gr["village"] & ~gr["wet"]].min()) - 4
    lo = min(lo, int(gr["before"][gr["village"]].min()) - 4)
    hi = meta["church"]["spire"] + 4
    hx1, hz1, hx2, hz2 = P.HEAD
    sw = [k for k, s in b.v.items() if P.in_ridge(k[0], k[2]) and P.in_rect((hx1 - 16, hz1, hx2, hz2), k[0], k[2]) and s != "minecraft:air"]
    hlo = min(int(P.B4(gr, x, z)) for x in range(hx1, hx2 + 1) for z in range(hz1, hz2 + 1)) - 2
    hhi = max(k[1] for k in sw) + 2
    sx1 = min(k[0] for k in sw)
    replace_lines(os.path.join(ROOT, "zones/zones.txt"), ["heather ", "heather_head "],
                  ["heather         overworld box  %d %d %d  %d %d %d   # T-031: the Village of Heather (adventure, spawning on)" % (P.VILLAGE[0], lo, P.VILLAGE[1], P.VILLAGE[2], hi, P.VILLAGE[3]),
                   "heather_head    overworld box  %d %d %d  %d %d %d   # T-031: the head of the Dragon Ridge and the sword (the rest of the ridge breaks)" % (sx1, hlo, hz1, hx2, hhi, hz2)])
    return [lo, hi], [sx1, hlo, hz1, hx2, hhi, hz2]

# ---------------------------------------------------------------- the plan picture
def plan_png(gr, pl, rl, b, meta, info, path):
    from PIL import Image, ImageDraw
    S = 4; x1, z1, x2, z2 = P.RIDGE[0] - 14, P.RIDGE[1] - 14, P.RIDGE[2] + 14, P.VILLAGE[3] + 14
    w, h = (x2 - x1 + 1) * S, (z2 - z1 + 1) * S
    img = Image.new("RGB", (w, h + 150), (20, 20, 24)); d = ImageDraw.Draw(img)
    T = rl["T"]; tops = {}
    for (x, y, z), s in b.v.items():
        if s == "minecraft:air" or not (x1 <= x <= x2 and z1 <= z <= z2): continue
        if y >= tops.get((x, z), (-999, ""))[0]: tops[(x, z)] = (y, s)
    for z in range(z1, z2 + 1):
        for x in range(x1, x2 + 1):
            i, j = ix(gr, x, z); y = int(T[i, j])
            g = int(np.clip(30 + (y - 60) * 3.0, 20, 250)); col = (g // 2 + 20, g // 2 + 30, g // 3 + 15)
            if gr["wet"][i, j]: col = (30, 60, 130)
            if T[i, j] != gr["before"][i, j] and not gr["wet"][i, j]: col = (col[0] + 35, col[1] + 10, col[2])
            t = tops.get((x, z))
            if t:
                s = t[1].split("[")[0].split("{")[0].replace("minecraft:", "")
                if "poplar_leaves" in s: col = (200, 150, 40) if "yellow" in s else (210, 110, 40) if "orange" in s else (180, 60, 40)
                elif "dark_oak_leaves" in s: col = (40, 70, 30)
                elif s in ("bricks", "mud_bricks", "brick_wall") or "deepslate_tile" in s: col = (170, 50, 40)
                elif "spruce_stairs" in s or "spruce_slab" in s or s == "spruce_planks": col = (120, 85, 50)
                elif s == "hay_block": col = (200, 180, 70)
                elif s in ("gravel", "coarse_dirt") or "cobblestone" in s: col = (150, 145, 130)
                elif s in ("tuff", "cobbled_deepslate", "stone", "andesite", "polished_tuff", "dripstone_block") or "pointed" in s: col = (115, 115, 125)
                elif "fence" in s: col = (140, 100, 60)
                elif "poppy" in s: col = (220, 30, 30)
            if gr["pad"][i, j]: col = (110, 90, 70)
            if not gr["place"][i, j]: col = tuple(v // 3 for v in col)
            elif not (gr["village"][i, j] or gr["ridge"][i, j]): col = tuple(int(v * 0.6) for v in col)
            d.rectangle([(x - x1) * S, (z - z1) * S, (x - x1) * S + S - 1, (z - z1) * S + S - 1], fill=col)
    def R(r, c, wd=2): d.rectangle([(r[0] - x1) * S, (r[1] - z1) * S, (r[2] + 1 - x1) * S, (r[3] + 1 - z1) * S], outline=c, width=wd)
    def T_(x, z, t, c=(255, 255, 255)): d.text(((x - x1) * S + 2, (z - z1) * S + 1), t, fill=c)
    R(P.VILLAGE, (255, 70, 70)); R(P.RIDGE, (230, 90, 230)); R(P.PAD, (255, 150, 0)); R(P.HEAD, (90, 220, 255)); R(P.MOUTH, (255, 255, 0))
    R(pl["church"], (255, 60, 60), 3); T_(pl["church"][0], pl["church"][1], "church %d" % pl["cL"])
    R(pl["square"], (255, 220, 120)); T_(pl["square"][0], pl["square"][1], "square %d" % pl["sL"])
    for hh in meta["houses"]:
        R(hh["r"], (255, 255, 255)); T_(hh["r"][0], hh["r"][1], "%d %s" % (hh["k"] + 1, hh["kind"]), (255, 255, 160))
    for k, q in pl["plain"].items():
        R(q["r"], (120, 230, 90)); T_(q["r"][0], q["r"][1], k, (180, 255, 150))
    for q in pl["surf"]:
        cx, cz = (q[0] - x1) * S + S // 2, (q[1] - z1) * S + S // 2; d.point((cx, cz), fill=(255, 255, 0))
    for q in pl["tsurf"]:
        cx, cz = (q[0] - x1) * S + S // 2, (q[1] - z1) * S + S // 2; d.point((cx, cz), fill=(0, 255, 255))
    for (x, y, z, *_r) in meta.get("zombies_pts", []):
        cx, cz = (x - x1) * S, (z - z1) * S; d.ellipse([cx - 4, cz - 4, cx + 4, cz + 4], outline=(80, 255, 80), width=2)
    for k, c in (("ringer", (255, 255, 255)),):
        x, y, z = meta["church"]["ringer"]; cx, cz = (x - x1) * S, (z - z1) * S; d.ellipse([cx - 5, cz - 5, cx + 5, cz + 5], fill=c)
    sb = meta["head"]["sword_base"]; T_(sb[0], sb[2], "sword", (255, 255, 255))
    T_(P.MOUTH[0], P.MOUTH[1] - 4, "mouth %d" % P.MOUTH_Y, (255, 255, 0))
    lines = ["T-031 Village of Heather + Dragon Ridge: plan (1 block = %d px, north up). Red box = place heather, magenta = dragon_ridge, dim = seams; relief by height, reddish = changed" % S,
             "bridge %d rows from the pad of bonfire 9 (orange); street (yellow) %d cells, half a block per step, cut <= %d (max %d), fill on walls (max %d); retaining walls %d cells"
             % (info["bridge"], info["street_len"], P.STREET_CUT, info["street_cut"], info["street_fill"], meta["walls"]),
             "terraces: church %d (cut/fill %d), square %d (%d), houses (max %d), plain (max %d); houses 1..%d with their oddity, the miller's house; green = mill, gardens, pasture"
             % (pl["cL"], info["church"], pl["sL"], info["square"], info["houses"], info["plain"], len(meta["houses"])),
             "trail (cyan) %d cells from the church to the mouth (cut max %d, fill max %d); head 30 x 30 (blue), skull top %d, fill to the top %d (<= 50); mouth platform (yellow) at %d"
             % (info["trail_len"], info["trail_cut"], info["trail_fill"], P.HEAD_TOP, info["head_fill_top"], P.MOUTH_Y),
             "green rings = the dead villagers' points, white dot = the ringer; trees: poplars %d, dark oaks %d" % (meta["trees"]["poplars"], meta["trees"]["dark_oaks"])]
    for k, t in enumerate(lines): d.text((6, h + 6 + 18 * k), t, fill=(255, 255, 255))
    img.save(path)

def lecterns(b, meta):
    """HQ T-031, 5: six notes (written books) on lecterns: one per oddity (the first house of each kind) and the sacristy"""
    import heather_dp as HD
    out = []; done = set()
    for h_ in meta["houses"]:
        n = h_.get("note")
        if not n or n in done: continue
        done.add(n); x, y, z = h_["lectern"]
        f = HB.Frame(h_["r"], h_["face"])
        a, t, text = HD.NOTES[n]
        b.set(x, y, z, HB.lectern_book(t, a, HD.pages(text), f.d("out")))
        out.append(dict(n=n, pos=[x, y, z], author=a, house=h_["k"]))
    x, y, z = meta["church"]["sacristy"]["lectern"]
    a, t, text = HD.NOTES[6]
    b.set(x, y, z, HB.lectern_book(t, a, HD.pages(text), "south")); out.append(dict(n=6, pos=[x, y, z], author=a, house=None))
    meta["lecterns"] = sorted(out, key=lambda q: q["n"])

# ---------------------------------------------------------------- the build
def build(gr, pl, rl):
    b = B("heather"); T = rl["T"]; meta = {}
    def glo(r): return int(gr["before"][ix(gr, r[0], r[1])[0]:ix(gr, r[2], r[3])[0] + 1, ix(gr, r[0], r[1])[1]:ix(gr, r[2], r[3])[1] + 1].min())
    # the ridge keep-out for trees: the trail, the spine band, the head
    keep = set(pl["tsurf"]) | {(x, z) for x in range(P.HEAD[0] - 16, P.HEAD[2] + 1) for z in range(P.HEAD[1], P.HEAD[3] + 1)}
    for (x, (z, y)) in pl["axis"].items():
        for c in range(-2, 3): keep.add((x, z + c))
    meta["_ridge_keep"] = keep
    surface_walks(b, gr, pl, rl, meta)
    bridge(b, gr, pl, meta)
    meta["houses"] = []
    for spec in pl["houses"]:
        meta["houses"].append(HB.house(b, spec, glo(spec["r"]), meta))
    pm = pl["plain"]
    HB.miller_house(b, pm["miller"]["r"], "west", pm["miller"]["L"], glo(pm["miller"]["r"]), meta)
    HB.mill(b, pm["mill"]["r"], pm["mill"]["L"], glo(pm["mill"]["r"]), meta)
    for k in ("garden1", "garden2", "garden3"): HB.garden(b, pm[k]["r"], pm[k]["L"], 3440 + int(k[-1]), meta, k)
    HB.pasture(b, pm["pasture"]["r"], lambda x, z: int(T[ix(gr, x, z)]), 3450, meta)
    import heather_dp as HD
    meta["scarecrows"] = [list(p) for p in HD.scarecrow_points(meta, lambda x, z: int(T[ix(gr, x, z)]))]
    sq = pl["square"]; HB.well(b, (sq[0] + sq[2]) // 2, (sq[1] + sq[3]) // 2, pl["sL"], meta)
    HB.church(b, pl["church"], pl["cL"], lambda x, z: int(gr["before"][ix(gr, x, z)]), meta)
    lecterns(b, meta)
    # the ridge: the head first (its cells are final), the spine, the slopes
    sk, sw = HR.head(b, meta)
    tkeep = set(pl["tsurf"]) | set(rl["wall"])
    HR.spine(b, gr, T, tkeep | {(x, z) for x in range(P.HEAD[0], P.HEAD[2] + 1) for z in range(P.HEAD[1], P.HEAD[3] + 1)}, meta)
    meta["slopes"] = HR.slopes(b, gr, T, tkeep | set(rl["flat"]))
    trees(b, gr, pl, rl, meta)
    return b, meta, sk, sw

def main(plan_only=False):
    gr = P.grids()
    pl = P.plan(gr)
    rl = relief(gr, pl)
    info = checks(gr, pl, rl)
    b, meta, sk, sw = build(gr, pl, rl)
    if not plan_only: untree(b, gr, pl, rl, meta)
    from connect import connect
    connect(b)
    bad = [k for k in b.v if not P.in_place(k[0], k[2])]
    if bad: raise SystemExit("blocks outside the places: %s" % bad[:5])
    padb = [k for k in b.v if P.on_pad(k[0], k[2])]
    if padb: raise SystemExit("blocks on the pad of bonfire 9: %s" % padb[:5])
    import heather_dp
    meta["zombies_pts"] = heather_dp.zombie_points(meta, pl)
    os.makedirs(os.path.join(ROOT, "docs/reports/T-031"), exist_ok=True)
    plan_png(gr, pl, rl, b, meta, info, os.path.join(ROOT, "docs/reports/T-031/heather_plan.png"))
    if plan_only:
        print("plan:", info); return
    # the templates: the head (its cells), the sword in two pieces by height
    hx1, hz1, hx2, hz2 = P.HEAD
    nbt("head", {k: s for k, s in sk.items()}, (hx1, min(k[1] for k in sk), hz1))
    ys = sorted({k[1] for k in sw}); mid = ys[len(ys) // 2]
    lo = {k: s for k, s in sw.items() if k[1] < mid}; hi = {k: s for k, s in sw.items() if k[1] >= mid}
    nbt("sword_lo", lo, (min(k[0] for k in lo), min(k[1] for k in lo), min(k[2] for k in lo)))
    nbt("sword_hi", hi, (min(k[0] for k in hi), min(k[1] for k in hi), min(k[2] for k in hi)))
    ncol = write_terrain(gr, rl, b)
    np.savez_compressed(os.path.join(OUT, "heather_T.npz"), T=rl["T"], x1=gr["x1"], z1=gr["z1"])    # the ground of the places (heather_check)
    n = b.write_placements(os.path.join(OUT, "heather.txt"))
    zv, zh = zone_lines(gr, rl, b, meta)
    meta.pop("_ridge_keep", None)
    out = dict(meta); out.update(info=info, terrain_columns=ncol, blocks=n, zone=zv, zone_head=zh, bonfire=list(P.HEARTH), pad=list(P.PAD),
                                 church_r=list(pl["church"]), cL=pl["cL"], square=list(pl["square"]), sL=pl["sL"], plain={k: dict(r=list(q["r"]), L=q["L"]) for k, q in pl["plain"].items()},
                                 street=[list(c) for c in pl["street"]], trail=[list(c) for c in pl["trail"]], deck=sorted([x, z, v] for (x, z), v in pl["deck"].items()),
                                 mouth=list(P.MOUTH), mouth_y=P.MOUTH_Y, head_rect=list(P.HEAD), neck_end=list(P.NECK_END))
    heather_dp.run(out)
    json.dump(out, open(os.path.join(OUT, "heather.json"), "w"), ensure_ascii=False, default=lambda o: list(o) if isinstance(o, (set, tuple)) else (int(o) if isinstance(o, np.integer) else str(o)))
    print("heather: terrain %d columns, %d blocks, %s, houses %d, removed %s, trees %s, walls %d" % (ncol, n, info, len(meta["houses"]), meta.get("removed"), meta["trees"], meta["walls"]))

if __name__ == "__main__" and sys.argv[1:2] == ["plan"]:
    main(plan_only=True)
elif __name__ == "__main__":
    main()
