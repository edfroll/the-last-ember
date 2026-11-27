#!/usr/bin/env python3
"""T-034: the Grotto of the Jelly (Грот Студня, Р1, card 5.4) under the north cliff of the bowl of the Crooked Fens, and its side channel.

  python3 tools/build/r1_grotto.py   -> server/build/r1/grotto.txt (tools/blockwriter.sh apply), grotto.json (points for the datapack,
                                        the tests, the bot, the boat), docs/reports/T-034/grotto_plan.png, datapack treasury/gen/grotto_*
                                        (treasury_dp.py), the zone lines, the vault line
Inputs: server/build/r1/grotto_pre.bin (the box now; the first run keeps it in grotto_before.npz), fens.json, fens.txt, base.bin.

HQ T-034, 3: the plan is tools/build/treasury_grotto.py (the grotto with the cover 8 / 6, the channel: open cut, then the tunnel). The
grotto: the floor W - 1, the water W (sources), air to W + 9 (lower at the walls), the roof W + 10; the dry ledge 9 x 9 at W + 1 in the
middle with the chest grown into slime (the lock: a slime block over it), the stepping stones of half slabs from the water up to it; the
walls of calcite, dripstone, tuff and moss with slime in patches above the water, pointed dripstone from the roof, glow lichen only on the
roof. The channel: 3 wide, water W - 1 .. W on a bed at W - 2; the open part a cut with sheer walls of the cliff's palette; the tunnel
(the roof at W + 3) curtained with hanging roots, slime on the roots by its mouth. The sunken boat and the post with the waxed sign at the
channel's start. The box of the grotto + 6 and round the tunnel 3: vanilla caves, water, lava filled with rock. Re-run: 0 columns."""
import json, math, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import treasury_grotto as P
from lib import B, Mix, h as hsh

ROOT = P.ROOT; OUT = P.OUT
ROCK_OK = re.compile(r"minecraft:(stone|andesite|diorite|granite|tuff|deepslate|dirt|coarse_dirt|calcite|grass_block|dripstone_block|mud|clay|moss_block)$")
CLIFF = Mix({"calcite": 38, "dripstone_block": 24, "tuff": 22, "moss_block": 8, "andesite": 8}, salt=61)
ROOF = Mix({"calcite": 30, "dripstone_block": 40, "tuff": 30}, salt=62)
BED = Mix({"tuff": 40, "calcite": 20, "clay": 20, "mud": 20}, salt=63)
LEDGE = Mix({"calcite": 30, "tuff": 30, "moss_block": 25, "dripstone_block": 15}, salt=64)
WATER = "minecraft:water[level=0]"


def under_blocks(gr, box, ylo, yhi, name):
    cp = os.path.join(OUT, name + ".npz"); key = gr.key + repr(box) + str(ylo) + str(yhi)
    if os.path.exists(cp):
        d = np.load(cp, allow_pickle=True)
        if str(d["key"]) == key: return {tuple(int(t) for t in k): str(n) for k, n in zip(d["pos"], d["name"])}
    import fens_scan
    old = fens_scan.BAN; fens_scan.BAN = re.compile(r"(?!%s).*" % ROCK_OK.pattern)
    try: found = fens_scan.scan(os.path.join(ROOT, "server/world"), box=box)
    finally: fens_scan.BAN = old
    found = [(x, y, z, n) for (x, y, z, n) in found if ylo <= y <= min(yhi, gr.g(x, z))]
    np.savez_compressed(cp, pos=np.array([[x, y, z] for (x, y, z, n) in found] or np.zeros((0, 3)), np.int32),
                        name=np.array([n for (x, y, z, n) in found], object), key=key)
    return {(x, y, z): n for (x, y, z, n) in found}


class Ctx:
    def __init__(self, gr, pl):
        self.gr, self.pl = gr, pl; self.W = pl["W"]; self.r = tuple(pl["rect"])
        self.line = [((l[0], l[1]), (l[2], l[3]), bool(l[4])) for l in pl["line"]]
        self.air = set(); self.water = set(); self.meta = {}; self.ceil = {}


def band(c, d):
    p = (-d[1], d[0]); return [(c[0] + k * p[0], c[1] + k * p[1]) for k in (-1, 0, 1)]


