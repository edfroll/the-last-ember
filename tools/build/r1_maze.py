#!/usr/bin/env python3
"""T-024: the Enchanted Maze (Р1) on its place `maze` of tools/build/r1_plots.txt (rect 120x120 round (-150,-430) + 16).

  python3 tools/build/r1_maze.py      -> server/build/r1/maze_terrain.bin (tools/terrain.sh apply), maze.txt (tools/blockwriter.sh apply),
                                         maze.json (points for the tests and the walk bot), docs/reports/T-024/maze_plan.png,
                                         datapack structure/maze/*.nbt and function/maze/gen/* (tools/build/maze_dp.py)
  python3 tools/build/r1_maze.py check -> only the check of the 729 combinations of the movable cells on the block grid
Inputs: server/build/r1/base.bin (the ground before the R1 frame), maze_pre.bin (scan of the place after the frame), allow.npz (r1.py).
The plan of the cells (which nodes are joined) is tools/build/maze_plan.json (tools/build/maze_layout.py: partitions of the ports in
maze_macro.json -> trees; checked there on the node graph and here on the block grid).

Layout (card «Заколдованный лабиринт», HQ T-024 and its answer on the relief): paths at y 111 (= the pad of bonfire 3), the square
x -210..-91, z -490..-371 of 5x5 cells 24x24 + an outer hedge ring (x -211 / -90, z -491 / -370): the wall is 2 thick everywhere.
Hedges: socle 1 (y 112) + leaves 6 (113..118), barrier ceiling at y 119 over all of it except the dome of the sanctum. The terrace
(the square + a band of 8 on the level of the paths): earth fill; over the bay of the lake a deck on piers; on the north and east,
where the ground falls by more than the 8 blocks of the margin, a retaining wall (buttresses, belt courses, rock at the foot, ivy),
with a parapet 2 high along the band."""
import json, math, os, struct, subprocess, sys
from collections import deque
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanio import Scan, write_grid, NONE
from lib import B, Mix, h as hsh
import maze_layout as ML

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "server/build/r1")
DP = os.path.join(ROOT, "datapack/data/last_ember")
G = 111                       # top of the path blocks (= the pad of bonfire 3: hearth y 112)
Y = G + 1                     # feet
CEIL = G + 8                  # barrier ceiling
X0, Z0 = -210, -490           # north-west corner of cell (0, 0)
CS = 24
OX1, OX2, OZ1, OZ2 = X0 - 1, X0 + 5 * CS, Z0 - 1, Z0 + 5 * CS          # the outer ring: -211 / -90, -491 / -370
BAND = 8
TX1, TX2, TZ1, TZ2 = OX1 - BAND, OX2 + BAND, OZ1 - BAND, OZ2 + BAND    # the terrace top: -219..-82, -499..-362
CX, CZ = -150, -430           # centre of the sanctum = a block corner (cell (2,2) spans -162..-139, -442..-419)
MARGIN = 16
PLACE = (-226, -506, -74, -354)   # rect core 120 + margin 16 (x1 z1 x2 z2), r1.plot_dist for rect: |X-cx| <= 60 + 16
def in_place(x, z):
    """r1.plot_dist of the place <= its margin: the corners of PLACE are rounded (radius 16)"""
    return np.hypot(np.maximum(np.abs(x + 150) - 60, 0), np.maximum(np.abs(z + 430) - 60, 0)) <= 16
PAD = (-156, -367, -143, -354)    # the pad of bonfire 3 (14x14): never written; its rim is levelled to the paths (the gate is 3 blocks north)
HEARTH = (-150, 112, -362)
GATE_X = (-151, -149)         # the gate: local 11..13 of cell column 2
EXIT_X = (-152, -149)         # the secret exit: the middle lane (local 10..13) of cell column 2
EXIT_Z = (OZ1, Z0 + 2 * CS + 1)   # -491 .. -441: from the outer ring through the corridor cells (2,0) (2,1) to the court of the sanctum
S_FLAT, S_FOREST, S_ROCK, S_MOSS = 7, 2, 10, 6
R_WEST = 1

def cell_origin(c): return X0 + CS * c[0], Z0 + CS * c[1]
def plan():
    d = json.load(open(os.path.join(ROOT, "tools/build/maze_plan.json")))
    cells = {}
    for k, vs in d["cells"].items():
        c = tuple(int(t) for t in k.split(","))
        cells[c] = [dict(groups=v["groups"], links={((a, b), (e, f)) for a, b, e, f in v["links"]}, dead=[((i, j), dd) for i, j, dd in v["dead"]]) for v in vs]
    return cells
MOVABLE = ML.MOVABLE                      # k = index + 1: (1,1) (3,1) (1,3) (3,3) (0,2) (4,2)

# ---------------------------------------------------------------- palette
LEAF = "[distance=1,persistent=true,waterlogged=false]"
HEDGE = Mix({"dark_oak_leaves" + LEAF: 40, "spruce_leaves" + LEAF: 20, "red_poplar_leaves" + LEAF: 12.5, "orange_poplar_leaves" + LEAF: 12.5,
             "azalea_leaves" + LEAF: 10, "flowering_azalea_leaves" + LEAF: 5}, 2401)
SOCLE = Mix({"mossy_cobblestone": 50, "mossy_stone_bricks": 50}, 2402)
PATH = Mix({"coarse_dirt": 35, "gravel": 25, "moss_block": 20, "podzol[snowy=false]": 20}, 2403)
FLOWERS = {"NE": ["poppy", "red_tulip"], "NW": ["lily_of_the_valley", "white_tulip"], "SW": ["cornflower", "blue_orchid"],
           "SE": ["dandelion", "wildflowers[facing=%s,flower_amount=%d]"]}
PLATE = Mix({"polished_andesite": 55, "stone_bricks": 35, "mossy_stone_bricks": 10}, 2404)
COLUMN = ["calcite", "polished_diorite"]
DOME = Mix({"stone_bricks": 60, "mossy_stone_bricks": 25, "cracked_stone_bricks": 15}, 2405)
def quarter(x, z):
    return ("N" if z < CZ else "S") + ("E" if x >= CX else "W")

# ---------------------------------------------------------------- cells: 24x24 masks (True = path), statues
def lane_span(i): o, w = ML.LANES[i]; return o, o + w - 1
def node_box(n):
    (x1, x2), (z1, z2) = lane_span(n[0]), lane_span(n[1]); return x1, z1, x2, z2
