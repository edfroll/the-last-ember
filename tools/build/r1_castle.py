#!/usr/bin/env python3
"""T-028: the approaches to the Enchanted Castle (Р1) on the place `castle` (circle r 100 round (450, 0) + 16 of seam) of
tools/build/r1_plots.txt: the gorge with the lake, the descent from bonfire 7, the causeway, the pier between the two colossi, the sword of
the fallen Bearer, the knock zone and the sandy way out, the stair in the rock with the rest platform and the ambush niches, the
bridgehead with bonfire 8, the rift, the bridge, the barbican with its locked gate, the castle table (left empty for the castle task).

  python3 tools/build/r1_castle.py        -> server/build/r1/castle_terrain.bin (tools/terrain.sh apply), castle.txt (tools/blockwriter.sh
                                             apply), castle.json (points for the tests, the bot and the datapack), docs/reports/T-028/
                                             castle_plan.png, structure/castle/*.nbt, datapack function/castle/gen/* (tools/build/castle_dp.py)
  python3 tools/build/r1_castle.py plan   only the plan (and the stop conditions of HQ T-028, 1)
Inputs: server/build/r1/base.bin, terrain.bin, allow.npz (the R1 frame), castle_pre.bin (scan of the place now; the re-run writes only
the columns that differ from what they should be). The castle itself (next task) is to be added to this module (build_castle hook);
the approaches do not depend on it."""
import json, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import write_grid, NONE
from lib import B, h as hsh
import castle_plan as P
import castle_build as CB

ROOT, OUT = P.ROOT, P.OUT
R_CASTLE = 9                               # Terrain.java rock style 9 (the card's palette of the rock)
S_FOREST, S_PLATFORM, S_BARE, S_TOP, S_BED = 2, 7, 10, 11, 12

def lights_bridgehead(b, gr, rl, taken):
    """lanterns on posts (2 walls + a lantern at the rock top + 3) over the bridgehead, placed greedily until every cell of it has block
    light >= 1 at the feet (no monster spawns at block light 0): |dx| + |dz| + 2 <= 14 from a lantern; never on the pad, the slots, the
    walked line (x 433 and z 2 to the bridge) or next to them"""
    X, Z = gr["X"], gr["Z"]
    cells = [(int(X[i, j]), int(Z[i, j])) for i, j in zip(*np.nonzero(rl["pred"] & ~gr["pad"]))]
    occ = set(taken)
    def bad(x, z):
        if (x, z) in occ or gr["pad"][P.ix(gr, x, z)] or not rl["pred"][P.ix(gr, x, z)]: return True
        if any((x + a, z + c) in occ for a in (-1, 0, 1) for c in (-1, 0, 1)): return True
        bx = (P.BRIDGE_X[0] + P.BRIDGE_X[1]) // 2           # the walked line: from the top of the stair east along z -28, then south to the bridge
        if abs(z - (P.LANE_B[1] + 2)) <= 1 and x <= bx + 2 or abs(x - bx) <= 3 and z >= P.LANE_B[1]: return True
        return x <= P.FACE_X
    cand = [c for c in cells if not bad(*c)]
    left = set(cells); out = []
    while left:
        best = max(cand, key=lambda c: (sum(1 for q in left if abs(q[0] - c[0]) + abs(q[1] - c[1]) <= 12), -c[0], -c[1]))
        cov = {q for q in left if abs(q[0] - best[0]) + abs(q[1] - best[1]) <= 12}
        if not cov: break
        left -= cov; x, z = best; cand = [c for c in cand if abs(c[0] - x) + abs(c[1] - z) > 6]
        b.set(x, P.PRED_Y + 1, z, "minecraft:stone_brick_wall"); b.set(x, P.PRED_Y + 2, z, "minecraft:stone_brick_wall"); b.set(x, P.PRED_Y + 3, z, CB.lantern())
        out.append((x, P.PRED_Y + 3, z))
    if left: raise SystemExit("the bridgehead: no lantern can light %s" % sorted(left)[:6])
    return out