def grotto(b, c):
    """the room: floor, water, vault, the shell, the ledge, the stepping stones, the chest and its lock, the pointed dripstone, the lichen"""
    x1, z1, x2, z2 = c.r; W = c.W
    door = c.line[0][0]; dd = c.line[0][1]                    # the first cell of the channel, just outside a wall; dd points out
    inside_door = (door[0] - dd[0], door[1] - dd[1])
    doorband = set(band(inside_door, dd))
    cols = {}
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            e = min(x - x1, x2 - x, z - z1, z2 - z)
            if e == 0 and (x, z) not in doorband and (hsh(x, 0, z, 71) < 0.3 or (min(x - x1, x2 - x) == 0 and min(z - z1, z2 - z) == 0)): continue
            cols[(x, z)] = W + 9 - max(0, 2 - e) - (1 if hsh(x, 1, z, 72) < 0.3 else 0)
    c.ceil = cols
    # the ledge 9 x 9 in the middle (W, W + 1 solid; feet W + 2)
    mx, mz = (x1 + x2) // 2, (z1 + z2) // 2
    L = (mx - 4, mz - 4, mx + 4, mz + 4); c.ledge = L
    for (x, z), top in cols.items():
        b.set(x, W - 1, z, BED)
        led = L[0] <= x <= L[2] and L[1] <= z <= L[3]
        if led:
            corner = (x in (L[0], L[2])) and (z in (L[1], L[3]))
            b.set(x, W, z, LEDGE); b.set(x, W + 1, z, "minecraft:moss_block" if hsh(x, 2, z, 73) < 0.4 and not corner else LEDGE)
            for y in range(W + 2, top + 1): b.set(x, y, z, "minecraft:air"); c.air.add((x, y, z))
        else:
            b.set(x, W, z, WATER); c.water.add((x, W, z))
            for y in range(W + 1, top + 1): b.set(x, y, z, "minecraft:air"); c.air.add((x, y, z))
    # the shell: rock next to the air or the water (calcite, dripstone, tuff, moss); slime in patches in the walls above the water
    vol = c.air | c.water
    for (x, y, z) in sorted(vol):
        for (a, e, f) in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, -1)):
            q = (x + a, y + e, z + f)
            if q in vol or b.get(*q) is not None: continue
            if e == 1: b.set(*q, ROOF)
            elif y >= W + 1 and hsh(*q, 74) < 0.09: b.set(*q, "minecraft:slime_block")
            else: b.set(*q, CLIFF)
    # the stepping stones from the water to the ledge on the side facing the door: slab at W, block at W, slab at W + 1 (2 wide)
    tx, tz = inside_door
    ld = (0, 1) if tz > L[3] else (0, -1) if tz < L[1] else (1, 0) if tx > L[2] else (-1, 0)
    if ld[1]: sx, sz = max(L[0] + 2, min(L[2] - 3, tx)), (L[3] + 1 if ld[1] > 0 else L[1] - 1)
    else: sx, sz = (L[2] + 1 if ld[0] > 0 else L[0] - 1), max(L[1] + 2, min(L[3] - 3, tz))
    p = (-ld[1], ld[0]) if ld[1] else (ld[1], ld[0])
    p = (1, 0) if ld[1] else (0, 1)
    steps = []
    for k, (yy, kind) in enumerate([(W + 1, "slab"), (W, "block"), (W, "slab")]):
        for w in (0, 1):
            x, z = sx + ld[0] * k + p[0] * w, sz + ld[1] * k + p[1] * w
            for y in range(W, yy + 1): c.water.discard((x, y, z))
            if kind == "slab":
                if yy == W + 1: b.set(x, W, z, LEDGE)
                b.set(x, yy, z, "minecraft:tuff_slab[type=bottom,waterlogged=%s]" % ("true" if yy == W else "false"))
            else: b.set(x, W, z, "minecraft:calcite")
            steps.append((x, z))
    c.meta["steps"] = [[x, z] for (x, z) in steps]
    c.meta["water_foot"] = [sx + ld[0] * 3 + 0.5, W, sz + ld[1] * 3 + 0.5]     # standing in the water at the foot of the stones
    # the chest on the ledge, grown into slime: slime blocks round it on three sides, the lock over it; facing the stones
    face = {(0, 1): "south", (0, -1): "north", (1, 0): "east", (-1, 0): "west"}[ld]
    cx, cz = sx - ld[0] * 3, sz - ld[1] * 3
    b.set(cx, W + 2, cz, 'minecraft:chest[facing=%s,type=single,waterlogged=false]{LootTable:"last_ember:vault/r1_grotto"}' % face)
    b.set(cx, W + 3, cz, "minecraft:slime_block")
    for (a, f) in ((p[0], p[1]), (-p[0], -p[1]), (-ld[0], -ld[1])):
        b.set(cx + a, W + 2, cz + f, "minecraft:slime_block")
    b.set(cx - ld[0] + p[0], W + 2, cz - ld[1] + p[1], "minecraft:slime_block")
    c.meta.update(chest=[cx, W + 2, cz], lock=[cx, W + 3, cz], lock_block="minecraft:slime_block", chest_facing=face)
    c.meta["ledge"] = list(L)
    # pointed dripstone from the roof (3 long: base, middle, tip) and glow lichen on the roof (light 7, none at the water)
    for (x, z), top in cols.items():
        if (x, top + 1, z) not in vol and b.get(x, top + 1, z) is not None:
            r = hsh(x, 3, z, 75)
            led = L[0] - 1 <= x <= L[2] + 1 and L[1] - 1 <= z <= L[3] + 1
            if r < 0.06 and not led and top - 3 > W + 2:
                b.set(x, top, z, "minecraft:pointed_dripstone[thickness=base,vertical_direction=down,waterlogged=false]")
                b.set(x, top - 1, z, "minecraft:pointed_dripstone[thickness=middle,vertical_direction=down,waterlogged=false]")
                b.set(x, top - 2, z, "minecraft:pointed_dripstone[thickness=tip,vertical_direction=down,waterlogged=false]")
            elif r < 0.16:
                b.set(x, top, z, "minecraft:glow_lichen[down=false,east=false,north=false,south=false,up=true,waterlogged=false,west=false]")
    c.meta["rest"] = [sx + ld[0] * 4 + p[0] * 3 + 0.5, W + 0.2, sz + ld[1] * 4 + p[1] * 3 + 0.5]   # the Jelly asleep in the water by the ledge
    c.meta["room"] = [x1, W - 1, z1, x2, W + 9, z2]


