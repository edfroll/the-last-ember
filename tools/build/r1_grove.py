#!/usr/bin/env python3
"""T-030: the Mushroom Grove of the Advisor (Р1) on the place `grove` (circle r 45 round (-420, 60)) + 16 of seam.

  python3 tools/build/r1_grove.py         -> server/build/r1/grove_terrain.bin (tools/terrain.sh apply), grove.txt (tools/blockwriter.sh apply),
                                             grove.json (points for the tests, the bot and the datapack), docs/reports/T-030/grove_plan.png,
                                             structure/grove/face_<k>_closed|open.nbt, datapack function/grove/gen/* (tools/build/grove_dp.py),
                                             the zone line
  python3 tools/build/r1_grove.py plan    only the plan (needs server/build/r1/grove_pre.bin: the scan of the place now)
Inputs: server/build/r1/base.bin (the ground before the R1 frame), terrain.bin (the frame), grove_pre.bin (scan of the place now: the
        approaches of T-022 are cut into the frame by blocks, their real ground is read here), r1.json (their walked profile).

Layout (HQ T-030, 1: the grove stays on its slope): earth work only under the house terrace (L, at most 10 of cut/fill), the garden north of
the pad of bonfire 10 (at the pad's level, at most 6) and the path from the pad's west edge to the door (half a block per cell, at most 4);
1:1 banks round them, retaining walls where the ground falls away more than 3 beside them. The old trees of the circle go; on their
places (base.bin) grow the giant mushrooms, the 6 thick poplars with faces and the poplars. Small glowing mushrooms are placed until
every walked cell and every cell of the circle has block light >= 1. Re-run: the same place, 0 columns changed."""
import json, math, os, re, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, write_grid, NONE
from lib import B, Mix, h as hsh, stairs, slab, lantern
import grove_plan as P
import grove_build as GB
from grove_plan import ix

ROOT = P.ROOT; OUT = P.OUT
DP = os.path.join(ROOT, "datapack/data/last_ember")
S_FOREST = 2
R_STONE = 0
STR = os.path.join(DP, "structure/grove")

def ground_at(rl, gr):
    T = rl["T"]
    return lambda x, z: int(T[ix(gr, x, z)])

def build(gr, rl, plan_only=False):
    b = B("grove"); T = rl["T"]; L = rl["L"]; meta = dict(L=L)
    g = ground_at(rl, gr)
    GB.house(b, P.HX, P.HZ, L, meta)
    giants, faces, poplars = P.layout(gr, rl)
    meta["giants"] = []
    for (x, z, k, rot) in giants:
        kind, hh, cr = P.GIANTS[k]
        hh += int(hsh(x, 4, z, 3020) * 2)
        lo = min(g(x + a, z + c) for a in (-1, 0, 1) for c in (-1, 0, 1))
        meta["giants"].append(GB.giant(b, x, z, kind, rot, lo, g, hh, cr))
    meta["faces"] = []; templates = {}
    for k, (x, z, side) in enumerate(faces, 1):
        lo = min(g(x + a, z + c) for a in (-1, 0, 1) for c in (-1, 0, 1)); gy = max(g(x + a, z + c) for a in (-1, 0, 1) for c in (-1, 0, 1))
        hh = 20 + int(hsh(x, 5, z, 3021) * 5)
        GB.thick_poplar(b, x, gy, z, hh, lo, 3100 + k)
        closed = GB.face_cells(x, gy, z, side, "closed"); opened = GB.face_cells(x, gy, z, side, "open")
        for kk, s in closed.items(): b.set(*kk, s)
        cells = set(closed) | set(opened)
        templates[k] = ({c: closed.get(c, "minecraft:air") for c in cells}, {c: opened.get(c, "minecraft:air") for c in cells})
        ox = min(c[0] for c in cells); oy = min(c[1] for c in cells); oz = min(c[2] for c in cells)
        meta["faces"].append(dict(k=k, x=x, z=z, y=gy, side=side, origin=[ox, oy, oz], eye=[x + GB.DXZ[side][0] * 2, gy + 5, z + GB.DXZ[side][1] * 2]))
    meta["poplars"] = []
    for (x, z) in poplars:
        hh = 11 + int(hsh(x, 6, z, 3022) * 7)
        meta["poplars"].append(GB.poplar(b, x, g(x, z), z, hh, 3200 + (x * 7 + z) % 37))
    # small mushrooms at the roots of the poplars (on podzol / mycelium: they keep in any light there)
    for p in meta["poplars"]:
        for (a, c) in ((1, 1), (-1, 1), (1, -1), (-2, 0)):
            x, z = p["x"] + a, p["z"] + c
            if hsh(x, 9, z, 3023) < 0.45 and b.get(x, g(x, z) + 1, z) is None and not rl["flatm"][ix(gr, x, z)] and not rl["app"][ix(gr, x, z)]:
                b.set(x, g(x, z), z, "minecraft:podzol[snowy=false]" if hsh(x, 1, z, 3024) < 0.6 else "minecraft:mycelium[snowy=false]")
                b.set(x, g(x, z) + 1, z, "minecraft:brown_mushroom" if hsh(x, 2, z, 3025) < 0.6 else "minecraft:red_mushroom")
    # crowns and caps never go into the hillside (a tree low on the slope reaches over higher ground): leaves, shelf mushrooms, cap blocks
    # at or under the ground of their column go (trunks and stems go down into the ground on purpose)
    for (x, y, z) in [k for k, s in b.v.items() if re.search(r"leaves|shelf_mushroom|mushroom_block|shroomlight", s)]:
        i, j = ix(gr, x, z)
        if 0 <= i < T.shape[0] and 0 <= j < T.shape[1] and y <= int(T[i, j]): del b.v[(x, y, z)]
    walks(b, gr, rl, meta)
    garden(b, gr, rl, meta)
    return b, meta, templates

