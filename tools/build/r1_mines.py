#!/usr/bin/env python3
"""T-033: the Iron Ore Mines (Шахты Железных Руд, Р1) on the place `mines` (rect 280 -60 60 50) + 16 of seam (x <= 323: the castle's scan).

  python3 tools/build/r1_mines.py        -> server/build/r1/mines_terrain.bin (tools/terrain.sh apply), mines.txt (tools/blockwriter.sh apply),
                                            mines.json (points for the tests, the bot and the datapack), mines_T.npz (the ground the step
                                            writes), docs/reports/T-033/mines_plan.png, structure/mines/*.nbt, datapack function/mines/gen/*
                                            (tools/build/mines_dp.py), the zone lines
  python3 tools/build/r1_mines.py plan   only the plan picture (needs server/build/r1/mines_pre.bin)
Inputs: server/build/r1/base.bin, terrain.bin, r1.json (the trails of T-022 to bonfire 7), mines_pre.bin (the place now).

HQ T-033, 2: the yard on a terrace (search), the workings under the place only, the box of the place filled with rock from H3 - 10 to the
ground - 6 but for the workings. Re-run on the built place: 0 columns changed."""
import json, math, os, re, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import write_grid, NONE
from lib import h as hsh
import mines_plan as P
import mines_build as MB
from mines_plan import ix, in_rect

ROOT = P.ROOT; OUT = P.OUT
DP = os.path.join(ROOT, "datapack/data/last_ember")
STR = os.path.join(DP, "structure/mines")
S_GRASS, R_STONE = 1, 0
VANILLA_TREE = re.compile(r"minecraft:(oak|birch|spruce|dark_oak|jungle|acacia|mangrove|cherry|pale_oak|azalea|flowering_azalea)_(log|leaves|wood)$|minecraft:(vine|pale_moss_carpet|pale_hanging_moss|cocoa|leaf_litter|bee_nest)$")
SNOW = re.compile(r"minecraft:(snow|snow_block|powder_snow)$")
PLANTS = re.compile(r"minecraft:(short_grass|tall_grass|fern|large_fern|sweet_berry_bush|dead_bush|wildflowers|bush|firefly_bush|short_dry_grass|tall_dry_grass|dandelion|poppy|.*_tulip|azure_bluet|oxeye_daisy|cornflower|lily_of_the_valley|allium|brown_mushroom|red_mushroom|lilac|rose_bush|peony|sunflower)$")

def world_scan(regex, inside):
    import fens_scan
    old = fens_scan.BAN; fens_scan.BAN = regex
    try: return fens_scan.scan(os.path.join(ROOT, "server/world"), box=P.BOX, inside=inside)
    finally: fens_scan.BAN = old

def ours_cols(c):
    """the columns the step rewrites on top: the yard and its walls and slopes, the approach and its banks (T != before), with 2 round"""
    gr = c.gr
    m = (c.T != gr["before"]) | c.rl["yard"]
    for (x, z) in c.walk: m[ix(gr, x, z)] = True
    p = m.copy()
    for _ in range(2):
        q = np.pad(p, 1); p = p | q[:-2, 1:-1] | q[2:, 1:-1] | q[1:-1, :-2] | q[1:-1, 2:]
    return p & gr["place"] & ~gr["ftrail"]