def channel(b, c):
    """the channel along the plan's line: water W - 1, W on the bed W - 2, 3 wide; open: everything over the band up to the old top gone,
    sheer walls of the cliff's palette up to the ground, banks at W + 1 where the ground is lower; the tunnel: air W + 1, W + 2, the
    roof W + 3 (and its walls), hanging roots under the roof at the cells near its mouth"""
    gr = c.gr; W = c.W
    cells = {}
    for k, (cc, d, tun) in enumerate(c.line):
        for q in [(cc[0] + a, cc[1] + e) for a in (-1, 0, 1) for e in (-1, 0, 1)]:     # 3 x 3 round the line: the band and full corners
            cells[q] = cells.get(q, False) or not tun
    c.chan = cells
    for (x, z), open_ in cells.items():
        b.set(x, W - 2, z, BED); b.set(x, W - 1, z, WATER); b.set(x, W, z, WATER); c.water |= {(x, W - 1, z), (x, W, z)}
        if open_:
            top = max(gr.g(x, z), int(gr.T[z - gr.z1, x - gr.x1]))
            for y in range(W + 1, top + 3): b.set(x, y, z, "minecraft:air")      # + 2: grass, flowers, snow over the old top
        else:
            for y in (W + 1, W + 2): b.set(x, y, z, "minecraft:air")
            b.set(x, W + 3, z, ROOF)
    for (x, z), open_ in cells.items():
        for (a, f) in P.DIRS:
            q = (x + a, z + f)
            if q in cells or q in c.ceil: continue
            if gr.wet(*q) and gr.w(*q) == W and gr.g(*q) < W: continue      # the water of the bowl: the channel opens into it
            g = gr.g(*q)
            hi = max(g, W + 1) if open_ else W + 3
            for y in range(W - 2, hi + 1):
                if b.get(q[0], y, q[1]) is None: b.set(q[0], y, q[1], CLIFF if y <= g or y <= W + 1 else CLIFF)
            if open_ and g < W + 1:
                c.meta.setdefault("banks", []).append([q[0], q[1]])
    # the tunnel's mouth: the first open line cell after the tunnel; hanging roots under the roof of its last 3 cells, slime on the face
    k0 = next(k for k, (cc, d, tun) in enumerate(c.line) if not tun)
    mouth_cell, md = c.line[k0][0], c.line[k0][1]
    for k in range(max(0, k0 - 3), k0):
        cc, d, tun = c.line[k]
        for (x, z) in band(cc, d):
            b.set(x, W + 2, z, "minecraft:hanging_roots[waterlogged=false]")
    # the cliff face round the mouth: slime in patches, rooted dirt with hanging roots over the edge
    face = []
    pm = (-md[1], md[0])
    for w in range(-3, 4):
        for y in range(W + 3, W + 9):
            x, z = c.line[k0 - 1][0][0] + pm[0] * w, c.line[k0 - 1][0][1] + pm[1] * w
            if gr.g(x, z) >= y and (x, z) not in cells:
                s = b.get(x, y, z)
                if s is None or s == "minecraft:air": continue
            if gr.g(x, z) >= y and hsh(x, y, z, 76) < 0.28 and b.get(x, y, z) is None:
                b.set(x, y, z, "minecraft:slime_block"); face.append([x, y, z])
    c.meta["mouth"] = [mouth_cell[0] + 0.5, W + 1, mouth_cell[1] + 0.5]
    c.meta["roots"] = [[x + 0.5, W + 2.2, z + 0.5] for (cc, d, tun) in c.line[max(0, k0 - 3):k0] for (x, z) in band(cc, d)][:6]
    c.meta["slime_face"] = face