def link_box(a, b):
    """the gap in the 2-thick hedge between two neighbouring nodes"""
    (i1, j1), (i2, j2) = sorted([a, b])
    if j1 == j2:   # east-west
        x1 = lane_span(i1)[1] + 1; x2 = lane_span(i2)[0] - 1; z1, z2 = lane_span(j1); return x1, z1, x2, z2
    z1 = lane_span(j1)[1] + 1; z2 = lane_span(j2)[0] - 1; x1, x2 = lane_span(i1); return x1, z1, x2, z2
def port_box(d):
    p0, p1 = ML.PORT
    i, j = ML.PORT_NODE[d]; nx1, nz1, nx2, nz2 = node_box((i, j))
    if d == "N": return p0, 0, p1, nz1 - 1
    if d == "S": return p0, nz2 + 1, p1, CS - 1
    if d == "W": return 0, p0, nx1 - 1, p1
    return nx2 + 1, p0, CS - 1, p1
def cell_mask(c, v):
    m = np.zeros((CS, CS), bool)
    def carve(b):
        x1, z1, x2, z2 = b; m[z1:z2 + 1, x1:x2 + 1] = True
    for n in ML.nodes_of(c): carve(node_box(n))
    for a, b in v["links"]: carve(link_box(a, b))
    for d in ML.cell_ports(c): carve(port_box(d))
    return m
def statues_of(c, v):
    """dead-end statues: (lx, lz, exit direction): in the dead-end node against its far side, in the middle of the lane"""
    out = []
    for (i, j), d in v["dead"]:
        x1, z1, x2, z2 = node_box((i, j)); mx = (x1 + x2) // 2; mz = (z1 + z2) // 2
        if d == "N": out.append((mx, z2, d))
        elif d == "S": out.append((mx, z1, d))
        elif d == "W": out.append((x2, mz, d))
        else: out.append((x1, mz, d))
    return out
STAIR_FACE = {"N": "north", "S": "south", "E": "east", "W": "west"}
def head_state(exit_dir, follow):
    """the head is a stair: its low step is the broken face. rest: the face looks away from the exit (straight along the dead end,
    at the hedge); follow: the face looks along the way out (after the player). facing = the high side = opposite of the face"""
    face = exit_dir if follow else ML.OPP[exit_dir]
    return "minecraft:polished_diorite_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]" % STAIR_FACE[ML.OPP[face]]

def cell_blocks(c, v, k_var=0):
    """{(lx, ly, lz): state}: ly 0 = path layer (y G) .. 8 = ceiling. Corridor cells leave the middle lane to the exit template."""
    m = cell_mask(c, v); out = {}
    ox, oz = cell_origin(c)
    corridor = c in ML.CORRIDOR
    sts = {(sx, sz): d for sx, sz, d in statues_of(c, v)}
    for lz in range(CS):
        for lx in range(CS):
            if corridor and 10 <= lx <= 13: continue
            x, z = ox + lx, oz + lz
            out[(lx, 8, lz)] = "minecraft:barrier"
            if not m[lz, lx]:
                out[(lx, 0, lz)] = "minecraft:coarse_dirt"; out[(lx, 1, lz)] = SOCLE.at(x, Y, z)
                for ly in range(2, 8): out[(lx, ly, lz)] = HEDGE.at(x, G + ly, z)
                continue
            for ly in range(1, 8): out[(lx, ly, lz)] = "minecraft:air"
            fl = PATH.at(x, G, z)
            if (lx, lz) in sts:
                d = sts[(lx, lz)]
                out[(lx, 0, lz)] = "minecraft:moss_block"; out[(lx, 1, lz)] = "minecraft:calcite"; out[(lx, 2, lz)] = "minecraft:polished_diorite"
                out[(lx, 3, lz)] = head_state(d, False)
                continue
            # flowers along the socle (low, passable): on cells next to a hedge
            near = any(0 <= lx + dx < CS and 0 <= lz + dz < CS and not m[lz + dz, lx + dx] for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            r = hsh(x, 7, z, 2410)
            if near and r < 0.24:
                q = FLOWERS[quarter(x, z)]; f = q[int(hsh(x, 8, z, 2411) * 2)]
                if "%" in f: f = f % (("north", "east", "south", "west")[int(hsh(x, 9, z, 2412) * 4)], 1 + int(hsh(x, 10, z, 2413) * 3))
                out[(lx, 0, lz)] = "minecraft:coarse_dirt" if r < 0.12 else "minecraft:moss_block"
                out[(lx, 1, lz)] = "minecraft:" + f
                continue
            out[(lx, 0, lz)] = "minecraft:" + fl.replace("minecraft:", "")
            if "moss_block" in fl and hsh(x, 11, z, 2414) < 0.7: out[(lx, 1, lz)] = "minecraft:moss_carpet"
            elif any(0 <= lx + dx < CS and 0 <= lz + dz < CS and (lx + dx, lz + dz) in sts for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))) and hsh(x, 12, z, 2415) < 0.6:
                out[(lx, 0, lz)] = "minecraft:moss_block"; out[(lx, 1, lz)] = "minecraft:moss_carpet"   # moss round the feet of the statues
    return out

# ---------------------------------------------------------------- the sanctum (cell (2,2)): court r 10, dry fountain, rotunda, dome, guards
R_COURT = 10.0
GUARDS = [("n", (0, -1)), ("e", (1, 0)), ("s", (0, 1)), ("w", (-1, 0))]        # at 5 from the centre, facing it
def guard_box(d):
    """the 2x2 pedestal of a guard: x1 z1 (north-west block) and the direction to the centre"""
    dx, dz = d
    if dx == 0: x1 = CX - 1; z1 = CZ - 6 if dz < 0 else CZ + 4
    else: z1 = CZ - 1; x1 = CX - 6 if dx < 0 else CX + 4
    return x1, z1
def dist(x, z): return math.hypot(x + 0.5 - CX, z + 0.5 - CZ)
COLUMNS = []
for k in range(8):
    a = math.radians(22.5 + 45 * k); COLUMNS.append((int(math.floor(CX + 7 * math.sin(a))), int(math.floor(CZ - 7 * math.cos(a)))))
DOME_R = 8.6
def dome_top(r):
    """outer surface of the dome over radius r (blocks above G+7)"""
    if r > DOME_R: return None
    return G + 7 + int(round(math.sqrt(max(DOME_R ** 2 - r * r, 0)) * 0.85))