def walks(b, gr, rl, meta):
    """the path (mossy cobblestone, cobblestone slabs on the half steps), the terrace round the house, the retaining walls with parapets"""
    T = rl["T"]; L = rl["L"]
    for (x, z), v in rl["flat"].items():
        y = v // 2
        if P.in_rect(P.GARDEN, x, z): continue
        if P.in_rect(P.TERRACE, x, z):
            if abs(x - P.HX) <= 4 and abs(z - P.HZ) <= 4 and GB.octagon(x - P.HX, z - P.HZ): continue
            on = (P.PATH_Z[0] <= z <= P.PATH_Z[1] and x > P.HX + 4)
            b.set(x, y, z, GB.PATH if on else GB.GROUND)
            continue
        b.set(x, y, z, GB.PATH)
        if v % 2: b.set(x, y + 1, z, slab("cobblestone_slab"))
    for (lx_, lz_) in ((P.TERRACE[2], P.PATH_Z[0] - 2), (P.TERRACE[2], P.PATH_Z[1] + 2), (P.TERRACE[0] + 1, P.TERRACE[1]), (P.TERRACE[0] + 1, P.TERRACE[3])):
        b.set(lx_, L + 1, lz_, "minecraft:spruce_fence"); b.set(lx_, L + 2, lz_, "minecraft:spruce_fence"); b.set(lx_, L + 3, lz_, lantern())
    meta["path"] = [[x, z, rl["flat"][(x, z)] / 2 + 1] for (x, z) in sorted(rl["flat"]) if P.PATH_X[0] <= x <= P.PATH_X[1] and P.PATH_Z[0] <= z <= P.PATH_Z[1]]
    # glow lichen along the edges of the path (on the ground beside it)
    for x in range(P.PATH_X[0], P.PATH_X[1] + 1):
        for z in (P.PATH_Z[0] - 1, P.PATH_Z[1] + 1):
            if (x, z) in rl["flat"] or (x, z) in rl["wall"]: continue
            if hsh(x, 3, z, 3030) < 0.6: b.set(x, int(T[ix(gr, x, z)]) + 1, z, "minecraft:glow_lichen[down=true,east=false,north=false,south=false,up=false,waterlogged=false,west=false]")
    for (x, z), y in rl["wall"].items():
        lo = int(gr["before"][ix(gr, x, z)])
        if "live" in gr: lo = min(lo, int(gr["live"][ix(gr, x, z)]))
        for yy in range(lo - 2, y + 1): b.set(x, yy, z, GB.WALL)
        b.set(x, y + 1, z, "minecraft:mossy_cobblestone_wall")
    meta["walls"] = len(rl["wall"])