def rock_surface(b, gr, rl):
    """the rock (bridgehead, table, peak) where its top is the natural ground (the terrain write skips such a column): the top block of the
    card's rock with moss like the rewritten ones, nothing growing on it (air from the top to what stood there: the trees of the table)"""
    T, bf = rl["Tw"], gr["before"]; n = 0
    for i, j in zip(*np.nonzero(rl["rock"] & (T == bf) & ~gr["pad"])):
        x, z = j + gr["x1"], i + gr["z1"]; y = int(T[i, j])
        if (x, z) in rl["hang"]: continue
        if b.get(x, y, z) is None: b.set(x, y, z, CB.top_at(x, y, z, 0))
        top = int(gr["top"][i, j]) if "top" in gr else y
        for yy in range(y + 1, min(top, y + 40) + 1):
            if b.get(x, yy, z) is None: b.set(x, yy, z, "minecraft:air"); n += 1
    return n

def build(gr, rl):
    b = B("castle"); meta = dict(W=P.W, P=rl["P"])
    cn, mn = CB.colossus(-46, +1); cs, ms = CB.colossus(-21, -1)
    for m in (cn, cs):
        for k, s in m.items(): b.set(*k, s)
    meta["colossi"] = {"n": mn, "s": ms}
    meta["pier_posts"] = CB.pier(b, gr, rl)
    meta["causeway"], meta["piles"] = CB.causeway(b, gr, rl)
    CB.sand(b, gr, rl)
    meta["sword"] = CB.sword(b)
    meta["recess"] = CB.recess(b, gr, rl)
    meta["grooves"] = CB.face_grooves(b, gr, rl)
    meta["overhang_blocks"] = CB.overhangs(b, gr, rl)
    meta["desc_lamps"] = CB.descent(b, rl)
    meta["stair"] = CB.stair_blocks(b)
    meta["bridge"] = CB.bridge(b)
    meta["barbican"] = CB.barbican(b, rl["P"])
    taken = set()
    for (x, y, z) in b.v: taken.add((x, z))
    meta["pred_lamps"] = lights_bridgehead(b, gr, rl, taken)
    meta["rock_top_cleared"] = rock_surface(b, gr, rl)
    meta["moss_carpets"] = CB.moss_edges(b, gr, rl, lambda x, z: (x, z) not in taken)
    # boulders on the rift floor (dry, under the bridge "the abyss")
    T = rl["Tw"]; nb = 0
    for i, j in zip(*np.nonzero(rl["rift"])):
        x, z = j + gr["x1"], i + gr["z1"]
        if hsh(x, 7, z, 2850) < 0.035 and (x, z) not in taken and not (P.BRIDGE_X[0] <= x <= P.BRIDGE_X[1]):
            y = int(T[i, j]); b.set(x, y + 1, z, "minecraft:mossy_cobblestone" if hsh(x, 8, z, 2851) < 0.5 else "minecraft:andesite"); nb += 1
            if hsh(x, 9, z, 2852) < 0.3: b.set(x, y + 2, z, "minecraft:cobblestone")
    meta["boulders"] = nb
    # the lake columns that carry our blocks (colossi, pier, causeway, islet, sand, platform): the rest of the column is written too
    # (water to W, air above to the old top): the terrain write skips a column whose scanned top already looks right (a colossus
    # where the plateau stood at its height), and the natural rock, snow or trees inside it would stay
    cols = {}
    for (x, y, z) in b.v: cols.setdefault((x, z), []).append(y)
    for (x, z), ys in cols.items():
        i, j = P.ix(gr, x, z)
        if rl["Wt"][i, j] == NONE: continue
        top = max(int(gr["top"][i, j]) if "top" in gr else 0, max(ys), P.W + 1) + 2
        for y in range(int(T[i, j]) + 1, min(top, 320) + 1):
            if b.get(x, y, z) is None: b.set(x, y, z, "minecraft:water[level=0]" if y <= P.W else "minecraft:air")
    return b, meta

def drain(b, gr, rl):
    """standing water above the ground that our cuts would spill (natural pools of the plateau, the pool the R1 frame left over the west
    edge of the pad of bonfire 8): every pool touching a column that is now lower than its water goes, all of it (air from the ground
    up). Read from the scan before the place (castle_pre.bin): a re-run finds none. The pads' ground is not touched (only water over it)."""
    if "lwater" not in gr: return 0
    T, now, lw = rl["Tw"], gr["live"], gr["lwater"]
    wet = (lw != NONE) & (lw > now) & gr["place"] & (rl["Wt"] == NONE)
    rew = (T != gr["before"]) | (rl["Wt"] != NONE)
    seed = np.zeros(T.shape, bool)
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nT = np.roll(np.roll(T, dz, 0), dx, 1); nwet = np.roll(np.roll(wet, dz, 0), dx, 1)
        seed |= wet & ~nwet & (nT < lw)
    pools = P.flood(wet, list(zip(*np.nonzero(seed))))
    n = 0
    for i, j in zip(*np.nonzero(pools)):
        if rew[i, j] and not gr["pad"][i, j]: continue            # the terrain rewrites this column anyway
        x, z = j + gr["x1"], i + gr["z1"]
        for y in range(int(now[i, j]) + 1, int(lw[i, j]) + 1):
            if b.get(x, y, z) is None: b.set(x, y, z, "minecraft:air"); n += 1
    return n