def guard_cells(d, statue=True):
    """{(x, y, z): state} of the 2x2x5 box of a guard: pedestal + (statue | air)"""
    x1, z1 = guard_box(d); dx, dz = d; out = {}
    # 'front' = the side towards the centre; 'left/right' seen from the statue
    cells = [(x1, z1), (x1 + 1, z1), (x1, z1 + 1), (x1 + 1, z1 + 1)]
    def front(p): return (p[0] + 0.5 - CX) * -dx + (p[1] + 0.5 - CZ) * -dz > -5.0 if False else ((p[0] - x1) == (1 if dx < 0 else 0) if dx else (p[1] - z1) == (1 if dz < 0 else 0))
    fr = [p for p in cells if front(p)]; bk = [p for p in cells if not front(p)]
    # left of the statue looking at the centre (direction -d): left = rotate(-d) ccw
    lx_, lz_ = dz, -dx      # left vector for facing (-dx, -dz)
    fr.sort(key=lambda p: -(p[0] * lx_ + p[1] * lz_)); bk.sort(key=lambda p: -(p[0] * lx_ + p[1] * lz_))
    fl, frr = fr; bl, br = bk
    to_back = {(0, -1): "south", (0, 1): "north", (1, 0): "west", (-1, 0): "east"}[(-dx, -dz)]       # stairs facing the back of the statue
    for p in cells: out[(p[0], Y, p[1])] = "minecraft:chiseled_stone_bricks"
    for y in range(Y + 1, Y + 5):
        for p in cells: out[(p[0], y, p[1])] = "minecraft:air"
    if statue:
        W = "minecraft:polished_deepslate_wall[east=none,north=none,south=none,up=true,waterlogged=false,west=none]"
        out[(bl[0], Y + 1, bl[1])] = "minecraft:andesite"; out[(br[0], Y + 1, br[1])] = "minecraft:andesite"
        out[(fl[0], Y + 1, fl[1])] = W; out[(fl[0], Y + 2, fl[1])] = W; out[(fl[0], Y + 3, fl[1])] = W
        out[(bl[0], Y + 2, bl[1])] = "minecraft:mossy_stone_bricks"; out[(br[0], Y + 2, br[1])] = "minecraft:mossy_stone_bricks"
        out[(bl[0], Y + 3, bl[1])] = "minecraft:mossy_stone_bricks"; out[(br[0], Y + 3, br[1])] = "minecraft:mossy_stone_bricks"
        out[(frr[0], Y + 2, frr[1])] = "minecraft:andesite_stairs[facing=%s,half=top,shape=straight,waterlogged=false]" % to_back
        out[(frr[0], Y + 3, frr[1])] = "minecraft:andesite_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]" % to_back
        out[(bl[0], Y + 4, bl[1])] = "minecraft:polished_andesite"
        out[(br[0], Y + 4, br[1])] = "minecraft:polished_andesite_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]" % to_back
    return out