def garden(b, gr, rl, meta):
    """the Advisor's garden north of the pad (at the pad's level): beds in a fence (a player cannot jump onto them: farmland is trampled
    by players in adventure too), the bee nest with 2 bees on a post, the stump of stripped oak, a bench by it and a bench at the pad's
    north edge facing the fire"""
    x1, z1, x2, z2 = P.GARDEN; y = P.PAD_Y
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1): b.set(x, y, z, GB.GROUND)
    beds = [(x1 + 1, z1 + 1, x1 + 4, z1 + 2), (x1 + 6, z1 + 1, x1 + 9, z1 + 2)]
    crops = ["wheat[age=7]", "carrots[age=7]", "potatoes[age=7]", "beetroots[age=3]"]
    for k, (a1, c1, a2, c2) in enumerate(beds):
        for x in range(a1 - 1, a2 + 2):
            for z in range(c1 - 1, c2 + 2):
                if a1 <= x <= a2 and c1 <= z <= c2:
                    b.set(x, y, z, "minecraft:farmland[moisture=7]"); b.set(x, y + 1, z, "minecraft:" + crops[(k * 2 + (x + z)) % 4])
                else: b.set(x, y + 1, z, "minecraft:spruce_fence")
    b.set(x1 + 5, y, z1 + 1, "minecraft:water"); b.set(x1 + 5, y + 1, z1 + 1, "minecraft:spruce_trapdoor[facing=north,half=bottom,open=false]")
    # the bee nest on a post at the garden's west end, 2 bees inside
    nx, nz = x1, z1 + 4
    b.set(nx, y + 1, nz, "minecraft:stripped_oak_log[axis=y]"); b.set(nx, y + 2, nz, "minecraft:stripped_oak_log[axis=y]")
    b.set(nx, y + 3, nz, "minecraft:bee_nest[facing=east,honey_level=0]{bees:[{entity_data:{id:\"minecraft:bee\"},min_ticks_in_hive:600,ticks_in_hive:0},{entity_data:{id:\"minecraft:bee\"},min_ticks_in_hive:600,ticks_in_hive:0}]}")
    for (a, c) in ((1, 0), (2, 1), (1, -1)): b.set(nx + a, y + 1, nz + c, "minecraft:" + ("allium" if (a + c) % 2 else "oxeye_daisy"))
    # the stump and its bench
    sx, sz = x1 + 4, z1 + 4
    b.set(sx, y + 1, sz, "minecraft:stripped_oak_wood[axis=y]")
    b.set(sx + 1, y + 1, sz, stairs("spruce_stairs", "east")); b.set(sx + 1, y + 1, sz - 1, stairs("spruce_stairs", "east"))
    # the bench at the pad's north edge (z = garden's south row), facing the fire
    for x in (P.HEARTH[0] - 2, P.HEARTH[0] - 1, P.HEARTH[0] + 1, P.HEARTH[0] + 2):
        b.set(x, y + 1, z2, stairs("spruce_stairs", "north"))
    b.set(P.HEARTH[0] - 3, y + 1, z2, "minecraft:spruce_trapdoor[facing=west,half=bottom,open=true]")
    b.set(P.HEARTH[0] + 3, y + 1, z2, "minecraft:spruce_trapdoor[facing=east,half=bottom,open=true]")
    for (lx_, lz_) in ((x1, z1), (x2, z1), (x1 + 7, z1 + 4)):          # lantern posts
        b.set(lx_, y + 1, lz_, "minecraft:spruce_fence"); b.set(lx_, y + 2, lz_, "minecraft:spruce_fence"); b.set(lx_, y + 3, lz_, lantern())
    meta["garden"] = dict(beds=beds, nest=[nx, y + 3, nz], stump=[sx, y + 1, sz], bench=[P.HEARTH[0] - 2, y + 1, z2], bench_stump=[sx + 1, y + 1, sz])

# ---------------------------------------------------------------- light (block light, flood through non-opaque cells)
EMIT = {"shroomlight": 15, "campfire": 15, "lantern": 15, "glow_lichen": 7, "verdant_froglight": 15, "pearlescent_froglight": 15}
CLEAR = re.compile(r"air|glass_pane|leaves|slab|stairs|fence|wall|trapdoor|door|lichen|mushroom$|lantern|chain|banner|bed|pot|carpet|crops|wheat|carrots|potatoes|beetroots|allium|daisy|campfire|lectern|shelf_mushroom|water")
def light_grid(b, gr, rl, y0, y1):
    """block light over the circle's box (y0..y1): the ground column (<= T) and our solid blocks are opaque"""
    T = rl["T"]; x1, z1 = P.CX - P.R - 2, P.CZ - P.R - 2; n = 2 * P.R + 5
    ny = y1 - y0 + 1
    op = np.zeros((ny, n, n), bool); lt = np.zeros((ny, n, n), np.int8)
    Tc = T[ix(gr, x1, z1)[0]:ix(gr, x1, z1)[0] + n, ix(gr, x1, z1)[1]:ix(gr, x1, z1)[1] + n]
    yy = np.arange(y0, y1 + 1)[:, None, None]
    op |= yy <= Tc[None]
    for (x, y, z), s in b.v.items():
        if not (x1 <= x < x1 + n and z1 <= z < z1 + n and y0 <= y <= y1): continue
        nm = s.split("[")[0].split("{")[0].replace("minecraft:", "")
        k = (y - y0, z - z1, x - x1)
        if nm in EMIT and ("campfire" not in nm or "lit=true" in s): lt[k] = EMIT[nm]; op[k] = False
        else: op[k] = not CLEAR.search(nm)
    for _ in range(15):
        p = np.pad(lt, 1)
        m = np.maximum.reduce([p[2:, 1:-1, 1:-1], p[:-2, 1:-1, 1:-1], p[1:-1, 2:, 1:-1], p[1:-1, :-2, 1:-1], p[1:-1, 1:-1, 2:], p[1:-1, 1:-1, :-2]]) - 1
        lt = np.where(op, lt, np.maximum(lt, m)).astype(np.int8)
    return lt, (x1, y0, z1)