def clear(b, c, meta):
    """the vanilla trees standing on the yard, its slopes and the approach (logs; leaves within 3 of those logs unless another trunk
    outside is within 4), snow, the plants over changed columns, everything above the new ground up to the old top where nothing of ours
    stands. Run after the templates and the points: what it reads is the world now (it differs on a re-run)"""
    gr = c.gr; T = c.T; oc = ours_cols(c)
    def ours(x, z): return P.in_place(x, z) and bool(oc[ix(gr, x, z)])
    tr = world_scan(VANILLA_TREE, lambda x, z: P.in_place(x, z))
    gone = [(x, y, z) for (x, y, z, nm) in tr if ("_log" in nm or "_wood" in nm) and ours(x, z)]
    stay = [(x, y, z) for (x, y, z, nm) in tr if ("_log" in nm or "_wood" in nm) and not ours(x, z)]
    near_gone = set(); near_stay = {}
    for (x, y, z) in gone:
        for a in range(-3, 4):
            for e in range(-3, 4): near_gone.add((x + a, z + e))
    for (x, y, z) in stay:
        for a in range(-4, 5):
            for e in range(-4, 5): near_stay.setdefault((x + a, z + e), []).append(y)
    n = 0
    for (x, y, z, nm) in tr:
        if b.get(x, y, z) is not None or not P.in_place(x, z): continue
        if ("_log" in nm or "_wood" in nm) and ours(x, z) or (("leaves" in nm or "vine" in nm) and ((x, z) in near_gone or ours(x, z))
                and not any(abs(y - yy) <= 5 for yy in near_stay.get((x, z), []))):
            if y > int(T[ix(gr, x, z)]): b.set(x, y, z, "minecraft:air"); n += 1
    ns = 0
    for (x, y, z, nm) in world_scan(SNOW, lambda x, z: ours(x, z)):
        if b.get(x, y, z) is None and y > int(T[ix(gr, x, z)]): b.set(x, y, z, "minecraft:air"); ns += 1
    npl = 0
    for (x, y, z, nm) in world_scan(PLANTS, lambda x, z: ours(x, z)):
        if b.get(x, y, z) is not None or y <= int(T[ix(gr, x, z)]): continue
        b.set(x, y, z, "minecraft:air"); npl += 1
    nair = 0
    for i, j in zip(*np.nonzero(oc & (c.T != gr["before"]))):
        x, z = j + gr["x1"], i + gr["z1"]; y = int(T[i, j])
        top = max(int(gr["top"][i, j]), int(gr["btop"][i, j]), int(gr["before"][i, j]) + 1)
        for yy in range(y + 1, min(top, y + 30) + 1):
            if b.get(x, yy, z) is None: b.set(x, yy, z, "minecraft:air"); nair += 1
    meta["removed"] = dict(tree_blocks=n, snow=ns, plants=npl, air=nair)

def write_terrain(gr, rl, b):
    import r1_fens as RF
    T = rl["T"]; Wt = np.full(T.shape, NONE, np.int32)
    now, nw = gr["live"], gr["lwater"]
    cols = {}
    for (x, y, z), s_ in b.v.items(): cols.setdefault((x, z), {})[y] = s_
    act = gr["place"] & ~gr["ftrail"] & ~gr["wet"]
    cand = act & ((T != gr["before"]) | (T != now) | rl["yard"])
    touch = np.zeros(T.shape, bool)
    for i, j in zip(*np.nonzero(cand)):
        x, z = j + gr["x1"], i + gr["z1"]
        eg, ew = RF.expected_scan(T, Wt, cols, x, z, i, j)
        if now[i, j] != eg or (nw[i, j] != ew and ew != NONE): touch[i, j] = True
    H = np.where(touch, T, NONE).astype(np.int32)
    lo = T.copy()
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): lo = np.minimum(lo, np.roll(np.roll(lo, dz, 0), dx, 1))
    F = np.minimum(np.minimum(T, now), lo) - 4
    S = np.full(T.shape, S_GRASS, np.uint8)
    write_grid(os.path.join(OUT, "mines_terrain.bin"), gr["x1"], gr["z1"], H, F, np.full(T.shape, NONE, np.int32), S, np.full(T.shape, R_STONE, np.uint8), np.zeros(T.shape, np.uint8))
    return int(touch.sum())

