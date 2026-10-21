"""Shortcut gates (card «Ворота шорткатов»): portal 9x10 in the arcade wall, 5x7 opening with iron bars (closed) and dark oak
leaves behind, vestibule 7x9 (height 6) going outward, ending in a blank wall (transfer trigger). Region sign = accent blocks
around the keystone. Built in local coordinates (u outward from the arcade wall, v to the right) and rotated to the gate angle."""
import math
from lib import B, Mix, h
from geo import FLOOR, unrot, face_rot
ACCENT = {"r1": ("mossy_stone_bricks", "red_poplar_leaves[persistent=true]"), "r2": ("prismarine_bricks", None), "r3": ("calcite", "packed_ice"),
          "r4": ("cut_red_sandstone", None), "r5": ("deepslate_tiles", "iron_chain"), "r6": ("polished_blackstone", "basalt")}
R0 = 30
def local_model(reg):
    acc, acc2 = ACCENT[reg]; m = {}
    def put(u, v, dy, s): m[(u, v, dy)] = s
    for u in range(0, 3):                              # wall thickness 3 (u 0..2), portal frame 9 wide, 10 high
        for v in range(-4, 5):
            for dy in range(1, 11):
                inside = abs(v) <= 2 and dy <= 7
                if inside: put(u, v, dy, "air")
                else: put(u, v, dy, "polished_tuff" if abs(v) in (3, 4) and u == 0 else "stone_bricks")
    for v in range(-3, 4): put(0, v, 8, "stone_bricks"); put(0, v, 9, "stone_bricks")
    put(0, 0, 9, "chiseled_stone_bricks"); put(0, -1, 9, acc); put(0, 1, 9, acc); put(0, 0, 10, acc); put(0, 0, 8, acc)
    for v in range(-2, 3):
        for dy in range(1, 8): put(1, v, dy, "iron_bars")           # portcullis (closed)
    for v in range(-2, 3):
        for dy in range(3, 8): put(2, v, dy, "dark_oak_planks")
    put(2, -2, 1, "dark_oak_door[facing=SOUTHIN,half=lower,hinge=left,open=false]"); put(2, -2, 2, "dark_oak_door[facing=SOUTHIN,half=upper,hinge=left,open=false]")
    put(2, -1, 1, "dark_oak_door[facing=SOUTHIN,half=lower,hinge=right,open=false]"); put(2, -1, 2, "dark_oak_door[facing=SOUTHIN,half=upper,hinge=right,open=false]")
    put(2, 1, 1, "dark_oak_door[facing=SOUTHIN,half=lower,hinge=left,open=false]"); put(2, 1, 2, "dark_oak_door[facing=SOUTHIN,half=upper,hinge=left,open=false]")
    put(2, 2, 1, "dark_oak_door[facing=SOUTHIN,half=lower,hinge=right,open=false]"); put(2, 2, 2, "dark_oak_door[facing=SOUTHIN,half=upper,hinge=right,open=false]")
    put(2, 0, 1, "dark_oak_planks"); put(2, 0, 2, "dark_oak_planks")
    for u in range(3, 13):                             # vestibule 7 wide inside, height 6, walls, roof, floor
        for v in range(-4, 5):
            put(u, v, 0, "polished_deepslate")
            for dy in range(1, 8):
                wall = abs(v) == 4 or dy == 7 or u == 12
                put(u, v, dy, "deepslate_bricks" if wall else "air")
        if 4 <= u <= 10:
            put(u, -3, 1, "deepslate_brick_stairs[facing=RIGHT,half=bottom,shape=straight]"); put(u, 3, 1, "deepslate_brick_stairs[facing=LEFT,half=bottom,shape=straight]")
    if acc2:
        for v in (-4, 4): put(0, v, 1, acc2 if "leaves" not in acc2 and "iron_chain" not in acc2 else ("flower_pot" if "leaves" in acc2 else acc2))
    return m
def build(ang, reg):
    m = local_model(reg); b = B(f"gate_{reg}"); y = FLOOR
    us = [k[0] for k in m]; vs = [k[1] for k in m]
    pts = []
    for u in (min(us) - 1, max(us) + 1):
        for v in (min(vs) - 1, max(vs) + 1):
            a = math.radians(ang); pts.append((R0 + u) * math.sin(a) + v * math.cos(a)); pts.append(-(R0 + u) * math.cos(a) + v * math.sin(a))
    xs, zs = pts[0::2], pts[1::2]
    for x in range(int(min(xs)) - 1, int(max(xs)) + 2):
        for z in range(int(min(zs)) - 1, int(max(zs)) + 2):
            u, v = unrot(0, 0, ang, x, z); ui, vi = int(round(u - R0)), int(round(v))
            for dy in range(0, 11):
                s = m.get((ui, vi, dy))
                if s is None: continue
                s = s.replace("SOUTHIN", face_rot("in", ang)).replace("RIGHT", face_rot("left", ang)).replace("LEFT", face_rot("right", ang))
                b.set(x, y + dy, z, s)
    def at(u, v): x, z = (round(R0 * 0 + (R0 + u) * math.sin(math.radians(ang)) + v * math.cos(math.radians(ang))), round(-(R0 + u) * math.cos(math.radians(ang)) + v * math.sin(math.radians(ang)))); return x, z
    for name, u, dy in (("gate_swap", 1, 1), ("gate_banner", -1, 10), ("gate_exit", 7, 1), ("gate_transfer", 11, 1)):
        x, z = at(u, 0); b.marker(f"{name}_{reg}", x, y + dy, z, f"angle {ang}")
    return b