def walk_cells(b, gr, rl, meta):
    """feet cells that must be lit: the path, the terrace, the garden, the approaches in the circle, the house floors; plus the whole circle"""
    T = rl["T"]; must = []; rest = []
    for i, j in zip(*np.nonzero(gr["circle"] & ~gr["pad"])):
        x, z = int(gr["X"][i, j]), int(gr["Z"][i, j]); y = int(T[i, j]) + 1
        while b.get(x, y, z) is not None and not CLEAR.search(b.get(x, y, z).split("[")[0]): y += 1
        if y - T[i, j] > 3: continue                                  # under a trunk / a giant's stem
        (must if (rl["flatm"][i, j] or rl["app"][i, j]) else rest).append((x, y, z))
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            c = (P.HX + dx, meta["floors"]["f1"], P.HZ + dz); s_ = b.get(*c)
            if s_ is None or CLEAR.search(s_.split("[")[0]): must.append(c)
    return must, rest

def place_lights(b, gr, rl, meta):
    """glowing mushrooms: first along the path, then greedily until every cell of the circle has light >= 1"""
    T = rl["T"]; g = ground_at(rl, gr); out = []
    ko = P.keepout(gr, rl)
    def free(x, z):
        if not P.in_circle(x, z, P.R - 2) or ko[ix(gr, x, z)]: return False
        gy = g(x, z)
        if any(b.get(x + a, yy, z + c) is not None for a in (-2, -1, 0, 1, 2) for c in (-2, -1, 0, 1, 2) for yy in range(gy + 1, gy + 5)): return False
        sub = T[ix(gr, x, z)[0] - 1:ix(gr, x, z)[0] + 2, ix(gr, x, z)[1] - 1:ix(gr, x, z)[1] + 2]
        return sub.max() - sub.min() <= 2
    for k, x in enumerate(range(P.PATH_X[0], P.PATH_X[1] + 1, 4)):
        z = P.PATH_Z[1] + 3 if k % 2 else P.PATH_Z[0] - 3
        if free(x, z): out.append(GB.glow_mushroom(b, x, g(x, z), z, g))
    # along the approaches of T-022 in the circle (their banks are 1:1, the free test would refuse them): every 6 cells, both sides
    acells = sorted({(int(gr["X"][i, j]), int(gr["Z"][i, j])) for i, j in zip(*np.nonzero(rl["app"] & gr["circle"]))})
    for k, x in enumerate(range(min(c[0] for c in acells) + 2, max(c[0] for c in acells) + 1, 6)):
        zs = sorted(z for (xx, z) in acells if xx == x)
        if not zs: continue
        z = zs[0] - 2 if k % 2 else zs[-1] + 2
        if ko[ix(gr, x, z)] and not rl["app"][ix(gr, x, z)] and (x, z) not in rl["flat"] and not gr["pad"][ix(gr, x, z)]:
            if all(b.get(x + a, g(x, z) + yy, z + c) is None for a in (-1, 0, 1) for c in (-1, 0, 1) for yy in (1, 2, 3)):
                out.append(GB.glow_mushroom(b, x, g(x, z), z, g))
    y0 = int(T[gr["circle"]].min()) - 1; y1 = y0 + 110
    for rnd in range(90):
        lt, (lx, ly, lz) = light_grid(b, gr, rl, y0, y1)
        must, rest = walk_cells(b, gr, rl, meta)
        dark = [c for c in must + rest if lt[c[1] - ly, c[2] - lz, c[0] - lx] < 1]
        if not dark: break
        cand = {}
        for (x, y, z) in dark:
            for a in range(-9, 10, 3):
                for c in range(-9, 10, 3):
                    q = (x + a, z + c)
                    if q not in cand: cand[q] = None
        best = None
        for q in cand:
            if not free(*q): continue
            gy = g(*q); sc = sum(1 for (x, y, z) in dark if abs(x - q[0]) + abs(z - q[1]) + abs(y - gy - 2) <= 12)
            if best is None or sc > best[0]: best = (sc, q)
        if best is None or best[0] == 0: break
        for _ in range(1):
            out.append(GB.glow_mushroom(b, best[1][0], g(*best[1]), best[1][1], g))
    lt, (lx, ly, lz) = light_grid(b, gr, rl, y0, y1)
    must, rest = walk_cells(b, gr, rl, meta)
    dm = [c for c in must if lt[c[1] - ly, c[2] - lz, c[0] - lx] < 1]; dr = [c for c in rest if lt[c[1] - ly, c[2] - lz, c[0] - lx] < 1]
    meta["light"] = dict(mushrooms=len(out), must=len(must), must_dark=len(dm), rest=len(rest), rest_dark=len(dr), dark_e_g=dm[:5] + dr[:5])
    if dm: raise SystemExit("walked cells without light (%d): %s" % (len(dm), dm[:40]))
    return out

