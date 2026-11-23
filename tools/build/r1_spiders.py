#!/usr/bin/env python3
"""T-032: the Spider Thicket (Паучья чаща, Р1) on the place `spiders` (rect 150 -300 80 80) + 16 of seam.

  python3 tools/build/r1_spiders.py        -> server/build/r1/spiders_terrain.bin (tools/terrain.sh apply), spiders.txt (tools/blockwriter.sh
                                              apply), spiders.json (points for the tests, the bot and the datapack), spiders_T.npz (the ground
                                              the step writes: spiders_check), docs/reports/T-032/spiders_plan.png, structure/spiders/*.nbt,
                                              datapack function/spiders/gen/* (tools/build/spiders_dp.py), the zone lines
  python3 tools/build/r1_spiders.py plan   only the plan (needs server/build/r1/spiders_pre.bin)
Inputs: server/build/r1/base.bin, terrain.bin, r1.json (the trail Heather -> Garden of T-022), spiders_pre.bin (the place now).

HQ T-032, 2: the thicket lies on the natural slope; the relief changes only at the nest, the burrow and the trails; elsewhere only the top
block and the trees. Snow, ice and the vanilla trees of the place go. Re-run on the built place: 0 columns changed."""
import json, math, os, re, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import write_grid, NONE
from lib import B, h as hsh
import spiders_plan as P
import spiders_build as SB
from spiders_plan import ix

ROOT = P.ROOT; OUT = P.OUT
DP = os.path.join(ROOT, "datapack/data/last_ember")
STR = os.path.join(DP, "structure/spiders")
S_FOREST, R_STONE = 2, 0
VANILLA_TREE = re.compile(r"minecraft:(oak|birch|spruce|dark_oak|jungle|acacia|mangrove|cherry|pale_oak|azalea|flowering_azalea)_(log|leaves|wood)$|minecraft:(vine|pale_moss_carpet|pale_hanging_moss|cocoa|leaf_litter)$")
SNOW = re.compile(r"minecraft:(snow|snow_block|powder_snow|ice|packed_ice|blue_ice)$")
PLANTS = re.compile(r"minecraft:(short_grass|tall_grass|fern|large_fern|sweet_berry_bush|dead_bush|wildflowers|bush|firefly_bush|short_dry_grass|tall_dry_grass|dandelion|poppy|.*_tulip|azure_bluet|oxeye_daisy|cornflower|lily_of_the_valley|allium|brown_mushroom|red_mushroom)$")

def world_scan(regex, inside):
    import fens_scan
    old = fens_scan.BAN; fens_scan.BAN = regex
    try: return fens_scan.scan(os.path.join(ROOT, "server/world"), box=P.BOX, inside=inside)
    finally: fens_scan.BAN = old

def trail_near(c, d=2):
    """the seam cells within d of a walk (the trails run through the seam: its trees and snow there go)"""
    out = set()
    for (x, z) in c.walk:
        for a in range(-d, d + 1):
            for cc in range(-d, d + 1): out.add((x + a, z + cc))
    return out