def nbt(name, cells, origin):
    os.makedirs(STR, exist_ok=True)
    p = os.path.join(OUT, "tpl_mines_%s.txt" % name)
    with open(p, "w") as f:
        for (x, y, z), s in sorted(cells.items()): f.write("%d %d %d %s\n" % (x, y, z, s))
    r = subprocess.run([os.path.join(ROOT, "tools/blockwriter.sh"), "nbt", p, str(origin[0]), str(origin[1]), str(origin[2]), os.path.join(STR, name + ".nbt")], capture_output=True, text=True)
    if r.returncode or "nbt:" not in r.stdout: raise SystemExit(r.stdout + r.stderr)

def templates(b, c, meta):
    """structure/mines/cave_<n>_before|after (the zone from the floor + 1 to the ceiling; the datapack places `after`; `before` restores
    it for the admin reset); before clear(): the same cells on every run"""
    for cv in meta["caves"]:
        x1, z1, x2, z2 = cv["rect"]; f = cv["floor"]
        before = {}
        for x in range(x1, x2 + 1):
            for y in range(f + 1, f + 5):
                for z in range(z1, z2 + 1): before[(x, y, z)] = b.get(x, y, z) or "minecraft:air"
        nbt("cave_%d_before" % cv["n"], before, cv["origin"])
        nbt("cave_%d_after" % cv["n"], MB.cave_after(b, cv), cv["origin"])

def free3(b, x, y, z):
    """a scaled elite (1.2) or a mob at the centre of (x, y, z): 3 x 2 x 3 round the feet cell free of solid blocks (T-032)"""
    for a in (-1, 0, 1):
        for e in (-1, 0, 1):
            for d in (0, 1):
                s = b.get(x + a, y + d, z + e)
                if s is None or not re.search(r"air$|rail|lantern|water", s): return False
    return True

def points(b, c, meta):
    """the dead miners on their points (HQ T-033, 3: 2 on H2, 3 on H3; facing a wall, out of the cave-ins and the water), Bran in the
    pocket, the carts, the decor item_displays, the push targets of the cave-ins, the box of the workings, the yard's centre"""
    lv = c.lv; f2, f3 = lv[2], lv[3]
    cand = [  # (x, z, horizon, yaw facing the wall)
        (300, -60, 2, 180), (305, -47, 2, 90),
        (290, -45, 3, 0), (275, -58, 3, -90), (264, -55, 3, 90)]
    dead = []
    for (x, z, h, yaw) in cand:
        y = lv[h] + 1
        ok = all(b.get(x, y + d, z) == "minecraft:air" for d in (0, 1))
        if not ok: raise SystemExit("the dead miner's point %s is not free" % ((x, y, z),))
        dead.append([x + 0.5, y, z + 0.5, yaw, h])
    out = dict(dead=dead, bran=meta["bran"])
    # the push targets: the drift cells just outside the zone's both ends along its axis (the middle lane)
    for cv in meta["caves"]:
        x1, z1, x2, z2 = cv["rect"]; f = cv["floor"]
        if cv["axis"] == "x": mz = (z1 + z2) // 2; ends = [(x1 - 2, mz), (x2 + 2, mz)]
        else: mx = (x1 + x2) // 2; ends = [(mx, z1 - 2), (mx, z2 + 2)]
        cv["ends"] = [[e[0] + 0.5, f + 1, e[1] + 0.5] for e in ends]
        for e in ends:
            if b.get(e[0], f + 1, e[1]) != "minecraft:air": raise SystemExit("the push target %s of cave-in %d is not free" % (e, cv["n"]))
    # the box of the workings (mobs, the cap, the hats) and the yard
    xs = [q[0] for q in c.W["air"]]; ys = [q[1] for q in c.W["air"]]; zs = [q[2] for q in c.W["air"]]
    out["work_box"] = [min(xs) - 1, min(ys) - 1, min(zs) - 1, max(xs) + 1, lv[0] - 2, max(zs) + 1]
    yx1, yz1, yx2, yz2 = c.pl["yard"]["r"]
    out["yard_c"] = [(yx1 + yx2 + 1) / 2, lv[0] + 1, (yz1 + yz2 + 1) / 2]
    t = meta["office"]["table"]
    out["lunch"] = [[t[0] + 0.3, t[1] + 1.0, t[2] + 0.5, "bread", 20], [t[0] + 0.9, t[1] + 1.0, t[2] + 0.4, "bowl", 0],
                    [t[0] + 1.5, t[1] + 1.0, t[2] + 0.6, "decorated_pot", 0]]
    out["pick"] = meta["big"]["pick"]; out["torch"] = meta["big"]["torch"]
    out["carts"] = meta["carts"]
    return out