# ---------------------------------------------------------------- the surface, the old trees, the snow
VANILLA_TREE = re.compile(r"minecraft:(oak|birch|spruce|dark_oak|jungle|acacia|mangrove|cherry|pale_oak|azalea|flowering_azalea)_(log|leaves|wood)$|minecraft:(vine|pale_moss_carpet|pale_hanging_moss|cocoa)$")
SNOW = re.compile(r"minecraft:(snow|snow_block|powder_snow)$")
WATER = re.compile(r"minecraft:water$")
def world_scan(regex, inside):
    import fens_scan
    old = fens_scan.BAN; fens_scan.BAN = regex
    try: return fens_scan.scan(os.path.join(ROOT, "server/world"), box=P.BOX, inside=inside)
    finally: fens_scan.BAN = old

def surface(b, gr, rl):
    """every column of the circle (not the pad, not the approaches): the top block gets the card's palette (podzol, moss, mycelium,
    coarse dirt; steep: stone and cobble), everything above the ground goes (the old trees, the snow layers) where nothing of ours is"""
    T = rl["T"]; n = 0
    for i, j in zip(*np.nonzero(gr["circle"] & ~gr["pad"] & ~rl["app"] & ~rl["wallm"])):
        x, z = j + gr["x1"], i + gr["z1"]; y = int(T[i, j])
        if b.get(x, y, z) is None:
            nb = [T[i + a, j + d] for a, d in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            steep = max(abs(v - y) for v in nb) >= 3
            b.set(x, y, z, GB.STEEP if steep else GB.GROUND)
            for k in (1, 2):
                if b.get(x, y - k, z) is None: b.set(x, y - k, z, "minecraft:dirt" if not steep else "minecraft:stone")
        top = max(int(gr["top"][i, j]) if "top" in gr else y + 1, int(gr["before"][i, j]) + 1, y + 1)
        top = max(top, int(gr["nat"][i, j] + max(gr["trees"][i, j], 0)))
        for yy in range(y + 1, min(top, y + 48) + 1):
            if b.get(x, yy, z) is None: b.set(x, yy, z, "minecraft:air"); n += 1
    return n

def approaches(b, gr, rl):
    """HQ T-030: the approaches of T-022 inside the circle get the path's palette on top, the heights stay: read their top blocks"""
    if "live" not in gr: return 0
    cells = {(int(gr["X"][i, j]), int(gr["Z"][i, j])) for i, j in zip(*np.nonzero(rl["app"] & gr["circle"]))}
    n = 0
    for (x, z) in cells:
        y = int(gr["before"][ix(gr, x, z)])           # the ground before the place (grove_plan: the first scan)
        b.set(x, y, z, GB.PATH); n += 1
    return n

def untree_unsnow(b, gr, rl):
    """the old trees: logs and leaves of the circle (surface() takes the columns; here the leaves of the circle's trees hanging over the
    seam), the snow under the ground of the circle (snow blocks, powder snow: dirt within 3 of the ground, stone deeper)"""
    T = rl["T"]; n = 0
    tr = world_scan(VANILLA_TREE, lambda x, z: P.in_circle(x, z, P.R + 14))
    logs_out = [(x, y, z) for (x, y, z, nm) in tr if ("_log" in nm or "_wood" in nm) and not P.in_circle(x, z) and b.get(x, y, z) is None]
    lo = {}
    for (x, y, z) in logs_out:
        for a in range(-4, 5):
            for c in range(-4, 5): lo.setdefault((x + a, z + c), []).append(y)
    for (x, y, z, nm) in tr:
        if b.get(x, y, z) is not None: continue
        if not P.in_circle(x, z, P.R + 9): continue
        if P.in_circle(x, z):
            if y > int(T[ix(gr, x, z)]): b.set(x, y, z, "minecraft:air"); n += 1      # below the new ground the terrain write took it
            continue
        if "leaves" in nm and not any(abs(y - yy) <= 4 for yy in lo.get((x, z), [])): b.set(x, y, z, "minecraft:air"); n += 1
    ns = 0
    for (x, y, z, nm) in world_scan(SNOW, lambda x, z: P.in_circle(x, z)):
        if P.on_pad(x, z): continue
        g = int(T[ix(gr, x, z)])
        cur = b.get(x, y, z)
        if cur is not None and cur != "minecraft:air" and not cur.startswith("minecraft:dirt") and not cur.startswith("minecraft:stone"): continue
        if y <= g: b.set(x, y, z, (GB.GROUND.at(x, y, z) if y == g else "minecraft:dirt") if y >= g - 3 else "minecraft:stone")
        else: b.set(x, y, z, "minecraft:air")
        ns += 1
    # the springs (T-028 precedent): water above the ground that can run off (a side at its level open to the air) goes, repeated until
    # only enclosed pools stay; the frame generated the chunks frozen, the springs of the slope above the grove would flood the path
    wat = {(x, y, z) for (x, y, z, nm) in world_scan(WATER, lambda x, z: P.in_place(x, z))}
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
    return n, ns, nw

def write_terrain(gr, rl, b):
    """only the columns whose scan is not yet what it should be (a re-run on the built place rewrites nothing)"""
    import r1_fens as RF
    T = rl["T"]; Wt = np.full(T.shape, NONE, np.int32)
    now, nw = gr["live"], gr["lwater"]
    cols = {}
    for (x, y, z), s_ in b.v.items(): cols.setdefault((x, z), {})[y] = s_
    cand = gr["circle"] & ~gr["pad"] & ~rl["app"] & (T != gr["before"]) | (gr["circle"] & ~gr["pad"] & ~rl["app"] & (T != now))
    touch = np.zeros(T.shape, bool)
    for i, j in zip(*np.nonzero(cand)):
        x, z = j + gr["x1"], i + gr["z1"]
        eg, ew = RF.expected_scan(T, Wt, cols, x, z, i, j)
        if now[i, j] != eg or nw[i, j] != ew: touch[i, j] = True
    H = np.where(touch, T, NONE).astype(np.int32)
    lo = T.copy()
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): lo = np.minimum(lo, np.roll(np.roll(lo, dz, 0), dx, 1))
    F = np.minimum(np.minimum(T, now), lo) - 4
    S = np.full(T.shape, S_FOREST, np.uint8)
    write_grid(os.path.join(OUT, "grove_terrain.bin"), gr["x1"], gr["z1"], H, F, np.full(T.shape, NONE, np.int32), S, np.full(T.shape, R_STONE, np.uint8), np.zeros(T.shape, np.uint8))
    return int(touch.sum())