def unsnow(b, gr, rl):
    """HQ T-028, 1: no snow in the place (snow blocks / powder snow under the ground: dirt within 3, stone deeper; snow layers: air; snowy
    grass: not snowy), no spruces (air; dark oaks of our model where they stood, on the untouched natural ground). Read from the world."""
    import fens_scan, re
    from lib import Mix
    T = rl["Tw"]; n = 0; spruce = set()
    changed, F = rewritten(gr, rl)
    steep = np.zeros(T.shape, bool)
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): steep |= np.abs(np.roll(np.roll(T, dz, 0), dx, 1) - T) >= 3
    ROCK = Mix({"stone": 4, "andesite": 2, "tuff": 2, "cobblestone": 1}, 2861)
    fens_scan.BAN = re.compile(fens_scan.BAN.pattern[:-2] + "|packed_ice|blue_ice)$")   # + the ice of the peak (not snow, but white-blue)
    inside = lambda x, z: bool(P.in_place(x, z)) and not gr["pad"][P.ix(gr, x, z)]
    for (x, y, z, nm) in fens_scan.scan(os.path.join(ROOT, "server/world"), box=P.BOX, inside=inside):
        if b.get(x, y, z) is not None: continue
        i, j = P.ix(gr, x, z); g = int(T[i, j])
        if "spruce_log" in nm: spruce.add((x, z))
        if changed[i, j]:                       # the terrain rewrites this column from F up: only the snow under it is ours to replace
            if y < F[i, j]: b.set(x, y, z, "minecraft:stone"); n += 1
            continue
        if nm in ("minecraft:snow_block", "minecraft:powder_snow", "minecraft:packed_ice", "minecraft:blue_ice") and y <= g:
            if steep[i, j] or "ice" in nm: b.set(x, y, z, ROCK.at(x, y, z))
            else: b.set(x, y, z, ("minecraft:grass_block[snowy=false]" if y == g else "minecraft:dirt") if y >= g - 3 else "minecraft:stone")
        elif "ice" in nm: b.set(x, y, z, ROCK.at(x, y, z))
        else: b.set(x, y, z, "minecraft:air")
        n += 1
    for (x, y, z) in snowy_grass(gr):
        i, j = P.ix(gr, x, z)
        if b.get(x, y, z) is None and not (changed[i, j] and y >= F[i, j]): b.set(x, y, z, "minecraft:grass_block[snowy=false]"); n += 1
    return n, spruce

def rewritten(gr, rl):
    """the columns the terrain write rewrites (changed ground or water) and their floor F (the same formula as write_terrain)"""
    T = rl["Tw"]; now = gr["live"]
    lo = T.copy()
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): lo = np.minimum(lo, np.roll(np.roll(lo, dz, 0), dx, 1))
    F = np.minimum(np.minimum(T, now), lo) - 4
    return (T != gr["before"]) | (rl["Wt"] != NONE), F