def clear(b, c, meta):
    """HQ T-032, 2: the vanilla trees of the place (logs, leaves, wood; leaves of crowns hanging in from outside when no trunk outside is
    within 4), the trees standing on the trails in the seam (and their crowns); snow (layers, blocks, powder), ice and packed ice ->
    ground (rooted dirt / dirt near the top, stone deeper) or air; the plants over changed columns; everything above the ground of the
    place up to the old top where nothing of ours stands"""
    gr = c.gr; T = c.T; near = trail_near(c)
    def ours(x, z): return (P.in_place(x, z, 0) or (x, z) in near) and not gr["ftrail"][ix(gr, x, z)]      # the trail of T-022 is never written
    tr = world_scan(VANILLA_TREE, lambda x, z: P.in_place(x, z, 8))
    logs_out = [(x, y, z) for (x, y, z, nm) in tr if ("_log" in nm or "_wood" in nm) and not ours(x, z)]
    logs_on = [(x, y, z) for (x, y, z, nm) in tr if ("_log" in nm or "_wood" in nm) and (x, z) in near and not P.in_place(x, z, 0)]
    lo = {}
    for (x, y, z) in logs_out:
        for a in range(-4, 5):
            for cc in range(-4, 5): lo.setdefault((x + a, z + cc), []).append(y)
    gone_crown = set()
    for (x, y, z) in logs_on:
        for a in range(-3, 4):
            for cc in range(-3, 4): gone_crown.add((x + a, z + cc))
    n = 0
    for (x, y, z, nm) in tr:
        if b.get(x, y, z) is not None: continue
        g = int(T[ix(gr, x, z)])
        if ours(x, z) or (x, z) in gone_crown and "leaves" in nm and not any(abs(y - yy) <= 4 for yy in lo.get((x, z), [])):
            if y > g: b.set(x, y, z, "minecraft:air"); n += 1
            elif y == g and P.in_place(x, z, 0): b.set(x, y, z, "minecraft:rooted_dirt"); n += 1
            continue
        if "leaves" in nm and P.in_place(x, z, 0) is False and P.in_place(x, z, 8) and False: pass
    ns = 0
    for (x, y, z, nm) in world_scan(SNOW, lambda x, z: ours(x, z)):
        g = int(T[ix(gr, x, z)])
        if b.get(x, y, z) not in (None, "minecraft:air"): continue
        if y > g: b.set(x, y, z, "minecraft:air")
        elif y >= g - 3: b.set(x, y, z, "minecraft:rooted_dirt" if y == g else "minecraft:dirt")
        else: b.set(x, y, z, "minecraft:stone")
        ns += 1
    npl = 0
    for (x, y, z, nm) in world_scan(PLANTS, lambda x, z: ours(x, z)):
        i, j = ix(gr, x, z)
        if b.get(x, y, z) is not None or y <= int(T[i, j]): continue      # under the new ground: the terrain write takes it
        b.set(x, y, z, "minecraft:air"); npl += 1
    # everything above the ground of the place up to the old top (the snow layers, the old trees) where nothing of ours is
    nair = 0
    for i, j in zip(*np.nonzero(gr["inner"])):
        x, z = j + gr["x1"], i + gr["z1"]; y = int(T[i, j])
        top = max(int(gr["top"][i, j]), int(gr["btop"][i, j]), int(gr["before"][i, j]) + 1)
        for yy in range(y + 1, min(top, y + 40) + 1):
            if b.get(x, yy, z) is None: b.set(x, yy, z, "minecraft:air"); nair += 1
    meta["removed"] = dict(tree_blocks=n, snow_ice=ns, plants=npl, air=nair)