def sanctum_blocks(b):
    c = ML.SANCTUM; ox, oz = cell_origin(c)
    v = {"links": set()}
    guard_xz = set()
    for _, d in GUARDS:
        x1, z1 = guard_box(d); guard_xz |= {(x1, z1), (x1 + 1, z1), (x1, z1 + 1), (x1 + 1, z1 + 1)}
    for lz in range(CS):
        for lx in range(CS):
            x, z = ox + lx, oz + lz; r = dist(x, z)
            if EXIT_X[0] <= x <= EXIT_X[1] and z <= EXIT_Z[1]: continue        # the exit template
            b.set(x, CEIL, z, "barrier")
            port = (ML.PORT[0] <= lx <= ML.PORT[1] and lz > 12) or ML.PORT[0] <= lz <= ML.PORT[1]     # S, W, E ports (N = the exit)
            if r > R_COURT and not port:
                b.set(x, G, z, "coarse_dirt"); b.set(x, Y, z, SOCLE)
                for y in range(Y + 1, CEIL): b.set(x, y, z, HEDGE)
                continue
            # floor: plates, a ring of stone bricks round the court
            b.set(x, G, z, PLATE if r <= R_COURT else PATH)
            for y in range(Y, CEIL): b.set(x, y, z, "air")
    # dry fountain: rim of slabs (r 2..3.3), the bowl floor of cracked bricks, the pedestal of the key 2x2 in the middle
    for x in range(CX - 4, CX + 4):
        for z in range(CZ - 4, CZ + 4):
            r = dist(x, z)
            if 2.0 < r <= 3.3: b.set(x, Y, z, "mossy_stone_brick_slab[type=bottom,waterlogged=false]" if hsh(x, 0, z, 2420) < 0.7 else "stone_brick_slab[type=bottom,waterlogged=false]")
            elif r <= 2.0: b.set(x, G, z, "cracked_stone_bricks" if hsh(x, 1, z, 2421) < 0.5 else "mossy_stone_bricks")
    for x in (CX - 1, CX):
        for z in (CZ - 1, CZ): b.set(x, Y, z, "chiseled_stone_bricks"); b.set(x, Y + 1, z, "mossy_stone_brick_slab[type=bottom,waterlogged=false]")
    # candles on the rim
    for k in range(8):
        a = math.radians(k * 45 + 10); x = int(math.floor(CX + 2.7 * math.sin(a))); z = int(math.floor(CZ - 2.7 * math.cos(a)))
        b.set(x, Y + 1, z, "candle[candles=%d,lit=true,waterlogged=false]" % (2 + k % 3))
    # columns (8, r 7) and the entablature ring at G+7, the dome above
    for i, (x, z) in enumerate(COLUMNS):
        b.set(x, Y, z, "chiseled_stone_bricks")
        for y in range(Y + 1, Y + 6): b.set(x, y, z, COLUMN[(y + i) % 2])
    for x in range(CX - 10, CX + 10):
        for z in range(CZ - 10, CZ + 10):
            r = dist(x, z); t = dome_top(r)
            if t is None: continue
            if r >= 6.0: b.set(x, G + 7, z, DOME)
            lo = G + 8 if r >= 6.0 else max(G + 8, t - 1)
            for y in range(G + 8, lo): b.set(x, y, z, "air")         # the inside of the dome
            for y in range(lo, t + 1): b.set(x, y, z, DOME)
    # stairs on the outer surface of the dome, a lantern on the top inside
    for x in range(CX - 10, CX + 10):
        for z in range(CZ - 10, CZ + 10):
            r = dist(x, z); t = dome_top(r)
            if t is None or t <= G + 8 or r < 1.0: continue
            tn = [dome_top(dist(x + dx, z + dz)) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if any(q is None or q < t for q in tn):
                ax, az = x + 0.5 - CX, z + 0.5 - CZ
                f = ("west" if ax > 0 else "east") if abs(ax) > abs(az) else ("north" if az > 0 else "south")
                b.set(x, t, z, "stone_brick_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]" % f)
    for x, z in ((CX - 1, CZ - 1), (CX, CZ - 1), (CX - 1, CZ), (CX, CZ)):
        b.set(x, dome_top(0.8) + 1, z, "chiseled_stone_bricks")
    # lanterns hanging from the entablature (between the columns, on the diagonals)
    for k in range(4):
        a = math.radians(45 + 90 * k); x = int(math.floor(CX + 6.3 * math.sin(a))); z = int(math.floor(CZ - 6.3 * math.cos(a)))
        b.set(x, G + 6, z, "lantern[hanging=true,waterlogged=false]")
    # pedestals of the guards (the statues are templates)
    for _, d in GUARDS:
        for (x, y, z), s in guard_cells(d, statue=False).items():
            if y == Y: b.set(x, y, z, s)
    return guard_xz

# ---------------------------------------------------------------- the outer ring, the gate, the exit
def ring_blocks(b):
    for x in range(OX1, OX2 + 1):
        for z in range(OZ1, OZ2 + 1):
            if OX1 < x < OX2 and OZ1 < z < OZ2: continue
            if EXIT_X[0] <= x <= EXIT_X[1] and z == OZ1: continue      # exit template
            b.set(x, CEIL, z, "barrier")
            if z == OZ2 and GATE_X[0] <= x <= GATE_X[1]:
                b.set(x, G, z, PATH)
                for y in range(Y, Y + 4): b.set(x, y, z, "air")
                for y in range(Y + 4, CEIL): b.set(x, y, z, "iron_bars[east=true,north=false,south=false,waterlogged=false,west=true]")
                continue
            b.set(x, G, z, "coarse_dirt"); b.set(x, Y, z, SOCLE)
            for y in range(Y + 1, CEIL): b.set(x, y, z, HEDGE)
    # the gate: posts of stone bricks in the outer ring, iron bars over the opening in both rows (the cell border row too), lanterns outside
    for x in (GATE_X[0] - 1, GATE_X[1] + 1):
        for y in range(Y, CEIL): b.set(x, y, OZ2, "stone_bricks" if y != Y + 3 else "chiseled_stone_bricks")
        b.set(x, CEIL - 1 + 1, OZ2, "barrier")
    for x in range(GATE_X[0], GATE_X[1] + 1):
        for y in range(Y + 4, CEIL): b.set(x, y, OZ2 - 1, "iron_bars[east=true,north=false,south=false,waterlogged=false,west=true]")
    # leaves of the gate swung open outside (iron bars against the ring), two lantern posts in front
    for x in (GATE_X[0] - 2, GATE_X[1] + 2):
        for y in range(Y, Y + 4): b.set(x, y, OZ2 + 1, "iron_bars[east=true,north=false,south=false,waterlogged=false,west=true]")
    for x in (GATE_X[0] - 4, GATE_X[1] + 4):
        b.set(x, Y, OZ2 + 1, "stone_bricks"); b.set(x, Y + 1, OZ2 + 1, "stone_brick_wall[east=none,north=none,south=none,up=true,waterlogged=false,west=none]")
        b.set(x, Y + 2, OZ2 + 1, "lantern[hanging=false,waterlogged=false]")
def exit_cells(open_):
    """the corridor of the secret exit: x -152..-149, z -491..-441, y G..CEIL"""
    out = {}
    for x in range(EXIT_X[0], EXIT_X[1] + 1):
        for z in range(EXIT_Z[0], EXIT_Z[1] + 1):
            out[(x, CEIL, z)] = "minecraft:barrier"
            if open_:
                out[(x, G, z)] = "minecraft:" + ("gravel" if hsh(x, 0, z, 2430) < 0.4 else "coarse_dirt" if hsh(x, 0, z, 2430) < 0.75 else "moss_block")
                for y in range(Y, CEIL): out[(x, y, z)] = "minecraft:air"
            else:
                out[(x, G, z)] = "minecraft:coarse_dirt"; out[(x, Y, z)] = SOCLE.at(x, Y, z)
                for y in range(Y + 1, CEIL): out[(x, y, z)] = HEDGE.at(x, y, z)
    return out

# ---------------------------------------------------------------- the block-level walk grid and the 729 check
def walk_grid(cells, combo, exit_open=False):
    """122 x 122 (x -211..-90, z -491..-370): True = a player can stand here (feet and head free) on the level of the paths"""
    W = np.zeros((OZ2 - OZ1 + 1, OX2 - OX1 + 1), bool)
    def put(x, z, val): W[z - OZ1, x - OX1] = val
    for c, vs in cells.items():
        if c == ML.SANCTUM: continue
        v = vs[combo.get(c, 0)]; ox, oz = cell_origin(c); m = cell_mask(c, v)
        sts = {(sx, sz) for sx, sz, d in statues_of(c, v)}
        for lz in range(CS):
            for lx in range(CS):
                if c in ML.CORRIDOR and 10 <= lx <= 13: continue
                put(ox + lx, oz + lz, bool(m[lz, lx]) and (lx, lz) not in sts)
    sb = B("s"); sanctum_blocks(sb)
    for _, d in GUARDS: sb.v.update({k: v for k, v in guard_cells(d, True).items()})
    ox, oz = cell_origin(ML.SANCTUM)
    for x in range(ox, ox + CS):
        for z in range(oz, oz + CS):
            if EXIT_X[0] <= x <= EXIT_X[1] and z <= EXIT_Z[1]: continue
            f, hd = sb.get(x, Y, z), sb.get(x, Y + 1, z)
            free = lambda s: s is None or any(t in s for t in ("air", "slab", "candle", "carpet", "lantern"))
            put(x, z, free(f) and free(hd) and not (f and "slab" in f and hd and "slab" in hd))
    for x in range(GATE_X[0], GATE_X[1] + 1): put(x, OZ2, True)
    if exit_open:
        for x in range(EXIT_X[0], EXIT_X[1] + 1):
            for z in range(EXIT_Z[0], EXIT_Z[1] + 1): put(x, z, True)
    return W
def reach(W, start):
    seen = np.zeros(W.shape, bool); dq = deque([start]); seen[start] = True
    while dq:
        z, x = dq.popleft()
        for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (z + dz, x + dx)
            if 0 <= q[0] < W.shape[0] and 0 <= q[1] < W.shape[1] and W[q] and not seen[q]: seen[q] = True; dq.append(q)
    return seen
def check_729(cells, verbose=True):
    start = (OZ2 - OZ1, -150 - OX1); goal = (CZ - 8 - OZ1, CX - OX1)     # the gate; a cell of the court north of the fountain
    bad = []; lens = []
    for vs in __import__("itertools").product(range(3), repeat=6):
        combo = dict(zip(MOVABLE, vs)); W = walk_grid(cells, combo)
        S = reach(W, start)
        pockets = int((W & ~S).sum())
        if not S[goal] or pockets: bad.append((vs, bool(S[goal]), pockets))
        if vs == (0,) * 6:      # the open secret exit: the court reaches the outer edge straight through the exit lane
            S2 = reach(walk_grid(cells, combo, exit_open=True), goal)
            if not S2[0, EXIT_X[0] + 1 - OX1]: bad.append(("exit", False, 0))
    if verbose: print("729 combinations on the block grid: %d bad%s; the open exit leads from the court to the north edge" % (len(bad), (" e.g. %s" % bad[:3]) if bad else ""))
    return bad

# ---------------------------------------------------------------- all the blocks written offline (permanent cells, sanctum, ring)
def maze_blocks(cells):
    b = B("maze")
    for c, vs in cells.items():
        if c in MOVABLE or c == ML.SANCTUM: continue
        ox, oz = cell_origin(c)
        for (lx, ly, lz), s in cell_blocks(c, vs[0]).items(): b.v[(ox + lx, G + ly, oz + lz)] = s if s.startswith("minecraft:") else "minecraft:" + s
    guard_xz = sanctum_blocks(b)
    ring_blocks(b)
    # solid ground under the whole floor (a cut hill may have a cave right under it: gravel of the paths would fall when a template
    # is placed); the deck over the bay replaces it with masonry
    for x in range(OX1, OX2 + 1):
        for z in range(OZ1, OZ2 + 1):
            for y in (G - 2, G - 1):
                if (x, y, z) not in b.v: b.v[(x, y, z)] = "minecraft:dirt"
    return b, guard_xz

if __name__ == "__main__" and sys.argv[1:2] == ["check"]:
    check_729(plan())

# ---------------------------------------------------------------- terrain: the terrace (earth), the seam, the retaining walls
def grids():
    x1, z1, x2, z2 = PLACE; X, Z = np.meshgrid(np.arange(x1, x2 + 1), np.arange(z1, z2 + 1))
    pre = Scan(os.path.join(OUT, "maze_pre.bin"))
    def grid(a): return a[z1 - pre.z0:z2 - pre.z0 + 1, x1 - pre.x0:x2 - pre.x0 + 1].astype(np.int32)
    al = np.load(os.path.join(OUT, "allow.npz")); A = al["allow"]; ax0, az0 = int(al["x0"]), int(al["z0"])
    allow = A[z1 - az0:z2 - az0 + 1, x1 - ax0:x2 - ax0 + 1].copy()
    base = Scan(os.path.join(OUT, "base.bin"))
    nat = base.ground[z1 - base.z0:z2 - base.z0 + 1, x1 - base.x0:x2 - base.x0 + 1].astype(np.int32)
    bw = base.water[z1 - base.z0:z2 - base.z0 + 1, x1 - base.x0:x2 - base.x0 + 1].astype(np.int32)
    # the ground before the maze, the same on every run (the decisions - walls, seam, rock foot - must not follow our own earlier
    # writes): the R1 frame's grid (terrain.bin, r1.py) where it wrote a column, the ground before the frame (base.bin) elsewhere
    d = open(os.path.join(OUT, "terrain.bin"), "rb").read(); assert d[:4] == b"LETA"
    tx0, tz0, tw, th = struct.unpack("<4i", d[4:20]); TH = np.frombuffer(d, "<i2", tw * th, 20).reshape(th, tw).astype(np.int32)
    fr = TH[z1 - tz0:z2 - tz0 + 1, x1 - tx0:x2 - tx0 + 1]
    before = np.where(fr != NONE, fr, nat)
    return dict(X=X, Z=Z, x1=x1, z1=z1, now=before, live=grid(pre.ground), top=grid(pre.top), water=grid(pre.water), allow=allow, nat=nat,
                natwater=np.where((bw != NONE) & (bw > nat), bw, NONE))
def terrace(gr):
    """masks and heights: T (terrace top), deck (T over the natural water of the bay), wall (T edge columns that are a retaining wall),
    the seam outside T, the rock foot of the walls"""
    X, Z, now, nat = gr["X"], gr["Z"], gr["now"], gr["nat"]
    T = (X >= TX1) & (X <= TX2) & (Z >= TZ1) & (Z <= TZ2)
    pad = (X >= PAD[0]) & (X <= PAD[2]) & (Z >= PAD[1]) & (Z <= PAD[3])
    water = gr["natwater"] != NONE
    deck = T & water
    # edge columns of T and their outward normal; a wall where the 1:1 slope from the band does not reach the ground inside the margin
    wall = np.zeros(X.shape, bool); foot = np.full(X.shape, NONE)
    def at(a, x, z): return int(a[z - gr["z1"], x - gr["x1"]])
    sides = [("N", [(x, TZ1) for x in range(TX1, TX2 + 1)], (0, -1)), ("S", [(x, TZ2) for x in range(TX1, TX2 + 1)], (0, 1)),
             ("W", [(TX1, z) for z in range(TZ1, TZ2 + 1)], (-1, 0)), ("E", [(TX2, z) for z in range(TZ1, TZ2 + 1)], (1, 0))]
    for name, cols, (nx, nz) in sides:
        need = []
        for x, z in cols:
            lowest = min(at(now, x + nx * k, z + nz * k) for k in range(1, 8))
            need.append(G - lowest > 8 - 1)
        need = np.array(need)
        grow = need.copy()
        for k in range(1, 5): grow[k:] |= need[:-k]; grow[:-k] |= need[k:]
        for (x, z), w in zip(cols, grow):
            if w and not pad[z - gr["z1"], x - gr["x1"]]: wall[z - gr["z1"], x - gr["x1"]] = True
    # seam: slopes 1:1 from the non-wall edge of T (fill and cut), natural ground in front of the walls (+ a rock foot)
    def cheb(src, n=9):
        d = np.where(src, 0, 99)
        for _ in range(n):
            p = np.pad(d, 1, constant_values=99); m = d.copy()
            for dz in (0, 1, 2):
                for dx in (0, 1, 2): m = np.minimum(m, p[dz:dz + d.shape[0], dx:dx + d.shape[1]] + 1)
            d = m
        return d
    d_slope = cheb(T & ~wall & ~deck); d_wall = cheb(wall | (deck & ~T)); d_any = cheb(T)
    H = now.astype(float).copy(); S = np.full(X.shape, S_FOREST, np.uint8); fixed = np.zeros(X.shape, bool)
    land = T & ~deck & ~pad
    H[land] = G; S[land] = S_MOSS; S[(X >= OX1) & (X <= OX2) & (Z >= OZ1) & (Z <= OZ2)] = S_FLAT
    seam = ~T & (d_any <= 9) & ~gr["allow"] & (gr["natwater"] == NONE) & in_place(X, Z)
    up = np.clip(now, G - d_slope, G + d_slope)
    near_wall = seam & (d_wall < d_slope)
    sl = seam & ~near_wall & (d_slope <= 8)
    H[sl] = up[sl]
    S[sl] = np.where(np.abs(up - now)[sl] > 0, S_FOREST, S[sl])
    # the rock foot in front of a wall: natural rock 10..20 high at the face, falling 2 per block outward
    rh = 10 + (np.vectorize(lambda x, z: hsh(x // 5, 0, z // 5, 2440))(X, Z) * 10).astype(int)
    rock = near_wall & (d_wall <= 6) & in_place(X, Z)
    footv = np.maximum(now, now + rh - 2 * d_wall)
    H[rock] = np.minimum(footv[rock], G - 6); S[rock] = S_ROCK
    return dict(T=T, deck=deck, wall=wall, pad=pad, land=land, H=H, S=S, seam=sl | rock, rock=rock, d_wall=d_wall)

def write_terrain(gr, tr, b):
    """only the columns whose ground is not yet what it should be (a re-run on the built maze rewrites nothing: terrain apply would
    remove the entities and the blocks of the columns it touches). Our own blocks over the wanted ground are not a reason to rewrite."""
    H, now, X, Z = tr["H"], gr["live"], gr["X"], gr["Z"]
    want = np.round(H).astype(int)
    top = np.full(H.shape, -999, int)
    for (x, y, z), s in b.v.items():
        nm = s.split("[")[0]
        if nm in ("minecraft:air", "minecraft:barrier") or "leaves" in nm: continue
        i, j = z - gr["z1"], x - gr["x1"]
        if 0 <= i < H.shape[0] and 0 <= j < H.shape[1] and y > want[i, j]: top[i, j] = max(top[i, j], y)
    # the templates of the datapack (movable cells: socle and statues up to G+3; the guards up to G+5; the exit: socle G+1)
    for c in MOVABLE:
        ox, oz = cell_origin(c); top[oz - gr["z1"]:oz + CS - gr["z1"], ox - gr["x1"]:ox + CS - gr["x1"]] = np.maximum(top[oz - gr["z1"]:oz + CS - gr["z1"], ox - gr["x1"]:ox + CS - gr["x1"]], G + 3)
    for _, d in GUARDS:
        x1, z1 = guard_box(d); sl = (slice(z1 - gr["z1"], z1 + 2 - gr["z1"]), slice(x1 - gr["x1"], x1 + 2 - gr["x1"])); top[sl] = np.maximum(top[sl], G + 5)
    top[EXIT_Z[0] - gr["z1"]:EXIT_Z[1] + 1 - gr["z1"], EXIT_X[0] - gr["x1"]:EXIT_X[1] + 1 - gr["x1"]] = np.maximum(top[EXIT_Z[0] - gr["z1"]:EXIT_Z[1] + 1 - gr["z1"], EXIT_X[0] - gr["x1"]:EXIT_X[1] + 1 - gr["x1"]], G + 1)
    own = (now <= np.maximum(top, want)) & (now >= want)
    cand = (tr["land"] | tr["seam"]) & ~tr["pad"] & ~tr["deck"]
    touch = cand & (now != want) & ~own
    Hh = np.where(touch, want, NONE).astype(np.int32)
    lo = want.copy()
    for dz, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): lo = np.minimum(lo, np.roll(np.roll(lo, dz, 0), dx, 1))
    F = np.minimum(np.minimum(want, now), lo) - 4
    write_grid(os.path.join(OUT, "maze_terrain.bin"), gr["x1"], gr["z1"], Hh, F, np.full(H.shape, NONE, np.int32), tr["S"], np.full(H.shape, R_WEST, np.uint8), np.zeros(H.shape, np.uint8))
    tr["touch"] = touch
    return int(touch.sum())

# ---------------------------------------------------------------- blocks of the terrace: wall faces, buttresses, belts, ivy, parapet, the deck and its piers
FACE_HI = Mix({"mossy_stone_bricks": 45, "mossy_cobblestone": 30, "stone_bricks": 10, "cracked_stone_bricks": 15}, 2441)
FACE_LO = Mix({"stone": 30, "andesite": 25, "tuff": 20, "cobblestone": 10, "mossy_cobblestone": 15}, 2442)
ROCKS = Mix({"stone": 40, "andesite": 30, "tuff": 20, "cobblestone": 10}, 2443)
DECK = Mix({"stone_bricks": 45, "mossy_stone_bricks": 35, "cracked_stone_bricks": 20}, 2444)
def face_block(x, y, z, foot):
    """rock at the foot (10..20 blocks), masonry above with a mixed band in between; mangrove roots from some cracks"""
    rh = 10 + int(hsh(x // 5, 0, z // 5, 2440) * 10)
    t = (y - foot - rh) / 6.0
    if hsh(x, y, z, 2445) < 0.012 and y > foot + 4: return "minecraft:mangrove_roots[waterlogged=false]"
    if t < 0 or hsh(x, y, z, 2446) > t: return ROCKS.at(x, y, z) if t < -0.5 else FACE_LO.at(x, y, z)
    return FACE_HI.at(x, y, z)
def terrace_blocks(gr, tr, b):
    X, Z, now = gr["X"], gr["Z"], gr["now"]
    def at(a, x, z): return a[z - gr["z1"], x - gr["x1"]]
    def inside(x, z): return PLACE[0] <= x <= PLACE[2] and PLACE[1] <= z <= PLACE[3]
    n_face = 0
    # retaining walls: the outer 2 columns of T on the wall edges, from the natural foot up to G; parapet on the outer one
    outward = {}
    for x in range(TX1, TX2 + 1): outward[(x, TZ1)] = (0, -1); outward[(x, TZ2)] = (0, 1)
    for z in range(TZ1, TZ2 + 1): outward[(TX1, z)] = (-1, 0); outward[(TX2, z)] = (1, 0)
    for (x, z), (nx, nz) in sorted(outward.items()):
        if not at(tr["wall"], x, z) or at(tr["pad"], x, z): continue
        deck = bool(at(tr["deck"], x, z))
        foot = int(min(at(now, x + nx, z + nz), at(gr["nat"], x, z)))
        if deck: foot = int(at(gr["nat"], x, z))
        ground_out = int(round(at(tr["H"], x + nx, z + nz)))          # the ground in front of the face after the rock foot
        for k in (0, 1):
            qx, qz = x - nx * k, z - nz * k
            if deck: continue        # over the bay: piers (below), the deck edge is masonry
            for y in range(foot - 2, G): b.set(qx, y, qz, face_block(qx, y, qz, foot)); n_face += 1
        # parapet 2 high on the outer column (solid + wall)
        b.set(x, Y, z, "mossy_stone_bricks" if hsh(x, 1, z, 2447) < 0.6 else "stone_bricks")
        b.set(x, Y + 1, z, "mossy_stone_brick_wall" if hsh(x, 2, z, 2448) < 0.6 else "stone_brick_wall")
        # belt courses: upside-down stairs one block out, at G-10, G-22, G-34 (where the face is high enough)
        if not deck:
            fac = {(0, -1): "south", (0, 1): "north", (-1, 0): "east", (1, 0): "west"}[(nx, nz)]
            for yb in (G - 10, G - 22, G - 34):
                if yb > foot + 12 and yb > ground_out + 2:
                    b.set(x + nx, yb, z + nz, "mossy_stone_brick_stairs[facing=%s,half=top,shape=straight,waterlogged=false]" % fac if hsh(x, yb, z, 2449) < 0.5 else
                          "stone_brick_stairs[facing=%s,half=top,shape=straight,waterlogged=false]" % fac)
                    if hsh(x, yb, z, 2450) < 0.25: b.set(x + nx, yb - 1, z + nz, "hanging_roots[waterlogged=false]")
            # ivy from the top: vines on the air column in front of the face
            if hsh(x, 3, z, 2451) < 0.55:
                L = 3 + int(hsh(x, 4, z, 2452) * 18); vside = {(0, -1): "south", (0, 1): "north", (-1, 0): "east", (1, 0): "west"}[(nx, nz)]
                for k in range(1, L + 1):
                    y = G - k
                    if y <= max(foot, ground_out) + 2 or b.get(x + nx, y, z + nz) is not None: break
                    st = {"north": "false", "south": "false", "east": "false", "west": "false"}; st[vside] = "true"
                    b.set(x + nx, y, z + nz, "vine[east=%s,north=%s,south=%s,up=false,west=%s]" % (st["east"], st["north"], st["south"], st["west"]))
    # buttresses every 14 blocks along the wall edges: 3 wide, 3 out at the foot, 2 from 40%, 1 from 75% of the height, stairs on the steps
    for (x, z), (nx, nz) in sorted(outward.items()):
        if not at(tr["wall"], x, z) or at(tr["deck"], x, z): continue
        along = x if nz else z
        if (along - TX1) % 14 != 7: continue
        foot = int(at(now, x + nx, z + nz)); hgt = G - 2 - foot
        if hgt < 10: continue
        for w in (-1, 0, 1):
            px, pz = (x + w, z) if nz else (x, z + w)
            for y in range(foot - 2, G - 2):
                f = (y - foot) / hgt; depth = 3 if f < 0.4 else 2 if f < 0.75 else 1
                for dd in range(1, depth + 1):
                    qx, qz = px + nx * dd, pz + nz * dd
                    if inside(qx, qz): b.set(qx, y, qz, face_block(qx, y, qz, foot))
            fac = {(0, -1): "south", (0, 1): "north", (-1, 0): "east", (1, 0): "west"}[(nx, nz)]
            for f0, dd in ((0.4, 3), (0.75, 2)):
                qx, qz = px + nx * dd, pz + nz * dd; y = foot + int(math.ceil(f0 * hgt))
                if inside(qx, qz): b.set(qx, y, qz, "mossy_stone_brick_stairs[facing=%s,half=bottom,shape=straight,waterlogged=false]" % fac)
    # the deck over the bay: masonry G-3..G-1, path layer at G (maze floor written by the maze, band: coarse dirt / moss); 2x2 piers every 9
    for z in range(TZ1, TZ2 + 1):
        for x in range(TX1, TX2 + 1):
            if not at(tr["deck"], x, z) or at(tr["pad"], x, z): continue
            for y in range(G - 3, G): b.set(x, y, z, DECK)
            inmaze = OX1 <= x <= OX2 and OZ1 <= z <= OZ2
            if not inmaze: b.set(x, G, z, "coarse_dirt" if hsh(x, 5, z, 2453) < 0.6 else "moss_block")
            edge = x in (TX1, TX2) or z in (TZ1, TZ2)
            if (x % 9 in (0, 1) and z % 9 in (0, 1)) or (edge and (x + z) % 7 in (0, 1)):
                bot = int(at(gr["nat"], x, z))
                for y in range(bot, G - 3): b.set(x, y, z, FACE_LO.at(x, y, z) if y < 62 else FACE_HI.at(x, y, z))
            if edge and not inmaze:
                b.set(x, Y, z, "mossy_stone_bricks"); b.set(x, Y + 1, z, "mossy_stone_brick_wall")
            if edge and (x + z) % 7 == 3: b.set(x, G - 4, z, "hanging_roots[waterlogged=false]")
    return n_face
def clear_trees(gr, tr, b):
    """air over the terrace top where the scan sees something above our blocks (trees of the forest that stood there)"""
    n = 0
    for z in range(TZ1, TZ2 + 1):
        for x in range(TX1, TX2 + 1):
            i, j = z - gr["z1"], x - gr["x1"]
            if tr["pad"][i, j]: continue
            tp = int(gr["top"][i, j]); lo = CEIL + 1 if OX1 <= x <= OX2 and OZ1 <= z <= OZ2 else Y
            if ML.SANCTUM == ((x - X0) // CS, (z - Z0) // CS): lo = G + 17
            for y in range(lo, min(tp, G + 45) + 1):
                if b.get(x, y, z) is None: b.set(x, y, z, "air"); n += 1
    return n

# ---------------------------------------------------------------- plan picture, data files, main
def plan_png(cells, statues, tr, gr, path):
    from PIL import Image, ImageDraw
    S = 5; x1, z1, x2, z2 = PLACE; w, h = (x2 - x1 + 1) * S, (z2 - z1 + 1) * S
    W = walk_grid(cells, {})
    img = Image.new("RGB", (w, h + 40), (20, 20, 24)); d = ImageDraw.Draw(img)
    for z in range(z1, z2 + 1):
        for x in range(x1, x2 + 1):
            i, j = z - z1, x - x1
            if OX1 <= x <= OX2 and OZ1 <= z <= OZ2:
                col = (196, 184, 140) if W[z - OZ1, x - OX1] else (34, 74, 38)
                if (x - X0) // CS * 0 == 0 and ((x - X0) // CS, (z - Z0) // CS) in MOVABLE and not W[z - OZ1, x - OX1]: col = (60, 110, 60)
            elif tr["T"][i, j]: col = (70, 120, 170) if tr["deck"][i, j] else (120, 140, 90)
            else:
                g = int(np.clip((gr["now"][i, j] - 40) * 2.5, 0, 255)); col = (g // 2, g // 2, g // 2)
                if gr["natwater"][i, j] != NONE: col = (40, 70, 150)
            if tr["wall"][i, j]: col = (150, 150, 150)
            d.rectangle([j * S, i * S, j * S + S - 1, i * S + S - 1], fill=col)
    if True:   # exit corridor (open), the gate
        for x in range(EXIT_X[0], EXIT_X[1] + 1):
            for z in range(EXIT_Z[0], EXIT_Z[1] + 1): d.rectangle([(x - x1) * S, (z - z1) * S, (x - x1) * S + S - 1, (z - z1) * S + S - 1], fill=(150, 120, 170))
    for c in [(cx, cz) for cx in range(5) for cz in range(5)]:
        ox, oz = cell_origin(c)
        k = (" M%d" % (MOVABLE.index(c) + 1)) if c in MOVABLE else ""
        d.rectangle([(ox - x1) * S, (oz - z1) * S, (ox + CS - x1) * S - 1, (oz + CS - z1) * S - 1], outline=(255, 210, 60) if c in MOVABLE else (90, 90, 90))
        d.text(((ox - x1) * S + 3, (oz - z1) * S + 2), "%d,%d%s" % (c[0], c[1], k), fill=(255, 255, 255))
    for s in statues:
        if s["var"] not in (None, 1): continue
        cx_, cz_ = (s["x"] - x1) * S + S // 2, (s["z"] - z1) * S + S // 2
        d.ellipse([cx_ - 3, cz_ - 3, cx_ + 3, cz_ + 3], fill=(230, 60, 60)); d.text((cx_ + 3, cz_ - 4), str(s["id"]), fill=(255, 190, 190))
    d.rectangle([(PAD[0] - x1) * S, (PAD[1] - z1) * S, (PAD[2] + 1 - x1) * S, (PAD[3] + 1 - z1) * S], outline=(255, 140, 0), width=2)
    d.text((6, h + 4), "T-024 maze plan (1 block = %d px, north up): yellow = movable cells M1..M6 (variant 1 shown), red = dead-end statues (id), violet = secret exit," % S, fill=(255, 255, 255))
    d.text((6, h + 20), "terrace: green = earth, blue = deck over the bay, grey = retaining wall; orange = pad of bonfire 3", fill=(255, 255, 255))
    img.save(path)

def data_files():
    from r1 import replace_lines
    replace_lines(os.path.join(ROOT, "zones/zones.txt"), ["maze "], ["maze            overworld box  %d %d %d  %d %d %d   no_blink,no_chorus   # T-024: Enchanted Maze (ground -8 .. ceiling +4)" % (OX1, G - 8, OZ1, OX2, CEIL + 4, OZ2)])
    replace_lines(os.path.join(ROOT, "zones/zones.txt"), ["maze_sanctum "], ["maze_sanctum    overworld cyl  %d %d 11  %d %d     no_spawn" % (CX, CZ, G - 2, G + 17)])
    replace_lines(os.path.join(ROOT, "altars/keys.txt"), ["thread_labyrinth "], ["thread_labyrinth 1 %d,%d,%d Нить Лабиринта" % (CX, Y + 2, CZ)])
    rp = os.path.join(ROOT, "biomes/registry.json"); s = open(rp, encoding="utf-8").read()
    import re
    s2 = re.sub(r'\{"id": "hedge_maze", "shape": "rect", "v": \[[^\]]*\]', '{"id": "hedge_maze", "shape": "rect", "v": [%d, %d, %d, %d]' % (TX1, TZ1, TX2, TZ2), s)
    if s2 != s: open(rp, "w", encoding="utf-8").write(s2)

def main():
    cells = plan()
    bad = check_729(cells)
    if bad: raise SystemExit("the plan has bad combinations")
    gr = grids(); tr = terrace(gr)
    b, guard_xz = maze_blocks(cells)
    nf = terrace_blocks(gr, tr, b)
    nt = clear_trees(gr, tr, b)
    from connect import connect
    connect(b)
    outside = [k for k in b.v if not in_place(k[0], k[2])]
    if outside: raise SystemExit("blocks outside the place: %s" % outside[:5])
    inpad = [k for k in b.v if PAD[0] <= k[0] <= PAD[2] and PAD[1] <= k[2] <= PAD[3]]
    if inpad: raise SystemExit("blocks on the pad of bonfire 3: %s" % inpad[:5])
    ncol = write_terrain(gr, tr, b)
    n = b.write_placements(os.path.join(OUT, "maze.txt"))
    import maze_dp
    statues, probes, GD = maze_dp.run(sys.modules[__name__], cells)
    data_files()
    meta = dict(G=G, ceil=CEIL, gate=[-150, Y, OZ2 + 1], sanctum=[CX, Y, CZ], key=[CX, Y + 2, CZ], exit_in=[-151, Y, EXIT_Z[1]], exit_out=[-151, Y, OZ1 - 3],
                hearth=list(HEARTH), movable=[[*cell_origin(c)] for c in MOVABLE], statues=statues, guards={k: [v["x1"], v["z1"]] for k, v in GD.items()},
                terrain_columns=ncol, blocks=n, face_blocks=nf, cleared=nt, walls=int(tr["wall"].sum()), deck=int(tr["deck"].sum()))
    json.dump(meta, open(os.path.join(OUT, "maze.json"), "w"), ensure_ascii=False)
    os.makedirs(os.path.join(ROOT, "docs/reports/T-024"), exist_ok=True)
    plan_png(cells, statues, tr, gr, os.path.join(ROOT, "docs/reports/T-024/maze_plan.png"))
    print(f"maze: terrain {ncol} columns, {n} blocks (wall faces {nf}, cleared {nt}), statues {len(statues)}, wall columns {int(tr['wall'].sum())}, deck {int(tr['deck'].sum())}")
if __name__ == "__main__" and sys.argv[1:2] != ["check"]: main()