def start_props(b, c):
    """at the channel's start (the last line cell, by the bowl's water): the half sunk boat (planks and slabs under and at the water) on
    one side, the post with the waxed sign «Лодка вернулась пустая. / И липкая.» on the bank of the other"""
    W = c.W; gr = c.gr
    cc, d, _ = c.line[-1]
    p = (-d[1], d[0])
    # the sign: on the first bank cell beside the last few line cells (ground >= W + 1, not in the channel)
    for k in range(1, 8):
        cc2, d2, _ = c.line[-k]
        p2 = (-d2[1], d2[0])
        for s in (2, -2):
            x, z = cc2[0] + p2[0] * s, cc2[1] + p2[1] * s
            if (x, z) in c.chan: continue
            g = max(gr.g(x, z), W)
            if g >= W and not gr.wet(x, z):
                rot = {(0, 1): 0, (0, -1): 8, (1, 0): 12, (-1, 0): 4}[(-p2[0] * (1 if s > 0 else -1), -p2[1] * (1 if s > 0 else -1))]
                b.set(x, g + 1, z, "minecraft:spruce_fence")
                b.set(x, g + 2, z, 'minecraft:spruce_sign[rotation=%d,waterlogged=false]{is_waxed:1b,front_text:{messages:["","Лодка вернулась пустая.","И липкая.",""]},back_text:{messages:["","","",""]}}' % rot)
                c.meta["sign"] = [x, g + 2, z]
                break
        if "sign" in c.meta: break
    if "sign" not in c.meta: raise SystemExit("no bank for the sign at the channel's start")
    # the half sunk boat: a hull of 2 x 3 in the shallow water of the bowl beside the channel's start, off the way of a boat (>= 3 from
    # the line of the channel and its continuation, the cells all water at W over ground <= W - 1)
    end = c.line[-1][0]; d = c.line[-1][1]; p = (-d[1], d[0])
    best = None
    for k in range(-2, 7):
        for s_ in (-4, -5, -6, 4, 5, 6):
            hx, hz = end[0] + d[0] * k + p[0] * s_, end[1] + d[1] * k + p[1] * s_
            cells = [(hx + d[0] * i + p[0] * j, hz + d[1] * i + p[1] * j) for i in range(3) for j in range(2)]
            if all(gr.wet(*q) and gr.w(*q) == W and gr.g(*q) <= W - 1 and q not in c.chan for q in cells):
                best = cells; break
        if best: break
    if best is None: raise SystemExit("no shallow water off the way for the sunk boat at the channel's start")
    hull = []
    for i, (x, z) in enumerate(best):
        b.set(x, W - 1, z, "minecraft:spruce_planks" if i % 2 == 0 else "minecraft:stripped_spruce_log[axis=%s]" % ("z" if d[1] else "x"))
        if i < 2: b.set(x, W, z, "minecraft:spruce_slab[type=bottom,waterlogged=true]")
        hull.append([x, z])
    c.meta["boat_wreck"] = hull
    # the wreck at the mouth inside the grotto: planks and a broken side 2 cells beside the door, in its water
    door = c.line[0][0]; dd = c.line[0][1]; pp = (-dd[1], dd[0])
    for i in range(3):
        x, z = door[0] - dd[0] * (2 + i) + pp[0] * 4, door[1] - dd[1] * (2 + i) + pp[1] * 4
        if (x, W, z) in c.water:
            b.set(x, W - 1, z, "minecraft:spruce_planks")
            if i == 1: b.set(x, W, z, "minecraft:spruce_trapdoor[facing=north,half=bottom,open=false,powered=false,waterlogged=true]")
    c.meta["wreck_in"] = [door[0] - dd[0] * 3 + pp[0] * 4, door[1] - dd[1] * 3 + pp[1] * 4]