def springs(b, gr, rl):
    """natural springs above the lake (water / lava in the place, out of the lake): a source in a cliff face would run down the sheer edge
    of the rock and the walls of the gorge (and a waterfall can be swum up). Inside the ground -> rock, open on top -> air. Read from the
    world: a re-run finds none."""
    import fens_scan
    from lib import Mix
    ROCK = Mix({"stone": 4, "andesite": 2, "tuff": 2}, 2862)
    out = []; x1, z1, x2, z2 = P.BOX; sb = fens_scan.sb; T = rl["Tw"]; g = gr.get("live", gr["before"])
    for rx in range(x1 // 512, x2 // 512 + 1):
        for rz in range(z1 // 512, z2 // 512 + 1):
            path = os.path.join(ROOT, "server/world/dimensions/minecraft/overworld/region", "r.%d.%d.mca" % (rx, rz))
            if not os.path.exists(path): continue
            for c in sb.chunks(path):
                cx, cz = c.get("xPos"), c.get("zPos")
                if cx is None or cx * 16 + 15 < x1 or cx * 16 > x2 or cz * 16 + 15 < z1 or cz * 16 > z2: continue
                for s in c.get("sections", []):
                    if (s.get("Y", 0) + 1) * 16 <= P.W + 2: continue
                    bs = s.get("block_states") or {}; pal = bs.get("palette", [])
                    hit = [k for k, p in enumerate(pal) if (p if isinstance(p, str) else (p.get("id") or p.get("Name") or "")) in ("minecraft:water", "minecraft:lava")]
                    if not hit: continue
                    data = bs.get("data") or []
                    if len(pal) == 1: idx = [0] * 4096
                    else:
                        bits = max(4, (len(pal) - 1).bit_length()); per = 64 // bits; idx = []
                        for v in data:
                            v &= (1 << 64) - 1
                            for k in range(per):
                                if len(idx) < 4096: idx.append((v >> (k * bits)) & ((1 << bits) - 1))
                    for n_, i in enumerate(idx):
                        if i not in hit: continue
                        x, y, z = cx * 16 + n_ % 16, s.get("Y", 0) * 16 + n_ // 256, cz * 16 + (n_ // 16) % 16
                        if y <= P.W + 1 or not (x1 <= x <= x2 and z1 <= z <= z2) or not P.in_place(x, z): continue
                        ii, jj = P.ix(gr, x, z)
                        if rl["Wt"][ii, jj] != NONE or b.get(x, y, z) is not None: continue
                        if gr["pad"][ii, jj] and y <= int(g[ii, jj]): continue
                        out.append((x, y, z, y < int(g[ii, jj]) and y <= int(T[ii, jj])))
    for (x, y, z, inside) in out: b.set(x, y, z, ROCK.at(x, y, z) if inside else "minecraft:air")
    return len(out)

def snowy_grass(gr):
    """grass / podzol / mycelium with snowy=true in the place (the snow layer over it is gone)"""
    import fens_scan
    out = []; x1, z1, x2, z2 = P.BOX
    sb = fens_scan.sb
    for rx in range(x1 // 512, x2 // 512 + 1):
        for rz in range(z1 // 512, z2 // 512 + 1):
            path = os.path.join(ROOT, "server/world/dimensions/minecraft/overworld/region", "r.%d.%d.mca" % (rx, rz))
            if not os.path.exists(path): continue
            for c in sb.chunks(path):
                cx, cz = c.get("xPos"), c.get("zPos")
                if cx is None or cx * 16 + 15 < x1 or cx * 16 > x2 or cz * 16 + 15 < z1 or cz * 16 > z2: continue
                for s in c.get("sections", []):
                    bs = s.get("block_states") or {}; pal = bs.get("palette", [])
                    hit = [k for k, p in enumerate(pal) if isinstance(p, dict) and (p.get("id") or p.get("Name") or "").endswith(("grass_block", "podzol", "mycelium"))
                           and str((p.get("properties") or p.get("Properties") or {}).get("snowy")) == "true"]
                    if not hit: continue
                    data = bs.get("data") or []; bits = max(4, (len(pal) - 1).bit_length()); per = 64 // bits; idx = []
                    for v in data:
                        v &= (1 << 64) - 1
                        for k in range(per):
                            if len(idx) < 4096: idx.append((v >> (k * bits)) & ((1 << bits) - 1))
                    for n_, i in enumerate(idx):
                        if i not in hit: continue
                        x, y, z = cx * 16 + n_ % 16, s.get("Y", 0) * 16 + n_ // 256, cz * 16 + (n_ // 16) % 16
                        if x1 <= x <= x2 and z1 <= z <= z2 and P.in_place(x, z) and not gr["pad"][P.ix(gr, x, z)]: out.append((x, y, z))
    return out

def trees(b, gr, rl, spruce):
    """one dark oak (our repeatable model) for every spruce tree that stood on ground we did not change, nothing near what we built.
    The spruce trunks are read from the world on the first run and kept in server/build/r1/castle_spruce.json (a re-run finds none)."""
    cache = os.path.join(OUT, "castle_spruce.json")
    if spruce: json.dump(sorted(spruce), open(cache, "w"))
    elif os.path.exists(cache): spruce = {tuple(p) for p in json.load(open(cache))}
    T, bf = rl["T"], gr["before"]; spots = []; seen = set()
    for (x, z) in sorted(spruce):
        if any((x + a, z + c) in seen for a in range(-3, 4) for c in range(-3, 4)): continue
        seen.add((x, z)); spots.append((x, z))
    n = 0
    for (x, z) in spots:
        i, j = P.ix(gr, x, z)
        blk = T[i - 2:i + 4, j - 2:j + 4]; nat = bf[i - 2:i + 4, j - 2:j + 4]
        if (blk != nat).any() or rl["rock"][i - 3:i + 5, j - 3:j + 5].any() or rl["moat"][i - 3:i + 5, j - 3:j + 5].any(): continue
        if np.abs(T[i - 1:i + 3, j - 1:j + 3] - T[i, j]).max() > 4 or gr["allow"][i, j]: continue
        if any(b.get(x + a, y, z + c) not in (None, "minecraft:air") for a in range(-3, 5) for c in range(-3, 5)
               for y in range(int(T[P.ix(gr, x + a, z + c)]) + 1, int(T[i, j]) + 14)): continue
        CB.dark_oak(b, x, z, int(T[i, j]), 2860 + (x * 7 + z) % 31, lambda xx, zz: int(T[P.ix(gr, xx, zz)])); n += 1
    return n

def write_terrain(gr, rl, b):
    """only the columns whose scan is not yet what it should be (a re-run on the built place rewrites nothing)"""
    import r1_fens as RF
    T, Wt = rl["Tw"], rl["Wt"]; bf = gr["before"]
    now, nw = gr["live"], gr["lwater"]
    cols = {}
    for (x, y, z), s_ in b.v.items(): cols.setdefault((x, z), {})[y] = s_
    cand = gr["place"] & ~gr["pad"]
    touch = np.zeros(T.shape, bool)
    for i, j in zip(*np.nonzero(cand)):
        x, z = j + gr["x1"], i + gr["z1"]
        if T[i, j] == bf[i, j] and Wt[i, j] == NONE and now[i, j] == bf[i, j] and nw[i, j] == NONE and (x, z) not in cols: continue
        eg, ew = RF.expected_scan(T, Wt, cols, x, z, i, j)
        if now[i, j] != eg or nw[i, j] != ew: touch[i, j] = True
    H = np.where(touch, T, NONE).astype(np.int32)
    F = rewritten(gr, rl)[1]
    steep = np.zeros(T.shape, bool)
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): steep |= np.abs(np.roll(np.roll(T, dz, 0), dx, 1) - T) >= 3
    S = np.where(steep, S_BARE, S_FOREST).astype(np.uint8)
    S[rl["rift"] | rl["moat"]] = S_PLATFORM
    S[rl["rock"]] = S_TOP
    for (x, z) in rl["hang"]: S[P.ix(gr, x, z)] = S_PLATFORM      # the ground under an overhang is the moat's
    S[Wt != NONE] = S_BED
    Wg = np.where(touch, Wt, NONE).astype(np.int32)
    write_grid(os.path.join(OUT, "castle_terrain.bin"), gr["x1"], gr["z1"], H, F, Wg, S, np.full(T.shape, R_CASTLE, np.uint8), np.zeros(T.shape, np.uint8))
    return int(touch.sum())

def nbt(name, cells, origin=None):
    """a structure template of the cells (BlockWriter nbt; origin = the min corner unless given)"""
    STR = os.path.join(ROOT, "datapack/data/last_ember/structure/castle"); os.makedirs(STR, exist_ok=True)
    ox = min(p[0] for p in cells) if origin is None else origin[0]; oy = min(p[1] for p in cells) if origin is None else origin[1]
    oz = min(p[2] for p in cells) if origin is None else origin[2]
    p = os.path.join(OUT, "tpl_castle_%s.txt" % name)
    with open(p, "w") as f:
        for (x, y, z), s in sorted(cells.items()): f.write("%d %d %d %s\n" % (x, y, z, s))
    r = subprocess.run([os.path.join(ROOT, "tools/blockwriter.sh"), "nbt", p, str(ox), str(oy), str(oz), os.path.join(STR, name + ".nbt")], capture_output=True, text=True)
    if r.returncode or "nbt:" not in r.stdout: raise SystemExit(r.stdout + r.stderr)
    return [ox, oy, oz]

def templates(b, gr, rl, meta):
    """the colossi in two pieces each (lo: plinth .. W+23, hi: W+24 .. the crown; the card), the south colossus's hi piece without the
    raised arm (the faded lake), the lake tiles alive / faded (the swamp of the fade: water W-1..W, mud under, hummocks, sedge, lilies)"""
    out = {}
    for key in ("n", "s"):
        c = meta["colossi"][key]; x1, y1, z1, x2, y2, z2 = c["box"]
        for part, (ya, yb) in (("lo", (y1, P.W + 23)), ("hi", (P.W + 24, y2))):
            cells = {(x, y, z): b.get(x, y, z) or "minecraft:air" for x in range(x1, x2 + 1) for y in range(ya, yb + 1) for z in range(z1, z2 + 1)}
            for k in cells:
                if cells[k] == "minecraft:air" and ya <= P.W and k[1] <= P.W: cells[k] = "minecraft:water[level=0]"
            out["colossus_%s_%s" % (key, part)] = nbt("colossus_%s_%s" % (key, part), cells, (x1, ya, z1))
    c = meta["colossi"]["s"]; x1, y1, z1, x2, y2, z2 = c["box"]; arm = set(map(tuple, c["arm"]))
    cells = {(x, y, z): ("minecraft:air" if (x, y, z) in arm else (b.get(x, y, z) or "minecraft:air")) for x in range(x1, x2 + 1) for y in range(P.W + 24, y2 + 1) for z in range(z1, z2 + 1)}
    out["colossus_s_hi_broken"] = nbt("colossus_s_hi_broken", cells, (x1, P.W + 24, z1))
    # the lake: tiles of 32 x 32; the cells from the lake floor + 1 to W + 2 that are water now (nothing of ours there)
    T, Wt = rl["T"], rl["Wt"]; fallen = CB.fallen_arm(-21, -1)
    tiles = {}
    for i, j in zip(*np.nonzero(Wt != NONE)):
        x, z = j + gr["x1"], i + gr["z1"]; fl = int(T[i, j])
        for y in range(fl + 1, P.W + 3):
            if b.get(x, y, z) not in (None, "minecraft:air", "minecraft:water[level=0]"): continue
            alive = "minecraft:water[level=0]" if y <= P.W else "minecraft:air"
            if (x, y, z) in fallen: dead = fallen[(x, y, z)]
            elif y <= P.W - 2: dead = "minecraft:mud"
            elif y <= P.W:
                hum = hsh(x // 2, 0, z // 2, 2870) < 0.16 and not rl["knock"][i, j] or hsh(x, 1, z, 2871) < 0.04
                dead = ("minecraft:mud" if y < P.W else "minecraft:muddy_mangrove_roots[axis=y]" if hsh(x, 2, z, 2872) < 0.2 else "minecraft:moss_block") if hum else \
                       ("minecraft:seagrass" if y == P.W - 1 and hsh(x, 3, z, 2873) < 0.25 else "minecraft:water[level=0]")
            elif y == P.W + 1:
                hum = hsh(x // 2, 0, z // 2, 2870) < 0.16 and not rl["knock"][i, j] or hsh(x, 1, z, 2871) < 0.04
                r_ = hsh(x, 4, z, 2874)
                dead = ("minecraft:short_grass" if r_ < 0.4 else "minecraft:fern" if r_ < 0.55 else "minecraft:sugar_cane[age=0]" if r_ < 0.75 else "minecraft:air") if hum \
                       else ("minecraft:lily_pad" if r_ < 0.07 else "minecraft:air")
            else:
                below = hsh(x, 4, z, 2874)
                hum = hsh(x // 2, 0, z // 2, 2870) < 0.16 and not rl["knock"][i, j] or hsh(x, 1, z, 2871) < 0.04
                dead = "minecraft:sugar_cane[age=0]" if hum and 0.55 <= below < 0.75 and hsh(x, 5, z, 2875) < 0.5 else "minecraft:air"
            k = ((x - P.LAKE[1][0]) // 32, (z - P.LAKE[0][1]) // 32)
            tiles.setdefault(k, ({}, {}))
            tiles[k][0][(x, y, z)] = alive; tiles[k][1][(x, y, z)] = dead
    # sugar cane only where it stands on mud/moss next to water (else air): checked on the dead tile itself
    lt = []
    for k, (al, de) in sorted(tiles.items()):
        for (x, y, z), s in list(de.items()):
            if "sugar_cane" in s:
                under = de.get((x, y - 1, z)) or ""; ok = ("mud" in under or "moss" in under) or (y == P.W + 2 and "sugar_cane" in under)
                if y == P.W + 1 and ok: ok = any("water" in (de.get((x + a, P.W, z + c)) or "") for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if not ok: de[(x, y, z)] = "minecraft:air"
        name = "lake_%d_%d" % k
        o = (min(p[0] for p in al), min(p[1] for p in al), min(p[2] for p in al))
        nbt(name + "_alive", al, o); nbt(name + "_faded", de, o); lt.append([name, list(o)])
    out["lake_tiles"] = lt
    return out

def plan_main(gr=None):
    gr = gr or P.grids(); rl = P.relief(gr); ch = P.checks(gr, rl)
    return gr, rl, ch

def main(plan_only=False):
    gr, rl, ch = plan_main()
    if ch["stop"]: raise SystemExit("STOP (HQ T-028, 1): %s" % ch["stop"])
    os.makedirs(os.path.join(ROOT, "docs/reports/T-028"), exist_ok=True)
    txt = ["T-028 castle approaches: plan (1 block = 4 px, north up). W = %d (lake), P = %d (table), bridgehead %d; blue = lake, light blue = knock zone 16x14 (floor W-5);" % (P.W, ch["P"], P.PRED_Y),
           "brown = the rock (bridgehead, NE peak, table), lilac = the dry moat (>= 6 under the rock within %d, then 1:1), dark = the rift (floor W+2 sill .. W-7, dry)," % P.MOAT_D,
           "grey = causeway (3 wide, W+1), sand = the way out (+0.5 a cell), boxes: colossi (12 x 11, 50 high from W), pier 12 x 9, red = the colossi trigger, magenta = the rest platform",
           "7x7 (y 140) and the 2 niches 3x3x4 (y %d..%d); yellow = the stair in the rock (F1..F4, 116 -> 162), the descent from bonfire 7 (%d cells, 167 -> 116); bridge 25, barbican." % (P.NICHE_Y + 1, P.NICHE_Y + 4, ch["desc_cells"]),
           "Checks: rock edge min %d (>= 6) on %d cells, max fill under the rock %d (<= 40), moat out of the place %d, knock zone depth >= %d; green circle = biome castle_dream r 100, red = the place r 116." % (ch["edge_min"], ch["edge_cells"], ch["max_fill_rock"], ch["moat_out_of_place"], ch["knock_min_depth"])]
    P.plan_png(gr, rl, os.path.join(ROOT, "docs/reports/T-028/castle_plan.png"), txt)
    if plan_only:
        for k, v in ch.items(): print(k, v)
        return
    b, meta = build(gr, rl)
    meta["drained"] = drain(b, gr, rl)
    meta["springs"] = springs(b, gr, rl)
    nsnow, spruce = unsnow(b, gr, rl)
    meta["trees"] = trees(b, gr, rl, spruce)
    from connect import connect
    connect(b)
    bad = [k for k in b.v if not P.in_place(k[0], k[2])]
    if bad: raise SystemExit("blocks outside the place: %s" % bad[:5])
    pad = [k for k, v in b.v.items() if gr["pad"][P.ix(gr, k[0], k[2])] and not (v == "minecraft:air" and k[1] > (P.PAD8_Y if k[0] > 400 else P.PAD7_Y))]
    if pad: raise SystemExit("blocks on a bonfire pad: %s" % pad[:5])
    meta["templates"] = templates(b, gr, rl, meta)
    ncol = write_terrain(gr, rl, b)
    n = b.write_placements(os.path.join(OUT, "castle.txt"))
    meta.update(terrain_columns=ncol, blocks=n, snow=nsnow, checks=ch, hearth7=list(P.HEARTH7), hearth8=list(P.HEARTH8))
    import castle_dp
    castle_dp.run(gr, rl, meta)
    json.dump(meta, open(os.path.join(OUT, "castle.json"), "w"), ensure_ascii=False, default=lambda o: list(o) if isinstance(o, (set, tuple)) else int(o) if isinstance(o, np.integer) else str(o))
    print(f"castle: terrain {ncol} columns, {n} blocks (snow/spruce replaced {nsnow}, water drained {meta['drained']}, springs {meta['springs']}), trees {meta['trees']}, W {P.W}, P {ch['P']}, boulders {meta['boulders']}")

if __name__ == "__main__" and sys.argv[1:2] == ["plan"]:
    main(plan_only=True)
elif __name__ == "__main__":
    main()