# ---------------------------------------------------------------- light (sky and block light over the place + seam)
OPAQUE_NOT = re.compile(r"air$|leaves|cobweb|slab|stairs|fence|wall$|trapdoor|door|lichen|chain|tripwire|button|carpet|leaf_litter|turtle_egg|frogspawn|mangrove_roots|_mushroom$|grass$|fern|sapling|torch|lantern|flower|bush")
DIFFUSE = re.compile(r"leaves|cobweb|mangrove_roots")
def light(b, c, y0=None, y1=None):
    """sky light (and block light: no emitters in the place, 0) after the build by the vanilla rules: straight down from the sky without
    loss through non-diffusing cells, otherwise - max(1, opacity) per step; leaves, cobweb and mangrove roots diffuse (1), full blocks stop
    it. The ground is the step's T; the seam: open over its ground (no trees counted: more light leaks in than in the world)"""
    gr = c.gr; T = np.where(c.rl["pit"], gr["before"], c.T)
    x1, z1, x2, z2 = P.PLACE[0] - P.MARGIN, P.PLACE[1] - P.MARGIN, P.PLACE[2] + P.MARGIN, P.PLACE[3] + P.MARGIN
    sub = c.T[ix(gr, x1, z1)[0]:ix(gr, x2, z2)[0] + 1, ix(gr, x1, z1)[1]:ix(gr, x2, z2)[1] + 1]
    ys = [k[1] for k in b.v]
    y0 = int(sub.min()) - 1 if y0 is None else y0; y1 = max(ys) + 2 if y1 is None else y1
    nz, nx, ny = z2 - z1 + 1, x2 - x1 + 1, y1 - y0 + 1
    op = np.zeros((ny, nz, nx), np.int8)
    yy = np.arange(y0, y1 + 1)[:, None, None]
    op[yy <= sub[None]] = 15
    for (x, y, z), s in b.v.items():
        if not (x1 <= x <= x2 and z1 <= z <= z2 and y0 <= y <= y1): continue
        nm = s.split("[")[0].split("{")[0].replace("minecraft:", "")
        op[y - y0, z - z1, x - x1] = 0 if not DIFFUSE.search(nm) and OPAQUE_NOT.search(nm) else (1 if DIFFUSE.search(nm) else 15)
    # direct sky: from the top down while the cells are clear (0)
    clear = (op == 0)
    direct = np.flip(np.logical_and.accumulate(np.flip(clear, 0), 0), 0)
    L = np.where(direct, 15, 0).astype(np.int8)
    cost = np.maximum(1, op).astype(np.int8)
    for _ in range(16):
        p = np.pad(L, 1)
        m = np.maximum.reduce([p[2:, 1:-1, 1:-1], p[:-2, 1:-1, 1:-1], p[1:-1, 2:, 1:-1], p[1:-1, :-2, 1:-1], p[1:-1, 1:-1, 2:], p[1:-1, 1:-1, :-2]])
        new = np.where(op >= 15, 0, np.maximum(L, m - cost)).astype(np.int8)
        if np.array_equal(new, L): break
        L = new
    return L, (x1, y0, z1)

def deep_light(b, c, L, org, deep_from=12):
    """the feet cells of the deep (farther than 12 from the outline): the first cell over the ground (the lid over the pit, the trails'
    slabs) that is not one of our solid blocks; the share with sky light <= 7"""
    gr = c.gr; x0, y0, z0 = org; cells = []
    for i, j in zip(*np.nonzero(gr["inner"])):
        x, z = j + gr["x1"], i + gr["z1"]
        if P.edge_dist(x, z) <= deep_from: continue
        hole = c.pl["hole"]
        if hole[0] <= x <= hole[2] and hole[1] <= z <= hole[3]: continue
        y = int(gr["before"][i, j]) + 1 if c.rl["pit"][i, j] else int(c.T[i, j]) + 1
        s = b.get(x, y, z)
        while s is not None and not SB_clear(s): y += 1; s = b.get(x, y, z)
        if y - c.T[i, j] > 8 and not c.rl["pit"][i, j]: continue                 # under a trunk / the giant
        cells.append((x, y, z, int(L[y - y0, z - z0, x - x0])))
    dark = sum(1 for q in cells if q[3] <= 7)
    return dict(cells=len(cells), dark=dark, share=round(dark / max(1, len(cells)), 3), max=max(q[3] for q in cells),
                hist={k: sum(1 for q in cells if q[3] == k) for k in range(16)}), cells
def SB_clear(s):
    nm = s.split("[")[0].replace("minecraft:", "")
    return bool(re.search(r"air$|cobweb|slab|leaf_litter|tripwire|turtle_egg|frogspawn|grass$|fern", nm))

# ---------------------------------------------------------------- the terrain write, the templates, the zones
def write_terrain(gr, rl, b):
    import r1_fens as RF
    T = rl["T"]; Wt = np.full(T.shape, NONE, np.int32)
    now, nw = gr["live"], gr["lwater"]
    cols = {}
    for (x, y, z), s_ in b.v.items(): cols.setdefault((x, z), {})[y] = s_
    act = gr["place"] & ~gr["ftrail"] & ~gr["wet"]
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
    S = np.full(T.shape, S_FOREST, np.uint8)
    write_grid(os.path.join(OUT, "spiders_terrain.bin"), gr["x1"], gr["z1"], H, F, np.full(T.shape, NONE, np.int32), S, np.full(T.shape, R_STONE, np.uint8), np.zeros(T.shape, np.uint8))
    return int(touch.sum())

