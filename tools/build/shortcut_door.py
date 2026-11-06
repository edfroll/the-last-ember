#!/usr/bin/env python3
"""T-021: the shortcut door inside a region (card «Ворота шорткатов», «Дверь шортката в регионе»).

Portal 9x10 of the region's accent block with an arch 3x5, a heavy dark oak door (1 wide) in a plank frame, behind it a vestibule
7x7 (inner), height 5, ending in a blank wall (the transfer trigger: a box 5x3x3 at the wall). Locked: chains criss-cross in the
arch above the door. Open: chains gone, 2 lanterns in the vestibule, the door open. One template 9x10x10 per region.

Local frame: u = depth into the rock (0 = portal face, 9 = blank wall), v = to the right when looking into the rock (-4..4),
dy = height from the floor block (0..9). Canonical template: the door faces south (the region side is +z, the rock is -z):
template x = v + 4, y = dy, z = 9 - u (origin = min corner). The door block (lower half) is (u 1, v 0, dy 1) = template (4, 1, 8).

  python3 tools/build/shortcut_door.py [rN ...]     -> datapack/data/last_ember/structure/shortcut/door_rN.nbt (all 6 by default)
The geometry helpers (world cells of the door, chains, lanterns, trigger, exit for a door position and yaw) are imported by
tools/gen_gates.py."""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "datapack/data/last_ember/structure/shortcut")
TMP = os.path.join(ROOT, "server/build/shortcut")
# accent of the portal, its second accent (sign relief), local stone of the vestibule, its floor, the lantern
REG = {"r1": ("mossy_stone_bricks", "moss_block", "mossy_cobblestone", "cobblestone", "lantern"),
       "r2": ("prismarine_bricks", "dark_prismarine", "stone", "polished_andesite", "lantern"),
       "r3": ("calcite", "packed_ice", "packed_ice", "polished_diorite", "lantern"),
       "r4": ("cut_red_sandstone", "chiseled_red_sandstone", "red_sandstone", "smooth_red_sandstone", "lantern"),
       "r5": ("deepslate_tiles", "chiseled_deepslate", "deepslate", "polished_deepslate", "lantern"),
       "r6": ("polished_blackstone", "polished_basalt[axis=y]", "blackstone", "polished_blackstone_bricks", "soul_lantern")}
DOOR = (1, 0, 1)                       # (u, v, dy) of the lower door half
CHAINS = [(0, -1, 5), (0, 1, 5), (0, 0, 4), (0, -1, 3), (0, 1, 3)]      # criss-cross in the arch above the door
LANTERNS = [(3, 0, 5), (6, 0, 5)]      # hanging from the ceiling (dy 6)
TRIGGER = ((6, 8), (-2, 2), (1, 3))    # u, v, dy ranges (inclusive): 5x3x3 at the blank wall
EXIT = (4, 0, 1)                       # the middle of the vestibule, facing the door
CLICK = (0, 0, 1)                      # the interaction in the arch in front of the door

def model(reg):
    acc, acc2, loc, floor, _ = REG[reg]; m = {}
    for u in range(0, 10):
        for v in range(-4, 5):
            for dy in range(0, 10):
                s = loc
                if u == 0:
                    s = "air" if (abs(v) <= 1 and 1 <= dy <= 5) else acc
                elif u == 1:
                    if abs(v) <= 1 and 1 <= dy <= 5: s = "dark_oak_planks"
                elif 2 <= u <= 8 and abs(v) <= 3 and 1 <= dy <= 5: s = "air"
                elif 2 <= u <= 8 and abs(v) <= 3 and dy == 0: s = floor
                m[(u, v, dy)] = s
    # the region's sign above the arch: keystone and relief of the second accent
    m[(0, 0, 7)] = "chiseled_stone_bricks"; m[(0, -1, 7)] = acc2; m[(0, 1, 7)] = acc2; m[(0, 0, 8)] = acc2; m[(0, 0, 6)] = acc2
    m[(1, 0, 1)] = "dark_oak_door[facing=south,half=lower,hinge=left,open=false]"
    m[(1, 0, 2)] = "dark_oak_door[facing=south,half=upper,hinge=left,open=false]"
    for c in CHAINS: m[c] = "iron_chain[axis=y]"
    for u in range(3, 6):                                     # benches along the side walls
        m[(u, -3, 1)] = "%s_stairs[facing=west,half=bottom,shape=straight]" % ("deepslate_brick" if reg != "r4" else "red_sandstone")
        m[(u, 3, 1)] = "%s_stairs[facing=east,half=bottom,shape=straight]" % ("deepslate_brick" if reg != "r4" else "red_sandstone")
    return m

def tcoord(u, v, dy): return v + 4, dy, 9 - u
# rotation of the template for a door yaw (MC yaw: 0 south, 90 west, 180 north, 270 east) and the world offset of a template cell
ROT = {0: "none", 90: "clockwise_90", 180: "180", 270: "counterclockwise_90"}
FACE = {0: "south", 90: "west", 180: "north", 270: "east"}
def trot(yaw, x, z):
    if yaw == 0: return x, z
    if yaw == 90: return -z, x          # StructureTemplate CLOCKWISE_90 about the origin
    if yaw == 180: return -x, -z
    if yaw == 270: return z, -x         # COUNTERCLOCKWISE_90
def world(door, yaw, u, v, dy):
    """world cell of local (u, v, dy) for a door (lower half) at door=(x, y, z) facing yaw"""
    tx, ty, tz = tcoord(u, v, dy); dx0, dz0 = trot(yaw, *tcoord(*DOOR)[0::2]); x, z = trot(yaw, tx, tz)
    return door[0] + x - dx0, door[1] + ty - 1, door[2] + z - dz0
def origin(door, yaw):
    """the position for `place template` (the template origin after rotation)"""
    dx0, dz0 = trot(yaw, *tcoord(*DOOR)[0::2]); return door[0] - dx0, door[1] - 1, door[2] - dz0
def norm_yaw(y):
    y = int(y) % 360
    if y not in ROT: raise ValueError("door yaw must be 0, 90, 180 or 270 (-90): %s" % y)
    return y

def build(reg):
    os.makedirs(TMP, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    p = os.path.join(TMP, "door_%s.txt" % reg)
    with open(p, "w") as f:
        for (u, v, dy), s in sorted(model(reg).items()):
            x, y, z = tcoord(u, v, dy); f.write("%d %d %d minecraft:%s\n" % (x, y, z, s))
    bw = os.path.join(ROOT, "tools/blockwriter.sh")
    r = subprocess.run([bw, "nbt", p, "0", "0", "0", os.path.join(OUT, "door_%s.nbt" % reg)], capture_output=True, text=True)
    out = [l for l in r.stdout.splitlines() if l.startswith("nbt:")]
    if r.returncode or not out: raise SystemExit(r.stdout + r.stderr)
    print(out[0])

if __name__ == "__main__":
    for reg in (sys.argv[1:] or sorted(REG)): build(reg)