def nbt(name, cells, origin):
    os.makedirs(STR, exist_ok=True)
    p = os.path.join(OUT, "tpl_grove_%s.txt" % name)
    with open(p, "w") as f:
        for (x, y, z), s in sorted(cells.items()): f.write("%d %d %d %s\n" % (x, y, z, s))
    r = subprocess.run([os.path.join(ROOT, "tools/blockwriter.sh"), "nbt", p, str(origin[0]), str(origin[1]), str(origin[2]), os.path.join(STR, name + ".nbt")], capture_output=True, text=True)
    if r.returncode or "nbt:" not in r.stdout: raise SystemExit(r.stdout + r.stderr)

# ---------------------------------------------------------------- the plan
def plan_png(gr, rl, b, meta, path, info):
    from PIL import Image, ImageDraw
    S = 6; x1, z1, x2, z2 = P.CX - P.R - 18, P.CZ - P.R - 18, P.CX + P.R + 18, P.CZ + P.R + 18
    w, h = (x2 - x1 + 1) * S, (z2 - z1 + 1) * S
    img = Image.new("RGB", (w, h + 110), (20, 20, 24)); d = ImageDraw.Draw(img)
    T = rl["T"]
    tops = {}
    for (x, y, z), s in b.v.items():
        if s == "minecraft:air" or not (x1 <= x <= x2 and z1 <= z <= z2): continue
        if y >= tops.get((x, z), (-999, ""))[0]: tops[(x, z)] = (y, s)
    for z in range(z1, z2 + 1):
        for x in range(x1, x2 + 1):
            i, j = ix(gr, x, z); y = int(T[i, j])
            gcol = int(np.clip(40 + (y - 85) * 2.2, 25, 250)); col = (gcol // 2 + 25, gcol // 2 + 30, gcol // 3 + 20)
            if T[i, j] != gr["before"][i, j]: col = (col[0] + 30, col[1] + 10, col[2])
            t = tops.get((x, z))
            if t:
                s = t[1].split("[")[0].split("{")[0]
                if "red_mushroom_block" in s: col = (190, 45, 40)
                elif "brown_mushroom_block" in s: col = (150, 105, 70)
                elif "poplar_leaves" in s: col = (200, 150, 40) if "yellow" in s else (210, 110, 40) if "orange" in s else (180, 60, 40)
                elif "cobblestone" in s and "wall" not in s: col = (150, 150, 150)
                elif "wall" in s: col = (110, 110, 120)
                elif "bricks" in s or "campfire" in s: col = (200, 90, 60)
                elif "farmland" in s or "wheat" in s or "carrots" in s or "potatoes" in s or "beet" in s: col = (120, 170, 60)
                elif "shroomlight" in s: col = (255, 200, 90)
                elif "fence" in s or "stairs" in s: col = (150, 110, 70)
            if gr["pad"][i, j]: col = (110, 90, 70)
            if rl["app"][i, j]: col = (170, 160, 130)
            if not gr["place"][i, j]: col = tuple(v // 3 for v in col)
            elif not gr["circle"][i, j]: col = tuple(int(v * 0.6) for v in col)
            d.rectangle([(x - x1) * S, (z - z1) * S, (x - x1) * S + S - 1, (z - z1) * S + S - 1], fill=col)
    def P2(x, z): return ((x - x1) * S + S // 2, (z - z1) * S + S // 2)
    def circ(x, z, r, c, wdt=2): cx, cz = P2(x, z); d.ellipse([cx - r * S, cz - r * S, cx + r * S, cz + r * S], outline=c, width=wdt)
    circ(P.CX, P.CZ, P.R, (230, 230, 230)); circ(P.CX, P.CZ, P.R + P.MARGIN, (120, 120, 120), 1)
    circ(P.HX, P.HZ, P.CAP_R, (255, 80, 60), 3)
    d.rectangle([(P.STEM[0] - x1) * S, (P.STEM[1] - z1) * S, (P.STEM[2] + 1 - x1) * S, (P.STEM[3] + 1 - z1) * S], outline=(255, 255, 255), width=2)
    d.rectangle([(P.TERRACE[0] - x1) * S, (P.TERRACE[1] - z1) * S, (P.TERRACE[2] + 1 - x1) * S, (P.TERRACE[3] + 1 - z1) * S], outline=(255, 220, 120), width=2)
    d.rectangle([(P.GARDEN[0] - x1) * S, (P.GARDEN[1] - z1) * S, (P.GARDEN[2] + 1 - x1) * S, (P.GARDEN[3] + 1 - z1) * S], outline=(120, 230, 90), width=2)
    d.rectangle([(P.PAD[0] - x1) * S, (P.PAD[1] - z1) * S, (P.PAD[2] + 1 - x1) * S, (P.PAD[3] + 1 - z1) * S], outline=(255, 140, 0), width=2)
    hx, hz = P2(P.HEARTH[0], P.HEARTH[2]); d.ellipse([hx - 6, hz - 6, hx + 6, hz + 6], fill=(255, 140, 0))
    for gi in meta["giants"]:
        cx, cz = P2(gi["x"], gi["z"]); d.text((cx - 8, cz - 6), "G", fill=(255, 255, 255))
    for f in meta["faces"]:
        cx, cz = P2(f["x"], f["z"]); d.rectangle([cx - 9, cz - 9, cx + 9, cz + 9], outline=(80, 255, 220), width=3)
        ex, ez = P2(f["eye"][0], f["eye"][2]); d.line([cx, cz, ex, ez], fill=(80, 255, 220), width=3); d.text((cx + 10, cz - 6), "face %d" % f["k"], fill=(80, 255, 220))
    for p in meta["poplars"]:
        cx, cz = P2(p["x"], p["z"]); d.ellipse([cx - 3, cz - 3, cx + 3, cz + 3], fill=(250, 200, 60))
    for (x, y, z) in meta.get("glow", []):
        cx, cz = P2(x, z); d.ellipse([cx - 4, cz - 4, cx + 4, cz + 4], outline=(255, 240, 150), width=2)
    for k, c in (("day", (255, 255, 80)), ("night", (120, 160, 255))):
        x, y, z = meta[k]; cx, cz = P2(x, z); d.ellipse([cx - 7, cz - 7, cx + 7, cz + 7], fill=c); d.text((cx + 9, cz - 16), "Advisor " + k, fill=c)
    lines = ["T-030 Mushroom Grove of the Advisor: plan (1 block = %d px, north up). White circle = place r 45, grey = seam r 61; relief by height (lighter = higher, reddish = changed)" % S,
             "house: stem 9x9 (white), cap r 10.5 (red), terrace y %d (yellow box: cut/fill <= %d); garden y %d (green box, <= %d) north of the pad of bonfire 10 (orange); path y %d..%d by half blocks (cut/fill <= %.1f)"
             % (info["L"], info["terrace_max"], P.PAD_Y, info["garden_max"], info["L"], P.PAD_Y, info["path_max"]),
             "door %.1f from the pad, cap reaches r %.1f; G = giant mushrooms (%d), yellow dots = poplars (%d), cyan = thick poplars with faces (line = where the face looks), rings = glowing mushrooms (%d)"
             % (info["door_dist"], info["cap_r"], len(meta["giants"]), len(meta["poplars"]), len(meta.get("glow", []))),
             "Advisor: day = armchair by the hearth (yellow), night = observatory by the spyglass (blue); approaches of T-022 (sand) keep their heights; retaining walls %d cells" % meta["walls"],
             "light: walked cells %s lit, circle %d of %d lit" % ("all" if meta["light"]["must_dark"] == 0 else "NOT all", meta["light"]["rest"] - meta["light"]["rest_dark"], meta["light"]["rest"])]
    for k, t in enumerate(lines): d.text((6, h + 6 + 18 * k), t, fill=(255, 255, 255))
    img.save(path)

def zone_line(gr, rl, b):
    from r1 import replace_lines
    T = rl["T"]; lo = int(T[gr["circle"]].min()) - 4
    hi = max(y for (x, y, z), s in b.v.items() if s != "minecraft:air" and P.in_circle(x, z)) + 8
    replace_lines(os.path.join(ROOT, "zones/zones.txt"), ["grove "],
                  ["grove           overworld cyl %d %d %d %d %d   no_spawn   # T-030: the Mushroom Grove of the Advisor (adventure, no monsters)" % (P.CX, P.CZ, P.R, lo, hi)])
    return lo, hi

def main(plan_only=False):
    gr = P.grids()
    if "live" not in gr: raise SystemExit("no server/build/r1/grove_pre.bin: tools/terrain.sh scan %d %d %d %d server/build/r1/grove_pre.bin" % P.BOX)
    rl = P.relief(gr)
    info = P.checks(gr, rl)
    b, meta, templates = build(gr, rl)
    meta["glow"] = place_lights(b, gr, rl, meta)
    nair = surface(b, gr, rl) if not plan_only else 0
    napp = approaches(b, gr, rl) if not plan_only else 0
    ntree, nsnow, nwat = untree_unsnow(b, gr, rl) if not plan_only else (0, 0, 0)
    from connect import connect
    connect(b)
    bad = [k for k in b.v if not P.in_place(k[0], k[2])]
    if bad: raise SystemExit("blocks outside the place: %s" % bad[:5])
    for k in [k for k in b.v if P.on_pad(k[0], k[2]) and k[1] > P.PAD_Y + 6]: del b.v[k]     # crowns hanging over the pad's edge
    pad = [k for k in b.v if P.on_pad(k[0], k[2])]
    if pad: raise SystemExit("blocks on the pad of bonfire 10: %s" % pad[:5])
    os.makedirs(os.path.join(ROOT, "docs/reports/T-030"), exist_ok=True)
    plan_png(gr, rl, b, meta, os.path.join(ROOT, "docs/reports/T-030/grove_plan.png"), info)
    if plan_only:
        print("plan:", info, meta["light"]); return meta
    for k, (cl, op) in templates.items():
        o = meta["faces"][k - 1]["origin"]
        nbt("face_%d_closed" % k, cl, o); nbt("face_%d_open" % k, op, o)
    ncol = write_terrain(gr, rl, b)
    n = b.write_placements(os.path.join(OUT, "grove.txt"))
    zlo, zhi = zone_line(gr, rl, b)
    out = dict(meta); out.update(info=info, terrain_columns=ncol, blocks=n, air=nair, approach_top=napp, trees_removed=ntree, snow=nsnow, springs=nwat,
                                 zone=[zlo, zhi], bonfire=list(P.HEARTH), pad=list(P.PAD), centre=[P.CX, P.CZ, P.R], house=[P.HX, P.HZ])
    import grove_dp
    grove_dp.run(out)
    json.dump(out, open(os.path.join(OUT, "grove.json"), "w"), ensure_ascii=False, default=lambda o: list(o) if isinstance(o, (set, tuple)) else str(o))
    print(f"grove: terrain {ncol} columns, {n} blocks (air {nair}, approach tops {napp}, old trees {ntree}, snow {nsnow}, spring water {nwat}), L {info['L']}, "
          f"giants {len(meta['giants'])}, faces {len(meta['faces'])}, poplars {len(meta['poplars'])}, glow {len(meta['glow'])}, light {meta['light']}")

if __name__ == "__main__" and sys.argv[1:2] == ["plan"]:
    main(plan_only=True)
elif __name__ == "__main__":
    main()