def nbt(name, cells, origin):
    os.makedirs(STR, exist_ok=True)
    p = os.path.join(OUT, "tpl_spiders_%s.txt" % name)
    with open(p, "w") as f:
        for (x, y, z), s in sorted(cells.items()): f.write("%d %d %d %s\n" % (x, y, z, s))
    r = subprocess.run([os.path.join(ROOT, "tools/blockwriter.sh"), "nbt", p, str(origin[0]), str(origin[1]), str(origin[2]), os.path.join(STR, name + ".nbt")], capture_output=True, text=True)
    if r.returncode or "nbt:" not in r.stdout: raise SystemExit(r.stdout + r.stderr)

def templates(b, c, meta, live):
    """structure/spiders/: cocoon_a|b|c (the hanging cocoons, unturned, chain cell over them), cocoon_live_closed|open (the datapack swaps
    them), nest_a|b (the giant and the nest in 2 pieces <= 40 x 24 x 20: artefact of the card, not placed by the datapack)"""
    for kind in "abc":
        cells = {}
        for (dx, dy, dz) in SB.cocoon_shape(kind): cells[(dx + 1, dy, dz + 1)] = SB.COCOON.at(dx + 7, dy, dz + 7)
        cells[(1, 3, 1)] = SB.CHAIN
        for x in range(3):
            for y in range(4):
                for z in range(3): cells.setdefault((x, y, z), "minecraft:structure_void")
        nbt("cocoon_" + kind, cells, (0, 0, 0))
    closed, opened, origin = live
    nbt("cocoon_live_closed", closed, origin); nbt("cocoon_live_open", opened, origin)
    x1, z1, x2, z2 = c.pl["nest"]["r"]; gi = c.pl["giant"]; F = c.pl["nest"]["floor"]
    ylo = F - 2; yhi = ylo + 39
    for k, (za, zb) in enumerate(((gi["za"], gi["za"] + 20), (gi["za"] + 21, gi["zb"] + 2))):
        cells = {}
        for (x, y, z), s in b.v.items():
            if x1 <= x <= x2 and za <= z <= zb and ylo <= y <= yhi: cells[(x, y, z)] = s
        for x in range(x1, x2 + 1):
            for z in range(za, zb + 1):
                for y in range(ylo, yhi + 1): cells.setdefault((x, y, z), "minecraft:structure_void")
        nbt("nest_" + "ab"[k], cells, (x1, ylo, za))
    meta["templates"] = dict(nest_pieces=[[x2 - x1 + 1, 40, gi["za"] + 21 - gi["za"]], [x2 - x1 + 1, 40, gi["zb"] + 2 - gi["za"] - 20]])

def zone_lines(c, b, meta):
    """spiders (the box of the place: the fire ban, the lists of the datapack; not a zone of T-004: the thicket is breakable) and
    spiders_nest (the pit, the giant and the burrow: floor - 2 .. trunk top + 3, no_spawn), spiders_cocoon (the live cocoon)"""
    from r1 import replace_lines
    x1, z1, x2, z2 = c.pl["nest"]["r"]; F = c.pl["nest"]["floor"]; gi = c.pl["giant"]
    top = int(max(P.trunk_y(gi, gi["za"]), P.trunk_y(gi, gi["zb"])) + 7) + 3
    nz = (x1 - 2, F - 2, gi["za"], x2 + 2, top, gi["zb"] + 2)
    lv = meta["live"]; o = lv["origin"]
    cz = (o[0], o[1], o[2], o[0] + 1, o[1] + 3, o[2] + 1)
    replace_lines(os.path.join(ROOT, "zones/zones.txt"), ["spiders_nest ", "spiders_cocoon "],
                  ["spiders_nest    overworld box %d %d %d %d %d %d   no_spawn   # T-032: the nest of the Spider Thicket (the pit, the giant, the burrow)" % nz,
                   "spiders_cocoon  overworld box %d %d %d %d %d %d              # T-032: the live cocoon (only the datapack opens it)" % cz])
    return nz, cz