def fill(b, c, under):
    W = c.W; x1, z1, x2, z2 = c.r; n = 0
    near = set()
    for (x, z), open_ in c.chan.items():
        if open_: continue
        for a in range(-3, 4):
            for f in range(-3, 4):
                for y in range(W - 5, W + 7): near.add((x + a, y, z + f))
    for (x, y, z), nm in sorted(under.items()):
        if b.get(x, y, z) is not None or y > c.gr.g(x, z): continue
        inbox = x1 - 6 <= x <= x2 + 6 and z1 - 6 <= z <= z2 + 6 and W - 6 <= y <= W + 16
        if not (inbox or (x, y, z) in near): continue
        b.set(x, y, z, "minecraft:stone" if y < W + 1 else "minecraft:tuff"); n += 1
    c.meta["filled"] = n


def zone_lines(c):
    from r1 import replace_lines
    x1, z1, x2, z2 = c.r; W = c.W
    room = (x1 - 1, W - 2, z1 - 1, x2 + 1, W + 11, z2 + 1)
    last = [q for (cc, d, tun) in c.line[:12] for q in band(cc, d)]
    xs = [q[0] for q in last]; zs = [q[1] for q in last]
    ch = (min(xs) - 1, W - 3, min(zs) - 1, max(xs) + 1, W + 6, max(zs) + 1)
    replace_lines(os.path.join(ROOT, "zones/zones.txt"), ["grotto ", "grotto_channel "],
                  ["grotto          overworld box  %d %d %d %d %d %d   dungeon   # T-034: the Grotto of the Jelly" % room,
                   "grotto_channel  overworld box  %d %d %d %d %d %d   dungeon   # T-034: the last 12 cells of its channel (under the roots)" % ch])
    return room, ch


def vault_line(c):
    from r1 import replace_lines
    x, y, z = c.meta["chest"]
    replace_lines(os.path.join(ROOT, "treasury/vaults.txt"), ["vault r1_grotto "],
                  ["vault r1_grotto r1 overworld %d %d %d block=chest[facing=%s] build=0   # T-034: the Grotto of the Jelly, on the ledge in slime" % (x, y, z, c.meta["chest_facing"])])


def main():
    gr, pl = P.plan()
    c = Ctx(gr, pl)
    b = B("grotto")
    x1, z1, x2, z2 = c.r; W = c.W
    under = under_blocks(gr, (x1 - 6, z1 - 6, x2 + 6, z2 + 6), W - 6, W + 16, "grotto_under")
    tun = [cc for (cc, d, t) in c.line if t]
    under.update(under_blocks(gr, (min(q[0] for q in tun) - 3, min(q[1] for q in tun) - 3, max(q[0] for q in tun) + 3, max(q[1] for q in tun) + 3),
                              W - 5, W + 6, "grotto_under_tunnel"))
    grotto(b, c)
    channel(b, c)
    start_props(b, c)
    fill(b, c, under)
    from connect import connect
    connect(b)
    bad = [k for k in b.v if not (P.BOX[0] <= k[0] <= P.BOX[2] and P.BOX[1] <= k[2] <= P.BOX[3])]
    if bad: raise SystemExit("blocks outside the box: %s" % bad[:5])
    n = b.write_placements(os.path.join(OUT, "grotto.txt"))
    room, ch = zone_lines(c)
    vault_line(c)
    pl2 = dict(pl); pl2["ledge"] = c.meta["ledge"]
    P.plan_png(gr, pl2, os.path.join(ROOT, "docs/reports/T-034/grotto_plan.png"))
    out = dict(W=W, rect=list(c.r), line=pl["line"], length=pl["length"], tunnel=pl["tunnel"], cut=pl["cut"], zone_room=list(room), zone_channel=list(ch),
               blocks=n, chan=[[x, z, int(o)] for (x, z), o in sorted(c.chan.items())], ceil={"%d,%d" % k: v for k, v in c.ceil.items()}, **c.meta)
    try:
        import treasury_dp
        treasury_dp.run_grotto(out)
    except ImportError: pass
    json.dump(out, open(os.path.join(OUT, "grotto.json"), "w"), ensure_ascii=False)
    print("grotto: %d blocks, rect %s, W %d, ledge %s, channel %d (tunnel %d, cut %d), filled %d, chest %s"
          % (n, c.r, W, c.meta["ledge"], pl["length"], pl["tunnel"], pl["cut"], c.meta["filled"], c.meta["chest"]))


if __name__ == "__main__":
    main()