def zone_lines(c, meta):
    """mines_headframe (the box 9 x 9 of the headframe from the yard's ground to its top + 2, no flags: adventure only); the rest of the
    mines is breakable (HQ T-033, 3)"""
    from r1 import replace_lines
    x1, z1, x2, z2 = P.HEADFRAME; Y = c.lv[0]
    hz = (x1 - 1, Y, z1 - 1, x2 + 1, Y + 24, z2 + 1)
    replace_lines(os.path.join(ROOT, "zones/zones.txt"), ["mines_headframe "],
                  ["mines_headframe overworld box %d %d %d %d %d %d              # T-033: the headframe of the Iron Ore Mines (a landmark)" % hz])
    return hz

def plan_png(c, b, meta, info, path):
    """the plan: a view from above (the yard, the approach, the three horizons in colours, the ore by type, the cave-ins and their
    bypasses, the big collapse, the pocket, the points) and a section along z = -45 .. the shaft (west -> east) with the levels"""
    from PIL import Image, ImageDraw
    gr = c.gr; S = 9; x1, z1, x2, z2 = P.PLACE[0] - 18, P.PLACE[1] - 4, min(P.PLACE[2] + 16, P.XMAX), P.PLACE[3] + 18
    w, h = (x2 - x1 + 1) * S, (z2 - z1 + 1) * S
    sec_h = 60 * 6
    img = Image.new("RGB", (w, h + sec_h + 230), (20, 20, 24)); d = ImageDraw.Draw(img)
    T = c.T
    for z in range(z1, z2 + 1):
        for x in range(x1, x2 + 1):
            i, j = ix(gr, x, z); y = int(T[i, j])
            g = int(np.clip(60 + (y - 100) * 3.0, 30, 230)); col = (g // 2 + 20, g // 2 + 35, g // 2 + 20)
            if c.rl["yard"][i, j]: col = (150, 130, 100)
            if (x, z) in c.walk: col = (200, 160, 90)
            if gr["ftrail"][i, j]: col = (110, 100, 80)
            if not gr["place"][i, j]: col = tuple(v // 3 for v in col)
            elif not gr["inner"][i, j]: col = tuple(int(v * 0.6) for v in col)
            d.rectangle([(x - x1) * S, (z - z1) * S, (x - x1) * S + S - 1, (z - z1) * S + S - 1], fill=col)
    for (x, z) in c.rl["walls"]["cut"] | c.rl["walls"]["fill"]:
        d.rectangle([(x - x1) * S + 2, (z - z1) * S + 2, (x - x1) * S + S - 3, (z - z1) * S + S - 3], fill=(120, 120, 120))
    HC = {1: (90, 170, 255), 2: (255, 170, 60), 3: (230, 70, 200), 4: (255, 255, 255)}
    for (x, z, hh), f in c.W["floor"].items():
        o = {1: 0, 2: 2, 3: 4, 4: 4}[hh]
        d.rectangle([(x - x1) * S + o, (z - z1) * S + o, (x - x1) * S + S - 1 - o, (z - z1) * S + S - 1 - o], outline=HC[hh], width=2)
    for nm, dd in c.W["inc"].items():
        for (x, z), (k, y) in dd["cells"].items():
            d.rectangle([(x - x1) * S + 3, (z - z1) * S + 3, (x - x1) * S + S - 4, (z - z1) * S + S - 4], fill=(200, 200, 200) if k != "land" else (120, 120, 120))
    OC = {"coal_ore": (40, 40, 40), "iron_ore": (220, 150, 110), "copper_ore": (60, 200, 150), "lapis_ore": (40, 60, 230)}
    for (x, y, z), s in b.v.items():
        k = s.replace("minecraft:", "")
        if k in OC and x1 <= x <= x2 and z1 <= z <= z2:
            d.rectangle([(x - x1) * S + 3, (z - z1) * S + 3, (x - x1) * S + 6, (z - z1) * S + 6], fill=OC[k])
    def R(r, col, wd=2): d.rectangle([(r[0] - x1) * S, (r[1] - z1) * S, (r[2] + 1 - x1) * S, (r[3] + 1 - z1) * S], outline=col, width=wd)
    R(P.PLACE, (230, 230, 230)); R(c.pl["yard"]["r"], (255, 230, 120), 2); R(P.SHAFT, (255, 255, 255), 3); R(P.HEADFRAME, (160, 110, 60), 2)
    R((255, -81, 263, -75), (200, 200, 200), 2); R((255, -72, 261, -69), (150, 120, 90), 2)
    for cv in meta["caves"]: R(cv["rect"], (255, 40, 40), 3)
    R(P.BIG["rect"], (150, 75, 0), 4)
    for p in meta["points"]["dead"]:
        cx, cz = (p[0] - x1) * S, (p[2] - z1) * S; d.polygon([(cx, cz - 8), (cx + 7, cz + 6), (cx - 7, cz + 6)], outline=(255, 255, 0), width=2)
    bx, by, bz, _ = meta["points"]["bran"]; cx, cz = (bx - x1) * S, (bz - z1) * S; d.ellipse([cx - 9, cz - 9, cx + 9, cz + 9], outline=(255, 255, 0), width=4)
    for bb in meta["barrels"]:
        cx, cz = (bb["pos"][0] - x1 + 0.5) * S, (bb["pos"][2] - z1 + 0.5) * S; d.rectangle([cx - 5, cz - 5, cx + 5, cz + 5], outline=(160, 255, 255), width=2)
    for ct in meta["carts"]:
        cx, cz = (ct[0] - x1) * S, (ct[2] - z1) * S; d.ellipse([cx - 5, cz - 5, cx + 5, cz + 5], fill=(170, 170, 200))
    # the section: x along, y up (H3 - 12 .. Y + 24), every working cell that is air in any z (projection), the ground at z -45 and -71
    oy = h + 10; Y = c.lv[0]; ylo, yhi = c.lv[3] - 12, Y + 26; sy = sec_h / (yhi - ylo)
    def SY(y): return oy + int((yhi - y) * sy)
    proj = {}
    for (x, y, z) in c.W["air"]:
        if x1 <= x <= x2: proj.setdefault((x, y), 0); proj[(x, y)] += 1
    for (x, y), n in proj.items():
        hh = c.horizon_of_y(y) if y < Y - 2 else 1
        d.rectangle([(x - x1) * S, SY(y + 1), (x - x1) * S + S - 1, SY(y) - 1], fill=HC[hh])
    for zz, col in ((-71, (100, 200, 100)), (-45, (200, 200, 100))):
        pts = [((x - x1) * S + S // 2, SY(int(T[ix(gr, x, zz)]) + 1)) for x in range(x1, x2 + 1)]
        d.line(pts, fill=col, width=2)
    for k, y in c.lv.items():
        if k < 4: d.line([(0, SY(y + 1)), (w, SY(y + 1))], fill=(90, 90, 90)); d.text((4, SY(y + 1) - 12), ["yard", "H1", "H2", "H3"][k] + " %d" % y, fill=(255, 255, 255))
    o = meta["ore"]
    lines = ["T-033 Iron Ore Mines: plan (1 block = %d px, north up). White = place 60 x 50; yellow = yard %s at Y %d (cut %d, fill %d; walls grey); sand = approach %d cells (cut %.1f, fill %.1f)"
             % (S, info["yard"], info["Y"], info["yard_cut"], info["yard_fill"], info["approach_len"], info["approach_cut"], info["approach_fill"]),
             "drifts: H1 blue (floor %d, 3 x 3), H2 orange (floor %d, 2 wide), H3 magenta (floor %d), pocket white; inclines grey (landings dark); shaft white square under the headframe (brown)" % (c.lv[1], c.lv[2], c.lv[3]),
             "cave-ins red (bypass drifts beside each), big collapse brown, Bran (ring), dead miners (triangles), barrels (cyan), carts (dots); ore: coal black, iron rust, copper green, lapis blue",
             "ore placed: " + ", ".join("%s %d" % (k, v) for k, v in o.items()),
             "cover over the workings >= %d (portal excepted); lowest floor %d; section below: all horizons projected on x (ground at z -71 green, z -45 yellow)" % (info["cover_min"], info["lowest"])]
    for k, t in enumerate(lines): d.text((6, h + sec_h + 30 + 22 * k), t, fill=(255, 255, 255))
    img.save(path)

def main(plan_only=False):
    gr = P.grids()
    pl = P.plan(gr)
    yd = pl["yard"]
    W = P.workings(yd["Y"])
    rl = P.relief(gr, yd, pl["ta"])
    info = P.checks(gr, yd, rl, W, pl["ta"])
    b, c = MB.build(gr, rl, pl, W)
    meta = c.meta
    from connect import connect
    connect(b)
    meta["points"] = points(b, c, meta)
    if not plan_only: templates(b, c, meta)
    if not plan_only: clear(b, c, meta)
    else: meta["removed"] = {}
    bad = [k for k in b.v if not P.in_place(k[0], k[2])]
    if bad: raise SystemExit("blocks outside the place: %s" % bad[:5])
    ft = [k for k in b.v if gr["ftrail"][ix(gr, k[0], k[2])]]
    if ft: raise SystemExit("blocks on the trails of T-022: %s" % ft[:5])
    os.makedirs(os.path.join(ROOT, "docs/reports/T-033"), exist_ok=True)
    plan_png(c, b, meta, info, os.path.join(ROOT, "docs/reports/T-033/mines_plan.png"))
    if plan_only:
        print("plan:", info, meta["ore"]); return
    ncol = write_terrain(gr, rl, b)
    np.savez_compressed(os.path.join(OUT, "mines_T.npz"), T=rl["T"], x1=gr["x1"], z1=gr["z1"], walk=np.array([[x, z, v] for (x, z), v in c.walk.items()]))
    n = b.write_placements(os.path.join(OUT, "mines.txt"))
    hz = zone_lines(c, meta)
    out = dict(meta); out.update(info=info, terrain_columns=ncol, blocks=n, zone_headframe=list(hz), place=list(P.PLACE), yard=list(yd["r"]), Y=yd["Y"],
                                 levels=W["lv"], shaft_box=list(P.SHAFT), headframe=list(P.HEADFRAME), pa=[list(p) for p in pl["pa"]],
                                 inclines={k: dict(face=v["face"], cells=[[x, z, kd, y] for (x, z), (kd, y) in sorted(v["cells"].items())]) for k, v in W["inc"].items()},
                                 big_rect=list(P.BIG["rect"]), water=list(P.WATER), pocket=meta["pocket"])
    try:
        import mines_dp
        mines_dp.run(out)
    except ImportError: pass
    json.dump(out, open(os.path.join(OUT, "mines.json"), "w"), ensure_ascii=False, default=lambda o: list(o) if isinstance(o, (set, tuple)) else (int(o) if isinstance(o, np.integer) else float(o) if isinstance(o, np.floating) else str(o)))
    print("mines: terrain %d columns, %d blocks, %s, removed %s, ore %s, filled %d" % (ncol, n, info, meta["removed"], meta["ore"], meta["filled"]))

if __name__ == "__main__" and sys.argv[1:2] == ["plan"]:
    main(plan_only=True)
elif __name__ == "__main__":
    main()