# ---------------------------------------------------------------- the plan
def plan_png(c, b, meta, info, path):
    from PIL import Image, ImageDraw
    gr = c.gr; S = 7; x1, z1, x2, z2 = P.PLACE[0] - P.MARGIN - 2, P.PLACE[1] - P.MARGIN - 2, P.PLACE[2] + P.MARGIN + 2, P.PLACE[3] + P.MARGIN + 2
    w, h = (x2 - x1 + 1) * S, (z2 - z1 + 1) * S
    img = Image.new("RGB", (w, h + 150), (20, 20, 24)); d = ImageDraw.Draw(img)
    T = c.T
    tops = {}
    for (x, y, z), s in b.v.items():
        if s == "minecraft:air" or not (x1 <= x <= x2 and z1 <= z <= z2): continue
        if y >= tops.get((x, z), (-999, ""))[0]: tops[(x, z)] = (y, s)
    for z in range(z1, z2 + 1):
        for x in range(x1, x2 + 1):
            i, j = ix(gr, x, z); y = int(gr["before"][i, j])
            gcol = int(np.clip(40 + (y - 90) * 3.2, 25, 250)); col = (gcol // 2 + 30, gcol // 2 + 30, gcol // 2 + 25)
            if c.rl["pit"][i, j]: col = (70, 40, 40)
            t = tops.get((x, z))
            if t:
                s = t[1].split("[")[0]
                if "poplar_leaves" in s: col = (200, 150, 40) if "yellow" in s else (210, 110, 40) if "orange" in s else (180, 60, 40)
                elif "dark_oak_leaves" in s: col = (int(60 + gcol * 0.2), int(70 + gcol * 0.2), int(55 + gcol * 0.2))
                elif "mushroom_stem" in s or "white_wool" in s or "cobweb" in s: col = (215, 215, 210)
            if (x, z) in c.pl["tv"] or (x, z) in c.pl["ts"]: col = (200, 120, 60)
            if (x, z) in c.pl["ta"]: col = (170, 140, 90)
            if gr["ftrail"][i, j]: col = (120, 110, 90)
            if not gr["place"][i, j]: col = tuple(v // 3 for v in col)
            elif not gr["inner"][i, j]: col = tuple(int(v * 0.6) for v in col)
            d.rectangle([(x - x1) * S, (z - z1) * S, (x - x1) * S + S - 1, (z - z1) * S + S - 1], fill=col)
    def P2(x, z): return ((x - x1) * S + S // 2, (z - z1) * S + S // 2)
    def R(r, col, wd=2): d.rectangle([(r[0] - x1) * S, (r[1] - z1) * S, (r[2] + 1 - x1) * S, (r[3] + 1 - z1) * S], outline=col, width=wd)
    R(P.PLACE, (230, 230, 230)); R((P.PLACE[0] + P.EDGE, P.PLACE[1] + P.EDGE, P.PLACE[2] - P.EDGE, P.PLACE[3] - P.EDGE), (240, 190, 80), 1)
    R((P.PLACE[0] - P.MARGIN, P.PLACE[1] - P.MARGIN, P.PLACE[2] + P.MARGIN, P.PLACE[3] + P.MARGIN), (110, 110, 110), 1)
    R(c.pl["nest"]["r"], (255, 60, 60), 3); R(c.pl["hole"], (0, 0, 0), 3)
    gi = c.pl["giant"]; R((gi["x"] - 2, gi["za"], gi["x"] + 2, gi["zb"]), (120, 70, 30), 3)
    R((gi["x"] - 6, gi["zb"], gi["x"] + 6, gi["zb"] + 1), (150, 90, 160), 3)
    for (x, z), v in P.lair_lanes(c.pl["lair"]).items():
        cx, cz = P2(x, z); d.rectangle([cx - 2, cz - 2, cx + 2, cz + 2], fill=(150, 90, 160))
    for t in meta["trips"]:
        a = P2(t["hooks"][0][0], t["hooks"][0][2]); bb = P2(t["hooks"][1][0], t["hooks"][1][2]); d.line([a, bb], fill=(255, 255, 0), width=3)
    for k in meta["cocoons"]:
        cx, cz = P2(k["x"], k["z"]); d.ellipse([cx - 4, cz - 4, cx + 4, cz + 4], fill=(255, 255, 255))
    for k in meta["remains"]:
        cx, cz = P2(k["barrel"][0], k["barrel"][2]); d.rectangle([cx - 6, cz - 6, cx + 6, cz + 6], outline=(120, 220, 255), width=3)
    lv = meta["live"]; cx, cz = P2(lv["origin"][0], lv["origin"][2] + 1); d.ellipse([cx - 8, cz - 8, cx + 8, cz + 8], outline=(80, 255, 80), width=4)
    for p in meta["points"]["elites"]:
        cx, cz = P2(p[0], p[2]); d.polygon([(cx, cz - 7), (cx + 7, cz + 6), (cx - 7, cz + 6)], outline=(255, 40, 200), width=2)
    bx, by, bz = meta["points"]["boss"]; cx, cz = P2(bx, bz); d.ellipse([cx - 9, cz - 9, cx + 9, cz + 9], outline=(255, 40, 200), width=4)
    for it in meta["points"]["items"]:
        cx, cz = P2(it[0], it[2]); d.ellipse([cx - 3, cz - 3, cx + 3, cz + 3], fill=(255, 220, 120))
    lt = meta["light"]
    lines = ["T-032 Spider Thicket: plan (1 block = %d px, north up). White = place 80 x 80, orange = edge band %d, grey = seam 16; relief by height; trails: victims + walk to the burrow (rust), animal (sand), T-022 trail (dark)" % (S, P.EDGE),
             "pit (red) %s floor %d (median - 14; ground under it varies %d, the least in the deep; whole place: %d at %s, on the edge band by the T-022 trail); drop 3x3 (black); giant (brown) z %d..%d, butt roots (violet)"
             % (info["pit"], info["floor"], info["pit_range"], info["pit_glob"]["range"], info["pit_glob"]["r"], gi["za"], gi["zb"]),
             "burrow of roots (violet squares): a ledge along the N, W and S walls from the floor to the exit by the live cocoon (green ring), %d cells, cut outside the pit %.1f; trip wires (yellow) %d"
             % (info["lair_len"], info["lair_cut"], len(meta["trips"])),
             "trails: victims %d cells (cut %.1f, fill %.1f), animal %d (cut %.1f, fill %.1f), walk to the burrow %d; half a block per cell, no jumps"
             % (info["victims_len"], info["victims_cut"], info["victims_fill"], info["animal_len"], info["animal_cut"], info["animal_fill"], info["spur_len"]),
             "cocoons on chains (white) %d, with remains (cyan) %d; elite spiders (magenta triangles) %d, the Mistress (magenta ring); things of the victims (dots) %d"
             % (len(meta["cocoons"]), len(meta["remains"]), len(meta["points"]["elites"]), len(meta["points"]["items"])),
             "light at noon in the deep (> 12 from the outline): %d of %d feet cells with sky light <= 7 (%.1f %%), block light 0 (no emitters)" % (lt["dark"], lt["cells"], 100 * lt["share"])]
    for k, t in enumerate(lines): d.text((6, h + 6 + 20 * k), t, fill=(255, 255, 255))
    img.save(path)

def build(gr, pl, rl):
    b = B("spiders"); c = SB.Ctx(gr, rl, pl); meta = {}
    x1, z1, x2, z2 = pl["nest"]["r"]; gi = pl["giant"]
    for x in range(x1 - 2, x2 + 3):
        for z in range(z1 - 2, z2 + 3): c.keep.add((x, z))
    for x in range(gi["x"] - 3, gi["x"] + 4):
        for z in range(gi["za"] - 6, gi["zb"] + 3): c.keep.add((x, z))
    for x in range(gi["x"] - 7, gi["x"] + 8):
        for z in range(gi["zb"] - 1, gi["zb"] + 4): c.keep.add((x, z))
    for q in P.lair_lanes(pl["lair"]): c.keep.add(q)
    SB.trails(b, c, meta)
    SB.nest(b, c, meta)
    SB.burrow(b, c, meta)
    SB.giant(b, c, meta)
    c.cb = SB.canopy_base(c)
    live = SB.live_cocoon(b, c, meta)
    SB.tripwires(b, c, meta)
    SB.remains(b, c, meta)
    trees = SB.forest(b, c, meta); c.trees = trees
    SB.web(b, c, meta, trees)
    SB.hanging(b, c, meta)
    SB.ground(b, c)
    return b, c, meta, live

def points(b, c, meta):
    """the elite spiders (6 in the thicket: on a trunk at 2..4 over the ground, under the canopy by a cocoon, by the trail of the victims
    4..9 off it; 3 in the nest on its walls), the Mistress (the lair in the middle), the things of the victims along the trail (the
    outer side of its lanes), the bow, Toivo"""
    gr = c.gr; pv = c.pl["pv"]; out = dict(elites=[], items=[])
    deep_trunks = [t for t in meta["_trees"] if t["kind"] in ("deep_dark_oak", "deep_oak")]
    used = []
    for f in (0.2, 0.4, 0.55, 0.7, 0.85, 0.95):
        x, z, v = pv[min(len(pv) - 1, int(len(pv) * f))]
        best = None
        for t in deep_trunks:
            d = max(abs(t["x"] - x), abs(t["z"] - z))
            if not 4 <= d <= 10 or any(max(abs(t["x"] - u[0]), abs(t["z"] - u[2])) < 8 for u in used): continue
            if best is None or d < best[0]: best = (d, t)
        if best is None: continue
        t = best[1]; side = 1 if x > t["x"] else -1
        # on the trunk's side toward the trail, 3 over the ground (NoAI holds her there)
        px = t["x"] + (2 if side > 0 and t["kind"] == "deep_dark_oak" else 1 if side > 0 else -1)
        if b.get(px, c.g(px, t["z"]) + 3, t["z"]) is not None: continue
        yaw = 90 if side < 0 else -90
        used.append((px + 0.5, c.g(px, t["z"]) + 3, t["z"] + 0.5, yaw))
    for k in meta["cocoons"]:                                   # top up to 6 by the cocoons, under the canopy
        if len(used) >= 6: break
        x, z = k["x"] + 1, k["z"]
        y = int(c.cb[P.ix(gr, x, z)]) - 2
        if b.get(x, y, z) is None and b.get(x, y + 1, z) is None and y > c.g(x, z) + 3 and all(max(abs(x - u[0]), abs(z - u[2])) >= 8 for u in used):
            used.append((x + 0.5, y, z + 0.5, 0))
    out["elites"] = [list(u) for u in used[:6]]
    x1, z1, x2, z2 = c.pl["nest"]["r"]; F = c.pl["nest"]["floor"]
    out["elites"] += [[x2 - 0.5, F + 4, z1 + 4.5, 90], [x1 + 4.5, F + 1, z1 + 2.5, 180], [x2 - 2.5, F + 1, z2 - 4.5, -90]]
    mx, my, mz = meta["nest"]["lair_mid"]; out["boss"] = [mx + 0.5, my, mz + 0.5]
    # the things of the victims: helmet, shield, torch, boot + bone, rag, a broken arrow, a bowl
    kinds = ["leather_helmet", "shield", "torch", "leather_boots", "bone", "rag", "arrow", "bowl"]
    for n, kd in enumerate(kinds):
        x, z, v = pv[min(len(pv) - 2, 3 + int((len(pv) - 8) * n / len(kinds)))]
        k = P.D.index((pv[min(len(pv) - 1, pv.index((x, z, v)) + 1)][0] - x, pv[min(len(pv) - 1, pv.index((x, z, v)) + 1)][1] - z))
        sx, sz = P.side(k)
        if (x + sx, z + sz) not in c.walk: sx, sz = -sx, -sz
        q = (x - sx, z - sz) if n % 2 else (x + 2 * sx, z + 2 * sz)
        if q in c.walk: q = (x, z)
        yy = c.walk.get(q, 2 * c.g(*q)) / 2 + 1
        out["items"].append([q[0] + 0.5, yy, q[1] + 0.5, kd, int(hsh(x, 1, z, 3290) * 360)])
    return out

def main(plan_only=False):
    gr = P.grids()
    pl = P.plan(gr)
    rl = P.relief(gr, pl["nest"], pl["giant"], pl["lair"], pl["tv"], pl["ta"], pl["ts"])
    info = P.checks(gr, pl["nest"], pl["lair"], rl, pl["tv"], pl["ta"], pl["ts"])
    b, c, meta, live = build(gr, pl, rl)
    if not plan_only: clear(b, c, meta)
    from connect import connect
    connect(b)
    bad = [k for k in b.v if not P.in_place(k[0], k[2])]
    if bad: raise SystemExit("blocks outside the place: %s" % bad[:5])
    ft = [k for k in b.v if gr["ftrail"][ix(gr, k[0], k[2])]]
    if ft: raise SystemExit("blocks on the trail of T-022: %s" % ft[:5])
    L, org = light(b, c)
    meta["light"], _ = deep_light(b, c, L, org)
    if meta["light"]["share"] < 0.8: raise SystemExit("STOP (HQ T-032, 2): the deep has %.1f %% of its cells at sky light <= 7 (< 80 %%)" % (100 * meta["light"]["share"]))
    meta["_trees"] = c.trees
    meta["points"] = points(b, c, meta)
    os.makedirs(os.path.join(ROOT, "docs/reports/T-032"), exist_ok=True)
    plan_png(c, b, meta, info, os.path.join(ROOT, "docs/reports/T-032/spiders_plan.png"))
    if plan_only:
        print("plan:", info, meta["light"]); return
    templates(b, c, meta, live)
    ncol = write_terrain(gr, rl, b)
    np.savez_compressed(os.path.join(OUT, "spiders_T.npz"), T=rl["T"], x1=gr["x1"], z1=gr["z1"], walk=np.array([[x, z, v] for (x, z), v in c.walk.items()]))
    n = b.write_placements(os.path.join(OUT, "spiders.txt"))
    nz, cz = zone_lines(c, b, meta)
    meta.pop("_trees", None)
    out = dict(meta); out.update(info=info, terrain_columns=ncol, blocks=n, zone_nest=list(nz), zone_cocoon=list(cz), place=list(P.PLACE),
                                 nest_r=list(pl["nest"]["r"]), floor=pl["nest"]["floor"], hole=list(pl["hole"]), giant_xz=[pl["giant"]["x"], pl["giant"]["za"], pl["giant"]["zb"]],
                                 lair_path=pl["lair"]["path"], lair_exit=pl["lair"]["exit"], pv=[list(p) for p in pl["pv"]], pa=[list(p) for p in pl["pa"]], ps=[list(p) for p in pl["ps"]],
                                 frame_join=list(pl["pa"][0]), cocoon=list(pl["cocoon"]))
    try:
        import spiders_dp
        spiders_dp.run(out)
    except ImportError: pass
    json.dump(out, open(os.path.join(OUT, "spiders.json"), "w"), ensure_ascii=False, default=lambda o: list(o) if isinstance(o, (set, tuple)) else (int(o) if isinstance(o, np.integer) else float(o) if isinstance(o, np.floating) else str(o)))
    print("spiders: terrain %d columns, %d blocks, %s, removed %s, forest %s, web %s, cocoons %d, light %s" % (
        ncol, n, info, meta["removed"], meta["forest"], meta["web"], len(meta["cocoons"]), {k: meta["light"][k] for k in ("cells", "dark", "share", "max")}))

if __name__ == "__main__" and sys.argv[1:2] == ["plan"]:
    main(plan_only=True)
elif __name__ == "__main__":
    main()
